from app import db
from datetime import datetime, timezone


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    referrer_site = db.Column(db.String(100), nullable=True)
    salary_range_low = db.Column(db.Float, nullable=True)
    salary_range_high = db.Column(db.Float, nullable=True)
    remote_option = db.Column(db.String(50), nullable=True)
    posting_id = db.Column(db.String(100), unique=True, nullable=False)
    created_dt = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    job_description_file = db.Column(db.String(50), nullable=True)
    resume_file = db.Column(db.String(50), nullable=True)
    cover_letter_file = db.Column(db.String(50), nullable=True)
    posting_open = db.Column(db.Boolean, default=True)


    def __repr__(self):
        return f'<Job {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'company': self.company,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'referrer_site': self.referrer_site,
            'salary_range_low': self.salary_range_low,
            'salary_range_high': self.salary_range_high,
            'remote_option': self.remote_option,
            'posting_id': self.posting_id,
            'posted_at': self.created_dt,
            'job_description_file': self.job_description_file,
            'resume_file': self.resume_file,
            'cover_letter_file': self.cover_letter_file,
            'posting_open': self.posting_open
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at,
            'is_active': self.is_active
        }