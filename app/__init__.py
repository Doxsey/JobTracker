from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.startup_tasks import run_startup_tasks
import os, json

db = SQLAlchemy()



def create_app():
    app = Flask(__name__)

    settings_path = os.path.join(os.path.dirname(__file__), 'app_settings.json')
    with open(settings_path, 'r') as f:
        app_settings = json.load(f)

    if "app_folder" not in app_settings:
        raise KeyError("The 'app_folder' key is missing from app_settings.json.")

    app_base_folder = app_settings.get("app_folder")

    if not os.path.isabs(app_base_folder):
        raise ValueError("The 'app_folder' value in app_settings.json must be an absolute path.")

    parent_dir = os.path.dirname(app_base_folder)
    if not os.path.exists(parent_dir):
        raise FileNotFoundError(f"The parent directory '{parent_dir}' of 'app_folder' does not exist.")
    
    if os.path.exists(app_base_folder) and not os.path.isdir(app_base_folder):
        raise NotADirectoryError(f"The path '{app_base_folder}' exists but is not a directory.")

    if not isinstance(app_base_folder, str) or not app_base_folder.strip():
        raise ValueError("The 'app_folder' value in app_settings.json must be a non-empty string.")

    file_storage_folder = f'{app_base_folder}/JobTrackerFiles'

    create_folders(app_base_folder, file_storage_folder)

    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{app_base_folder}/app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['FILE_STORAGE_PATH'] = file_storage_folder
    app.config['LOCAL_TIMEZONE'] = 'America/Chicago'  # Set your local timezone here

    # Initialize extensions
    db.init_app(app)

    migrate = Migrate(app, db)
    
    # Register blueprints
    from app.blueprints.main import main_bp
    from app.blueprints.jobs import jobs_bp
    from app.blueprints.job_notes import job_notes_bp
    from app.blueprints.job_activities import job_activities_bp
    from app.blueprints.select_activity import select_activity_bp
    from app.blueprints.files import files_bp
    from app.blueprints.settings import settings_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(jobs_bp, url_prefix='/jobs')
    app.register_blueprint(job_notes_bp, url_prefix='/job_notes')
    app.register_blueprint(job_activities_bp, url_prefix='/job_activities')
    app.register_blueprint(select_activity_bp, url_prefix='/select_activity')
    app.register_blueprint(files_bp, url_prefix='/files')
    app.register_blueprint(settings_bp, url_prefix='/settings')

    run_startup_tasks(db, app)
    
    return app

def create_folders(app_base_folder, file_storage_folder):
    additional_folders = [
        "Resumes",
        "Cover_Letters",
        "Job_Descriptions",
    ]
    
    # Ensure the database folder exists
    if not os.path.exists(app_base_folder):
        os.makedirs(app_base_folder)
    if not os.path.exists(file_storage_folder):
        os.makedirs(file_storage_folder)

    # Create additional folders
    for folder in additional_folders:
        folder_path = os.path.join(file_storage_folder, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)