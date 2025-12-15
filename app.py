# IT Asset Management System
# Main Flask Application
# Author: Tahir Uddin


from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///it_assets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
from models import db
db.init_app(app)

# Import models and routes after db initialization
from models import User, Asset, Category, Location
from routes import *

# Ensure database tables exist and default admin is created,
# even when running under Gunicorn (Render) where __main__ is not executed.
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@company.com',
            password=generate_password_hash('Admin@123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created: username='admin', password='Admin@123'")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
