from flask import Blueprint, render_template, redirect, url_for, session, flash, request, jsonify
from app.models.models import Admin, User, Subject, Chapter, Quiz, Question, db
from app.forms import SubjectForm, ChapterForm, QuizForm, QuestionForm
from app.utils import is_json_requested, serialize_subject, serialize_chapter, serialize_quiz, serialize_question, serialize_score
from flask_login import login_required
from app.routes.auth import admin_required

admin = Blueprint('admin', __name__)

@admin.route('/dashboard')
@admin_required
def dashboard():
    """
    Admin Dashboard
    ---
    tags:
      - admin
    summary: Get admin dashboard data
    description: Returns statistics and recent subjects for the admin dashboard
    security:
      - session: []
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
                counts:
                  type: object
                  properties:
                    users:
                      type: integer
                    subjects:
                      type: integer
                    chapters:
                      type: integer
                    quizzes:
                      type: integer
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
                      chapter_count:
                        type: integer
      401:
        description: Not authenticated as admin
    """
    user_count = User.query.count()
    
    subject_count = Subject.query.count()
    
    chapter_count = Chapter.query.count()
    
    quiz_count = Quiz.query.count()
    
    recent_subjects = Subject.query.order_by(Subject.created_at.desc()).limit(5).all()
    
    if is_json_requested():
        return jsonify({
            'success': True,
            'counts': {
                'users': user_count,
                'subjects': subject_count,
                'chapters': chapter_count,
                'quizzes': quiz_count
            },
            'recent_subjects': [serialize_subject(subject) for subject in recent_subjects]
        })
        
    return render_template('admin/dashboard.html',
                           title='Admin Dashboard',
                           user_count=user_count,
                           subject_count=subject_count,
                           chapter_count=chapter_count,
                           quiz_count=quiz_count,
                           recent_subjects=recent_subjects)

@admin.route('/subjects')
@admin_required
def subject_list():
    """
    List Subjects
    ---
    tags:
      - admin
    summary: Get all subjects
    description: Returns a list of all subjects
    security:
      - session: []
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
      401:
        description: Not authenticated as admin
    """
    subjects = Subject.query.all()
    
    if is_json_requested():
        return jsonify({
            'success': True,
            'count': len(subjects),
            'subjects': [serialize_subject(subject) for subject in subjects]
        })
        
    return render_template('admin/subjects/list.html', 
                           title='Subject Management',
                           subjects=subjects)

