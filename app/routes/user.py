from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify, abort
from app.models.models import User, Subject, Quiz, Score, Chapter, Question, db
from app.routes.auth import login_required
from app.utils import is_json_requested, serialize_subject, serialize_chapter, serialize_quiz, serialize_question, serialize_score
from datetime import datetime
import json

user = Blueprint('user', __name__)

@user.route('/dashboard')
@login_required
def dashboard():
    """
    User Dashboard
    ---
    tags:
      - user
    summary: Get user dashboard data
    description: Returns user information, recent subjects, and recent scores
    responses:
      200:
        description: Successful operation
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
                    username:
                      type: string
                    full_name:
                      type: string
                    qualification:
                      type: string
                    dob:
                      type: string
                      format: date
                recent_subjects:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      name:
                        type: string
                      description:
                        type: string
                      created_at:
                        type: string
                        format: date-time
                      chapters_count:
                        type: integer
                recent_scores:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      quiz_id:
                        type: integer
                      quiz_title:
                        type: string
                      chapter_name:
                        type: string
                      subject_name:
                        type: string
                      total_scored:
                        type: integer
                      total_questions:
                        type: integer
                      percentage:
                        type: number
                        format: float
                      attempt_date:
                        type: string
                        format: date-time
    """
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    if is_json_requested():
        subjects = Subject.query.order_by(Subject.id.desc()).limit(3).all()
        recent_scores = Score.query.filter_by(user_id=user_id).order_by(Score.time_stamp_of_attempt.desc()).limit(5).all()
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'qualification': user.qualification,
                'dob': user.dob.isoformat() if user.dob else None
            },
            'recent_subjects': [serialize_subject(subject) for subject in subjects],
            'recent_scores': [serialize_score(score) for score in recent_scores]
        })
    
    return render_template('user/dashboard.html',
                           title='User Dashboard',
                           user=user)

@user.route('/subjects')
@login_required
def subject_list():
    """
    Subjects List
    ---
    tags:
      - user
    summary: Get all subjects
    description: Returns a list of all available subjects
    responses:
      200:
        description: Successful operation
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                count:
                  type: integer
                subjects:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      name:
                        type: string
                      description:
                        type: string
                      created_at:
                        type: string
                        format: date-time
                      chapters_count:
                        type: integer
    """
    subjects = Subject.query.all()
    
    if is_json_requested():
        return jsonify({
            'success': True,
            'count': len(subjects),
            'subjects': [serialize_subject(subject) for subject in subjects]
        })
    
    return render_template('user/subjects/list.html',
                          title='Available Subjects')

@user.route('/subjects/<int:subject_id>')
@login_required
def subject_detail(subject_id):
    """Get a specific subject by ID"""
    subject = Subject.query.get_or_404(subject_id)
    
    if is_json_requested():
        return jsonify({
            'success': True,
            'subject': serialize_subject(subject)
        })
    
    return redirect(url_for('user.chapter_list', subject_id=subject_id))

@user.route('/subjects/<int:subject_id>/chapters')
@login_required
def chapter_list(subject_id):
    """
    List Chapters
    ---
    tags:
      - user
    summary: Get chapters for a subject
    description: Returns all chapters for a specific subject
    parameters:
      - name: subject_id
        in: path
        description: ID of the subject
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Successful operation
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                subject:
                  type: object
                  properties:
                    id:
                      type: integer
                    name:
                      type: string
                    description:
                      type: string
                count:
                  type: integer
                chapters:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      name:
                        type: string
                      description:
                        type: string
                      quiz_count:
                        type: integer
      404:
        description: Subject not found
    """
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    
    for chapter in chapters:
        chapter.quiz_count = Quiz.query.filter_by(chapter_id=chapter.id).count()
    
    if is_json_requested():
        return jsonify({
            'success': True,
            'subject': serialize_subject(subject),
            'count': len(chapters),
            'chapters': [serialize_chapter(chapter) for chapter in chapters]
        })
    
    return render_template('user/chapters/list.html', 
                        subject=subject,
                        chapters=chapters,
                        title=f'Chapters - {subject.name}')

@user.route('/chapters/<int:chapter_id>')
@login_required
def chapter_detail(chapter_id):
    """Get a specific chapter by ID"""
    chapter = Chapter.query.get_or_404(chapter_id)
    
    if is_json_requested():
        return jsonify({
            'success': True,
            'chapter': serialize_chapter(chapter)
        })
    
    return redirect(url_for('user.quiz_list', chapter_id=chapter_id))

