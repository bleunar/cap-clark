from functools import wraps
from flask import session, redirect, url_for, flash
from ..models.user import User
import uuid

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth_bp.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id_bytes = uuid.UUID(session['user_id']).bytes
            user = User.query.get(user_id_bytes)
            
            if not user or user.role != role_name:
                flash(f"You do not have permission to access this page.", 'danger')
                
                if user and user.role:
                    if user.role == 'customer':
                        return redirect(url_for('customer_bp.dashboard'))
                    elif user.role == 'owner':
                        return redirect(url_for('owner_bp.dashboard'))
                    elif user.role == 'rider':
                         return redirect(url_for('rider_bp.dashboard'))
                
                return redirect(url_for('auth_bp.login'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator