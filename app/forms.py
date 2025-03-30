from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, ValidationError, TextAreaField, SelectField, IntegerField, DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, Regexp, ValidationError
from app.models.models import User, Admin
from datetime import date, timedelta
import re

class LoginForm(FlaskForm):
    username = StringField('Email', validators=[
        DataRequired(message="Email is required"), 
        Email(message="Please enter a valid email address")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required")
    ])
    submit = SubmitField('Login')

class AdminLoginForm(FlaskForm):
    username = StringField('Email', validators=[
        DataRequired(message="Email is required"), 
        Email(message="Please enter a valid email address")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required")
    ])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Email', validators=[
        DataRequired(message="Email is required"), 
        Email(message="Please enter a valid email address"),
        Length(max=100, message="Email must be less than 100 characters")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required"),
        Length(min=6, message="Password must be at least 6 characters long"),
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{6,}$', 
               message="Password must contain at least one letter and one number")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Please confirm your password"),
        EqualTo('password', message="Passwords must match")
    ])
    full_name = StringField('Full Name', validators=[
        DataRequired(message="Full name is required"),
        Length(min=2, max=100, message="Full name must be between 2 and 100 characters"),
        Regexp(r'^[A-Za-z\s]+$', message="Full name should contain only letters and spaces")
    ])
    qualification = StringField('Qualification', validators=[
        DataRequired(message="Qualification is required"),
        Length(max=100, message="Qualification must be less than 100 characters")
    ])
    dob = DateField('Date of Birth', validators=[
        DataRequired(message="Date of Birth is required")
    ], format='%Y-%m-%d')
    
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That email is already registered. Please use a different one.')
            
    def validate_dob(self, dob):
        today = date.today()
        if dob.data > today:
            raise ValidationError('Date of Birth cannot be in the future.')
        
        age = today.year - dob.data.year - ((today.month, today.day) < (dob.data.month, dob.data.day))
        if age < 10:
            raise ValidationError('You must be at least 10 years old to register.')
        elif age > 100:
            raise ValidationError('Please enter a valid date of birth.')


class SubjectForm(FlaskForm):
    name = StringField('Subject Name', validators=[
        DataRequired(message="Subject name is required"),
        Length(min=2, max=100, message="Subject name must be between 2 and 100 characters")
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(message="Description is required"),
        Length(min=10, max=500, message="Description must be between 10 and 500 characters")
    ])
    submit = SubmitField('Submit')


class ChapterForm(FlaskForm):
    name = StringField('Chapter Name', validators=[
        DataRequired(message="Chapter name is required"),
        Length(min=2, max=100, message="Chapter name must be between 2 and 100 characters")
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(message="Description is required"),
        Length(min=10, max=500, message="Description must be between 10 and 500 characters")
    ])
    subject_id = SelectField('Subject', coerce=int, validators=[
        DataRequired(message="Please select a subject")
    ])
    submit = SubmitField('Submit')


class QuizForm(FlaskForm):
    title = StringField('Quiz Title', validators=[
        DataRequired(message="Quiz title is required"),
        Length(min=3, max=100, message="Quiz title must be between 3 and 100 characters")
    ])
    chapter_id = SelectField('Chapter', coerce=int, validators=[
        DataRequired(message="Please select a chapter")
    ])
    date_of_quiz = DateField('Date of Quiz', format='%Y-%m-%d', validators=[
        DataRequired(message="Quiz date is required")
    ])
    time_duration = StringField('Duration (HH:MM)', validators=[
        DataRequired(message="Duration is required"),
        Regexp(r'^([0-9]{1,2}):([0-5][0-9])$', message="Duration must be in the format HH:MM")
    ])
    remarks = TextAreaField('Remarks', validators=[
        Optional(),
        Length(max=500, message="Remarks must be less than 500 characters")
    ])
    submit = SubmitField('Submit')
    
    def validate_date_of_quiz(self, date_of_quiz):
        today = date.today()
        if date_of_quiz.data < today:
            raise ValidationError('Quiz date cannot be in the past.')


class QuestionForm(FlaskForm):
    question_statement = TextAreaField('Question', validators=[
        DataRequired(message="Question statement is required"),
        Length(min=10, max=500, message="Question must be between 10 and 500 characters")
    ])
    option1 = StringField('Option 1', validators=[
        DataRequired(message="Option 1 is required"),
        Length(min=1, max=200, message="Option must be between 1 and 200 characters")
    ])
    option2 = StringField('Option 2', validators=[
        DataRequired(message="Option 2 is required"),
        Length(min=1, max=200, message="Option must be between 1 and 200 characters")
    ])
    option3 = StringField('Option 3', validators=[
        DataRequired(message="Option 3 is required"),
        Length(min=1, max=200, message="Option must be between 1 and 200 characters")
    ])
    option4 = StringField('Option 4', validators=[
        DataRequired(message="Option 4 is required"),
        Length(min=1, max=200, message="Option must be between 1 and 200 characters")
    ])
    correct_option = SelectField('Correct Answer', 
                               choices=[(1, 'Option 1'), (2, 'Option 2'), (3, 'Option 3'), (4, 'Option 4')],
                               coerce=int, 
                               validators=[DataRequired(message="Please select the correct option")])
    submit = SubmitField('Submit') 