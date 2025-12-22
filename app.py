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

# Ensure instance folder exists
instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(instance_path, exist_ok=True)

# Use instance folder for database
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "it_assets.db")}'
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
    try:
        db.create_all()
        print("Database tables created successfully.")
        
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
        else:
            print("Admin user already exists.")
        
        if not User.query.filter_by(username='Tahir').first():
            tahir = User(
                username='Tahir',
                email='tahir@company.com',
                password=generate_password_hash('Admin@123'),
                is_admin=False
            )
            db.session.add(tahir)
            db.session.commit()
            print("Default user created: username='Tahir', password='Admin@123'")
        else:
            print("Tahir user already exists.")
        
        # Create default categories
        default_categories = [
            {'name': 'Laptop', 'description': 'Portable computers and notebooks'},
            {'name': 'Desktop', 'description': 'Desktop computers and workstations'},
            {'name': 'Server', 'description': 'Server hardware and equipment'},
            {'name': 'Monitor', 'description': 'Computer monitors and displays'},
            {'name': 'Printer', 'description': 'Printers and multifunction devices'},
            {'name': 'Network Equipment', 'description': 'Routers, switches, and network devices'},
            {'name': 'Mobile Device', 'description': 'Smartphones and tablets'},
            {'name': 'Software License', 'description': 'Software licenses and subscriptions'},
            {'name': 'Peripheral', 'description': 'Keyboards, mice, and other peripherals'},
            {'name': 'Accessory', 'description': 'Cables, adapters, and accessories'}
        ]
        
        categories_created = 0
        for cat_data in default_categories:
            if not Category.query.filter_by(name=cat_data['name']).first():
                category = Category(
                    name=cat_data['name'],
                    description=cat_data['description']
                )
                db.session.add(category)
                categories_created += 1
        if categories_created > 0:
            db.session.commit()
            print(f"Created {categories_created} default categories.")
        else:
            print("All default categories already exist.")
        
        # Create default locations
        default_locations = [
            {'name': 'Head Office', 'building': 'Main Building', 'floor': '1st Floor', 'room': '101'},
            {'name': 'IT Department', 'building': 'Main Building', 'floor': '2nd Floor', 'room': '201'},
            {'name': 'Sales Office', 'building': 'Main Building', 'floor': '3rd Floor', 'room': '301'},
            {'name': 'Warehouse', 'building': 'Warehouse Building', 'floor': 'Ground Floor', 'room': 'W-01'},
            {'name': 'Conference Room A', 'building': 'Main Building', 'floor': '1st Floor', 'room': '105'},
            {'name': 'Remote Work', 'building': 'N/A', 'floor': 'N/A', 'room': 'N/A'},
            {'name': 'Data Center', 'building': 'Main Building', 'floor': 'Basement', 'room': 'B-01'},
            {'name': 'HR Department', 'building': 'Main Building', 'floor': '2nd Floor', 'room': '205'},
            {'name': 'Finance Office', 'building': 'Main Building', 'floor': '3rd Floor', 'room': '305'},
            {'name': 'Reception', 'building': 'Main Building', 'floor': '1st Floor', 'room': '100'}
        ]
        
        locations_created = 0
        for loc_data in default_locations:
            if not Location.query.filter_by(name=loc_data['name']).first():
                location = Location(
                    name=loc_data['name'],
                    building=loc_data['building'],
                    floor=loc_data['floor'],
                    room=loc_data['room']
                )
                db.session.add(location)
                locations_created += 1
        if locations_created > 0:
            db.session.commit()
            print(f"Created {locations_created} default locations.")
        else:
            print("All default locations already exist.")
        
        # Create default assets (need categories and locations to exist)
        # Get category and location IDs
        laptop_cat = Category.query.filter_by(name='Laptop').first()
        desktop_cat = Category.query.filter_by(name='Desktop').first()
        server_cat = Category.query.filter_by(name='Server').first()
        monitor_cat = Category.query.filter_by(name='Monitor').first()
        printer_cat = Category.query.filter_by(name='Printer').first()
        network_cat = Category.query.filter_by(name='Network Equipment').first()
        mobile_cat = Category.query.filter_by(name='Mobile Device').first()
        software_cat = Category.query.filter_by(name='Software License').first()
        peripheral_cat = Category.query.filter_by(name='Peripheral').first()
        accessory_cat = Category.query.filter_by(name='Accessory').first()
        
        it_dept = Location.query.filter_by(name='IT Department').first()
        head_office = Location.query.filter_by(name='Head Office').first()
        sales_office = Location.query.filter_by(name='Sales Office').first()
        warehouse = Location.query.filter_by(name='Warehouse').first()
        data_center = Location.query.filter_by(name='Data Center').first()
        remote = Location.query.filter_by(name='Remote Work').first()
        
        default_assets = [
            {
                'asset_tag': 'LAP-001',
                'name': 'Dell Latitude 5520',
                'description': 'Business laptop for IT department',
                'serial_number': 'DL5520123456',
                'manufacturer': 'Dell',
                'model': 'Latitude 5520',
                'status': 'Active',
                'assigned_to': 'Tahir',
                'category': laptop_cat,
                'location': it_dept
            },
            {
                'asset_tag': 'DESK-001',
                'name': 'HP EliteDesk 800 G6',
                'description': 'Desktop workstation for office use',
                'serial_number': 'HP800G6123456',
                'manufacturer': 'HP',
                'model': 'EliteDesk 800 G6',
                'status': 'Active',
                'assigned_to': 'admin',
                'category': desktop_cat,
                'location': head_office
            },
            {
                'asset_tag': 'SRV-001',
                'name': 'Dell PowerEdge R740',
                'description': 'Production server for applications',
                'serial_number': 'DLR740123456',
                'manufacturer': 'Dell',
                'model': 'PowerEdge R740',
                'status': 'Active',
                'assigned_to': None,
                'category': server_cat,
                'location': data_center
            },
            {
                'asset_tag': 'MON-001',
                'name': 'LG UltraWide 34" Monitor',
                'description': 'Widescreen monitor for development',
                'serial_number': 'LG34UW123456',
                'manufacturer': 'LG',
                'model': '34WP65C-B',
                'status': 'Active',
                'assigned_to': 'Tahir',
                'category': monitor_cat,
                'location': it_dept
            },
            {
                'asset_tag': 'PRT-001',
                'name': 'HP LaserJet Pro M404dn',
                'description': 'Network printer for office use',
                'serial_number': 'HPM404123456',
                'manufacturer': 'HP',
                'model': 'LaserJet Pro M404dn',
                'status': 'Active',
                'assigned_to': None,
                'category': printer_cat,
                'location': head_office
            },
            {
                'asset_tag': 'NET-001',
                'name': 'Cisco Catalyst 2960 Switch',
                'description': '24-port network switch',
                'serial_number': 'CS2960123456',
                'manufacturer': 'Cisco',
                'model': 'Catalyst 2960',
                'status': 'Active',
                'assigned_to': None,
                'category': network_cat,
                'location': data_center
            },
            {
                'asset_tag': 'MOB-001',
                'name': 'iPhone 14 Pro',
                'description': 'Company mobile device',
                'serial_number': 'IP14P123456',
                'manufacturer': 'Apple',
                'model': 'iPhone 14 Pro',
                'status': 'Active',
                'assigned_to': 'admin',
                'category': mobile_cat,
                'location': remote
            },
            {
                'asset_tag': 'SW-001',
                'name': 'Microsoft Office 365 License',
                'description': 'Annual subscription for Office 365',
                'serial_number': 'MS365123456',
                'manufacturer': 'Microsoft',
                'model': 'Office 365 Business',
                'status': 'Active',
                'assigned_to': None,
                'category': software_cat,
                'location': None
            },
            {
                'asset_tag': 'PER-001',
                'name': 'Logitech MX Master 3 Mouse',
                'description': 'Wireless mouse for office',
                'serial_number': 'LGMX3123456',
                'manufacturer': 'Logitech',
                'model': 'MX Master 3',
                'status': 'Active',
                'assigned_to': 'Tahir',
                'category': peripheral_cat,
                'location': it_dept
            },
            {
                'asset_tag': 'ACC-001',
                'name': 'USB-C Hub',
                'description': 'Multi-port USB-C hub adapter',
                'serial_number': 'USBC123456',
                'manufacturer': 'Anker',
                'model': 'USB-C Hub 7-in-1',
                'status': 'Active',
                'assigned_to': None,
                'category': accessory_cat,
                'location': warehouse
            }
        ]
        
        assets_created = 0
        for asset_data in default_assets:
            if not Asset.query.filter_by(asset_tag=asset_data['asset_tag']).first():
                if asset_data['category']:  # Only create if category exists
                    asset = Asset(
                        asset_tag=asset_data['asset_tag'],
                        name=asset_data['name'],
                        description=asset_data['description'],
                        serial_number=asset_data['serial_number'],
                        manufacturer=asset_data['manufacturer'],
                        model=asset_data['model'],
                        status=asset_data['status'],
                        assigned_to=asset_data['assigned_to'],
                        category_id=asset_data['category'].id,
                        location_id=asset_data['location'].id if asset_data['location'] else None
                    )
                    db.session.add(asset)
                    assets_created += 1
        if assets_created > 0:
            db.session.commit()
            print(f"Created {assets_created} default assets.")
        else:
            print("All default assets already exist.")
            
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
