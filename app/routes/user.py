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
    
    # Get questions
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    total_questions = len(questions)
    
    # Calculate score
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