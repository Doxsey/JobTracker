from app import db
from sqlalchemy import Index
from datetime import datetime, timezone


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100), nullable=False)
    company_website = db.Column(db.String(200), nullable=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    referrer = db.Column(db.String(100), nullable=True)
    referrer_posting_id = db.Column(db.String(100), nullable=True)
    salary_range_low = db.Column(db.Float, nullable=True)
    salary_range_high = db.Column(db.Float, nullable=True)
    remote_option = db.Column(db.String(50), nullable=True)
    posting_id = db.Column(db.String(100), nullable=True)
    created_dt = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    job_description_file = db.Column(db.String(50), nullable=True)
    resume_file = db.Column(db.String(50), nullable=True)
    cover_letter_file = db.Column(db.String(50), nullable=True)
    posting_status = db.Column(db.String(50), default='Open')
    posting_url = db.Column(db.String(200), nullable=True)
    # notes = db.relationship('JobNote', back_populates='job', cascade='all, delete-orphan')
    notes = db.relationship('JobNotes', backref='Job')
    activities = db.relationship('JobActivities', backref='Job')

    def __repr__(self):
        return f'<Job {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'company': self.company,
            'company_website': self.company_website,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'referrer': self.referrer,
            'referrer_posting_id': self.referrer_posting_id,
            'salary_range_low': self.salary_range_low,
            'salary_range_high': self.salary_range_high,
            'remote_option': self.remote_option,
            'posting_id': self.posting_id,
            'created_dt': self.created_dt,
            'job_description_file': self.job_description_file,
            'resume_file': self.resume_file,
            'cover_letter_file': self.cover_letter_file,
            'posting_status': self.posting_status,
            'posting_url': self.posting_url
        }
    
class JobNotes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f'<JobNote {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'content': self.content,
            'created_at': self.created_at
        }

class JobActivities(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    activity_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    activity_type = db.Column(db.String(50), nullable=False)
    activity_description = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<JobActivity {self.id} - {self.activity_type}>'

    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'activity_date': self.activity_date,
            'activity_type': self.activity_type,
            'activity_description': self.activity_description
        }
    
class JobActivityTypes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activity_type = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return f'<JobActivityType {self.activity_type}>'

    def to_dict(self):
        return {
            'id': self.id,
            'activity_type': self.activity_type
        }