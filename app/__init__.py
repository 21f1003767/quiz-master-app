from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flasgger import Swagger
from flask_wtf.csrf import CSRFProtect

# Initialize extensions
db = SQLAlchemy()
csrf = CSRFProtect()

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Configure app based on environment
    from config import config
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions with app
    db.init_app(app)
    csrf.init_app(app)
    
    # Configure Swagger
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs/"
    }
    swagger = Swagger(app, config=swagger_config)
    
    # Register blueprints
    from app.routes.main import main
    from app.routes.auth import auth
    from app.routes.admin import admin
    from app.routes.user import user
    
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(user, url_prefix='/user')
    
    # Configure CSRF exemptions for API endpoints if needed
    # Example: csrf.exempt(blueprint_or_view)
    
    return app 