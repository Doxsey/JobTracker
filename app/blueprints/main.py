from flask import Blueprint, render_template, request
from app.models import Job

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    title = "Open Job Applications"
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)  # Default 10 jobs per page
    
    # Paginate the query
    jobs_pagination = Job.query.filter_by(posting_status="Open").paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return render_template('index.html', 
                         jobs=jobs_pagination.items,
                         pagination=jobs_pagination,
                         title=title)

@main_bp.route('/all')
def all_jobs():
    title = "All Job Applications"
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Paginate the query
    jobs_pagination = Job.query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return render_template('index.html', 
                         jobs=jobs_pagination.items,
                         pagination=jobs_pagination,
                         title=title)