@admin.route('/subjects/create', methods=['GET', 'POST'])
@admin_required
def subject_create():
    """
    Create Subject
    ---
    tags:
      - admin
    summary: Create a new subject
    description: Creates a new subject with the provided data
    security:
      - session: []
    consumes:
      - application/json
      - application/x-www-form-urlencoded
    parameters:
      - name: name
        in: formData
        description: Subject name
        required: true
        type: string
      - name: description
        in: formData
        description: Subject description
        required: true
        type: string
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
                message:
                  type: string
                subject:
                  type: object
                  properties:
                    id:
                      type: integer
                    name:
                      type: string
                    description:
                      type: string
      400:
        description: Invalid input
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: false
                errors:
                  type: object
      401:
        description: Not authenticated as admin
    """
    form = SubjectForm()
    if form.validate_on_submit():
        subject = Subject(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(subject)
        db.session.commit()
        
        if is_json_requested():
            return jsonify({
                'success': True,
                'message': 'Subject created successfully!',
                'subject': serialize_subject(subject)
            })
            
        flash('Subject created successfully!', 'success')
        return redirect(url_for('admin.subject_list'))
        
    if is_json_requested() and request.method == 'POST':
        return jsonify({
            'success': False,
            'errors': form.errors
        }), 400
        
    return render_template('admin/subjects/form.html', 
                           title='Create Subject',
                           form=form,
                           action='Create')

@admin.route('/subjects/<int:id>', methods=['GET'])
@admin_required
def subject_detail(id):
    """
    Get Subject Detail
    ---
    tags:
      - admin
    summary: Get subject details
    description: Returns details of a specific subject and its chapters
    security:
      - session: []
    parameters:
      - name: id
        in: path
        description: Subject ID
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
                      subject_id:
                        type: integer
      401:
        description: Not authenticated as admin
      404:
        description: Subject not found
    """
    subject = Subject.query.get_or_404(id)
    
    if is_json_requested():
        return jsonify({
            'success': True,
            'subject': serialize_subject(subject),
            'chapters': [serialize_chapter(chapter) for chapter in subject.chapters]
        })
    return redirect(url_for('admin.subject_edit', id=id))

@admin.route('/subjects/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def subject_edit(id):
    """
    Edit Subject
    ---
    tags:
      - admin
    summary: Update an existing subject
    description: Updates an existing subject with the provided data
    security:
      - session: []
    consumes:
      - application/json
      - application/x-www-form-urlencoded
    parameters:
      - name: id
        in: path
        description: Subject ID
        required: true
        schema:
          type: integer
      - name: name
        in: formData
        description: Subject name
        required: true
        type: string
      - name: description
        in: formData
        description: Subject description
        required: true
        type: string
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
                message:
                  type: string
                subject:
                  type: object
                  properties:
                    id:
                      type: integer
                    name:
                      type: string
                    description:
                      type: string
      400:
        description: Invalid input
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: false
                errors:
                  type: object
      401:
        description: Not authenticated as admin
      404:
        description: Subject not found
    """
    subject = Subject.query.get_or_404(id)
    form = SubjectForm(obj=subject)
    if form.validate_on_submit():
        subject.name = form.name.data
        subject.description = form.description.data
        db.session.commit()
        
        if is_json_requested():
            return jsonify({
                'success': True,
                'message': 'Subject updated successfully!',
                'subject': serialize_subject(subject)
            })
            
        flash('Subject updated successfully!', 'success')
        return redirect(url_for('admin.subject_list'))
        
    if is_json_requested() and request.method == 'POST':
        return jsonify({
            'success': False,
            'errors': form.errors
        }), 400
        
    return render_template('admin/subjects/form.html', 
                           title='Edit Subject',
                           form=form,
                           action='Edit')

@admin.route('/subjects/delete/<int:id>', methods=['POST', 'DELETE'])
@admin_required
def subject_delete(id):
    """
    Delete Subject
    ---
    tags:
      - admin
    summary: Delete a subject
    description: Deletes a subject with the specified ID
    security:
      - session: []
    parameters:
      - name: id
        in: path
        description: Subject ID
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
                message:
                  type: string
      401:
        description: Not authenticated as admin
      404:
        description: Subject not found
    """
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    
    if is_json_requested():
        return jsonify({
            'success': True,
            'message': 'Subject deleted successfully!'
        })
        
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('admin.subject_list'))

@admin.route('/api/subjects', methods=['GET'])
@admin_required
def api_subjects():
    """
    Admin Subjects API
    ---
    tags:
      - admin
    summary: Get all subjects (admin only)
    description: Returns a list of all subjects in the system with additional admin information
    security:
      - session: []
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
                      chapter_count:
                        type: integer
                      quiz_count:
                        type: integer
                      date_created:
                        type: string
                        format: date-time
      401:
        description: Not authenticated as admin
    """
    subjects = Subject.query.all()
    
    for subject in subjects:
        subject.chapter_count = Chapter.query.filter_by(subject_id=subject.id).count()
        chapter_ids = [c.id for c in Chapter.query.filter_by(subject_id=subject.id).all()]
        subject.quiz_count = Quiz.query.filter(Quiz.chapter_id.in_(chapter_ids)).count() if chapter_ids else 0
    
    return jsonify({
        'success': True,
        'count': len(subjects),
        'subjects': [{
            'id': s.id,
            'name': s.name,
            'description': s.description,
            'chapter_count': s.chapter_count,
            'quiz_count': s.quiz_count,
            'date_created': s.date_created.isoformat() if s.date_created else None
        } for s in subjects]
    })

@admin.route('/chapters')
@admin_required
def chapter_list():
    """
    List Chapters
    ---
    tags:
      - admin
    summary: Get all chapters
    description: Returns a list of all chapters
    security:
      - session: []
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
                      subject_id:
                        type: integer
                      subject_name:
                        type: string
      401:
        description: Not authenticated as admin
    """
    chapters = Chapter.query.all()
    
    if is_json_requested():
        return jsonify({
            'success': True,
            'count': len(chapters),
            'chapters': [serialize_chapter(chapter) for chapter in chapters]
        })
        
    return render_template('admin/chapters/list.html', 
                           title='Chapter Management',
                           chapters=chapters)

@admin.route('/chapters/create', methods=['GET', 'POST'])
@admin_required
def chapter_create():
    """
    Create Chapter
    ---
    tags:
      - admin
    summary: Create a new chapter
    description: Creates a new chapter with the provided data
    security:
      - session: []
    consumes:
      - application/json
      - application/x-www-form-urlencoded
    parameters:
      - name: name
        in: formData
        description: Chapter name
        required: true
        type: string
      - name: description
        in: formData
        description: Chapter description
        required: true
        type: string
      - name: subject_id
        in: formData
        description: Subject ID
        required: true
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
                message:
                  type: string
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
      400:
        description: Invalid input
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: false
                errors:
                  type: object
      401:
        description: Not authenticated as admin
    """
    form = ChapterForm()
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.all()]
    
    if form.validate_on_submit():
        chapter = Chapter(
            name=form.name.data,
            description=form.description.data,
            subject_id=form.subject_id.data
        )
        db.session.add(chapter)
        db.session.commit()
        
        if is_json_requested():
            return jsonify({
                'success': True,
                'message': 'Chapter created successfully!',
                'chapter': serialize_chapter(chapter)
            })
            
        flash('Chapter created successfully!', 'success')
        return redirect(url_for('admin.chapter_list'))
        
    if is_json_requested() and request.method == 'POST':
        return jsonify({
            'success': False,
            'errors': form.errors
        }), 400
        
    return render_template('admin/chapters/form.html', 
                           title='Create Chapter',
                           form=form,
                           action='Create')

