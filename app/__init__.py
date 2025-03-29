from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.models.models import db

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
  
    from app.routes.auth import auth
    app.register_blueprint(auth)

        
    from app.routes.admin import admin
    app.register_blueprint(admin, url_prefix='/admin')
    
    return app 