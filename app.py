from flask import Flask, render_template, request, redirect, session, url_for, g
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# Pages
pages = ["Home", "About", "Programmes", "News", "Contact", "Volunteer", "DONATE",]

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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



# Route for index page
@app.route('/')
def index():
    return render_template('index.html', pages=pages, users = users)

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


# Run the app
if __name__ == '__main__':
    app.run(debug=True)