@user.route('/chapters/<int:chapter_id>/quizzes')
@login_required
def quiz_list(chapter_id):
    """
    List Quizzes
    ---
    tags:
      - user
    summary: Get quizzes for a chapter
    description: Returns all quizzes for a specific chapter
    parameters:
      - name: chapter_id
        in: path
        description: ID of the chapter
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Successful operation
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                chapter:
                  type: object
                  properties:
                    id:
                      type: integer
                    name:
                      type: string
                    description:
                      type: string
                    subject_id:
                      type: integer
                    subject_name:
                      type: string
                count:
                  type: integer
                quizzes:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      title:
                        type: string
                      description:
                        type: string
                      date_of_quiz:
                        type: string
                        format: date
                      time_duration:
                        type: string
                      availability_start:
                        type: string
                        format: time
                      availability_end:
                        type: string
                        format: time
                      is_available:
                        type: boolean
                      availability_window:
                        type: string
                      user_score:
                        type: object
                        nullable: true
                        properties:
                          score_id:
                            type: integer
                          total_scored:
                            type: integer
                          total_questions:
                            type: integer
                          percentage:
                            type: number
                            format: float
      404:
        description: Chapter not found
    """
    chapter = Chapter.query.get_or_404(chapter_id)
    subject = Subject.query.get(chapter.subject_id)
    user_id = session['user_id']
    
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    
    for quiz in quizzes:
        score = Score.query.filter_by(user_id=user_id, quiz_id=quiz.id).first()
        quiz.user_score = score
        
        quiz.is_available = quiz.is_available()
        quiz.availability_window = quiz.get_availability_window()
    
    if is_json_requested():
        return jsonify({
            'success': True,
            'chapter': {
                **serialize_chapter(chapter),
                'subject_name': subject.name
            },
            'count': len(quizzes),
            'quizzes': [serialize_quiz(quiz) for quiz in quizzes]
        })
    
    return render_template('user/quizzes/list.html', 
                         chapter=chapter,
                         subject=subject,
                         quizzes=quizzes,
                         title=f'Quizzes - {chapter.name}')

@user.route('/quizzes/<int:quiz_id>')
@login_required
def quiz_detail(quiz_id):
    """Get a specific quiz by ID"""
    user_id = session['user_id']
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if is_json_requested():
        return jsonify({
            'success': True,
            'quiz': serialize_quiz(quiz, user_id)
        })
    
    return redirect(url_for('user.quiz_start', quiz_id=quiz_id))

@user.route('/quizzes/<int:quiz_id>/questions')
@login_required
def quiz_questions(quiz_id):
    """
    Quiz Questions
    ---
    tags:
      - user
    summary: Get questions for a quiz
    description: Returns all questions for a specific quiz
    parameters:
      - name: quiz_id
        in: path
        description: ID of the quiz
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Successful operation
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                quiz_id:
                  type: integer
                title:
                  type: string
                total_questions:
                  type: integer
                time_duration:
                  type: string
                total_seconds:
                  type: integer
                questions:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      question_statement:
                        type: string
                      options:
                        type: array
                        items:
                          type: string
      403:
        description: Quiz already attempted or not available
      404:
        description: Quiz not found or has no questions
    """
    user_id = session['user_id']
    quiz = Quiz.query.get_or_404(quiz_id)
    
    existing_score = Score.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
    if existing_score:
        if is_json_requested():
            return jsonify({
                'success': False,
                'message': f'You have already attempted this quiz. You scored {existing_score.total_scored} out of {existing_score.total_questions} questions.'
            }), 403
        flash(f'You have already attempted this quiz. You scored {existing_score.total_scored} out of {existing_score.total_questions} questions.', 'info')
        return redirect(url_for('user.quiz_list', chapter_id=quiz.chapter_id))
    
    if not quiz.is_available():
        availability_window = quiz.get_availability_window()
        if is_json_requested():
            return jsonify({
                'success': False,
                'message': f'This quiz is not available for attempt at this time. It is scheduled for {quiz.date_of_quiz.strftime("%Y-%m-%d")} during the time window {availability_window}.'
            }), 403
        flash(f'This quiz is not available for attempt at this time. It is scheduled for {quiz.date_of_quiz.strftime("%Y-%m-%d")} during the time window {availability_window}.', 'warning')
        return redirect(url_for('user.quiz_list', chapter_id=quiz.chapter_id))
    
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    if not questions:
        if is_json_requested():
            return jsonify({
                'success': False,
                'message': 'This quiz has no questions yet!'
            }), 404
        flash('This quiz has no questions yet!', 'warning')
        return redirect(url_for('user.quiz_list', chapter_id=quiz.chapter_id))
    
    duration_parts = quiz.time_duration.split(':')
    total_seconds = int(duration_parts[0]) * 3600 + int(duration_parts[1]) * 60
    
    if is_json_requested():
        return jsonify({
            'success': True,
            'quiz_id': quiz.id,
            'title': quiz.title,
            'total_questions': len(questions),
            'time_duration': quiz.time_duration,
            'total_seconds': total_seconds,
            'questions': [serialize_question(question) for question in questions]
        })
    
    return redirect(url_for('user.quiz_start', quiz_id=quiz_id))

