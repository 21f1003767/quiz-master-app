import os
import sys
from app import create_app, db

config_name = os.environ.get('FLASK_ENV', 'development')
if len(sys.argv) > 1:
    config_name = sys.argv[1]

app = create_app(config_name)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=config_name=='development') 