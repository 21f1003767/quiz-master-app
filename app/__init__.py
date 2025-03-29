from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.models.models import db
from datetime import datetime
from flasgger import Swagger

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['SWAGGER'] = {
        'title': 'Quiz Master API',
        'description': 'API for the Quiz Master application',
        'version': '1.0.0',
        'uiversion': 3,
        'termsOfService': '',
        'specs_route': '/api/docs/',
        'securityDefinitions': {
            'sessionAuth': {
                'type': 'apiKey',
                'in': 'cookie',
                'name': 'session'
            }
        },
        'security': [
            {
                'sessionAuth': []
            }
        ]
    }
    
    db.init_app(app)
    @app.context_processor
    def utility_processor():
        def now():
            return datetime.utcnow()
        return {'now': now}
  
    from app.routes.auth import auth
    app.register_blueprint(auth)

        
    from app.routes.admin import admin
    app.register_blueprint(admin, url_prefix='/admin')

    from app.routes.user import user
    app.register_blueprint(user, url_prefix='/user')

    swagger = Swagger(app)
    
    return app 