@admin.route('/chapters/<int:id>', methods=['GET'])
@admin_required
def chapter_detail(id):
    chapter = Chapter.query.get_or_404(id)
    
    if is_json_requested():
        return jsonify({
            'success': True,
            'chapter': serialize_chapter(chapter),
            'quizzes': [serialize_quiz(quiz) for quiz in chapter.quizzes]
        })
    return redirect(url_for('admin.chapter_edit', id=id))

@admin.route('/chapters/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def chapter_edit(id):
    chapter = Chapter.query.get_or_404(id)
    form = ChapterForm(obj=chapter)
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.all()]
    
    if form.validate_on_submit():
        chapter.name = form.name.data
        chapter.description = form.description.data
        chapter.subject_id = form.subject_id.data
        db.session.commit()
        
        if is_json_requested():
            return jsonify({
                'success': True,
                'message': 'Chapter updated successfully!',
                'chapter': serialize_chapter(chapter)
            })
            
        flash('Chapter updated successfully!', 'success')
        return redirect(url_for('admin.chapter_list'))
        
    if is_json_requested() and request.method == 'POST':
        return jsonify({
            'success': False,
            'errors': form.errors
        }), 400
        
    return render_template('admin/chapters/form.html', 
                           title='Edit Chapter',
                           form=form,
                           action='Edit')

@admin.route('/chapters/delete/<int:id>', methods=['POST', 'DELETE'])
@admin_required
def chapter_delete(id):
    chapter = Chapter.query.get_or_404(id)
    db.session.delete(chapter)
    db.session.commit()
    
    if is_json_requested():
        return jsonify({
            'success': True,
            'message': 'Chapter deleted successfully!'
        })
        
    flash('Chapter deleted successfully!', 'success')
    return redirect(url_for('admin.chapter_list'))

