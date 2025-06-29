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
    from app.blueprints.jobs import jobs_bp
    from app.blueprints.job_notes import job_notes_bp
    from app.blueprints.job_activities import job_activities_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(jobs_bp, url_prefix='/jobs')
    app.register_blueprint(job_notes_bp, url_prefix='/job_notes')
    app.register_blueprint(job_activities_bp, url_prefix='/job_activities')

    # Create database tables
    with app.app_context():
        db.create_all()

        # Load default JobActivityTypes if not present
        from app.models import JobActivityTypes
        default_types = [
            # Application-Related Activities
            "Application Submitted",
            "Application Updated",
            "Application Withdrawn",
            "Referral Submitted",
            "Resume Uploaded",
            "Cover Letter Sent",

            # Communication Activities
            "Received Email",
            "Sent Email",
            "Received Phone Call",
            "Left Voicemail",
            "Sent Thank-You Email",
            "Sent Follow-Up Email",

            # Interview Activities
            "Interview Scheduled",
            "Phone Screen Completed",
            "Technical Interview Completed",
            "On-Site Interview Completed",
            "Final Interview Completed",
            "Interview Rescheduled",
            "Interview Canceled",

            # Company Actions
            "Application Viewed by Recruiter",
            "Application Moved to Next Round",
            "Shortlisted for Interview",
            "Offer Extended",
            "Offer Negotiated",
            "Offer Accepted",
            "Offer Declined",
            "Application Rejected",

            # Other Helpful Events
            "Job Saved",
            "Job Posting Closed",
            "Company Researched",
            "Networking Contact Made",
            "Notes Added",
            "Reminder Set"
        ]

        for activity_type in default_types:
            exists = JobActivityTypes.query.filter_by(activity_type=activity_type).first()
            if not exists:
                db.session.add(JobActivityTypes(activity_type=activity_type))
        db.session.commit()
    
    return app