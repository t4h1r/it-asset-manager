# IT Asset Management System

A secure web-based IT Asset Management System built with Flask and SQLite.

## Features

- **User Authentication**: Secure login/registration with password hashing
- **Role-Based Access Control**: Admin and regular user roles
- **Asset Management**: Full CRUD operations for IT assets
- **Category Management**: Organize assets by categories (laptops, desktops, servers, etc.)
- **Location Tracking**: Track asset locations by building, floor, and room
- **Search & Filter**: Search assets by name, tag, or serial number
- **Security**: Protection against OWASP Top 10 vulnerabilities

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd it-asset-manager
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and update SECRET_KEY
```

5. Run the application:
```bash
python app.py
```

6. Access the application at `http://localhost:5000`

## Default Credentials

- **Username**: admin
- **Password**: Admin@123

**Important**: Change the default admin password after first login!

## Database Schema

- **Users**: User authentication and authorization
- **Assets**: IT asset information (hardware/software)
- **Categories**: Asset categories
- **Locations**: Physical locations for assets

## Technology Stack

- **Backend**: Python 3.x, Flask
- **Database**: SQLite
- **Frontend**: HTML5, CSS3 (Bootstrap 5), JavaScript
- **Security**: Werkzeug password hashing, CSRF protection, input validation

## Testing

Run unit tests:
```bash
pytest
```

Run with coverage:
```bash
coverage run -m pytest
coverage report
```

## Security Features

1. **SQL Injection Prevention**: Parameterized queries with SQLAlchemy ORM
2. **XSS Prevention**: Template escaping, input sanitization
3. **CSRF Protection**: Session-based CSRF tokens
4. **Authentication**: Secure password hashing with Werkzeug
5. **Authorization**: Role-based access control
6. **Input Validation**: Server-side validation for all inputs