@admin.route('/quizzes')
@admin_required
def quiz_list():
    """
    List Quizzes
    ---
    tags:
      - admin
    summary: Get all quizzes
    description: Returns a list of all quizzes
    security:
      - session: []
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
                      chapter_id:
                        type: integer
                      chapter_name:
                        type: string
                      subject_name:
                        type: string
                      date_of_quiz:
                        type: string
                        format: date
                      time_duration:
                        type: string
      401:
        description: Not authenticated as admin
    """
    quizzes = Quiz.query.all()
    
    if is_json_requested():
        return jsonify({
            'success': True,
            'count': len(quizzes),
            'quizzes': [serialize_quiz(quiz) for quiz in quizzes]
        })
        
    return render_template('admin/quizzes/list.html', 
                           title='Quiz Management',
                           quizzes=quizzes)

@admin.route('/quizzes/create', methods=['GET', 'POST'])
@admin_required
def quiz_create():
    """
    Create Quiz
    ---
    tags:
      - admin
    summary: Create a new quiz
    description: Creates a new quiz with the provided data
    security:
      - session: []
    consumes:
      - application/json
      - application/x-www-form-urlencoded
    parameters:
      - name: title
        in: formData
        description: Quiz title
        required: true
        type: string
      - name: chapter_id
        in: formData
        description: Chapter ID
        required: true
        type: integer
      - name: date_of_quiz
        in: formData
        description: Date of quiz (YYYY-MM-DD)
        required: true
        type: string
        format: date
      - name: time_duration
        in: formData
        description: Time duration (HH:MM)
        required: true
        type: string
      - name: remarks
        in: formData
        description: Additional remarks
        required: false
        type: string
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
                message:
                  type: string
                quiz:
                  type: object
                  properties:
                    id:
                      type: integer
                    title:
                      type: string
                    chapter_id:
                      type: integer
                    date_of_quiz:
                      type: string
                      format: date
                    time_duration:
                      type: string
                    remarks:
                      type: string
      400:
        description: Invalid input
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: false
                errors:
                  type: object
      401:
        description: Not authenticated as admin
    """
    form = QuizForm()
    form.chapter_id.choices = [(c.id, f"{c.name} ({c.subject.name})") for c in Chapter.query.all()]
    
    if form.validate_on_submit():
        quiz = Quiz(
            title=form.title.data,
            chapter_id=form.chapter_id.data,
            date_of_quiz=form.date_of_quiz.data,
            time_duration=form.time_duration.data,
            remarks=form.remarks.data
        )
        db.session.add(quiz)
        db.session.commit()
        
        if is_json_requested():
            return jsonify({
                'success': True,
                'message': 'Quiz created successfully!',
                'quiz': serialize_quiz(quiz)
            })
            
        flash('Quiz created successfully!', 'success')
        return redirect(url_for('admin.quiz_list'))
        
    if is_json_requested() and request.method == 'POST':
        return jsonify({
            'success': False,
            'errors': form.errors
        }), 400
        
    return render_template('admin/quizzes/form.html', 
                           title='Create Quiz',
                           form=form,
                           action='Create')

@admin.route('/quizzes/<int:id>', methods=['GET'])
@admin_required
def quiz_detail(id):
    """
    Get Quiz Detail
    ---
    tags:
      - admin
    summary: Get quiz details with questions
    description: Returns details of a specific quiz and its questions
    security:
      - session: []
    parameters:
      - name: id
        in: path
        description: Quiz ID
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
                quiz:
                  type: object
                  properties:
                    id:
                      type: integer
                    title:
                      type: string
                    chapter_id:
                      type: integer
                    chapter_name:
                      type: string
                    subject_name:
                      type: string
                    date_of_quiz:
                      type: string
                      format: date
                    time_duration:
                      type: string
                    remarks:
                      type: string
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
                      correct_option:
                        type: integer
      401:
        description: Not authenticated as admin
      404:
        description: Quiz not found
    """
    quiz = Quiz.query.get_or_404(id)
    
    if is_json_requested():
        questions = [serialize_question(q, include_correct_answer=True) for q in quiz.questions]
        
        return jsonify({
            'success': True,
            'quiz': serialize_quiz(quiz),
            'questions': questions
        })
        
    return redirect(url_for('admin.question_list', quiz_id=id))

