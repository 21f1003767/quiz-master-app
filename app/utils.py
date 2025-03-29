from flask import request, jsonify, session
from datetime import datetime
from functools import wraps

def is_json_requested():
    """Check if JSON response is requested instead of HTML"""
    if request.headers.get('Accept') == 'application/json':
        return True
    return request.args.get('format') == 'json'

def serialize_subject(subject):
    """Serialize a Subject model to a dictionary"""
    return {
        'id': subject.id,
        'name': subject.name,
        'description': subject.description,
        'created_at': subject.created_at.isoformat() if subject.created_at else None,
        'chapters_count': len(subject.chapters)
    }

def serialize_chapter(chapter):
    """Serialize a Chapter model to a dictionary"""
    return {
        'id': chapter.id,
        'name': chapter.name,
        'description': chapter.description,
        'subject_id': chapter.subject_id,
        'subject_name': chapter.subject.name,
        'created_at': chapter.created_at.isoformat() if chapter.created_at else None,
        'quizzes_count': len(chapter.quizzes)
    }

def serialize_quiz(quiz, user_id=None):
    """Serialize a Quiz model to a dictionary"""
    from app.models.models import score
    attempted = False
    score = None

    if user_id:
        user_score = Score.query.filter_by(quiz_id=quiz.id, user_id=user_id).first()
        attempted = user_score is not None
        
        if attempted and user_score:
            score = {
                'score_id': user_score.id,
                'total_scored': user_score.total_scored,
                'total_questions': user_score.total_questions,
                'percentage': (user_score.total_scored / user_score.total_questions * 100) if user_score.total_questions > 0 else 0,
                'attempt_date': user_score.time_stamp_of_attempt.isoformat() if user_score.time_stamp_of_attempt else None
            }
    
    return {
        'id': quiz.id,
        'title': quiz.title,
        'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
        'time_duration': quiz.time_duration,
        'availability_window': quiz.get_availability_window(),
        'remarks': quiz.remarks,
        'created_at': quiz.created_at.isoformat() if quiz.created_at else None,
        'is_available': quiz.is_available(),
        'is_upcoming': quiz.date_of_quiz > datetime.utcnow().date() if quiz.date_of_quiz else False,
        'chapter_id': quiz.chapter_id,
        'chapter_name': quiz.chapter.name,
        'subject_id': quiz.chapter.subject_id,
        'subject_name': quiz.chapter.subject.name,
        'questions_count': len(quiz.questions),
        'attempted': attempted,
        'score': score
    }

def serialize_question(question, include_correct_answer=False):
    """Serialize a Question model to a dictionary"""
    result = {
        'id': question.id,
        'question_statement': question.question_statement,
        'options': [
            question.option1,
            question.option2,
            question.option3,
            question.option4
        ]
    }

    if include_correct_answer:
        result['correct_option'] = question.correct_option
        
    return result

def serialize_score(score):
    """Serialize a Score model to a dictionary"""
    return {
        'id': score.id,
        'quiz_id': score.quiz_id,
        'quiz_title': score.quiz.title,
        'chapter_name': score.quiz.chapter.name,
        'subject_name': score.quiz.chapter.subject.name,
        'total_scored': score.total_scored,
        'total_questions': score.total_questions,
        'percentage': (score.total_scored / score.total_questions * 100) if score.total_questions > 0 else 0,
        'attempt_date': score.time_stamp_of_attempt.isoformat() if score.time_stamp_of_attempt else None
    }

def api_response(func):
    """Decorator for routes that can return either HTML or JSON"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        
        if is_json_requested():
            if isinstance(response, tuple) and len(response) > 1:
                template_name, template_data = response
                return jsonify(template_data), 200
            return jsonify({'success': True}), 200
        return response
    
    return wrapper 