import pytest
from models import db, Category


class TestViewCategories:
    """Test view categories route."""
    
    def test_view_categories_requires_admin(self, client, test_user):
        """Test view categories requires admin."""
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        response = client.get('/categories', follow_redirects=False)
        assert response.status_code == 302
        assert '/dashboard' in response.location
    
    def test_view_categories_list(self, client, test_admin, test_category):
        """Test viewing categories list."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'adminpass123'
        })
        response = client.get('/categories')
        assert response.status_code == 200
        assert b'Laptop' in response.data


class TestAddCategory:
    """Test add category route."""
    
    def test_add_category_page_loads(self, client, test_admin):
        """Test add category page is accessible."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'adminpass123'
        })
        response = client.get('/categories/add')
        assert response.status_code == 200
    
    def test_add_category_success(self, client, test_admin):
        """Test successful category creation."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'adminpass123'
        })
        
        response = client.post('/categories/add', data={
            'name': 'Desktop',
            'description': 'Desktop computers'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        category = Category.query.filter_by(name='Desktop').first()
        assert category is not None
        assert category.description == 'Desktop computers'
    
    def test_add_category_missing_name(self, client, test_admin):
        """Test add category fails with missing name."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'adminpass123'
        })
        
        response = client.post('/categories/add', data={
            'name': '',
            'description': 'Some description'
        })
        
        assert response.status_code == 200
        category = Category.query.filter_by(description='Some description').first()
        assert category is None
    
    def test_add_category_duplicate_name(self, client, test_admin, test_category):
        """Test add category fails with duplicate name."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'adminpass123'
        })
        
        response = client.post('/categories/add', data={
            'name': 'Laptop',  # Duplicate
            'description': 'Different description'
        })
        
        assert response.status_code == 200
        categories = Category.query.filter_by(name='Laptop').all()
        assert len(categories) == 1
    
    def test_add_category_optional_description(self, client, test_admin):
        """Test add category with no description."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'adminpass123'
        })
        
        response = client.post('/categories/add', data={
            'name': 'Tablet',
            'description': ''
        }, follow_redirects=True)
        
        assert response.status_code == 200
        category = Category.query.filter_by(name='Tablet').first()
        assert category is not None
        assert category.description is None or category.description == ''