@user.route('/quizzes/<int:quiz_id>/start')
@login_required
def quiz_start(quiz_id):
    user_id = session['user_id']
    quiz = Quiz.query.get_or_404(quiz_id)
  
    existing_score = Score.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
    if existing_score:
        if is_json_requested():
            return jsonify({
                'success': False,
                'message': f'You have already attempted this quiz. You scored {existing_score.total_scored} out of {existing_score.total_questions} questions.'
            }), 403
        flash('You have already attempted this quiz. You scored {} out of {} questions.'.format(
            existing_score.total_scored, existing_score.total_questions), 'info')
        return redirect(url_for('user.quiz_list', chapter_id=quiz.chapter_id))

    if not quiz.is_available():
        availability_window = quiz.get_availability_window()
        if is_json_requested():
            return jsonify({
                'success': False,
                'message': f'This quiz is not available for attempt at this time. It is scheduled for {quiz.date_of_quiz.strftime("%Y-%m-%d")} during the time window {availability_window}.'
            }), 403
        flash(f'This quiz is not available for attempt at this time. It is scheduled for {quiz.date_of_quiz.strftime("%Y-%m-%d")} during the time window {availability_window}.', 'warning')
        return redirect(url_for('user.quiz_list', chapter_id=quiz.chapter_id))

    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    if not questions:
        if is_json_requested():
            return jsonify({
                'success': False,
                'message': 'This quiz has no questions yet!'
            }), 404
        flash('This quiz has no questions yet!', 'warning')
        return redirect(url_for('user.quiz_list', chapter_id=quiz.chapter_id))

    duration_parts = quiz.time_duration.split(':')
    total_seconds = int(duration_parts[0]) * 3600 + int(duration_parts[1]) * 60
    
    if is_json_requested():
        return jsonify({
            'success': True,
            'quiz_id': quiz.id,
            'title': quiz.title,
            'time_duration': quiz.time_duration,
            'total_seconds': total_seconds,
            'questions': [serialize_question(question) for question in questions]
        })
    
    return render_template('user/quizzes/attempt.html',
                          title=f'Attempt Quiz: {quiz.title}',
                          quiz=quiz,
                          questions=questions,
                          total_seconds=total_seconds)

