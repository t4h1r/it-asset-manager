import pytest
from models import db, Asset, Category, Location


class TestViewAssets:
    """Test view assets route."""
    
    def test_view_assets_requires_login(self, client):
        """Test view assets requires login."""
        response = client.get('/assets', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_view_assets_list(self, client, test_user, test_asset):
        """Test viewing assets list."""
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        response = client.get('/assets')
        assert response.status_code == 200
        assert b'LAP-001' in response.data
        assert b'Dell Latitude 7420' in response.data
    
    def test_view_assets_search(self, client, test_user, test_asset, db_session):
        """Test asset search functionality."""
        # Create another asset
        category = Category.query.first()
        asset2 = Asset(
            asset_tag='DESK-001',
            name='HP Desktop',
            category_id=category.id
        )
        db_session.add(asset2)
        db_session.commit()
        
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Search for 'Dell'
        response = client.get('/assets?search=Dell')
        assert response.status_code == 200
        assert b'LAP-001' in response.data
        assert b'DESK-001' not in response.data
    
    def test_view_assets_category_filter(self, client, test_user, test_asset, db_session):
        """Test asset category filter."""
        category2 = Category(name='Desktop', description='Desktop computers')
        db_session.add(category2)
        db_session.commit()
        
        asset2 = Asset(
            asset_tag='DESK-001',
            name='HP Desktop',
            category_id=category2.id
        )
        db_session.add(asset2)
        db_session.commit()
        
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Filter by category
        response = client.get(f'/assets?category={category2.id}')
        assert response.status_code == 200
        assert b'DESK-001' in response.data
        assert b'LAP-001' not in response.data
    
    def test_view_assets_status_filter(self, client, test_user, test_asset, db_session):
        """Test asset status filter."""
        category = Category.query.first()
        asset2 = Asset(
            asset_tag='RET-001',
            name='Retired Asset',
            status='Retired',
            category_id=category.id
        )
        db_session.add(asset2)
        db_session.commit()
        
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Filter by status
        response = client.get('/assets?status=Retired')
        assert response.status_code == 200
        assert b'RET-001' in response.data
        assert b'LAP-001' not in response.data


class TestAddAsset:
    """Test add asset route."""
    
    def test_add_asset_page_loads(self, client, test_user):
        """Test add asset page is accessible."""
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        response = client.get('/assets/add')
        assert response.status_code == 200
    
    def test_add_asset_success(self, client, test_user, test_category, test_location):
        """Test successful asset creation."""
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        response = client.post('/assets/add', data={
            'asset_tag': 'TAB-001',
            'name': 'iPad Pro',
            'description': 'Tablet device',
            'serial_number': 'SN999',
            'manufacturer': 'Apple',
            'model': 'iPad Pro 12.9',
            'status': 'Active',
            'assigned_to': 'Jane Doe',
            'category_id': str(test_category.id),
            'location_id': str(test_location.id)
        }, follow_redirects=True)
        
        assert response.status_code == 200
        asset = Asset.query.filter_by(asset_tag='TAB-001').first()
        assert asset is not None
        assert asset.name == 'iPad Pro'
        assert asset.category_id == test_category.id
    
    def test_add_asset_missing_required_fields(self, client, test_user, test_category):
        """Test add asset fails with missing required fields."""
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Missing asset_tag
        response = client.post('/assets/add', data={
            'name': 'Test Asset',
            'category_id': str(test_category.id)
        })
        
        assert response.status_code == 200
        asset = Asset.query.filter_by(name='Test Asset').first()
        assert asset is None
    
    def test_add_asset_duplicate_tag(self, client, test_user, test_asset, test_category):
        """Test add asset fails with duplicate asset tag."""
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        response = client.post('/assets/add', data={
            'asset_tag': 'LAP-001',  # Duplicate
            'name': 'Different Asset',
            'category_id': str(test_category.id)
        })
        
        assert response.status_code == 200
        assets = Asset.query.filter_by(asset_tag='LAP-001').all()
        assert len(assets) == 1
    
    def test_add_asset_optional_location(self, client, test_user, test_category):
        """Test add asset with no location."""
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        response = client.post('/assets/add', data={
            'asset_tag': 'MOB-001',
            'name': 'Mobile Device',
            'category_id': str(test_category.id),
            'location_id': ''
        }, follow_redirects=True)
        
        assert response.status_code == 200
        asset = Asset.query.filter_by(asset_tag='MOB-001').first()
        assert asset is not None
        assert asset.location_id is None


class TestEditAsset:
    """Test edit asset route."""
    
    def test_edit_asset_page_loads(self, client, test_user, test_asset):
        """Test edit asset page is accessible."""
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        response = client.get(f'/assets/edit/{test_asset.id}')
        assert response.status_code == 200
        assert b'LAP-001' in response.data
    
    def test_edit_asset_success(self, client, test_user, test_asset):
        """Test successful asset update."""
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        response = client.post(f'/assets/edit/{test_asset.id}', data={
            'asset_tag': 'LAP-001',
            'name': 'Updated Name',
            'description': 'Updated description',
            'serial_number': 'SN999',
            'manufacturer': 'Dell',
            'model': 'Latitude 7420',
            'status': 'Active',
            'assigned_to': 'Updated User',
            'category_id': str(test_asset.category_id),
            'location_id': str(test_asset.location_id) if test_asset.location_id else ''
        }, follow_redirects=True)
        
        assert response.status_code == 200
        test_asset = Asset.query.get(test_asset.id)
        assert test_asset.name == 'Updated Name'
        assert test_asset.description == 'Updated description'
    
    def test_edit_asset_duplicate_tag(self, client, test_user, test_asset, db_session):
        """Test edit asset fails with duplicate asset tag."""
        category = Category.query.first()
        asset2 = Asset(
            asset_tag='DESK-001',
            name='Desktop',
            category_id=category.id
        )
        db_session.add(asset2)
        db_session.commit()
        
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Try to change test_asset tag to asset2's tag
        response = client.post(f'/assets/edit/{test_asset.id}', data={
            'asset_tag': 'DESK-001',  # Duplicate
            'name': 'Test Asset',
            'category_id': str(test_asset.category_id)
        })
        
        assert response.status_code == 200
        # Original asset should still have its tag
        test_asset = Asset.query.get(test_asset.id)
        assert test_asset.asset_tag == 'LAP-001'
    
    def test_edit_asset_same_tag_allowed(self, client, test_user, test_asset):
        """Test edit asset allows keeping same asset tag."""
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        response = client.post(f'/assets/edit/{test_asset.id}', data={
            'asset_tag': 'LAP-001',  # Same tag
            'name': 'Updated Name',
            'category_id': str(test_asset.category_id)
        }, follow_redirects=True)
        
        assert response.status_code == 200
        test_asset = Asset.query.get(test_asset.id)
        assert test_asset.asset_tag == 'LAP-001'
        assert test_asset.name == 'Updated Name'


class TestDeleteAsset:
    """Test delete asset route."""
    
    def test_delete_asset_requires_admin(self, client, test_user, test_asset):
        """Test delete asset requires admin."""
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        response = client.post(f'/assets/delete/{test_asset.id}', follow_redirects=False)
        assert response.status_code == 302
        assert '/dashboard' in response.location
    
    def test_delete_asset_success(self, client, test_admin, test_asset):
        """Test successful asset deletion."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'adminpass123'
        })
        
        asset_id = test_asset.id
        response = client.post(f'/assets/delete/{asset_id}', follow_redirects=True)
        
        assert response.status_code == 200
        deleted_asset = Asset.query.get(asset_id)
        assert deleted_asset is None
    
    def test_delete_nonexistent_asset(self, client, test_admin):
        """Test delete non-existent asset returns 404."""
        client.post('/login', data={
            'username': 'admin',
            'password': 'adminpass123'
        })
        
        response = client.post('/assets/delete/99999')
        assert response.status_code == 404

