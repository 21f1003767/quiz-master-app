from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from app.forms import LoginForm, RegistrationForm, AdminLoginForm
from app.models.models import User, Admin, db
from functools import wraps

auth = Blueprint('auth', __name__)

# Login required decorators
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

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('user.dashboard'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            session['username'] = user.username
            session['full_name'] = user.full_name
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(url_for('user.dashboard'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')
    return render_template('auth/login.html', form=form, title='User Login')

@auth.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'admin_id' in session:
        return redirect(url_for('admin.dashboard'))
        
    form = AdminLoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and admin.check_password(form.password.data):
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            flash('Welcome back, Admin!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Admin login failed. Please check your credentials.', 'danger')
    return render_template('auth/admin_login.html', form=form, title='Admin Login')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('user.dashboard'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            full_name=form.full_name.data,
            qualification=form.qualification.data,
            dob=form.dob.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form, title='Register')

@auth.route('/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id')
        session.pop('username')
        session.pop('full_name')
        flash('You have been logged out.', 'info')
    if 'admin_id' in session:
        session.pop('admin_id')
        session.pop('admin_username')
        flash('Admin logged out.', 'info')
    return redirect(url_for('auth.index')) 