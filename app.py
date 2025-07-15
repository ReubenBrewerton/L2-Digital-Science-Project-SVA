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


with app.app_context():
    # Initialize the database
    db = SQLAlchemy(app)
    # Creating the table
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(80), unique=True, nullable=False)
        password = db.Column(db.String(120), nullable=False)
        first_name = db.Column(db.String(80), nullable=False)
        last_name = db.Column(db.String(80), nullable=False)
        hours = db.Column(db.Integer, nullable=True)
    db.create_all()
    users = User.query.all()

with app.app_context():
    # Create a mailing list table
    class mailinglist(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(80), unique=True, nullable=False)
    db.create_all()

with app.app_context():
    # Contact table
    class Contact(db.Model):
        id= db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(80), nullable=False)
        name = db.Column(db.String(80), nullable=False)
        message = db.Column(db.Text, nullable=False)
    db.create_all()


# Route for index page
@app.route('/')
def index():
    return render_template('index.html', pages=pages, users = users)

# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Authenticate user
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            return "Invalid credentials", 401

    return render_template('login.html', pages=pages)

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




