from flask import Blueprint, render_template, request
from app.models import Job

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Get filter parameters
    status_filter = request.args.get('status', 'open')  # Default to 'open'
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Build query based on status filter
    query = Job.query
    
    if status_filter == 'open':
        query = query.filter_by(posting_status="Open")
        title = "Open Job Applications"
    elif status_filter == 'closed':
        query = query.filter_by(posting_status="Closed")
        title = "Closed Job Applications"
    elif status_filter == 'all':
        title = "All Job Applications"
    else:
        # Default to open if invalid status provided
        query = query.filter_by(posting_status="Open")
        title = "Open Job Applications"
        status_filter = 'open'
    
    # Apply pagination
    jobs_pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return render_template('index.html', 
                         jobs=jobs_pagination.items,
                         pagination=jobs_pagination,
                         title=title,
                         current_status=status_filter)

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