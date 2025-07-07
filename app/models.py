from app import db
from sqlalchemy import Index
from sqlalchemy.types import JSON
from datetime import datetime
from flask import current_app
import pytz


class Job(db.Model):
    __tablename__ = 'jobs'

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
    created_dt = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone(current_app.config['LOCAL_TIMEZONE'])))
    job_description_file = db.Column(db.String(50), nullable=True)
    resume_file = db.Column(db.String(50), nullable=True)
    cover_letter_file = db.Column(db.String(50), nullable=True)
    posting_status = db.Column(db.String(50), default='Open')
    posting_url = db.Column(db.String(200), nullable=True)
    notes = db.relationship('JobNotes', backref='Job', cascade='all, delete-orphan')
    activities = db.relationship('JobActivities', backref='Job', cascade='all, delete-orphan')

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
    __tablename__ = 'job_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone(current_app.config['LOCAL_TIMEZONE'])))

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
    __tablename__ = 'job_activities'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    activity_date = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone(current_app.config['LOCAL_TIMEZONE'])))
    activity_type = db.Column(db.String(50), nullable=False)
    activity_brief = db.Column(db.String(100), nullable=True)  # New field for brief description
    activity_json_data = db.Column(JSON, nullable=False)

    def __repr__(self):
        return f'<JobActivity {self.id} - {self.activity_type}>'

    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'activity_date': self.activity_date,
            'activity_type': self.activity_type,
            'activity_brief': self.activity_brief,  # Include brief description in the dict
            'activity_json_data': self.activity_json_data
        }
    
class JobActivityTypes(db.Model):
    __tablename__ = 'job_activity_types'

    id = db.Column(db.Integer, primary_key=True)
    activity_type = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return f'<JobActivityType {self.activity_type}>'

    def to_dict(self):
        return {
            'id': self.id,
            'activity_type': self.activity_type
        }
    
class Settings(db.Model):
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), nullable=False, unique=True)
    value = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Setting {self.key}>'

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value
        }