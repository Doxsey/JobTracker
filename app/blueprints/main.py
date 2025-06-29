from flask import Blueprint, render_template
from app.models import Job

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    jobs = Job.query.filter_by(posting_status="Open").all()
    print(f"Number of open jobs: {len(jobs)}")
    print(jobs)
    for job in jobs:
        print(f"Job ID: {job.id}, Title: {job.title}, Company: {job.company}, Status: {job.posting_status}")
        for note in job.notes:
            print(f"  Note ID: {note.id}, Content: {note.content}, Created At: {note.created_at}")
    return render_template('index.html', jobs=jobs)

@main_bp.route('/about')
def about():
    return render_template('about.html')