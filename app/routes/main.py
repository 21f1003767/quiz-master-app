from flask import Blueprint, render_template, redirect, url_for

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """
    Home Page
    ---
    tags:
      - Main
    summary: Application home page
    description: Renders the main landing page of the application
    responses:
      200:
        description: Home page rendered successfully
    """
    return render_template('index.html')

@main.route('/about')
def about():
    """
    About Page
    ---
    tags:
      - Main
    summary: About page
    description: Renders the about page of the application
    responses:
      200:
        description: About page rendered successfully
    """
    return render_template('about.html')

@main.route('/contact')
def contact():
    """
    Contact Page
    ---
    tags:
      - Main
    summary: Contact page
    description: Renders the contact page of the application
    responses:
      200:
        description: Contact page rendered successfully
    """
    return render_template('contact.html') 