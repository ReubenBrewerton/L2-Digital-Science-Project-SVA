from flask import Flask, render_template, request, redirect, session, url_for, g 
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_login import login_required, current_user, login_user, logout_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash 
from datetime import datetime

# Pages
pages = ["Home", "About", "Contact", "Volunteer"]

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'my_secret_key'



# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Initialize the database
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    hours = db.Column(db.Integer, nullable=True)

    # Flask-Login required properties and methods
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

# Define the mailing list model
class mailinglist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)

# Define the Contact model
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    message = db.Column(db.Text, nullable=False)

# Define the Activity model
class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(80), nullable=False) 
    time = db.Column(db.String(80), nullable=False)  
    location = db.Column(db.String(120), nullable=False)

# Define the activities
activities = [
    Activity(name='Beach Cleanup', description='Join us for a beach cleanup to keep our shores clean.', date='2025-10-01', time='10:00 AM - 2:00 PM', location='Local Beach'),
    Activity(name='Tree Planting', description='Help us plant trees in the community park.', date='2025-10-15', time='9:00 AM - 1:00 PM', location='Community Park'),
    Activity(name='Food Drive', description='Donate non-perishable food items to help those in need.', date='2025-10-20', time='8:00 AM - 4:00 PM', location='Community Center'),
]

# Initialize the database and create tables if they don't exist
with app.app_context():
    db.create_all()
    users = User.query.all()


# Route for index page
@app.route('/')
def index():
    return render_template('index.html', pages=pages, users = users)

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            return "Email is required", 400
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        confirm_password = request.form.get('confirm_password')

        # Check if passwords match
        if password != confirm_password:
            passwords_match = False
            return render_template('signup.html', pages=pages, passwords_match=passwords_match)  # Redirect to signup if passwords do not match

        # Check if the user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            existing = True
            return render_template('signup.html', existing=existing, pages=pages)  # Redirect to signup if user exists
        else:
            # Create a new user
            new_user = User(
                email=email, 
                password=generate_password_hash(password, method='pbkdf2:sha256', salt_length=8), 
                first_name=first_name, 
                last_name=last_name,
                hours=0  # Initialize hours to 0
            )
            with app.app_context():
                db.session.add(new_user)
                db.session.commit()
            success = True
            return render_template('signup.html', success=success, pages=pages)
        
        

    return render_template('signup.html', pages=pages)
    

 
# Route for login page
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Authenticate user
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password.strip()):
            login_user(user)
            return redirect(url_for('volunteer')) # Redirect to volunteer page after successful login
        else:
            invalid_login = True
            return render_template('login.html', pages=pages, invalid_login=invalid_login)

    return render_template('login.html', pages=pages)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('login'))  # Redirect to login page after logout

@app.route('/log_hours', methods=['GET', 'POST'])
def log_hours():
    hours = calculateTimeDifference(request.form.get('start_time'), request.form.get('end_time'))
    if not hours:
        hours_required = True
        return redirect(url_for('volunteer', hours_required=hours_required))
    #if ValueError:
        invalid_hours = True
        return redirect(url_for('volunteer', invalid_hours=invalid_hours))
    if hours <= 0:
        less_than_zero = True
        return redirect(url_for('volunteer', less_than_zero=less_than_zero))
    if hours > 24:
        exceeded_24 = True
        return redirect(url_for('volunteer', exceeded_24=exceeded_24))
    # Update current user's hours
    current_user.hours += hours
    db.session.commit()
    activity_name = request.form.get('activity')
    if not activity_name:
        return "Activity name is required", 400
    # Create a new activity entry
    new_activity = Activity(
        name=activity_name,
        description=f"Logged {hours} hours for {activity_name}",
        date=datetime.now().strftime('%Y-%m-%d'),
        time=datetime.now().strftime('%H:%M'),
    )
        
    return redirect(url_for('volunteer'))

# Sanitize page names to create routes
def sanitize_route(page_name):
    return page_name.lower().replace(" ", "_")

# Gets the current page name
def catch_all(path):
    current_page = request.path

# Route for all pages
@app.route('/<page_name>')
def page(page_name):
    sanitized_page_name = sanitize_route(page_name) # Use the sanitized page name
    if sanitized_page_name in [sanitize_route(p) for p in pages]:
        return render_template(f'{sanitized_page_name}.html', pages=pages, users = users) # Renders the html file for the sanitized page
    else:
        return "Page not found", 404

# Badge calculation logic moved to a function
def calculate_badge(hours):
    if hours < 5 and hours >= 0:
        current_badge = "No Badge"  # Current badge is No Badge
        next_badge = "Member Badge"
        remaining_hours = 5 - (hours % 5)
    elif hours < 32 and hours >= 5:
        current_badge = "Member Badge"  # Current badge is Member
        next_badge = "Bronze Badge"
        remaining_hours = 32 - (hours % 32)
    elif hours < 250 and hours >= 32:
        current_badge = "Bronze Badge"  # Current badge is Bronze
        next_badge = "Silver Badge"
        remaining_hours = 250 - (hours % 250)
    elif hours < 500 and hours >= 250:
        current_badge = "Silver Badge"  # Current badge is Silver
        next_badge = "Gold Badge"
        remaining_hours = 500 - (hours % 500)
    else:
        current_badge = "Gold Badge"  # Current badge is Gold
        next_badge = "No next badge. Congratulations on reaching the maximum badge level!"
        remaining_hours = 0
    return next_badge, remaining_hours, current_badge

# Route for volunteer page
@app.route('/volunteer')
@login_required
def volunteer():
    exceeded_24 = request.args.get('exceeded_24', False, type=bool)
    less_than_zero = request.args.get('less_than_zero', False, type=bool)
    invalid_hours = request.args.get('invalid_hours', False, type=bool)
    hours_required = request.args.get('hours_required', False, type=bool)
    hours = current_user.hours
    next_badge, remaining_hours, current_badge = calculate_badge(hours)
    return render_template('volunteer.html', pages=pages, users=users, activities=activities, hours=hours,
                            next_badge=next_badge, remaining_hours=remaining_hours, current_badge=current_badge, 
                            exceeded_24=exceeded_24, less_than_zero=less_than_zero, invalid_hours=invalid_hours, hours_required=hours_required)

def calculateTimeDifference(start_time, end_time):
    # convert start_time and end_time to hours
    end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M')
    start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
    time_difference = end_time - start_time
    # convert time_difference to hours
    hours = time_difference.total_seconds() / 3600
    return hours

completed_activities = []

# Get contact information
@app.route('/Contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        message = request.form.get('message')

        # Check if the user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return redirect(url_for('index'))
        
        # Create a new contact entry
        new_contact = Contact(email=email, name=name, message=message)
        db.session.add(new_contact)
        db.session.commit()
        return redirect(url_for('index'))  # Redirect to index after handling POST request

    return render_template('contact.html', pages=pages)  # Render contact page for GET request

@app.route('/donate', methods=['POST'])
def donate():
    donation_amount = request.form.get('amount')
    


@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')

    # Check if the user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return redirect(url_for('index'))  # Redirect to index if user exists

    # Create a new user
    new_user = mailinglist(email=email)
    db.session.add(new_user)
    db.session.commit()
    
    return redirect(url_for('index'))  # Redirect to index after subscribing

# Run the app
if __name__ == '__main__':
    app.run(debug=True)




