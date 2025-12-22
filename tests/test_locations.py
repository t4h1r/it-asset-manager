import pytest
from models import db, Location


class TestViewLocations:
    """Test view locations route."""
    
    def test_view_locations_requires_admin(self, client, test_user):
        """Test view locations requires admin."""
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        response = client.get('/locations', follow_redirects=False)
        assert response.status_code == 302
        assert '/dashboard' in response.location
    
    def test_view_locations_list(self, client, test_admin, test_location):
        """Test viewing locations list."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'adminpass123'
        })
        response = client.get('/locations')
        assert response.status_code == 200
        assert b'Main Office' in response.data


class TestAddLocation:
    """Test add location route."""
    
    def test_add_location_page_loads(self, client, test_admin):
        """Test add location page is accessible."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'adminpass123'
        })
        response = client.get('/locations/add')
        assert response.status_code == 200
    
    def test_add_location_success(self, client, test_admin):
        """Test successful location creation."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'adminpass123'
        })
        
        response = client.post('/locations/add', data={
            'name': 'Remote Office',
            'building': 'Building B',
            'floor': '1st Floor',
            'room': 'Room 101'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        location = Location.query.filter_by(name='Remote Office').first()
        assert location is not None
        assert location.building == 'Building B'
        assert location.floor == '1st Floor'
        assert location.room == 'Room 101'
    
    def test_add_location_missing_name(self, client, test_admin):
        """Test add location fails with missing name."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'adminpass123'
        })
        
        response = client.post('/locations/add', data={
            'name': '',
            'building': 'Building A'
        })
        
        assert response.status_code == 200
        location = Location.query.filter_by(building='Building A').first()
        assert location is None
    
    def test_add_location_duplicate_name(self, client, test_admin, test_location):
        """Test add location fails with duplicate name."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'adminpass123'
        })
        
        response = client.post('/locations/add', data={
            'name': 'Main Office',  # Duplicate
            'building': 'Different Building'
        })
        
        assert response.status_code == 200
        locations = Location.query.filter_by(name='Main Office').all()
        assert len(locations) == 1
    
    def test_add_location_optional_fields(self, client, test_admin):
        """Test add location with optional fields empty."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'adminpass123'
        })
        
        response = client.post('/locations/add', data={
            'name': 'Simple Location',
            'building': '',
            'floor': '',
            'room': ''
        }, follow_redirects=True)
        
        assert response.status_code == 200
        location = Location.query.filter_by(name='Simple Location').first()
        assert location is not None
        assert location.building == '' or location.building is None

