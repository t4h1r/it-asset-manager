import pytest
import os
import sys
from datetime import datetime

# Ensure the project root (where app.py lives) is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app as flask_app
from models import db, User, Asset, Category, Location
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    """Create Flask test app with in-memory database."""
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_app.config['WTF_CSRF_ENABLED'] = False
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create Flask test client."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Provide database session with automatic rollback."""
    with app.app_context():
        yield db.session
        db.session.rollback()


@pytest.fixture
def test_user(db_session):
    """Create a regular test user."""
    user = User(
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('testpass123'),
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_admin(db_session):
    """Create an admin test user."""
    admin = User(
        username='admin',
        email='admin@example.com',
        password=generate_password_hash('adminpass123'),
        is_admin=True
    )
    db_session.add(admin)
    db_session.commit()
    return admin


@pytest.fixture
def test_category(db_session):
    """Create a test category."""
    category = Category(
        name='Laptop',
        description='Laptop computers'
    )
    db_session.add(category)
    db_session.commit()
    return category


@pytest.fixture
def test_location(db_session):
    """Create a test location."""
    location = Location(
        name='Main Office',
        building='Building A',
        floor='2nd Floor',
        room='Room 201'
    )
    db_session.add(location)
    db_session.commit()
    return location


@pytest.fixture
def test_asset(db_session, test_category, test_location):
    """Create a test asset."""
    asset = Asset(
        asset_tag='LAP-001',
        name='Dell Latitude 7420',
        description='Business laptop',
        serial_number='SN123456',
        manufacturer='Dell',
        model='Latitude 7420',
        status='Active',
        assigned_to='John Doe',
        category_id=test_category.id,
        location_id=test_location.id
    )
    db_session.add(asset)
    db_session.commit()
    return asset