@admin.route('/quizzes/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def quiz_edit(id):
    quiz = Quiz.query.get_or_404(id)
    form = QuizForm(obj=quiz)
    form.chapter_id.choices = [(c.id, f"{c.name} ({c.subject.name})") for c in Chapter.query.all()]
    
    if form.validate_on_submit():
        quiz.title = form.title.data
        quiz.chapter_id = form.chapter_id.data
        quiz.date_of_quiz = form.date_of_quiz.data
        quiz.time_duration = form.time_duration.data
        quiz.remarks = form.remarks.data
        db.session.commit()
        
        if is_json_requested():
            return jsonify({
                'success': True,
                'message': 'Quiz updated successfully!',
                'quiz': serialize_quiz(quiz)
            })
            
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('admin.quiz_list'))
        
    if is_json_requested() and request.method == 'POST':
        return jsonify({
            'success': False,
            'errors': form.errors
        }), 400
        
    return render_template('admin/quizzes/form.html', 
                           title='Edit Quiz',
                           form=form,
                           action='Edit')

@admin.route('/quizzes/delete/<int:id>', methods=['POST', 'DELETE'])
@admin_required
def quiz_delete(id):
    quiz = Quiz.query.get_or_404(id)
    db.session.delete(quiz)
    db.session.commit()
    
    if is_json_requested():
        return jsonify({
            'success': True,
            'message': 'Quiz deleted successfully!'
        })
        
    flash('Quiz deleted successfully!', 'success')
    return redirect(url_for('admin.quiz_list'))

@admin.route('/quizzes/<int:quiz_id>/questions')
@admin_required
def question_list(quiz_id):
    """
    List Quiz Questions
    ---
    tags:
      - admin
    summary: Get all questions for a quiz
    description: Returns a list of all questions for a specific quiz
    security:
      - session: []
    parameters:
      - name: quiz_id
        in: path
        description: Quiz ID
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
                quiz:
                  type: object
                  properties:
                    id:
                      type: integer
                    title:
                      type: string
                count:
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
                      correct_option:
                        type: integer
      401:
        description: Not authenticated as admin
      404:
        description: Quiz not found
    """
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    if is_json_requested():
        return jsonify({
            'success': True,
            'quiz': serialize_quiz(quiz),
            'count': len(questions),
            'questions': [serialize_question(q, include_correct_answer=True) for q in questions]
        })
        
    return render_template('admin/questions/list.html', 
                           title=f'Questions for {quiz.title}',
                           quiz=quiz,
                           questions=questions)

@admin.route('/quizzes/<int:quiz_id>/questions/create', methods=['GET', 'POST'])
@admin_required
def question_create(quiz_id):
    """
    Create Question
    ---
    tags:
      - admin
    summary: Create a new question for a quiz
    description: Creates a new question with the provided data
    security:
      - session: []
    consumes:
      - application/json
      - application/x-www-form-urlencoded
    parameters:
      - name: quiz_id
        in: path
        description: Quiz ID
        required: true
        schema:
          type: integer
      - name: question_statement
        in: formData
        description: Question text
        required: true
        type: string
      - name: option1
        in: formData
        description: Option 1
        required: true
        type: string
      - name: option2
        in: formData
        description: Option 2
        required: true
        type: string
      - name: option3
        in: formData
        description: Option 3
        required: true
        type: string
      - name: option4
        in: formData
        description: Option 4
        required: true
        type: string
      - name: correct_option
        in: formData
        description: Correct option (1-4)
        required: true
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
                message:
                  type: string
                question:
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
                    correct_option:
                      type: integer
      400:
        description: Invalid input
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: false
                errors:
                  type: object
      401:
        description: Not authenticated as admin
      404:
        description: Quiz not found
    """
    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuestionForm()
    
    if form.validate_on_submit():
        question = Question(
            quiz_id=quiz_id,
            question_statement=form.question_statement.data,
            option1=form.option1.data,
            option2=form.option2.data,
            option3=form.option3.data,
            option4=form.option4.data,
            correct_option=form.correct_option.data
        )
        db.session.add(question)
        db.session.commit()
        
        if is_json_requested():
            return jsonify({
                'success': True,
                'message': 'Question created successfully!',
                'question': serialize_question(question, include_correct_answer=True)
            })
            
        flash('Question created successfully!', 'success')
        return redirect(url_for('admin.question_list', quiz_id=quiz_id))
        
    if is_json_requested() and request.method == 'POST':
        return jsonify({
            'success': False,
            'errors': form.errors
        }), 400
        
    return render_template('admin/questions/form.html', 
                           title=f'Create Question for {quiz.title}',
                           form=form,
                           quiz=quiz,
                           action='Create')

