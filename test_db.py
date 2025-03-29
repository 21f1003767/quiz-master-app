"""
Test script to verify database relationships
"""

from app import create_app
from app.models.models import db, Admin, User, Subject, Chapter, Quiz, Question, Score
from datetime import datetime, date

def test_relationships():
    """Test database relationships by creating sample data"""
    app = create_app()
    
    with app.app_context():
        print("Testing database relationships...")
        
        # Create a test user
        test_user = User.query.filter_by(username='test@example.com').first()
        if not test_user:
            test_user = User(
                username='test@example.com',
                full_name='Test User',
                qualification='Bachelor of Science',
                dob=date(1990, 1, 1)
            )
            test_user.set_password('password123')
            db.session.add(test_user)
            print("Created test user")
        
        # Create a test subject
        test_subject = Subject.query.filter_by(name='Mathematics').first()
        if not test_subject:
            test_subject = Subject(
                name='Mathematics',
                description='Study of numbers, quantities, and shapes'
            )
            db.session.add(test_subject)
            print("Created test subject")
        
        # Make sure we have the subject ID for chapter creation
        db.session.flush()
        
        # Create a test chapter
        test_chapter = Chapter.query.filter_by(name='Algebra').first()
        if not test_chapter:
            test_chapter = Chapter(
                name='Algebra',
                description='Branch of mathematics dealing with symbols and rules for manipulating symbols',
                subject_id=test_subject.id
            )
            db.session.add(test_chapter)
            print("Created test chapter")
        
        # Make sure we have the chapter ID for quiz creation
        db.session.flush()
        
        # Create a test quiz
        test_quiz = Quiz.query.filter_by(title='Algebra Basics').first()
        if not test_quiz:
            test_quiz = Quiz(
                title='Algebra Basics',
                chapter_id=test_chapter.id,
                date_of_quiz=date(2023, 12, 31),
                time_duration='01:30',  # 1 hour and 30 minutes
                remarks='Basic quiz on algebraic operations'
            )
            db.session.add(test_quiz)
            print("Created test quiz")
        
        # Make sure we have the quiz ID for question creation
        db.session.flush()
        
        # Create test questions
        if Question.query.filter_by(quiz_id=test_quiz.id).count() == 0:
            questions = [
                Question(
                    quiz_id=test_quiz.id,
                    question_statement='What is the value of x in the equation 2x + 3 = 7?',
                    option1='1',
                    option2='2',
                    option3='3',
                    option4='4',
                    correct_option=2  # Option 2 is correct (x=2)
                ),
                Question(
                    quiz_id=test_quiz.id,
                    question_statement='Which of the following is a quadratic equation?',
                    option1='y = 2x + 1',
                    option2='y = x³ + 2',
                    option3='y = x² + 3x + 1',
                    option4='y = 3/x',
                    correct_option=3  # Option 3 is correct
                )
            ]
            
            for question in questions:
                db.session.add(question)
            print("Created test questions")
        
        # Create a test score
        if Score.query.filter_by(user_id=test_user.id, quiz_id=test_quiz.id).count() == 0:
            test_score = Score(
                user_id=test_user.id,
                quiz_id=test_quiz.id,
                time_stamp_of_attempt=datetime.utcnow(),
                total_scored=1,
                total_questions=2
            )
            db.session.add(test_score)
            print("Created test score")
        
        # Commit all changes
        db.session.commit()
        print("Successfully committed all changes!")
        
        # Verify relationships
        print("\nVerifying relationships:")
        
        # Get the subject and check chapters
        subject = Subject.query.filter_by(name='Mathematics').first()
        print(f"Subject: {subject.name}, Chapters count: {len(subject.chapters)}")
        
        # Get the chapter and check quizzes
        chapter = Chapter.query.filter_by(name='Algebra').first()
        print(f"Chapter: {chapter.name}, Subject: {chapter.subject.name}, Quizzes count: {len(chapter.quizzes)}")
        
        # Get the quiz and check questions
        quiz = Quiz.query.filter_by(title='Algebra Basics').first()
        print(f"Quiz: {quiz.title}, Chapter: {quiz.chapter.name}, Questions count: {len(quiz.questions)}")
        
        # Get the user and check scores
        user = User.query.filter_by(username='test@example.com').first()
        print(f"User: {user.full_name}, Scores count: {len(user.scores)}")
        
        # Get a score and check relationships
        score = Score.query.filter_by(user_id=user.id).first()
        print(f"Score: {score.total_scored}/{score.total_questions}, Quiz: {score.quiz.title}, User: {score.user.full_name}")

if __name__ == '__main__':
    test_relationships() 