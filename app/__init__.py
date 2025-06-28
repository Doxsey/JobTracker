from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()



def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Ryan/Documents/app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)

    migrate = Migrate(app, db)
    
    # Register blueprints
    from app.blueprints.main import main_bp
    from app.blueprints.users import users_bp
    from app.blueprints.jobs import jobs_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(jobs_bp, url_prefix='/jobs')

    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app