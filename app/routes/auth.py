from flask import Blueprint, render_template, redirect, url_for, flash, session, request, jsonify, abort
from app.forms import LoginForm, RegistrationForm, AdminLoginForm
from app.models.models import User, Admin, db
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from app.utils import is_json_requested
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
    @wraps(f)
    def decorated_function(*args, **kwargs):
        
        if request.is_json and 'Authorization' in request.headers:
            return f(*args, **kwargs)
            
        
        if request.method == 'POST' and not request.is_json:
            csrf_token = request.form.get('csrf_token')
            if not csrf_token or csrf_token != session.get('_csrf_token'):
                flash('CSRF token validation failed. Please try again.', 'danger')
                return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

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
    User Login API
    ---
    tags:
      - Authentication
    summary: Authenticate a user
    description: Authenticates a user with username and password
    parameters:
      - name: username
        in: formData
        required: true
        schema:
          type: string
      - name: password
        in: formData
        required: true
        schema:
          type: string
    responses:
      200:
        description: Login successful
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                message:
                  type: string
                  example: Login successful
                user:
                  type: object
                  properties:
                    username:
                      type: string
                    full_name:
                      type: string
      401:
        description: Invalid credentials
    """
    
    if 'admin_id' in session:
        session.pop('admin_id', None)
        session.pop('admin_username', None)
        session.pop('role', None)
    
    form = LoginForm()
    
    
    if request.method == 'GET':
        session.pop('_csrf_token', None)
    csrf_token = generate_csrf_token()
    
    if request.method == 'POST':
        print("Processing login POST request")  
        
        if is_json_requested():
            data = request.get_json()
            username = data.get('username', '')
            password = data.get('password', '')
        else:
            username = form.username.data
            password = form.password.data
            print(f"Form data received - Username: {username}")
        
        user = User.query.filter_by(username=username).first()
        print(f"User found: {user is not None}")
        
        if user:
            password_correct = False
            try:
                password_correct = user.check_password(password)
                print(f"Password check result: {password_correct}")
            except Exception as e:
                print(f"Password check error: {str(e)}")
                
            if password_correct:
                session['user_id'] = user.id
                session['username'] = user.username
                session['full_name'] = user.full_name
                session['role'] = 'USER'
                
                if is_json_requested():
                    return jsonify({
                        'success': True,
                        'message': 'Login successful',
                        'user': {
                            'username': user.username,
                            'full_name': user.full_name
                        }
                    })
                
                flash('Login successful!', 'success')
                return redirect(url_for('user.dashboard'))
        
        if is_json_requested():
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
                
        flash('Invalid username or password. Please try again.', 'danger')
    
    return render_template('auth/login.html', form=form, csrf_token=csrf_token)

@auth.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """
    Admin Login API
    ---
    tags:
      - Authentication
    summary: Authenticate an admin
    description: Authenticates an admin with username and password
    parameters:
      - name: username
        in: formData
        required: true
        schema:
          type: string
      - name: password
        in: formData
        required: true
        schema:
          type: string
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """
    if 'user_id' in session:
        session.pop('user_id', None)
        session.pop('username', None)
        session.pop('full_name', None)
        session.pop('role', None)
    
    form = AdminLoginForm()
    
    if request.method == 'GET':
        session.pop('_csrf_token', None)
    csrf_token = generate_csrf_token()
    
    if request.method == 'POST':
        print("Processing admin login POST request")
        
        if is_json_requested():
            data = request.get_json()
            username = data.get('username', '')
            password = data.get('password', '')
        else:
            username = form.username.data
            password = form.password.data
            print(f"Form data received - Username: {username}")
        
        admin = Admin.query.filter_by(username=username).first()
        print(f"Admin found: {admin is not None}")
        
        if admin:
            password_correct = False
            try:
                password_correct = admin.check_password(password)
                print(f"Password check result: {password_correct}")
            except Exception as e:
                print(f"Password check error: {str(e)}")
                
            if password_correct:
                session['admin_id'] = admin.id
                session['admin_username'] = admin.username
                session['role'] = 'ADMIN'
                
                if is_json_requested():
                    return jsonify({
                        'success': True,
                        'message': 'Admin login successful'
                    })
                
                flash('Admin login successful!', 'success')
                return redirect(url_for('admin.dashboard'))
        
        if is_json_requested():
            return jsonify({
                'success': False,
                'message': 'Invalid admin credentials'
            }), 401
                
        flash('Invalid admin credentials. Please try again.', 'danger')
    
    return render_template('auth/admin_login.html', form=form, csrf_token=csrf_token)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    User Registration API
    ---
    tags:
      - Authentication
    summary: Register a new user
    description: Creates a new user account
    parameters:
      - name: username
        in: formData
        required: true
        schema:
          type: string
      - name: password
        in: formData
        required: true
        schema:
          type: string
      - name: full_name
        in: formData
        required: true
        schema:
          type: string
      - name: qualification
        in: formData
        required: true
        schema:
          type: string
      - name: dob
        in: formData
        required: true
        schema:
          type: string
          format: date
    responses:
      201:
        description: Registration successful
      400:
        description: Invalid input or user already exists
    """
    if 'user_id' in session:
        session.pop('user_id', None)
        session.pop('role', None)
    if 'admin_id' in session:
        session.pop('admin_id', None)
        session.pop('role', None)
        
    form = RegistrationForm()
    
    csrf_token = generate_csrf_token()
    
    # Helper function to handle date format conversion
    def parse_date(date_str):
        # Try various date formats
        formats = ['%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d/%m/%Y']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None
    
    if request.method == 'POST':
        # Handle date format conversion for form input
        if request.form.get('dob'):
            dob_str = request.form.get('dob')
            parsed_date = parse_date(dob_str)
            if parsed_date:
                # Manually assign the parsed date to the form field
                form.dob.data = parsed_date
        
        if is_json_requested():
            data = request.get_json()
            username = data.get('username', '')
            password = data.get('password', '')
            full_name = data.get('full_name', '')
            qualification = data.get('qualification', '')
            dob = data.get('dob', '')
        else:
            if form.validate_on_submit():
                username = form.username.data
                password = form.password.data
                full_name = form.full_name.data
                qualification = form.qualification.data
                dob = form.dob.data
            else:
                # Add detailed error logging
                error_messages = []
                for field, errors in form.errors.items():
                    error_messages.append(f"{field}: {', '.join(errors)}")
                
                error_str = " | ".join(error_messages)
                print(f"Form validation errors: {error_str}")
                flash(f'Please check your input and try again. Errors: {error_str}', 'danger')
                return render_template('auth/register.html', form=form, csrf_token=csrf_token)
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            if is_json_requested():
                return jsonify({
                    'success': False,
                    'message': 'Username already exists'
                }), 400
                
            flash('Username already exists. Please choose a different one.', 'danger')
            return render_template('auth/register.html', form=form, csrf_token=csrf_token)
        
        new_user = User(username=username, full_name=full_name, 
                       qualification=qualification, dob=dob)
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            
            if is_json_requested():
                return jsonify({
                    'success': True,
                    'message': 'Registration successful',
                    'user': {
                        'username': new_user.username,
                        'full_name': new_user.full_name
                    }
                }), 201
                
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            
            if is_json_requested():
                return jsonify({
                    'success': False,
                    'message': 'Registration failed: ' + str(e)
                }), 500
                
            flash('An error occurred during registration. Please try again.', 'danger')
    
    return render_template('auth/register.html', form=form, csrf_token=csrf_token)

@auth.route('/logout')
def logout():
    """
    User Logout
    ---
    tags:
      - auth
    summary: Logout user
    description: Logs out a user and clears the session
    responses:
      302:
        description: Redirects to the home page after successful logout
    """
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.index'))

# The apidocs route was removed as it's redundant with Swagger UI accessible at /api/docs/ 