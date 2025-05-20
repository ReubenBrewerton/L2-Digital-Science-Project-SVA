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

def sanitize_route(page_name):
    # Sanitize page names to create routes
    return page_name.lower().replace(" ", "_")

# Route for each page
@app.route('/')
def index():
    return render_template('index.html', pages=pages, users = users)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)