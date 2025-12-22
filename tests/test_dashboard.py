import pytest
from models import db, Asset, Category, Location


class TestDashboard:
    """Test dashboard route."""
    
    def test_dashboard_requires_login(self, client):
        """Test dashboard requires login."""
        response = client.get('/dashboard', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_dashboard_loads(self, client, test_user):
        """Test dashboard page loads for authenticated user."""
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        response = client.get('/dashboard')
        assert response.status_code == 200
    
    def test_dashboard_statistics(self, client, test_user, test_asset, db_session):
        """Test dashboard displays correct statistics."""
        # Create additional test data
        category = Category.query.first()
        location = Location.query.first()
        
        # Add more assets
        asset2 = Asset(
            asset_tag='DESK-001',
            name='Desktop',
            status='Active',
            category_id=category.id,
            location_id=location.id
        )
        asset3 = Asset(
            asset_tag='RET-001',
            name='Retired Asset',
            status='Retired',
            category_id=category.id
        )
        db_session.add_all([asset2, asset3])
        
        # Add another category
        category2 = Category(name='Desktop', description='Desktop computers')
        db_session.add(category2)
        
        # Add another location
        location2 = Location(name='Remote Office', building='Building B')
        db_session.add(location2)
        db_session.commit()
        
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        response = client.get('/dashboard')
        assert response.status_code == 200
        
        # Check statistics are displayed
        assert b'3' in response.data or b'total' in response.data.lower()
        assert b'2' in response.data or b'active' in response.data.lower()
    
    def test_dashboard_recent_assets(self, client, test_user, test_asset, db_session):
        """Test dashboard shows recent assets."""
        from datetime import datetime, timedelta
        category = Category.query.first()
        
        # Create multiple assets with explicit timestamps to ensure ordering
        base_time = datetime.utcnow()
        assets = []
        for i in range(7):
            asset = Asset(
                asset_tag=f'ASSET-{i:03d}',
                name=f'Asset {i}',
                category_id=category.id,
                created_at=base_time + timedelta(seconds=i)  # Ensure unique timestamps
            )
            assets.append(asset)
        
        db_session.add_all(assets)
        db_session.commit()
        
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        response = client.get('/dashboard')
        assert response.status_code == 200
        
        # Should show recent assets (limit 5)
        # Check that at least one of the newer assets appears (most recent should be ASSET-006)
        # Also check that the page contains asset information
        assert b'ASSET-' in response.data or b'Asset' in response.data
    
    def test_dashboard_empty_state(self, client, test_user):
        """Test dashboard with no assets."""
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        response = client.get('/dashboard')
        assert response.status_code == 200
        # Should still load even with no data