@admin.route('/questions/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def question_edit(id):
    question = Question.query.get_or_404(id)
    quiz = Quiz.query.get_or_404(question.quiz_id)
    form = QuestionForm(obj=question)
    
    if form.validate_on_submit():
        question.question_statement = form.question_statement.data
        question.option1 = form.option1.data
        question.option2 = form.option2.data
        question.option3 = form.option3.data
        question.option4 = form.option4.data
        question.correct_option = form.correct_option.data
        db.session.commit()
        
        if is_json_requested():
            return jsonify({
                'success': True,
                'message': 'Question updated successfully!',
                'question': serialize_question(question, include_correct_answer=True)
            })
            
        flash('Question updated successfully!', 'success')
        return redirect(url_for('admin.question_list', quiz_id=question.quiz_id))
        
    if is_json_requested() and request.method == 'POST':
        return jsonify({
            'success': False,
            'errors': form.errors
        }), 400
        
    return render_template('admin/questions/form.html', 
                           title=f'Edit Question for {quiz.title}',
                           form=form,
                           quiz=quiz,
                           action='Edit')

@admin.route('/questions/delete/<int:id>', methods=['POST', 'DELETE'])
@admin_required
def question_delete(id):
    question = Question.query.get_or_404(id)
    quiz_id = question.quiz_id
    db.session.delete(question)
    db.session.commit()
    
    if is_json_requested():
        return jsonify({
            'success': True,
            'message': 'Question deleted successfully!'
        })
        
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('admin.question_list', quiz_id=quiz_id))

@admin.route('/users')
@admin_required
def user_list():
    users = User.query.all()
    
    if is_json_requested():
        result = []
        for user in users:
            user_data = {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
            result.append(user_data)
            
        return jsonify({
            'success': True,
            'count': len(users),
            'users': result
        })
        
    return render_template('admin/users/list.html', 
                           title='User Management',
                           users=users)

@admin.route('/search', methods=['GET'])
@admin_required
def search():
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
                'quizzes': [],
                'users': []
            })
        return render_template('admin/search/results.html', 
                               title='Search Results',
                               query=query,
                               search_type='all',
                               subjects=[],
                               chapters=[],
                               quizzes=[],
                               users=[],
                               questions=[])
    
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
    
    question_results = []
    if search_type in ['all', 'questions']:
        question_results = Question.query.filter(
            (Question.question_statement.ilike(f'%{query}%')) |
            (Question.option1.ilike(f'%{query}%')) |
            (Question.option2.ilike(f'%{query}%')) |
            (Question.option3.ilike(f'%{query}%')) |
            (Question.option4.ilike(f'%{query}%'))
        ).all()
    
    user_results = []
    if search_type in ['all', 'users']:
        user_results = User.query.filter(
            (User.full_name.ilike(f'%{query}%')) |
            (User.username.ilike(f'%{query}%'))
        ).all()
    
    if is_json_requested():
        subjects = [serialize_subject(subject) for subject in subject_results]
        chapters = [serialize_chapter(chapter) for chapter in chapter_results]
        quizzes = [serialize_quiz(quiz) for quiz in quiz_results]
        questions = [serialize_question(q, include_correct_answer=True) for q in question_results]
        users = []
        for user in user_results:
            users.append({
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
            
        return jsonify({
            'success': True,
            'query': query,
            'search_type': search_type,
            'subjects': subjects,
            'chapters': chapters,
            'quizzes': quizzes,
            'questions': questions,
            'users': users
        })

    return render_template('admin/search/results.html', 
                           title='Search Results',
                           query=query,
                           search_type=search_type,
                           subjects=subject_results,
                           chapters=chapter_results,
                           quizzes=quiz_results,
                           questions=question_results,
                           users=user_results) 