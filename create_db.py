from app import create_app
from app.models.models import db, Admin, User, Subject, Chapter, Quiz

def setup_database():
    """
    Initialize the database and create admin user
    """
    app = create_app()
    
    with app.app_context():
        
        db.create_all()
        
       
        admin_exists = Admin.query.filter_by(username='admin@quizmaster.com').first()
        
        if not admin_exists:
           
            admin = Admin(username='admin@quizmaster.com')
            admin.set_password('admin123') 
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists.")
            
        print("Database initialized successfully!")

if __name__ == '__main__':
    setup_database() 