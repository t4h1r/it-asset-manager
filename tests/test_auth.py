import pytest
from flask import session
from models import db, User
from werkzeug.security import check_password_hash


class TestRegistration:
    """Test user registration."""
    
    def test_register_page_loads(self, client):
        """Test registration page is accessible."""
        response = client.get('/register')
        assert response.status_code == 200
    
    def test_register_success(self, client, db_session):
        """Test successful user registration."""
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'newuser@example.com'
        assert check_password_hash(user.password, 'password123')
        assert user.is_admin is False
    
    def test_register_username_too_short(self, client):
        """Test registration fails with short username."""
        response = client.post('/register', data={
            'username': 'ab',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        assert response.status_code == 200
        user = User.query.filter_by(username='ab').first()
        assert user is None
    
    def test_register_invalid_email(self, client):
        """Test registration fails with invalid email."""
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        assert response.status_code == 200
        user = User.query.filter_by(username='testuser').first()
        assert user is None
    
    def test_register_password_too_short(self, client):
        """Test registration fails with short password."""
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'short',
            'confirm_password': 'short'
        })
        
        assert response.status_code == 200
        user = User.query.filter_by(username='testuser').first()
        assert user is None
    
    def test_register_password_mismatch(self, client):
        """Test registration fails when passwords don't match."""
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'different123'
        })
        
        assert response.status_code == 200
        user = User.query.filter_by(username='testuser').first()
        assert user is None
    
    def test_register_duplicate_username(self, client, test_user):
        """Test registration fails with duplicate username."""
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'different@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        assert response.status_code == 200
        users = User.query.filter_by(username='testuser').all()
        assert len(users) == 1
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration fails with duplicate email."""
        response = client.post('/register', data={
            'username': 'different',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        assert response.status_code == 200
        users = User.query.filter_by(email='test@example.com').all()
        assert len(users) == 1


class TestLogin:
    """Test user login."""
    
    def test_login_page_loads(self, client):
        """Test login page is accessible."""
        response = client.get('/login')
        assert response.status_code == 200
    
    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        with client.session_transaction() as sess:
            assert 'user_id' in sess
            assert sess['user_id'] == test_user.id
            assert sess['username'] == 'testuser'
            assert sess['is_admin'] is False
    
    def test_login_invalid_username(self, client, test_user):
        """Test login fails with invalid username."""
        response = client.post('/login', data={
            'username': 'wronguser',
            'password': 'testpass123'
        })
        
        assert response.status_code == 200
        with client.session_transaction() as sess:
            assert 'user_id' not in sess
    
    def test_login_invalid_password(self, client, test_user):
        """Test login fails with invalid password."""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 200
        with client.session_transaction() as sess:
            assert 'user_id' not in sess
    
    def test_login_empty_credentials(self, client):
        """Test login fails with empty credentials."""
        response = client.post('/login', data={
            'username': '',
            'password': ''
        })
        
        assert response.status_code == 200
        with client.session_transaction() as sess:
            assert 'user_id' not in sess
    
    def test_login_admin_session_flag(self, client, test_admin):
        """Test admin user has is_admin flag in session."""
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'adminpass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        with client.session_transaction() as sess:
            assert sess['is_admin'] is True


class TestLogout:
    """Test user logout."""
    
    def test_logout_clears_session(self, client, test_user):
        """Test logout clears session."""
        # Login first
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Verify session exists
        with client.session_transaction() as sess:
            assert 'user_id' in sess
        
        # Logout
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        
        # Verify session cleared
        with client.session_transaction() as sess:
            assert 'user_id' not in sess


class TestLoginRequired:
    """Test @login_required decorator."""
    
    def test_dashboard_requires_login(self, client):
        """Test dashboard redirects when not logged in."""
        response = client.get('/dashboard', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_assets_requires_login(self, client):
        """Test assets page redirects when not logged in."""
        response = client.get('/assets', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_dashboard_allows_authenticated(self, client, test_user):
        """Test dashboard accessible when logged in."""
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        response = client.get('/dashboard')
        assert response.status_code == 200


class TestAdminRequired:
    """Test @admin_required decorator."""
    
    def test_categories_requires_admin(self, client, test_user):
        """Test categories page requires admin access."""
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        response = client.get('/categories', follow_redirects=False)
        assert response.status_code == 302
        assert '/dashboard' in response.location
    
    def test_categories_allows_admin(self, client, test_admin):
        """Test categories page accessible by admin."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'adminpass123'
        })
        response = client.get('/categories')
        assert response.status_code == 200
    
    def test_locations_requires_admin(self, client, test_user):
        """Test locations page requires admin access."""
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        response = client.get('/locations', follow_redirects=False)
        assert response.status_code == 302
        assert '/dashboard' in response.location
    
    def test_delete_asset_requires_admin(self, client, test_user, test_asset):
        """Test delete asset requires admin access."""
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        response = client.post(f'/assets/delete/{test_asset.id}', follow_redirects=False)
        assert response.status_code == 302
        assert '/dashboard' in response.location

