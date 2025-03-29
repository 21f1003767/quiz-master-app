# Quiz Master App

A multi-user application built with Flask, Jinja2, and SQLite that acts as an exam preparation site for multiple courses.

## Overview

The Quiz Master App is a platform designed for both administrators and users. Administrators can create subjects, chapters, and quizzes, while users can register, attempt quizzes, and track their progress.

## Features

- Admin dashboard for managing subjects, chapters, and quizzes
- User registration and authentication
- Quiz creation and management
- Score tracking and viewing
- Responsive design using Bootstrap and CSS

## Setup Instructions

1. Clone this repository:
   ```
   git clone <repository-url>
   cd quiz-master-app
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Initialize the database:
   ```
   python create_db.py
   ```

6. Run the application:
   ```
   python run.py
   ```

7. Access the application in your web browser at `http://127.0.0.1:5000`

## Default Admin Credentials

- Username: admin@quizmaster.com
- Password: admin123

## Database Schema

The application uses SQLite with the following tables:
- User: Stores user information and credentials
- Admin: Stores admin credentials
- Subject: Contains various subjects for quizzes
- Chapter: Subdivisions of subjects
- Quiz: Quiz details including duration and date
- Question: Quiz questions with multiple-choice options
- Score: Records of user's quiz attempts
