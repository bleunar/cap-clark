from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from app import db
from ..models.user import User
from ..models.shop import Shop
import uuid

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        if User.query.filter_by(email=email).first():
            flash('Email address already registered.', 'danger')
            return redirect(url_for('auth_bp.register'))

        new_user = User(
            id=uuid.uuid4().bytes,
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            email=email,
            phone_number=request.form.get('phone_number'),
            role=role
        )
        new_user.set_password(password)

        db.session.add(new_user)
        
        if role == 'owner':
            new_shop = Shop(
                id=uuid.uuid4().bytes,
                owner_id=new_user.id,
                name=request.form.get('shop_name'),
                address=request.form.get('shop_address'),
                town=request.form.get('shop_town')
            )
            db.session.add(new_shop)

        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth_bp.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = str(user.get_uuid())
            session['user_role'] = user.role
            session['user_name'] = user.first_name
            
            flash(f'Welcome back, {user.first_name}!', 'success')

            if user.role == 'customer':
                return redirect(url_for('customer_bp.dashboard'))
            elif user.role == 'owner':
                return redirect(url_for('owner_bp.dashboard'))
            elif user.role == 'rider':
                return redirect(url_for('rider_bp.dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            return redirect(url_for('auth_bp.login'))

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been successfully logged out.', 'success')
    return redirect(url_for('auth_bp.login'))