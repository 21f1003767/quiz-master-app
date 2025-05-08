import os
from datetime import datetime

class Config:
    """Base configuration for the application"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-default-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    
    # Swagger configuration
    SWAGGER = {
        'title': 'Quiz Master API',
        'description': 'API for the Quiz Master application',
        'version': '1.0.0',
        'uiversion': 3,
        'termsOfService': '',
        'specs_route': '/api/docs/',
        'securityDefinitions': {
            'ApiKeyAuth': {
                'type': 'apiKey',
                'name': 'X-API-KEY',
                'in': 'header'
            },
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT'
            }
        }
    }
    
    # Context processor for templates
    @staticmethod
    def init_app(app):
        @app.context_processor
        def utility_processor():
            def now():
                return datetime.utcnow()
            return {'now': now}


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///instance/quiz_master.db'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///instance/test_quiz_master.db'
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing


class ProductionConfig(Config):
    """Production configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/quiz_master.db'
    
    # Use stronger secret key in production
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)

    # Additional production-specific settings
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Production-specific handling (logging, etc.)
        # Could add error handlers, loggers, etc.


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 