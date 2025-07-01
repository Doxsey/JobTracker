from flask import Blueprint, render_template
from app.models import Job

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    jobs = Job.query.filter_by(posting_status="Open").all()
    return render_template('index.html', jobs=jobs)

@main_bp.route('/about')
def about():
    return render_template('about.html')