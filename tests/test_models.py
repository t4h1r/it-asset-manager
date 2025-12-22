import pytest
from datetime import datetime
from models import db, User, Asset, Category, Location
from werkzeug.security import generate_password_hash


class TestUserModel:
    """Test User model."""
    
    def test_create_user(self, db_session):
        """Test creating a user."""
        user = User(
            username='newuser',
            email='newuser@example.com',
            password=generate_password_hash('password123'),
            is_admin=False
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.username == 'newuser'
        assert user.email == 'newuser@example.com'
        assert user.is_admin is False
        assert user.created_at is not None
    
    def test_user_unique_username(self, db_session, test_user):
        """Test username must be unique."""
        duplicate = User(
            username='testuser',
            email='different@example.com',
            password=generate_password_hash('pass123'),
            is_admin=False
        )
        db_session.add(duplicate)
        
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_user_unique_email(self, db_session, test_user):
        """Test email must be unique."""
        duplicate = User(
            username='different',
            email='test@example.com',
            password=generate_password_hash('pass123'),
            is_admin=False
        )
        db_session.add(duplicate)
        
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_user_repr(self, test_user):
        """Test User __repr__ method."""
        assert repr(test_user) == '<User testuser>'


class TestCategoryModel:
    """Test Category model."""
    
    def test_create_category(self, db_session):
        """Test creating a category."""
        category = Category(
            name='Desktop',
            description='Desktop computers'
        )
        db_session.add(category)
        db_session.commit()
        
        assert category.id is not None
        assert category.name == 'Desktop'
        assert category.description == 'Desktop computers'
    
    def test_category_unique_name(self, db_session, test_category):
        """Test category name must be unique."""
        duplicate = Category(name='Laptop', description='Different')
        db_session.add(duplicate)
        
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_category_assets_relationship(self, db_session, test_category, test_asset):
        """Test category has assets relationship."""
        assert len(test_category.assets) == 1
        assert test_category.assets[0].asset_tag == 'LAP-001'
    
    def test_category_repr(self, test_category):
        """Test Category __repr__ method."""
        assert repr(test_category) == '<Category Laptop>'


class TestLocationModel:
    """Test Location model."""
    
    def test_create_location(self, db_session):
        """Test creating a location."""
        location = Location(
            name='Remote Office',
            building='Building B',
            floor='1st Floor',
            room='Room 101'
        )
        db_session.add(location)
        db_session.commit()
        
        assert location.id is not None
        assert location.name == 'Remote Office'
        assert location.building == 'Building B'
        assert location.floor == '1st Floor'
        assert location.room == 'Room 101'
    
    def test_location_unique_name(self, db_session, test_location):
        """Test location name must be unique."""
        duplicate = Location(name='Main Office', building='Different')
        db_session.add(duplicate)
        
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_location_assets_relationship(self, db_session, test_location, test_asset):
        """Test location has assets relationship."""
        assert len(test_location.assets) == 1
        assert test_location.assets[0].asset_tag == 'LAP-001'
    
    def test_location_repr(self, test_location):
        """Test Location __repr__ method."""
        assert repr(test_location) == '<Location Main Office>'


class TestAssetModel:
    """Test Asset model."""
    
    def test_create_asset(self, db_session, test_category, test_location):
        """Test creating an asset."""
        asset = Asset(
            asset_tag='DESK-001',
            name='HP Desktop',
            description='Office desktop',
            serial_number='SN789',
            manufacturer='HP',
            model='EliteDesk 800',
            status='Active',
            assigned_to='Jane Smith',
            category_id=test_category.id,
            location_id=test_location.id
        )
        db_session.add(asset)
        db_session.commit()
        
        assert asset.id is not None
        assert asset.asset_tag == 'DESK-001'
        assert asset.name == 'HP Desktop'
        assert asset.status == 'Active'
        assert asset.category_id == test_category.id
        assert asset.location_id == test_location.id
        assert asset.created_at is not None
    
    def test_asset_unique_tag(self, db_session, test_asset):
        """Test asset tag must be unique."""
        duplicate = Asset(
            asset_tag='LAP-001',
            name='Different',
            category_id=test_asset.category_id
        )
        db_session.add(duplicate)
        
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_asset_default_status(self, db_session, test_category):
        """Test asset defaults to Active status."""
        asset = Asset(
            asset_tag='TAB-001',
            name='Tablet',
            category_id=test_category.id
        )
        db_session.add(asset)
        db_session.commit()
        
        assert asset.status == 'Active'
    
    def test_asset_category_relationship(self, test_asset, test_category):
        """Test asset has category relationship."""
        assert test_asset.category.id == test_category.id
        assert test_asset.category.name == 'Laptop'
    
    def test_asset_location_relationship(self, test_asset, test_location):
        """Test asset has location relationship."""
        assert test_asset.location.id == test_location.id
        assert test_asset.location.name == 'Main Office'
    
    def test_asset_optional_location(self, db_session, test_category):
        """Test asset location can be None."""
        asset = Asset(
            asset_tag='MOB-001',
            name='Mobile Device',
            category_id=test_category.id,
            location_id=None
        )
        db_session.add(asset)
        db_session.commit()
        
        assert asset.location_id is None
        assert asset.location is None
    
    def test_asset_updated_at_timestamp(self, db_session, test_asset):
        """Test asset updated_at changes on update."""
        original_updated = test_asset.updated_at
        test_asset.name = 'Updated Name'
        db_session.commit()
        
        assert test_asset.updated_at != original_updated
    
    def test_asset_repr(self, test_asset):
        """Test Asset __repr__ method."""
        assert repr(test_asset) == '<Asset LAP-001: Dell Latitude 7420>'

