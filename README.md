# Quiz Master Application

A comprehensive web application for managing and taking quizzes. The application supports both user and admin roles, with distinct functionality for each.

## Application Structure

```
quiz-master-app/
├── app/                     # Application package
│   ├── models/              # Database models
│   │   └── models.py        # SQLAlchemy model definitions
│   ├── routes/              # Route definitions
│   │   ├── admin.py         # Admin routes
│   │   ├── auth.py          # Authentication routes
│   │   └── user.py          # User routes
│   ├── static/              # Static files (CSS, JS, images)
│   ├── templates/           # HTML templates
│   │   ├── admin/           # Admin templates
│   │   ├── auth/            # Authentication templates
│   │   └── user/            # User templates
│   ├── forms.py             # Form definitions using Flask-WTF
│   ├── utils.py             # Utility functions
│   └── __init__.py          # Application factory
├── create_db.py             # Script to create and initialize database
├── requirements.txt         # Project dependencies
├── run.py                   # Script to run the application
└── SwaggerFile.json         # Swagger API documentation
```

## Database Schema

### User
- id: Integer (Primary Key)
- username: String (Unique)
- password_hash: String
- full_name: String
- qualification: String
- dob: Date
- created_at: DateTime
- Relationship: scores → Score

### Admin
- id: Integer (Primary Key)
- username: String (Unique)
- password_hash: String

### Subject
- id: Integer (Primary Key)
- name: String
- description: Text
- created_at: DateTime
- Relationship: chapters → Chapter

### Chapter
- id: Integer (Primary Key)
- name: String
- description: Text
- subject_id: Integer (Foreign Key to Subject)
- created_at: DateTime
- Relationship: quizzes → Quiz

### Quiz
- id: Integer (Primary Key)
- chapter_id: Integer (Foreign Key to Chapter)
- title: String
- date_of_quiz: Date
- time_duration: String
- remarks: Text
- created_at: DateTime
- Relationships:
  - questions → Question
  - scores → Score

### Question
- id: Integer (Primary Key)
- quiz_id: Integer (Foreign Key to Quiz)
- question_statement: Text
- option1: String
- option2: String
- option3: String
- option4: String
- correct_option: Integer

### Score
- id: Integer (Primary Key)
- quiz_id: Integer (Foreign Key to Quiz)
- user_id: Integer (Foreign Key to User)
- time_stamp_of_attempt: DateTime
- total_scored: Integer
- total_questions: Integer

## Routes Overview

### Authentication Routes
- `/login`: User login
- `/admin/login`: Admin login
- `/register`: User registration
- `/logout`: Logout for all users

### User Routes
- `/dashboard`: User dashboard with recent scores and subjects
- `/subjects`: List all available subjects
- `/subjects/<subject_id>`: View a specific subject
- `/subjects/<subject_id>/chapters`: List chapters for a subject
- `/chapters/<chapter_id>`: View a specific chapter
- `/chapters/<chapter_id>/quizzes`: List quizzes for a chapter
- `/quizzes/<quiz_id>`: View a specific quiz
- `/quizzes/<quiz_id>/questions`: Get questions for a quiz
- `/quizzes/<quiz_id>/start`: Start a quiz
- `/quizzes/<quiz_id>/submit`: Submit quiz answers
- `/quizzes/<quiz_id>/result`: View quiz results
- `/quizzes/<quiz_id>/report`: View detailed quiz report
- `/quiz-history`: View user's quiz history
- `/scores`: View all user scores
- `/search`: Search for subjects, chapters, and quizzes

### Admin Routes
- `/dashboard`: Admin dashboard with system statistics
- `/subjects`: List all subjects
- `/subjects/create`: Create a new subject
- `/subjects/<id>`: View a specific subject
- `/subjects/edit/<id>`: Edit a subject
- `/subjects/delete/<id>`: Delete a subject
- `/chapters`: List all chapters
- `/chapters/create`: Create a new chapter
- `/chapters/<id>`: View a specific chapter
- `/chapters/edit/<id>`: Edit a chapter
- `/chapters/delete/<id>`: Delete a chapter
- `/quizzes`: List all quizzes
- `/quizzes/create`: Create a new quiz
- `/quizzes/<id>`: View a specific quiz
- `/quizzes/edit/<id>`: Edit a quiz
- `/quizzes/delete/<id>`: Delete a quiz
- `/quizzes/<quiz_id>/questions`: List questions for a quiz
- `/quizzes/<quiz_id>/questions/create`: Create a new question
- `/questions/edit/<id>`: Edit a question
- `/questions/delete/<id>`: Delete a question
- `/users`: List all users
- `/search`: Search across all content types

## API Documentation

API documentation is available at `/api/docs/` using Swagger UI. This provides a comprehensive overview of all API endpoints, request/response formats, and allows for interactive testing.

## Installation & Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd quiz-master-app
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```
   python create_db.py
   ```
   This script will:
   - Create the necessary database tables
   - Add an admin account
   - Add a sample user account
   - Create sample subjects, chapters, quizzes, and questions

4. Run the application:
   ```
   python run.py
   ```

5. Access the application at `http://localhost:5000`

## Default Login Credentials

After running the database initialization script, you can log in with these credentials:

### Admin Account
- **Username:** admin@quizmaster.com
- **Password:** admin123

### Sample User Account
- **Username:** user@example.com
- **Password:** password123

## Key Features

- Role-based access control (User/Admin)
- Comprehensive quiz management
- Hierarchical organization (Subject > Chapter > Quiz > Question)
- Quiz scheduling with time constraints
- Detailed score tracking and reporting
- Search functionality
- RESTful API with Swagger documentation

## Technologies Used

- **Backend**: Flask, SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Session-based authentication
- **API Documentation**: Swagger UI via Flasgger
- **Form Handling**: Flask-WTF
- **Database**: SQLite (development)
- **Password Security**: Werkzeug Security
