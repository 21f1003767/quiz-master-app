from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from app.models.models import User, Subject, Quiz, Score, Chapter, Question, db
from app.routes.auth import login_required
from datetime import datetime
import json

user = Blueprint('user', __name__)

@user.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    user = User.query.get(user_id)
  
    subjects = Subject.query.all()
    
    recent_scores = Score.query.filter_by(user_id=user_id).order_by(Score.time_stamp_of_attempt.desc()).limit(5).all()
    
    attempted_quiz_ids = [score.quiz_id for score in Score.query.filter_by(user_id=user_id).all()]
    
    return render_template('user/dashboard.html', 
                           title='User Dashboard',
                           user=user,
                           subjects=subjects,
                           recent_scores=recent_scores,
                           attempted_quiz_ids=attempted_quiz_ids)

@user.route('/subjects')
@login_required
def subject_list():
    subjects = Subject.query.all()
    return render_template('user/subjects/list.html',
                          title='Available Subjects',
                          subjects=subjects)

@user.route('/subjects/<int:subject_id>/chapters')
@login_required
def chapter_list(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return render_template('user/chapters/list.html',
                          title=f'Chapters in {subject.name}',
                          subject=subject,
                          chapters=chapters)

@user.route('/chapters/<int:chapter_id>/quizzes')
@login_required
def quiz_list(chapter_id):
    user_id = session['user_id']
    chapter = Chapter.query.get_or_404(chapter_id)
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
 
    user_scores = {}
    for quiz in quizzes:
        score = Score.query.filter_by(user_id=user_id, quiz_id=quiz.id).first()
        if score:
            user_scores[quiz.id] = score
    
    return render_template('user/quizzes/list.html',
                          title=f'Quizzes in {chapter.name}',
                          chapter=chapter,
                          quizzes=quizzes,
                          user_id=user_id,
                          user_scores=user_scores)

@user.route('/quizzes/<int:quiz_id>/start')
@login_required
def quiz_start(quiz_id):
    user_id = session['user_id']
    quiz = Quiz.query.get_or_404(quiz_id)
  
    existing_score = Score.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
    if existing_score:
        flash('You have already attempted this quiz. You scored {} out of {} questions.'.format(
            existing_score.total_scored, existing_score.total_questions), 'info')
        return redirect(url_for('user.quiz_list', chapter_id=quiz.chapter_id))

    if not quiz.is_available():
        availability_window = quiz.get_availability_window()
        flash(f'This quiz is not available for attempt at this time. It is scheduled for {quiz.date_of_quiz.strftime("%Y-%m-%d")} during the time window {availability_window}.', 'warning')
        return redirect(url_for('user.quiz_list', chapter_id=quiz.chapter_id))

    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    if not questions:
        flash('This quiz has no questions yet!', 'warning')
        return redirect(url_for('user.quiz_list', chapter_id=quiz.chapter_id))

    duration_parts = quiz.time_duration.split(':')
    total_seconds = int(duration_parts[0]) * 3600 + int(duration_parts[1]) * 60
    
    return render_template('user/quizzes/attempt.html',
                          title=f'Attempt Quiz: {quiz.title}',
                          quiz=quiz,
                          questions=questions,
                          total_seconds=total_seconds)

@user.route('/quizzes/<int:quiz_id>/submit', methods=['POST'])
@login_required
def quiz_submit(quiz_id):
    user_id = session['user_id']
    quiz = Quiz.query.get_or_404(quiz_id)
    
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    total_questions = len(questions)
    
    score = 0
    user_answers = {}
    
    for question in questions:
        answer_key = f'question_{question.id}'
        if answer_key in request.form:
            user_answer = int(request.form[answer_key])
            user_answers[question.id] = user_answer
            if user_answer == question.correct_option:
                score += 1
    
    new_score = Score(
        quiz_id=quiz_id,
        user_id=user_id,
        time_stamp_of_attempt=datetime.utcnow(),
        total_scored=score,
        total_questions=total_questions
    )
    
    db.session.add(new_score)
    db.session.commit()
    
    session['quiz_results'] = {
        'user_answers': user_answers,
        'score_id': new_score.id
    }
    
    return redirect(url_for('user.quiz_result', quiz_id=quiz_id))

@user.route('/quizzes/<int:quiz_id>/result')
@login_required
def quiz_result(quiz_id):
    user_id = session['user_id']
    quiz = Quiz.query.get_or_404(quiz_id)
    
    quiz_results = session.get('quiz_results', {})
    user_answers = quiz_results.get('user_answers', {})
    score_id = quiz_results.get('score_id')
    
    if not user_answers or not score_id:
        flash('No quiz results found!', 'danger')
        return redirect(url_for('user.dashboard'))
    
    score = Score.query.get(score_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    session.pop('quiz_results', None)
    
    return render_template('user/quizzes/result.html',
                          title=f'Quiz Results: {quiz.title}',
                          quiz=quiz,
                          score=score,
                          questions=questions,
                          user_answers=user_answers)

@user.route('/quiz-history')
@login_required
def quiz_history():
    user_id = session['user_id']
    user = User.query.get(user_id)

    scores = Score.query.filter_by(user_id=user_id).order_by(Score.time_stamp_of_attempt.desc()).all()
    
    total_quizzes = len(scores)
    total_questions = sum(score.total_questions for score in scores)
    total_correct = sum(score.total_scored for score in scores)
    
    avg_score = 0
    if total_questions > 0:
        avg_score = (total_correct / total_questions) * 100

    subject_performance = {}
    for score in scores:
        subject_id = score.quiz.chapter.subject.id
        subject_name = score.quiz.chapter.subject.name
        
        if subject_id not in subject_performance:
            subject_performance[subject_id] = {
                'name': subject_name,
                'total_quizzes': 0,
                'total_questions': 0,
                'total_correct': 0,
                'percentage': 0
            }
        
        subject_performance[subject_id]['total_quizzes'] += 1
        subject_performance[subject_id]['total_questions'] += score.total_questions
        subject_performance[subject_id]['total_correct'] += score.total_scored

    for subject_id in subject_performance:
        total_q = subject_performance[subject_id]['total_questions']
        total_c = subject_performance[subject_id]['total_correct']
        if total_q > 0:
            subject_performance[subject_id]['percentage'] = (total_c / total_q) * 100
    
    return render_template('user/quiz_history.html',
                          title='Quiz History',
                          user=user,
                          scores=scores,
                          total_quizzes=total_quizzes,
                          total_questions=total_questions,
                          total_correct=total_correct,
                          avg_score=avg_score,
                          subject_performance=subject_performance)

@user.route('/quizzes/<int:quiz_id>/report')
@login_required
def quiz_report(quiz_id):
    user_id = session['user_id']
    quiz = Quiz.query.get_or_404(quiz_id)
 
    score = Score.query.filter_by(user_id=user_id, quiz_id=quiz_id).first_or_404()
 
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
  
    all_scores = Score.query.filter_by(quiz_id=quiz_id).all()
    total_attempts = len(all_scores)
 
    avg_score = 0
    if total_attempts > 0:
        avg_score = sum(s.total_scored for s in all_scores) / (total_attempts * len(questions)) * 100
    
    return render_template('user/quizzes/report.html',
                          title=f'Quiz Report: {quiz.title}',
                          quiz=quiz,
                          score=score,
                          questions=questions,
                          total_attempts=total_attempts,
                          avg_score=avg_score)

@user.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query', '')
    search_type = request.args.get('type', 'all')
    
    if not query:
        return render_template('user/search/results.html', 
                               title='Search Results',
                               query='',
                               search_type='all',
                               subjects=[],
                               chapters=[],
                               quizzes=[])
    
    subjects = []
    if search_type in ['all', 'subjects']:
        subjects = Subject.query.filter(
            (Subject.name.ilike(f'%{query}%')) |
            (Subject.description.ilike(f'%{query}%'))
        ).all()
    
    chapters = []
    if search_type in ['all', 'chapters']:
        chapters = Chapter.query.filter(
            (Chapter.name.ilike(f'%{query}%')) |
            (Chapter.description.ilike(f'%{query}%'))
        ).all()
    
    quizzes = []
    if search_type in ['all', 'quizzes']:
        quizzes = Quiz.query.filter(
            (Quiz.title.ilike(f'%{query}%')) |
            (Quiz.remarks.ilike(f'%{query}%'))
        ).all()
    
    user_id = session['user_id']
    attempted_quiz_ids = [score.quiz_id for score in Score.query.filter_by(user_id=user_id).all()]
    
    return render_template('user/search/results.html', 
                           title='Search Results',
                           query=query,
                           search_type=search_type,
                           subjects=subjects,
                           chapters=chapters,
                           quizzes=quizzes,
                           attempted_quiz_ids=attempted_quiz_ids) 