# Routes and View Functions
# IT Asset Management System

from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from app import app
from models import db, User, Asset, Category, Location
from datetime import datetime
import re

# Decorator for login required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorator for admin required
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Administrator access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Home/Landing Page
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        errors = []
        
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters long.')
        
        if not email or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append('Valid email address is required.')
        
        if not password or len(password) < 8:
            errors.append('Password must be at least 8 characters long.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        if User.query.filter_by(username=username).first():
            errors.append('Username already exists.')
        
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('register.html')
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            is_admin=False
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return render_template('register.html')
    
    return render_template('register.html')

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

# User Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

# Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    total_assets = Asset.query.count()
    active_assets = Asset.query.filter_by(status='Active').count()
    categories_count = Category.query.count()
    locations_count = Location.query.count()
    
    recent_assets = Asset.query.order_by(Asset.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         total_assets=total_assets,
                         active_assets=active_assets,
                         categories_count=categories_count,
                         locations_count=locations_count,
                         recent_assets=recent_assets)

# View All Assets
@app.route('/assets')
@login_required
def view_assets():
    search = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    status_filter = request.args.get('status', '')
    
    query = Asset.query
    
    if search:
        query = query.filter(
            (Asset.name.ilike(f'%{search}%')) |
            (Asset.asset_tag.ilike(f'%{search}%')) |
            (Asset.serial_number.ilike(f'%{search}%'))
        )
    
    if category_filter:
        query = query.filter_by(category_id=category_filter)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    assets = query.order_by(Asset.created_at.desc()).all()
    categories = Category.query.all()
    
    return render_template('assets/view_assets.html', 
                         assets=assets, 
                         categories=categories,
                         search=search,
                         category_filter=category_filter,
                         status_filter=status_filter)

# Add Asset
@app.route('/assets/add', methods=['GET', 'POST'])
@login_required
def add_asset():
    if request.method == 'POST':
        # Get form data
        asset_tag = request.form.get('asset_tag', '').strip()
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        serial_number = request.form.get('serial_number', '').strip()
        manufacturer = request.form.get('manufacturer', '').strip()
        model = request.form.get('model', '').strip()
        status = request.form.get('status', 'Active')
        assigned_to = request.form.get('assigned_to', '').strip()
        category_id = request.form.get('category_id', '')
        location_id = request.form.get('location_id', '')
        
        # Validation
        errors = []
        
        if not asset_tag:
            errors.append('Asset tag is required.')
        elif Asset.query.filter_by(asset_tag=asset_tag).first():
            errors.append('Asset tag already exists.')
        
        if not name:
            errors.append('Asset name is required.')
        
        if not category_id:
            errors.append('Category is required.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            categories = Category.query.all()
            locations = Location.query.all()
            return render_template('assets/add_asset.html', 
                                 categories=categories, 
                                 locations=locations)
        
        # Create new asset
        new_asset = Asset(
            asset_tag=asset_tag,
            name=name,
            description=description,
            serial_number=serial_number,
            manufacturer=manufacturer,
            model=model,
            status=status,
            assigned_to=assigned_to,
            category_id=category_id,
            location_id=location_id if location_id else None
        )
        
        try:
            db.session.add(new_asset)
            db.session.commit()
            flash('Asset added successfully!', 'success')
            return redirect(url_for('view_assets'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the asset.', 'danger')
    
    categories = Category.query.all()
    locations = Location.query.all()
    return render_template('assets/add_asset.html', 
                         categories=categories, 
                         locations=locations)

# Edit Asset
@app.route('/assets/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_asset(id):
    asset = Asset.query.get_or_404(id)
    
    if request.method == 'POST':
        # Get form data
        asset_tag = request.form.get('asset_tag', '').strip()
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        serial_number = request.form.get('serial_number', '').strip()
        manufacturer = request.form.get('manufacturer', '').strip()
        model = request.form.get('model', '').strip()
        status = request.form.get('status', 'Active')
        assigned_to = request.form.get('assigned_to', '').strip()
        category_id = request.form.get('category_id', '')
        location_id = request.form.get('location_id', '')
        
        # Validation
        errors = []
        
        if not asset_tag:
            errors.append('Asset tag is required.')
        elif asset_tag != asset.asset_tag and Asset.query.filter_by(asset_tag=asset_tag).first():
            errors.append('Asset tag already exists.')
        
        if not name:
            errors.append('Asset name is required.')
        
        if not category_id:
            errors.append('Category is required.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            categories = Category.query.all()
            locations = Location.query.all()
            return render_template('assets/edit_asset.html', 
                                 asset=asset,
                                 categories=categories, 
                                 locations=locations)
        
        # Update asset
        asset.asset_tag = asset_tag
        asset.name = name
        asset.description = description
        asset.serial_number = serial_number
        asset.manufacturer = manufacturer
        asset.model = model
        asset.status = status
        asset.assigned_to = assigned_to
        asset.category_id = category_id
        asset.location_id = location_id if location_id else None
        
        try:
            db.session.commit()
            flash('Asset updated successfully!', 'success')
            return redirect(url_for('view_assets'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the asset.', 'danger')
    
    categories = Category.query.all()
    locations = Location.query.all()
    return render_template('assets/edit_asset.html', 
                         asset=asset,
                         categories=categories, 
                         locations=locations)

# Delete Asset (Admin Only)
@app.route('/assets/delete/<int:id>', methods=['POST'])
@admin_required
def delete_asset(id):
    asset = Asset.query.get_or_404(id)
    
    try:
        db.session.delete(asset)
        db.session.commit()
        flash('Asset deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the asset.', 'danger')
    
    return redirect(url_for('view_assets'))

# Categories Management (Admin Only)
@app.route('/categories')
@admin_required
def view_categories():
    categories = Category.query.all()
    return render_template('categories/view_categories.html', categories=categories)

@app.route('/categories/add', methods=['GET', 'POST'])
@admin_required
def add_category():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash('Category name is required.', 'danger')
            return render_template('categories/add_category.html')
        
        if Category.query.filter_by(name=name).first():
            flash('Category already exists.', 'danger')
            return render_template('categories/add_category.html')
        
        new_category = Category(name=name, description=description)
        
        try:
            db.session.add(new_category)
            db.session.commit()
            flash('Category added successfully!', 'success')
            return redirect(url_for('view_categories'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the category.', 'danger')
    
    return render_template('categories/add_category.html')

# Locations Management (Admin Only)
@app.route('/locations')
@admin_required
def view_locations():
    locations = Location.query.all()
    return render_template('locations/view_locations.html', locations=locations)

@app.route('/locations/add', methods=['GET', 'POST'])
@admin_required
def add_location():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        building = request.form.get('building', '').strip()
        floor = request.form.get('floor', '').strip()
        room = request.form.get('room', '').strip()
        
        if not name:
            flash('Location name is required.', 'danger')
            return render_template('locations/add_location.html')
        
        if Location.query.filter_by(name=name).first():
            flash('Location already exists.', 'danger')
            return render_template('locations/add_location.html')
        
        new_location = Location(name=name, building=building, floor=floor, room=room)
        
        try:
            db.session.add(new_location)
            db.session.commit()
            flash('Location added successfully!', 'success')
            return redirect(url_for('view_locations'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the location.', 'danger')
    
    return render_template('locations/add_location.html')
