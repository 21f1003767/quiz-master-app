from flask import request, jsonify, session, redirect, url_for
from datetime import datetime
from functools import wraps
import re
import secrets
from flask_wtf.csrf import validate_csrf, generate_csrf

def is_json_request():
    """Check if the current request is a JSON request based on Content-Type header"""
    return request.is_json or request.headers.get('Content-Type') == 'application/json'

def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            if is_json_request():
                return jsonify({
                    'success': False,
                    'message': 'Admin authentication required'
                }), 401
            return redirect(url_for('auth.admin_login'))
        return func(*args, **kwargs)
    return decorated_function

def user_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if is_json_request():
                return jsonify({
                    'success': False,
                    'message': 'User authentication required'
                }), 401
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return decorated_function

def api_csrf_protected(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # Skip CSRF for non-mutating methods
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return func(*args, **kwargs)
            
        # Handle token validation
        token = None
        
        if is_json_request():
            # For JSON requests, get token from JSON body
            data = request.get_json(silent=True) or {}
            token = data.get('csrf_token')
        else:
            # For form submissions, get token from form data
            token = request.form.get('csrf_token')
            
        # If token not found in request, check headers
        if not token:
            token = request.headers.get('X-CSRF-TOKEN')
            
        # Validate the token
        try:
            if not token or not validate_csrf(token):
                if is_json_request():
                    return jsonify({
                        'success': False,
                        'message': 'CSRF token missing or invalid'
                    }), 400
                # For non-JSON requests, let Flask-WTF handle it
                pass
        except Exception as e:
            if is_json_request():
                return jsonify({
                    'success': False,
                    'message': 'CSRF token validation failed'
                }), 400
            # For non-JSON requests, let Flask-WTF handle it
            pass
            
        return func(*args, **kwargs)
    return decorated_function

def ensure_csrf_token():
    """Ensure a CSRF token is in the session"""
    if 'csrf_token' not in session:
        session['csrf_token'] = generate_csrf()
    return session['csrf_token']

def serialize_subject(subject):
    """Convert a subject object to a dictionary for JSON response"""
    return {
        'id': subject.id,
        'name': subject.name,
        'description': subject.description,
        'created_at': subject.created_at.isoformat() if subject.created_at else None,
        'updated_at': subject.updated_at.isoformat() if subject.updated_at else None
    }

def serialize_chapter(chapter):
    """Convert a chapter object to a dictionary for JSON response"""
    return {
        'id': chapter.id,
        'name': chapter.name,
        'description': chapter.description,
        'subject_id': chapter.subject_id,
        'created_at': chapter.created_at.isoformat() if chapter.created_at else None,
        'updated_at': chapter.updated_at.isoformat() if chapter.updated_at else None
    }

def format_date(date_obj, format_str='%d-%m-%Y'):
    """Format date objects for display"""
    if date_obj:
        return date_obj.strftime(format_str)
    return ''

def serialize_quiz(quiz, user_id=None):
    """Serialize a Quiz model to a dictionary"""
    quiz_data = {
        'id': quiz.id,
        'title': quiz.title,
        'chapter_id': quiz.chapter_id,
        'chapter_name': quiz.chapter.name if quiz.chapter else None,
        'quiz_date': quiz.quiz_date.isoformat() if quiz.quiz_date else None,
        'duration': quiz.duration,
        'remarks': quiz.remarks,
        'created_at': quiz.created_at.isoformat() if quiz.created_at else None,
        'questions_count': len(quiz.questions)
    }
    
    # Add user-specific score data if a user_id is provided
    if user_id:
        from app.models.models import Score
        score = Score.query.filter_by(quiz_id=quiz.id, user_id=user_id).first()
        if score:
            quiz_data['user_score'] = {
                'score': score.score,
                'total': score.total,
                'percentage': score.percentage,
                'attempted_at': score.attempted_at.isoformat() if score.attempted_at else None
            }
        else:
            quiz_data['user_score'] = None
    
    return quiz_data

def serialize_question(question, include_correct_answer=False):
    """Serialize a Question model to a dictionary"""
    question_data = {
        'id': question.id,
        'quiz_id': question.quiz_id,
        'question_statement': question.question_statement,
        'option_a': question.option_a,
        'option_b': question.option_b,
        'option_c': question.option_c,
        'option_d': question.option_d,
    }
    
    if include_correct_answer:
        question_data['correct_option'] = question.correct_option
    
    return question_data

def serialize_score(score):
    """Serialize a Score model to a dictionary"""
    return {
        'id': score.id,
        'user_id': score.user_id,
        'quiz_id': score.quiz_id,
        'quiz_title': score.quiz.title if score.quiz else None,
        'score': score.score,
        'total': score.total,
        'percentage': score.percentage,
        'attempted_at': score.attempted_at.isoformat() if score.attempted_at else None
    }

def json_response(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_json_request():
            return f(*args, **kwargs)
        
        response = f(*args, **kwargs)
        
        if is_json_request():
            if isinstance(response, tuple) and len(response) > 1:
                template_name, template_data = response
                return jsonify(template_data)
            elif isinstance(response, str):
                # Assume it's a template render
                return jsonify({'html': response})
        
        return response
    return decorated_function 