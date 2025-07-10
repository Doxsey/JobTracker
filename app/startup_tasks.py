

def run_startup_tasks(db, app):
    """
    Run startup tasks to initialize the application.
    This includes creating database tables and loading default job activity types.
    """
    create_job_activities(db, app)

def create_job_activities(db, app):
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
            "Note Added",
            "Note Updated",
            "Note Deleted",
            "Reminder Set"
        ]

        for activity_type in default_types:
            exists = JobActivityTypes.query.filter_by(activity_type=activity_type).first()
            if not exists:
                db.session.add(JobActivityTypes(activity_type=activity_type))
        db.session.commit()