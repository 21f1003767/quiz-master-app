from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length
from app.models.models import User
from datetime import date

class LoginForm(FlaskForm):
    username = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AdminLoginForm(FlaskForm):
    username = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    full_name = StringField('Full Name', validators=[DataRequired()])
    qualification = StringField('Qualification', validators=[DataRequired()])
    dob = DateField('Date of Birth', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That email is already registered. Please use a different one.')
            
    def validate_dob(self, dob):
        if dob.data > date.today():
            raise ValidationError('Date of Birth cannot be in the future.') 