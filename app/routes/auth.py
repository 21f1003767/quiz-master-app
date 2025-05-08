from flask import Blueprint, render_template, redirect, url_for, flash, session, request, jsonify, abort
from app.forms import LoginForm, RegistrationForm, AdminLoginForm
from app.models.models import User, Admin, db
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from app.utils import is_json_requested, api_csrf_protected, ensure_csrf_token
from datetime import datetime, timedelta
import re
import uuid
import secrets

auth = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session and 'admin_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('User access required', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Admin access required', 'danger')
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def csrf_protected(f):
    """This decorator is deprecated and will be removed"""
    return f

@auth.route('/')
def index():
    return render_template('index.html')

def generate_csrf_token():
    """Generate a secure CSRF token and store it in the session"""
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(16)
    return session['_csrf_token']

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    User Login
    ---
    tags:
      - Authentication
    summary: User login
    description: Authenticates a user and creates a session
    parameters:
      - name: username
        in: formData
        type: string
        required: true
        description: The user's email
      - name: password
        in: formData
        type: string
        required: true
        description: The user's password
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
      400:
        description: Invalid credentials
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
    """
    # Handle API requests
    is_api = is_json_requested()
    
    if is_api:
        data = request.get_json()
        form = LoginForm.with_csrf(enabled=False, formdata=None, data=data)
    else:
        form = LoginForm()
        ensure_csrf_token()  # Make sure CSRF token is in the session

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            session['user_role'] = 'user'
            session['username'] = user.username
            
            if is_api:
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'redirect': url_for('user.dashboard')
                })
            
            flash('Login successful!', 'success')
            return redirect(url_for('user.dashboard'))
        else:
            if is_api:
                return jsonify({
                    'success': False,
                    'message': 'Invalid email or password'
                }), 400
            
            flash('Invalid email or password', 'danger')
    elif is_api and request.method == 'POST':
        return jsonify({
            'success': False,
            'errors': form.errors
        }), 400
        
    return render_template('auth/login.html', form=form)

@auth.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """
    Admin Login
    ---
    tags:
      - Authentication
    summary: Admin login
    description: Authenticates an admin and creates a session
    parameters:
      - name: username
        in: formData
        type: string
        required: true
        description: The admin's email
      - name: password
        in: formData
        type: string
        required: true
        description: The admin's password
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
      400:
        description: Invalid credentials
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
    """
    # Handle API requests
    is_api = is_json_requested()
    
    if is_api:
        data = request.get_json()
        form = AdminLoginForm.with_csrf(enabled=False, formdata=None, data=data)
    else:
        form = AdminLoginForm()
        ensure_csrf_token()  # Make sure CSRF token is in the session

    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and check_password_hash(admin.password, form.password.data):
            session['admin_id'] = admin.id
            session['user_role'] = 'admin'
            session['username'] = admin.username
            
            if is_api:
                return jsonify({
                    'success': True,
                    'message': 'Admin login successful',
                    'redirect': url_for('admin.dashboard')
                })
            
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            if is_api:
                return jsonify({
                    'success': False,
                    'message': 'Invalid email or password'
                }), 400
            
            flash('Invalid email or password', 'danger')
    elif is_api and request.method == 'POST':
        return jsonify({
            'success': False,
            'errors': form.errors
        }), 400
        
    return render_template('auth/admin_login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    User Registration
    ---
    tags:
      - Authentication
    summary: Register a new user
    description: Registers a new user in the system
    parameters:
      - name: username
        in: formData
        type: string
        required: true
        description: The user's email
      - name: password
        in: formData
        type: string
        required: true
        description: The user's password
      - name: password_confirm
        in: formData
        type: string
        required: true
        description: Password confirmation
      - name: full_name
        in: formData
        type: string
        required: true
        description: User's full name
      - name: qualification
        in: formData
        type: string
        required: true
        description: User's qualification
      - name: date_of_birth
        in: formData
        type: string
        format: date
        required: true
        description: User's date of birth (YYYY-MM-DD)
    responses:
      200:
        description: Registration successful
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
      400:
        description: Registration failed
        schema:
          type: object
          properties:
            success:
              type: boolean
            errors:
              type: object
    """
    # Handle API requests
    is_api = is_json_requested()
    
    if is_api:
        data = request.get_json()
        form = RegistrationForm.with_csrf(enabled=False, formdata=None, data=data)
    else:
        form = RegistrationForm()
        ensure_csrf_token()  # Make sure CSRF token is in the session

    if form.validate_on_submit():
        # Check if username already exists
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            if is_api:
                return jsonify({
                    'success': False,
                    'message': 'Email already registered'
                }), 400
            
            flash('Email already registered', 'danger')
            return render_template('auth/register.html', form=form)
        
        # Generate a user ID
        user_id = str(uuid.uuid4())
        
        # Create new user
        new_user = User(
            id=user_id,
            username=form.username.data,
            password=form.password.data,  # Hashing is handled in the model
            full_name=form.full_name.data,
            qualification=form.qualification.data,
            date_of_birth=form.date_of_birth.data
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        if is_api:
            return jsonify({
                'success': True,
                'message': 'Registration successful. Please login.',
                'redirect': url_for('auth.login')
            })
        
        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('auth.login'))
    elif is_api and request.method == 'POST':
        return jsonify({
            'success': False,
            'errors': form.errors
        }), 400
    
    return render_template('auth/register.html', form=form)

@auth.route('/logout')
def logout():
    """
    Logout
    ---
    tags:
      - Authentication
    summary: Logout current user
    description: Logs out the current user by clearing their session
    responses:
      200:
        description: Logout successful
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
    """
    session.clear()
    
    if is_json_requested():
        return jsonify({
            'success': True,
            'message': 'Logged out successfully',
            'redirect': url_for('auth.login')
        })
    
    flash('Logged out successfully', 'success')
    return redirect(url_for('auth.login'))

@auth.route('/api', methods=['GET'])
def api_info():
    """
    API Information
    ---
    tags:
      - API
    summary: API information
    description: Returns information about the API
    responses:
      200:
        description: Information about the API
        schema:
          type: object
          properties:
            name:
              type: string
            version:
              type: string
            description:
              type: string
            endpoints:
              type: array
              items:
                type: string
    """
    return jsonify({
        'name': 'Quiz Master API',
        'version': '1.0.0',
        'description': 'API for the Quiz Master application',
        'endpoints': [
            '/api/auth/login',
            '/api/auth/admin/login',
            '/api/auth/register',
            '/api/auth/logout'
        ]
    })

# The apidocs route was removed as it's redundant with Swagger UI accessible at /api/docs/ 