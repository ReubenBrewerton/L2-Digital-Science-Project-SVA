from flask import Flask, render_template, request, redirect, session, url_for, g 
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_login import LoginManager

# Pages
pages = ["Home", "About", "Contact", "Volunteer", "DONATE",]

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


# Sanitize page names to create routes
def sanitize_route(page_name):
    return page_name.lower().replace(" ", "_")

# Gets the current page name
def catch_all(path):
    current_page = request.path

# Route for all pages except volunteer
@app.route('/<page_name>')
def page(page_name):
    sanitized_page_name = sanitize_route(page_name) # Use the sanitized page name
    if sanitized_page_name in [sanitize_route(p) for p in pages]:
        return render_template(f'{sanitized_page_name}.html', pages=pages, users = users) # Renders the html file for the sanitized page
    else:
        return "Page not found", 404
    
# Route for volunteer page
@app.route('/volunteer')
@login_required
def volunteer():
    return render_template('volunteer.html', pages=pages, users=users)

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




