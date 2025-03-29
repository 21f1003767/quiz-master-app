from flask import Blueprint, render_template, redirect, url_for, flash, session, request, jsonify
from app.forms import LoginForm, RegistrationForm, AdminLoginForm
from app.models.models import User, Admin, db
from functools import wraps
import bcrypt
from app.utils import is_json_requested

auth = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
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

@auth.route('/')
def index():
    return render_template('index.html')

@auth.route('/login', methods=['POST', 'GET'])
def login():
    """
    User Login
    ---
    tags:
      - auth
    summary: Login user
    description: Authenticate and login a user
    consumes:
      - application/x-www-form-urlencoded
      - application/json
    parameters:
      - name: email
        in: formData
        description: User email
        required: true
        type: string
      - name: password
        in: formData
        description: User password
        required: true
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
                user:
                  type: object
                  properties:
                    id:
                      type: integer
                    name:
                      type: string
                    email:
                      type: string
                    role:
                      type: string
                message:
                  type: string
      400:
        description: Invalid input
      401:
        description: Login failed
    """
    if 'user_id' in session:
        if is_json_requested():
            user = User.query.get(session['user_id'])
            return jsonify({
                'success': True,
                'message': 'User already logged in',
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'role': user.role
                }
            })
        if session['role'] == 'ADMIN':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('user.dashboard'))
    
    form = LoginForm()
    
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            
        elif form.validate_on_submit():
            email = form.email.data
            password = form.password.data
        else:
            email = request.form.get('email')
            password = request.form.get('password')
            
        if not email or not password:
            if is_json_requested():
                return jsonify({
                    'success': False,
                    'message': 'Email and password are required'
                }), 400
            flash('Email and password are required', 'danger')
            return render_template('auth/login.html', form=form, title='Login')
        
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['name'] = user.name
            session['email'] = user.email
            session['role'] = user.role
            
            if is_json_requested():
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'user': {
                        'id': user.id,
                        'name': user.name,
                        'email': user.email,
                        'role': user.role
                    }
                })
            
            if user.role == 'ADMIN':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('user.dashboard'))
        else:
            if is_json_requested():
                return jsonify({
                    'success': False,
                    'message': 'Invalid email or password'
                }), 401
            flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html', form=form, title='Login')

@auth.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """
    Admin Login
    ---
    tags:
      - auth
    summary: Login as admin
    description: Authenticate and login as an admin
    consumes:
      - application/x-www-form-urlencoded
      - application/json
    parameters:
      - name: username
        in: formData
        description: Admin username
        required: true
        type: string
      - name: password
        in: formData
        description: Admin password
        required: true
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
                admin:
                  type: object
                  properties:
                    id:
                      type: integer
                    username:
                      type: string
                message:
                  type: string
      400:
        description: Invalid input
      401:
        description: Login failed
    """
    if 'admin_id' in session:
        if is_json_requested():
            admin = Admin.query.get(session['admin_id'])
            return jsonify({
                'success': True,
                'message': 'Admin already logged in',
                'admin': {
                    'id': admin.id,
                    'username': admin.username
                }
            })
        return redirect(url_for('admin.dashboard'))
    
    form = AdminLoginForm()
    
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        elif form.validate_on_submit():
            username = form.username.data
            password = form.password.data
        else:
            username = request.form.get('username')
            password = request.form.get('password')
            
        if not username or not password:
            if is_json_requested():
                return jsonify({
                    'success': False,
                    'message': 'Username and password are required'
                }), 400
            flash('Username and password are required', 'danger')
            return render_template('auth/admin_login.html', form=form, title='Admin Login')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and bcrypt.check_password_hash(admin.password, password):
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            
            if is_json_requested():
                return jsonify({
                    'success': True,
                    'message': 'Admin login successful',
                    'admin': {
                        'id': admin.id,
                        'username': admin.username
                    }
                })
            
            flash(f'Welcome, {admin.username}!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            if is_json_requested():
                return jsonify({
                    'success': False,
                    'message': 'Invalid username or password'
                }), 401
            flash('Invalid username or password', 'danger')
    
    return render_template('auth/admin_login.html', form=form, title='Admin Login')

@auth.route('/register', methods=['POST', 'GET'])
def register():
    """
    User Registration
    ---
    tags:
      - auth
    summary: Register new user
    description: Register a new user account
    consumes:
      - application/x-www-form-urlencoded
      - application/json
    parameters:
      - name: name
        in: formData
        description: User full name
        required: true
        type: string
      - name: email
        in: formData
        description: User email
        required: true
        type: string
      - name: password
        in: formData
        description: User password
        required: true
        type: string
      - name: confirm_password
        in: formData
        description: Password confirmation
        required: true
        type: string
    responses:
      201:
        description: Registration successful
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                user:
                  type: object
                  properties:
                    id:
                      type: integer
                    name:
                      type: string
                    email:
                      type: string
                message:
                  type: string
      400:
        description: Invalid input or user already exists
    """
    if 'user_id' in session:
        if is_json_requested():
            return jsonify({
                'success': False,
                'message': 'You are already logged in'
            }), 400
        flash('You are already logged in', 'info')
        if session['role'] == 'ADMIN':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('user.dashboard'))
    
    form = RegistrationForm()
    
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')
            confirm_password = data.get('confirm_password')
        elif form.validate_on_submit():
            name = form.name.data
            email = form.email.data
            password = form.password.data
            confirm_password = form.confirm_password.data
        else:
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
        
        validation_errors = []
        if not name or not email or not password or not confirm_password:
            validation_errors.append('All fields are required')
        
        if password != confirm_password:
            validation_errors.append('Passwords do not match')
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            validation_errors.append('Email already registered')
        
        if validation_errors:
            if is_json_requested():
                return jsonify({
                    'success': False,
                    'message': 'Validation failed',
                    'errors': validation_errors
                }), 400
            for error in validation_errors:
                flash(error, 'danger')
            return render_template('auth/register.html', form=form, title='Register')
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        new_user = User(name=name, email=email, password=hashed_password, role='USER')
        db.session.add(new_user)
        db.session.commit()
        
        if is_json_requested():
            return jsonify({
                'success': True,
                'message': 'Registration successful. You can now login.',
                'user': {
                    'id': new_user.id,
                    'name': new_user.name,
                    'email': new_user.email
                }
            }), 201
        
        flash('Registration successful! You can now login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form, title='Register')

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

@auth.route('/api')
def api_info():
    """
    API Information
    ---
    tags:
      - api
    summary: Get API information
    description: Get information about the API endpoints and documentation
    responses:
      200:
        description: Successful operation
    """
    return render_template('api_info.html', title='API Documentation') 