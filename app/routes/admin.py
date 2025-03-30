from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from app.models.models import Admin, User, Subject, Chapter, Quiz, Question, db
from app.routes.auth import admin_required
from app.forms import SubjectForm, ChapterForm, QuizForm, QuestionForm, UserForm

admin = Blueprint('admin', __name__)

@admin.route('/dashboard')
@admin_required
def dashboard():
    user_count = User.query.count()
    
    subject_count = Subject.query.count()
    
    chapter_count = Chapter.query.count()
    
    quiz_count = Quiz.query.count()
    
    recent_subjects = Subject.query.order_by(Subject.created_at.desc()).limit(5).all()
    
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
    subjects = Subject.query.all()
    return render_template('admin/subjects/list.html', 
                           title='Subject Management',
                           subjects=subjects)

@admin.route('/subjects/create', methods=['GET', 'POST'])
@admin_required
def subject_create():
    form = SubjectForm()
    if form.validate_on_submit():
        subject = Subject(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(subject)
        db.session.commit()
        flash('Subject created successfully!', 'success')
        return redirect(url_for('admin.subject_list'))
    return render_template('admin/subjects/form.html', 
                           title='Create Subject',
                           form=form,
                           action='Create')

@admin.route('/subjects/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def subject_edit(id):
    subject = Subject.query.get_or_404(id)
    form = SubjectForm(obj=subject)
    if form.validate_on_submit():
        subject.name = form.name.data
        subject.description = form.description.data
        db.session.commit()
        flash('Subject updated successfully!', 'success')
        return redirect(url_for('admin.subject_list'))
    return render_template('admin/subjects/form.html', 
                           title='Edit Subject',
                           form=form,
                           action='Edit')

@admin.route('/subjects/delete/<int:id>', methods=['POST'])
@admin_required
def subject_delete(id):
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('admin.subject_list'))

@admin.route('/chapters')
@admin_required
def chapter_list():
    chapters = Chapter.query.all()
    return render_template('admin/chapters/list.html', 
                           title='Chapter Management',
                           chapters=chapters)

@admin.route('/chapters/create', methods=['GET', 'POST'])
@admin_required
def chapter_create():
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
        flash('Chapter created successfully!', 'success')
        return redirect(url_for('admin.chapter_list'))
    return render_template('admin/chapters/form.html', 
                           title='Create Chapter',
                           form=form,
                           action='Create')

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
        flash('Chapter updated successfully!', 'success')
        return redirect(url_for('admin.chapter_list'))
    return render_template('admin/chapters/form.html', 
                           title='Edit Chapter',
                           form=form,
                           action='Edit')

@admin.route('/chapters/delete/<int:id>', methods=['POST'])
@admin_required
def chapter_delete(id):
    chapter = Chapter.query.get_or_404(id)
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted successfully!', 'success')
    return redirect(url_for('admin.chapter_list'))

@admin.route('/quizzes')
@admin_required
def quiz_list():
    quizzes = Quiz.query.all()
    return render_template('admin/quizzes/list.html', 
                           title='Quiz Management',
                           quizzes=quizzes)

@admin.route('/quizzes/create', methods=['GET', 'POST'])
@admin_required
def quiz_create():
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
        flash('Quiz created successfully!', 'success')
        return redirect(url_for('admin.quiz_list'))
    return render_template('admin/quizzes/form.html', 
                           title='Create Quiz',
                           form=form,
                           action='Create')

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
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('admin.quiz_list'))
    return render_template('admin/quizzes/form.html', 
                           title='Edit Quiz',
                           form=form,
                           action='Edit')

@admin.route('/quizzes/delete/<int:id>', methods=['POST'])
@admin_required
def quiz_delete(id):
    quiz = Quiz.query.get_or_404(id)
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully!', 'success')
    return redirect(url_for('admin.quiz_list'))

@admin.route('/quizzes/<int:quiz_id>/questions')
@admin_required
def question_list(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('admin/questions/list.html', 
                           title=f'Questions for {quiz.title}',
                           quiz=quiz,
                           questions=questions)

@admin.route('/quizzes/<int:quiz_id>/questions/create', methods=['GET', 'POST'])
@admin_required
def question_create(quiz_id):
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
        flash('Question created successfully!', 'success')
        return redirect(url_for('admin.question_list', quiz_id=quiz_id))
    return render_template('admin/questions/form.html', 
                           title=f'Create Question for {quiz.title}',
                           form=form,
                           quiz=quiz,
                           action='Create')

@admin.route('/questions/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def question_edit(id):
    question = Question.query.get_or_404(id)
    quiz = question.quiz
    form = QuestionForm(obj=question)
    
    if form.validate_on_submit():
        question.question_statement = form.question_statement.data
        question.option1 = form.option1.data
        question.option2 = form.option2.data
        question.option3 = form.option3.data
        question.option4 = form.option4.data
        question.correct_option = form.correct_option.data
        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('admin.question_list', quiz_id=question.quiz_id))
    return render_template('admin/questions/form.html', 
                           title=f'Edit Question for {quiz.title}',
                           form=form,
                           quiz=quiz,
                           action='Edit')

@admin.route('/questions/delete/<int:id>', methods=['POST'])
@admin_required
def question_delete(id):
    question = Question.query.get_or_404(id)
    quiz_id = question.quiz_id
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('admin.question_list', quiz_id=quiz_id))

@admin.route('/users')
@admin_required
def user_list():
    users = User.query.all()
    return render_template('admin/users/list.html', 
                           title='User Management',
                           users=users)

@admin.route('/search', methods=['GET'])
@admin_required
def search():
    query = request.args.get('query', '')
    search_type = request.args.get('type', 'all')
    
    if not query:
        return render_template('admin/search/results.html', 
                               title='Search Results',
                               query='',
                               search_type='all',
                               users=[],
                               subjects=[],
                               chapters=[],
                               quizzes=[],
                               questions=[])

    users = []
    if search_type in ['all', 'users']:
        users = User.query.filter(
            (User.username.ilike(f'%{query}%')) |
            (User.full_name.ilike(f'%{query}%')) |
            (User.qualification.ilike(f'%{query}%'))
        ).all()
   
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
    
    questions = []
    if search_type in ['all', 'questions']:
        questions = Question.query.filter(
            (Question.question_statement.ilike(f'%{query}%')) |
            (Question.option1.ilike(f'%{query}%')) |
            (Question.option2.ilike(f'%{query}%')) |
            (Question.option3.ilike(f'%{query}%')) |
            (Question.option4.ilike(f'%{query}%'))
        ).all()
    
    return render_template('admin/search/results.html', 
                           title='Search Results',
                           query=query,
                           search_type=search_type,
                           users=users,
                           subjects=subjects,
                           chapters=chapters,
                           quizzes=quizzes,
                           questions=questions) 

@admin.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def user_edit(id):
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.full_name = form.full_name.data
        user.qualification = form.qualification.data
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.user_list'))
    
    return render_template('admin/users/form.html', 
                           title='Edit User',
                           form=form,
                           action='Edit')