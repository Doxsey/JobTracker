from flask import Blueprint, render_template
from app.models import Job

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    title = "Open Job Applications"
    jobs = Job.query.filter_by(posting_status="Open").all()
    return render_template('index.html', jobs=jobs, title=title)

@main_bp.route('/all')
def all_jobs():
    title = "All Job Applications"
    jobs = Job.query.all()
    return render_template('index.html', jobs=jobs, title=title)
