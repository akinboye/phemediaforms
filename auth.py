"""
Authentication and authorization helpers
"""

from functools import wraps
from flask import session, redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from models import SuperAdmin, Admin

def hash_password(password):
    """Hash a password"""
    return generate_password_hash(password)

def verify_password(password, password_hash):
    """Verify a password against its hash"""
    return check_password_hash(password_hash, password)

def is_superadmin_logged_in():
    """Check if a superadmin is logged in"""
    return 'superadmin_id' in session and session.get('user_type') == 'superadmin'

def is_admin_logged_in():
    """Check if an admin is logged in"""
    return 'admin_id' in session and session.get('user_type') == 'admin'

def is_admin_or_superadmin_logged_in():
    """Check if any admin user is logged in"""
    return is_superadmin_logged_in() or is_admin_logged_in()

def get_current_superadmin():
    """Get current logged-in superadmin"""
    if is_superadmin_logged_in():
        return SuperAdmin.query.get(session.get('superadmin_id'))
    return None

def get_current_admin():
    """Get current logged-in admin"""
    if is_admin_logged_in():
        return Admin.query.get(session.get('admin_id'))
    return None

def require_superadmin(f):
    """Decorator to require superadmin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_superadmin_logged_in():
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def require_admin_or_superadmin(f):
    """Decorator to require admin or superadmin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_or_superadmin_logged_in():
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function