@user.route('/quizzes/<int:quiz_id>/submit', methods=['POST'])
@login_required
def quiz_submit(quiz_id):
    """
    Submit Quiz
    ---
    tags:
      - user
    summary: Submit quiz answers
    description: Submit answers for a quiz and get the score
    parameters:
      - name: quiz_id
        in: path
        description: ID of the quiz
        required: true
        schema:
          type: integer
    requestBody:
      description: Quiz answers
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              answers:
                type: object
                additionalProperties:
                  type: integer
                example:
                  "1": 3
                  "2": 1
                  "3": 4
    responses:
      200:
        description: Successful operation
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                score_id:
                  type: integer
                total_scored:
                  type: integer
                total_questions:
                  type: integer
                percentage:
                  type: number
                  format: float
                question_results:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      correct:
                        type: boolean
                      correct_option:
                        type: integer
                      user_answer:
                        type: integer
      400:
        description: Invalid input or no answers provided
      403:
        description: Quiz already attempted
      404:
        description: Quiz not found or has no questions
    """
    user_id = session['user_id']
    quiz = Quiz.query.get_or_404(quiz_id)
    existing_score = Score.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
    if existing_score:
        if is_json_requested():
            return jsonify({
                'success': False,
                'message': f'You have already attempted this quiz. You scored {existing_score.total_scored} out of {existing_score.total_questions} questions.'
            }), 403
        flash('You have already attempted this quiz!', 'warning')
        return redirect(url_for('user.quiz_list', chapter_id=quiz.chapter_id))
    
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    total_questions = len(questions)
    
    score = 0
    user_answers = {}
    
    if request.is_json:
        data = request.get_json()
        if not data or 'answers' not in data:
            return jsonify({
                'success': False,
                'message': 'No answers provided!'
            }), 400
        
        user_answers = data['answers']  
        for question in questions:
            question_id = str(question.id)
            correct = False
            user_answer = None
            
            if question_id in user_answers:
                user_answer = int(user_answers[question_id])
                user_answers[question.id] = user_answer
                if user_answer == question.correct_option:
                    score += 1
                    correct = True
    else:
        
        user_answers = {}
        
        for question in questions:
            answer_key = f'question_{question.id}'
            correct = False
            user_answer = None
            
            if answer_key in request.form:
                user_answer = int(request.form[answer_key])
                user_answers[question.id] = user_answer
                if user_answer == question.correct_option:
                    score += 1
                    correct = True
    
    new_score = Score(
        quiz_id=quiz_id,
        user_id=user_id,
        time_stamp_of_attempt=datetime.utcnow(),
        total_scored=score,
        total_questions=total_questions
    )
    
    db.session.add(new_score)
    db.session.commit()
    
    percentage = (score / total_questions) * 100 if total_questions > 0 else 0
    
    if is_json_requested() or request.is_json:
        return jsonify({
            'success': True,
            'score_id': new_score.id,
            'total_scored': score,
            'total_questions': total_questions,
            'percentage': percentage,
            'question_results': [{'id': q_id, 'correct': correct, 'correct_option': q.correct_option, 'user_answer': ans} for q_id, ans in user_answers.items()]
        })

    session['quiz_results'] = {
        'user_answers': {str(q_id): ans for q_id, ans in user_answers.items()},
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

@user.route('/scores')
@login_required
def user_scores():
    """
    User Scores
    ---
    tags:
      - user
    summary: Get user quiz scores
    description: Returns all scores for the current user
    responses:
      200:
        description: Successful operation
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                count:
                  type: integer
                scores:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      quiz_id:
                        type: integer
                      quiz_title:
                        type: string
                      chapter_name:
                        type: string
                      subject_name:
                        type: string
                      total_questions:
                        type: integer
                      total_scored:
                        type: integer
                      percentage:
                        type: number
                        format: float
                      attempt_date:
                        type: string
                        format: date-time
    """
    user_id = session['user_id']
    scores = Score.query.filter_by(user_id=user_id).order_by(Score.id.desc()).all()
    
    if is_json_requested():
        return jsonify({
            'success': True,
            'count': len(scores),
            'scores': [serialize_score(score) for score in scores]
        })
    
    return render_template('user/scores/list.html', 
                           title='My Scores',
                           scores=scores)

@user.route('/search')
@login_required
def search():
    """
    Search
    ---
    tags:
      - user
    summary: Search subjects, chapters, and quizzes
    description: Performs a search across subjects, chapters, and quizzes
    parameters:
      - name: query
        in: query
        description: Search query
        required: true
        schema:
          type: string
      - name: type
        in: query
        description: Type of content to search (all, subjects, chapters, quizzes)
        required: false
        schema:
          type: string
          enum: [all, subjects, chapters, quizzes]
          default: all
    responses:
      200:
        description: Successful operation
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                query:
                  type: string
                search_type:
                  type: string
                subjects:
                  type: array
                  items:
                    $ref: '#/definitions/Subject'
                chapters:
                  type: array
                  items:
                    $ref: '#/definitions/Chapter'
                quizzes:
                  type: array
                  items:
                    $ref: '#/definitions/Quiz'
    definitions:
      Subject:
        type: object
        properties:
          id:
            type: integer
          name:
            type: string
          description:
            type: string
      Chapter:
        type: object
        properties:
          id:
            type: integer
          name:
            type: string
          description:
            type: string
          subject_id:
            type: integer
          subject_name:
            type: string
      Quiz:
        type: object
        properties:
          id:
            type: integer
          title:
            type: string
          description:
            type: string
          chapter_id:
            type: integer
          chapter_name:
            type: string
          date_of_quiz:
            type: string
            format: date
    """
    query = request.args.get('query', '')
    search_type = request.args.get('type', 'all')
    
    if not query:
        if is_json_requested():
            return jsonify({
                'success': True,
                'query': '',
                'search_type': search_type,
                'subjects': [],
                'chapters': [],
                'quizzes': []
            })
        return render_template('user/search/results.html', 
                               title='Search Results',
                               query=query,
                               subjects=[],
                               chapters=[],
                               quizzes=[])
    
    subject_results = []
    if search_type in ['all', 'subjects']:
        subject_results = Subject.query.filter(
            (Subject.name.ilike(f'%{query}%')) |
            (Subject.description.ilike(f'%{query}%'))
        ).all()
    
    chapter_results = []
    if search_type in ['all', 'chapters']:
        chapter_results = Chapter.query.filter(
            (Chapter.name.ilike(f'%{query}%')) |
            (Chapter.description.ilike(f'%{query}%'))
        ).all()
    
    quiz_results = []
    if search_type in ['all', 'quizzes']:
        quiz_results = Quiz.query.filter(
            (Quiz.title.ilike(f'%{query}%')) |
            (Quiz.remarks.ilike(f'%{query}%'))
        ).all()
    
    if is_json_requested():
        return jsonify({
            'success': True,
            'query': query,
            'search_type': search_type,
            'subjects': [serialize_subject(subject) for subject in subject_results],
            'chapters': [serialize_chapter(chapter) for chapter in chapter_results],
            'quizzes': [serialize_quiz(quiz) for quiz in quiz_results]
        })
        
    return render_template('user/search/results.html', 
                           title='Search Results',
                           query=query,
                           subjects=subject_results,
                           chapters=chapter_results,
                           quizzes=quiz_results) 