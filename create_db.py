from app import create_app
from app.models.models import db, Admin, User, Subject, Chapter, Quiz, Question
from datetime import datetime, timedelta
import os

def setup_database():
    """
    Initialize the database and create initial data
    """
    app = create_app()
    
    # Check if instance directory exists, create it if not
    instance_path = os.path.join(os.getcwd(), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
        print(f"Created instance directory at {instance_path}")
    
    with app.app_context():
        # Drop and recreate all tables
        db.drop_all()
        db.create_all()
        print("Database tables created.")
        
        # Create admin user
        admin = Admin(username='admin@quizmaster.com')
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create sample user
        sample_user = User(
            username='user@example.com',
            full_name='Sample User',
            qualification='Student',
            dob=datetime.strptime('2000-01-01', '%Y-%m-%d')
        )
        sample_user.set_password('password123')
        db.session.add(sample_user)
        
        # Create sample subjects
        subjects = [
            Subject(name='Mathematics', description='Basic and advanced mathematical concepts'),
            Subject(name='Science', description='General science concepts including physics, chemistry, and biology'),
            Subject(name='Computer Science', description='Programming, algorithms, and computing fundamentals')
        ]
        db.session.add_all(subjects)
        db.session.commit()
        print("Added sample subjects.")
        
        # Create sample chapters
        chapters = [
            # Math chapters
            Chapter(name='Algebra', description='Algebraic expressions and equations', subject_id=1),
            Chapter(name='Geometry', description='Shapes, areas, and volumes', subject_id=1),
            
            # Science chapters
            Chapter(name='Physics', description='Motion, forces, and energy', subject_id=2),
            Chapter(name='Chemistry', description='Elements, compounds, and reactions', subject_id=2),
            
            # Computer Science chapters
            Chapter(name='Python Programming', description='Fundamentals of Python programming', subject_id=3),
            Chapter(name='Data Structures', description='Arrays, linked lists, trees, and graphs', subject_id=3)
        ]
        db.session.add_all(chapters)
        db.session.commit()
        print("Added sample chapters.")
        
        # Create sample quizzes
        tomorrow = datetime.now().date() + timedelta(days=1)
        quizzes = [
            Quiz(
                title='Algebra Basics Quiz',
                chapter_id=1,
                date_of_quiz=tomorrow,
                time_duration='01:00',
                remarks='Fundamental algebraic concepts'
            ),
            Quiz(
                title='Python Fundamentals',
                chapter_id=5,
                date_of_quiz=tomorrow,
                time_duration='00:45',
                remarks='Basic Python syntax and concepts'
            )
        ]
        db.session.add_all(quizzes)
        db.session.commit()
        print("Added sample quizzes.")
        
        # Create sample questions for Algebra quiz
        algebra_questions = [
            Question(
                quiz_id=1,
                question_statement='What is the solution to x + 5 = 10?',
                option1='x = 5',
                option2='x = 15',
                option3='x = 0',
                option4='x = -5',
                correct_option=1
            ),
            Question(
                quiz_id=1,
                question_statement='Simplify: 3(x + 2) - 4',
                option1='3x + 6 - 4',
                option2='3x + 2',
                option3='3x + 2 - 4',
                option4='3x + 6',
                correct_option=1
            ),
            Question(
                quiz_id=1,
                question_statement='What is the value of x in the equation 2x - 7 = 5?',
                option1='x = 6',
                option2='x = 1',
                option3='x = -1',
                option4='x = 0',
                correct_option=1
            )
        ]
        
        # Create sample questions for Python quiz
        python_questions = [
            Question(
                quiz_id=2,
                question_statement='What is the correct way to create a function in Python?',
                option1='function myFunc():',
                option2='def myFunc():',
                option3='create myFunc():',
                option4='func myFunc():',
                correct_option=2
            ),
            Question(
                quiz_id=2,
                question_statement='Which of the following is used to create a comment in Python?',
                option1='//',
                option2='/* */',
                option3='#',
                option4='--',
                correct_option=3
            ),
            Question(
                quiz_id=2,
                question_statement='What data type is this? my_list = [1, 2, 3]',
                option1='Array',
                option2='Tuple',
                option3='Dictionary',
                option4='List',
                correct_option=4
            )
        ]
        
        db.session.add_all(algebra_questions)
        db.session.add_all(python_questions)
        db.session.commit()
        print("Added sample questions.")
        
        print("\nDatabase initialized successfully!")
        print("\nDefault login credentials:")
        print("Admin - Username: admin@quizmaster.com, Password: admin123")
        print("User - Username: user@example.com, Password: password123")

if __name__ == '__main__':
    setup_database() 