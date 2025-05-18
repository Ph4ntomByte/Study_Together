from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse as url_parse
from app import db, csrf
from app.models.user import User
from flask_wtf.csrf import generate_csrf

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        data = request.get_json()
        
        user = User.query.filter_by(email=data.get('email')).first()
        
        if user is None or not user.check_password(data.get('password')):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        login_user(user, remember=data.get('remember_me', False))
        next_page = request.args.get('next')
        
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        
        return jsonify({'success': True, 'redirect': next_page})
    
    return render_template('auth/login.html', title='Sign In')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        data = request.get_json()
        
        if User.query.filter_by(username=data.get('username')).first():
            return jsonify({'error': 'Username already taken'}), 400
        
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        user = User(
            username=data.get('username'),
            email=data.get('email'),
            name=data.get('name')
        )
        user.set_password(data.get('password'))
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return jsonify({'success': True})
    
    return render_template('auth/register.html', title='Register')

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    return redirect(url_for('main.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Handle user profile page."""
    if request.method == 'POST':
        data = request.get_json()
        
        # Update name if provided
        if data.get('name'):
            current_user.name = data.get('name')
        
        # Check if username should be updated
        if data.get('username') and data.get('username') != current_user.username:
            if User.query.filter_by(username=data.get('username')).first():
                return jsonify({'error': 'Username already taken'}), 400
            current_user.username = data.get('username')
        
        # Check if email should be updated
        if data.get('email') and data.get('email') != current_user.email:
            if User.query.filter_by(email=data.get('email')).first():
                return jsonify({'error': 'Email already registered'}), 400
            current_user.email = data.get('email')
        
        # Update password if provided
        if data.get('new_password'):
            if not current_user.check_password(data.get('current_password')):
                return jsonify({'error': 'Current password is incorrect'}), 400
            current_user.set_password(data.get('new_password'))
        
        # Save changes
        db.session.commit()
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    
    return render_template('auth/profile.html', title='My Profile') 
