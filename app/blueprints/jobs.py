from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from app import db
from flask_wtf import FlaskForm
from wtforms import DateField, StringField, BooleanField, SubmitField, TextAreaField, IntegerField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Optional
from werkzeug.utils import secure_filename
from app.models import Job, Settings
from ..services.api_service import APIService
from ..services.github_service import GitHubService
from app.utils.html_utils import sanitize_html
import os, uuid, json
import requests

jobs_bp = Blueprint('jobs', __name__)

class NewJobForm(FlaskForm):
    company = StringField('Company', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    location = StringField('Location', validators=[DataRequired()])
    salary_range_low = IntegerField('Salary Range Low', validators=[Optional()], render_kw={"type": "number", "step": "1"})
    salary_range_high = IntegerField('Salary Range High', validators=[Optional()], render_kw={"type": "number", "step": "1"})
    remote_option = StringField('Remote Option')
    posting_id = StringField('Posting ID')
    referrer = StringField('Referrer')
    referrer_posting_id = StringField('Referrer Posting ID')
    posting_url = StringField('Posting URL')
    company_website = StringField('Company Website')
    resume_file = FileField('Resume File', validators=[
        FileAllowed(['pdf', 'docx', 'doc', 'tex'], 
                   'Only PDF and document files allowed!')
    ])
    job_description_file = FileField('Job Description File', validators=[
        FileAllowed(['pdf', 'docx', 'doc', 'tex'], 
                   'Only PDF and document files allowed!')
    ])
    cover_letter_file = FileField('Cover Letter File', validators=[
        FileAllowed(['pdf', 'docx', 'doc', 'tex'], 
                   'Only PDF and document files allowed!')
    ])
    use_default_resume = BooleanField('Use Default Resume', default=True)
    create_github_branch = BooleanField('Create GitHub Branch on Job Creation', default=False)
    github_branch_name = StringField('GitHub Branch Name (auto-generated if empty)', validators=[Optional()])
    submit = SubmitField('Add Job')

class ViewJobForm(FlaskForm):
    company = StringField('Company', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    salary_range_low = IntegerField('Salary Range Low', validators=[Optional()], render_kw={"type": "number", "step": "1"})
    salary_range_high = IntegerField('Salary Range High', validators=[Optional()], render_kw={"type": "number", "step": "1"})
    remote_option = StringField('Remote Option')
    posting_id = StringField('Posting ID')
    referrer = StringField('Referrer')
    referrer_posting_id = StringField('Referrer Posting ID')
    posting_url = StringField('Posting URL')
    company_website = StringField('Company Website')
    created_dt = StringField('Date Created')
    github_branch = StringField('GitHub Branch', render_kw={'readonly': True})
    submit = SubmitField('Save Changes')

class DeleteJobForm(FlaskForm):
    submit = SubmitField('Delete')

class CloseJobForm(FlaskForm):
    closing_reason = StringField('Closing Reason')
    closing_date = DateField("Date Closed", format='%Y-%m-%d', default=date.today, validators=[DataRequired()])
    submit = SubmitField('Close Job')

@jobs_bp.route('/create-github-branch', methods=['POST'])
def create_github_branch():
    """Create a minimal job entry and GitHub branch"""
    github_configured = bool(current_app.config.get('GITHUB_TOKEN') and current_app.config.get('GITHUB_REPO'))
    
    if not github_configured:
        return jsonify({'error': 'GitHub integration not configured'}), 400
    
    data = request.get_json()
    company = data.get('company', '').strip()
    title = data.get('title', '').strip()
    custom_branch_name = data.get('github_branch_name', '').strip()
    
    if not company or not title:
        return jsonify({'error': 'Company and title are required'}), 400
    
    try:
        # Create minimal job entry
        job = Job(
            company=company,
            title=title,
            description='',  # Will be updated when full form is submitted
            location='',     # Will be updated when full form is submitted
            is_draft=True    # Mark as draft until full form is submitted
        )
        
        db.session.add(job)
        db.session.flush()  # Get the ID
        
        # Create GitHub branch
        github_service = GitHubService()
        if not custom_branch_name:
            branch_name = github_service.generate_branch_name(company, title, job.id)
        else:
            branch_name = custom_branch_name
        
        success, message = github_service.create_branch(branch_name)
        if success:
            job.github_branch = branch_name
            db.session.commit()
            
            return jsonify({
                'success': True,
                'job_id': job.id,
                'github_branch': branch_name,
                'github_branch_url': f"https://github.com/{current_app.config.get('GITHUB_REPO')}/tree/{branch_name}",
                'message': f'GitHub branch "{branch_name}" created successfully'
            }), 200
        else:
            db.session.rollback()
            return jsonify({'error': f'Failed to create GitHub branch: {message}'}), 500
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating GitHub branch: {str(e)}")
        return jsonify({'error': f'Error creating GitHub branch: {str(e)}'}), 500

@jobs_bp.route('/create', methods=['GET', 'POST'])
def create():
    settings = Settings.query.all()
    github_configured = bool(current_app.config.get('GITHUB_TOKEN') and current_app.config.get('GITHUB_REPO'))
    
    # Check if we're continuing from a GitHub branch creation
    draft_job_id = request.args.get('draft_job_id')
    draft_job = None
    if draft_job_id:
        draft_job = Job.query.filter_by(id=draft_job_id, is_draft=True).first()
    
    if request.method == 'GET':
        # Handle GET request - show the form
        form = NewJobForm()
        
        # Pre-populate form if continuing from draft
        if draft_job:
            form.company.data = draft_job.company
            form.title.data = draft_job.title
        
        return render_template('jobs/create.html', 
                             form=form, 
                             settings=settings, 
                             github_configured=github_configured,
                             draft_job=draft_job)
    
    # Handle POST request
    if request.method == 'POST':
        # Check if it's a JSON request or form submission
        is_json_request = request.is_json or request.content_type == 'application/json'
        is_multipart_request = 'multipart/form-data' in request.content_type if request.content_type else False
        
        # Handle API requests (JSON or multipart with JSON data)
        if is_json_request or (is_multipart_request and 'data' in request.form):
            try:
                # Extract JSON data
                if is_json_request:
                    data = request.get_json()
                    resume_file = None
                    job_description_file = None
                    cover_letter_file = None
                else:
                    # Handle multipart request with JSON data and file
                    data = json.loads(request.form.get('data', '{}'))
                    resume_file = request.files.get('resume_file')
                    job_description_file = request.files.get('job_description_file')
                    cover_letter_file = request.files.get('cover_letter_file')

                # Extract data from JSON
                company = data.get('company')
                company_website = data.get('company_website')
                title = data.get('title')
                description = data.get('description')
                location = data.get('location')
                salary_range_low = data.get('salary_range_low')
                salary_range_high = data.get('salary_range_high')
                remote_option = data.get('remote_option')
                posting_url = data.get('posting_url')
                posting_id = data.get('posting_id')
                referrer = data.get('referrer')
                referrer_posting_id = data.get('referrer_posting_id')
                create_github_branch = data.get('create_github_branch', False)
                github_branch_name = data.get('github_branch_name')
                draft_job_id = data.get('draft_job_id')  # Check if updating existing draft
                
                # Basic validation for required fields
                if not all([company, title, description]):
                    return jsonify({'error': 'Missing required fields: company, title, description'}), 400
                
                # Check if job already exists (unless updating draft)
                if posting_id and not draft_job_id:
                    existing_job = Job.query.filter_by(posting_id=posting_id).first()
                    if existing_job:
                        return jsonify({'error': 'Job posting ID already exists'}), 409
                
                # Handle file uploads
                unique_resume_filename = None
                unique_job_description_filename = None
                unique_cover_letter_filename = None

                # Process resume file
                if resume_file and resume_file.filename:
                    unique_resume_filename = process_file_upload(resume_file, 'Resumes')
                    if isinstance(unique_resume_filename, tuple):  # Error occurred
                        return unique_resume_filename
                    
                # Process job description file
                if job_description_file and job_description_file.filename:
                    unique_job_description_filename = process_file_upload(job_description_file, 'Job_Descriptions')
                    if isinstance(unique_job_description_filename, tuple):  # Error occurred
                        return unique_job_description_filename
                
                # Process cover letter file
                if cover_letter_file and cover_letter_file.filename:
                    unique_cover_letter_filename = process_file_upload(cover_letter_file, 'Cover_Letters')
                    if isinstance(unique_cover_letter_filename, tuple):  # Error occurred
                        return unique_cover_letter_filename
                
                # Update existing draft or create new job
                if draft_job_id:
                    # Update existing draft job
                    job = Job.query.filter_by(id=draft_job_id, is_draft=True).first()
                    if not job:
                        return jsonify({'error': 'Draft job not found'}), 404
                    
                    # Update all fields
                    job.company = company
                    job.company_website = company_website
                    job.title = title
                    job.description = description
                    job.location = location
                    job.salary_range_low = salary_range_low
                    job.salary_range_high = salary_range_high
                    job.remote_option = remote_option
                    job.posting_id = posting_id
                    job.referrer = referrer
                    job.referrer_posting_id = referrer_posting_id
                    job.posting_url = posting_url
                    job.resume_file = unique_resume_filename or job.resume_file
                    job.job_description_file = unique_job_description_filename or job.job_description_file
                    job.cover_letter_file = unique_cover_letter_filename or job.cover_letter_file
                    job.is_draft = False  # Mark as complete
                else:
                    # Create new job
                    job = Job(
                        company=company,
                        company_website=company_website,
                        title=title,
                        description=description,
                        location=location,
                        salary_range_low=salary_range_low,
                        salary_range_high=salary_range_high,
                        remote_option=remote_option,
                        posting_id=posting_id,
                        referrer=referrer,
                        referrer_posting_id=referrer_posting_id,
                        posting_url=posting_url,
                        resume_file=unique_resume_filename,
                        job_description_file=unique_job_description_filename,
                        cover_letter_file=unique_cover_letter_filename,
                        is_draft=False
                    )
                    
                    db.session.add(job)
                    db.session.flush()  # This assigns the ID without committing
                    
                    # Handle GitHub branch creation for new jobs
                    if create_github_branch and github_configured:
                        try:
                            github_service = GitHubService()
                            if not github_branch_name:
                                github_branch_name = github_service.generate_branch_name(company, title, job.id)
                            
                            success, message = github_service.create_branch(github_branch_name)
                            if success:
                                job.github_branch = github_branch_name
                            else:
                                # Log warning but don't fail the job creation
                                current_app.logger.warning(f"Failed to create GitHub branch: {message}")
                        except Exception as e:
                            current_app.logger.error(f"GitHub branch creation error: {str(e)}")
                
                # Commit the job
                db.session.commit()
                
                response_data = {
                    'message': 'Job created successfully' if not draft_job_id else 'Job updated successfully',
                    'job_id': job.id,
                    'company': job.company,
                    'title': job.title,
                }
                
                # Include file info in response if file was uploaded
                if unique_resume_filename:
                    response_data['resume_file'] = unique_resume_filename

                if unique_job_description_filename:
                    response_data['job_description_file'] = unique_job_description_filename

                if unique_cover_letter_filename:
                    response_data['cover_letter_file'] = unique_cover_letter_filename
                
                if job.github_branch:
                    response_data['github_branch'] = job.github_branch
                    response_data['github_branch_url'] = f"https://github.com/{current_app.config.get('GITHUB_REPO')}/tree/{job.github_branch}"

                return jsonify(response_data), 201
                
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid JSON data'}), 400
            except Exception as e:
                print(f"Error creating job via API: {e}")
                db.session.rollback()
                return jsonify({'error': 'Error creating job'}), 500
        
        else:
            # Handle regular form submission
            form = NewJobForm()
            
            # Check if we're updating a draft job
            draft_job_id = request.form.get('draft_job_id')
            if draft_job_id:
                draft_job = Job.query.filter_by(id=draft_job_id, is_draft=True).first()
            else:
                draft_job = None
            
            if form.validate_on_submit():
                company = form.company.data
                company_website = form.company_website.data
                title = form.title.data
                description = sanitize_html(form.description.data)
                location = form.location.data
                salary_range_low = form.salary_range_low.data
                salary_range_high = form.salary_range_high.data
                remote_option = form.remote_option.data
                posting_url = form.posting_url.data
                posting_id = form.posting_id.data
                referrer = form.referrer.data
                referrer_posting_id = form.referrer_posting_id.data
                use_default_resume = form.use_default_resume.data
                resume_file = form.resume_file.data
                job_description_file = form.job_description_file.data
                cover_letter_file = form.cover_letter_file.data
                create_github_branch = form.create_github_branch.data
                github_branch_name = form.github_branch_name.data
                
                # Handle default resume
                unique_resume_filename = None
                if use_default_resume:
                    resume_file = None
                    # Get the default resume filename from settings
                    default_resume_setting = Settings.query.filter_by(key='default_resume').first()
                    if default_resume_setting:
                        default_resume_file = default_resume_setting.value
                        file_path = os.path.join(current_app.config['FILE_STORAGE_PATH'], 'Resumes', default_resume_file)

                        if not os.path.exists(file_path):
                            flash('Default resume file not found!', 'error')
                            return render_template('jobs/create.html', form=form, settings=settings, 
                                                 github_configured=github_configured, draft_job=draft_job)

                        unique_resume_filename = generate_unique_filename(default_resume_file)
                        new_file_path = os.path.join(current_app.config['FILE_STORAGE_PATH'], 'Resumes', unique_resume_filename)
                        try:
                            # Copy the default resume file to a new unique filename
                            os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
                            with open(file_path, 'rb') as src_file:
                                with open(new_file_path, 'wb') as dest_file:
                                    dest_file.write(src_file.read())
                        except Exception as e:
                            flash(f'Error using default resume file: {str(e)}', 'error')
                            return render_template('jobs/create.html', form=form, settings=settings, 
                                                 github_configured=github_configured, draft_job=draft_job)

                # Handle uploaded resume file
                if resume_file and not use_default_resume:
                    original_resume_filename = secure_filename(resume_file.filename)
                    unique_resume_filename = generate_unique_filename(original_resume_filename)

                    # Create full file path
                    file_path = os.path.join(current_app.config['FILE_STORAGE_PATH'], 'Resumes', unique_resume_filename)

                    try:
                        # Save the file
                        resume_file.save(file_path)
                        
                    except Exception as e:
                        flash(f'Error uploading file: {str(e)}', 'error')

                # Handle other file uploads
                unique_job_description_filename = None
                if job_description_file:
                    original_job_description_filename = secure_filename(job_description_file.filename)
                    unique_job_description_filename = generate_unique_filename(original_job_description_filename)

                    # Create full file path
                    file_path = os.path.join(current_app.config['FILE_STORAGE_PATH'], 'Job_Descriptions', unique_job_description_filename)

                    try:
                        # Save the file
                        job_description_file.save(file_path)
                    except Exception as e:
                        flash(f'Error uploading file: {str(e)}', 'error')

                unique_cover_letter_filename = None
                if cover_letter_file:
                    original_cover_letter_filename = secure_filename(cover_letter_file.filename)
                    unique_cover_letter_filename = generate_unique_filename(original_cover_letter_filename)

                    # Create full file path
                    file_path = os.path.join(current_app.config['FILE_STORAGE_PATH'], 'Cover_Letters', unique_cover_letter_filename)

                    try:
                        # Save the file
                        cover_letter_file.save(file_path)
                    except Exception as e:
                        flash(f'Error uploading file: {str(e)}', 'error')

                # Check if job already exists (unless updating draft)
                if posting_id and not draft_job:
                    existing_job = Job.query.filter_by(posting_id=posting_id).first()
                    if existing_job:
                        flash('Job posting ID already exists!', 'error')
                        return render_template('jobs/create.html', form=form, settings=settings, 
                                             github_configured=github_configured, draft_job=draft_job)
                
                # Update existing draft or create new job
                if draft_job:
                    # Update existing draft job
                    job = draft_job
                    job.company = company
                    job.company_website = company_website
                    job.title = title
                    job.description = description
                    job.location = location
                    job.salary_range_low = salary_range_low
                    job.salary_range_high = salary_range_high
                    job.remote_option = remote_option
                    job.posting_id = posting_id
                    job.referrer = referrer
                    job.referrer_posting_id = referrer_posting_id
                    job.posting_url = posting_url
                    job.resume_file = unique_resume_filename or job.resume_file
                    job.job_description_file = unique_job_description_filename or job.job_description_file
                    job.cover_letter_file = unique_cover_letter_filename or job.cover_letter_file
                    job.is_draft = False  # Mark as complete
                else:
                    # Create new job
                    job = Job(
                        company=company,
                        company_website=company_website,
                        title=title,
                        description=description,
                        location=location,
                        salary_range_low=salary_range_low,
                        salary_range_high=salary_range_high,
                        remote_option=remote_option,
                        posting_id=posting_id,
                        referrer=referrer,
                        referrer_posting_id=referrer_posting_id,
                        posting_url=posting_url,
                        resume_file=unique_resume_filename,
                        job_description_file=unique_job_description_filename,
                        cover_letter_file=unique_cover_letter_filename,
                        is_draft=False
                    )
                
                try:
                    if not draft_job:
                        db.session.add(job)
                    db.session.flush()  # Get the ID before committing
                    
                    # Handle GitHub branch creation for new jobs
                    if create_github_branch and github_configured and not draft_job:
                        try:
                            github_service = GitHubService()
                            if not github_branch_name:
                                github_branch_name = github_service.generate_branch_name(company, title, job.id)
                            
                            success, message = github_service.create_branch(github_branch_name)
                            if success:
                                job.github_branch = github_branch_name
                                flash(f'GitHub branch created: {github_branch_name}', 'success')
                            else:
                                flash(f'GitHub branch creation failed: {message}', 'warning')
                        except Exception as e:
                            flash(f'GitHub integration error: {str(e)}', 'warning')
                    
                    db.session.commit()
                    flash('Job created successfully!' if not draft_job else 'Job updated successfully!', 'success')
                    return redirect('/')
                except Exception as e:
                    print(f"Error creating job: {e}")
                    db.session.rollback()
                    flash('Error creating job!', 'error')

            return render_template('jobs/create.html', form=form, settings=settings, 
                                 github_configured=github_configured, draft_job=draft_job)

@jobs_bp.route('/<int:job_id>/view', methods=['GET', 'POST'])
def view(job_id):
    form = ViewJobForm()
    job: Job = Job.query.get_or_404(job_id)

    if request.method == 'GET':
        form.description.data = job.description
        return render_template('jobs/view.html', job=job, form=form)

    if request.method == 'POST':
        if form.validate_on_submit():
            job.company = form.company.data
            job.company_website = form.company_website.data
            job.title = form.title.data
            job.description = sanitize_html(form.description.data)
            job.location = request.form['location']
            job.salary_range_low = request.form['salary_range_low']
            job.salary_range_high = request.form['salary_range_high']
            job.remote_option = request.form['remote_option']
            job.posting_url = request.form['posting_url']
            job.posting_id = request.form['posting_id']
            job.referrer = request.form['referrer']
            job.referrer_posting_id = request.form['referrer_posting_id']
            
            try:
                db.session.commit()
                flash('Job updated successfully!', 'success')
            except Exception as e:
                print(f"Error updating job: {e}")
                db.session.rollback()
                flash('Error updating job!', 'error')

    return render_template('jobs/view.html', job=job, form=form)

@jobs_bp.route('/<int:job_id>/close', methods=['GET', 'POST'])
def close(job_id):
    form = CloseJobForm()
    job = Job.query.get_or_404(job_id)

    if request.method == 'GET':
        form.process()  # Apply default values
        return render_template('jobs/close.html', job=job, form=form)

    if request.method == 'POST':
        if form.validate_on_submit():
            closing_reason = {
                "reason": form.closing_reason.data
            }

            closing_reason_json = json.dumps(closing_reason)

            api = APIService()

            activity_data = {
                "job_id": job.id,
                "activity_type": "Job Posting Closed",
                "activity_date": f"{form.closing_date.data}",
                "activity_brief": f"Job closed: {form.closing_reason.data}",
                "activity_json_data": closing_reason_json
            }

            try:
                response = api.create_job_activity(activity_data)
                if response.status_code != 201:
                    flash('Failed to log job closing activity.', 'warning')
                    return render_template('jobs/close.html', job=job, form=form)
            except Exception as e:
                flash('Error logging job closing activity.', 'warning')
                return render_template('jobs/close.html', job=job, form=form)

            job.posting_status = 'Closed'
            
            db.session.commit()
            flash('Job closed successfully!', 'success')
            return redirect('/')

    return render_template('jobs/close.html', job=job, form=form)

@jobs_bp.route('/<int:job_id>/delete', methods=['GET', 'POST'])
def delete(job_id):
    form = DeleteJobForm()
    job = Job.query.get_or_404(job_id)
    if request.method == 'GET':
        print("GET request for job delete")
        return render_template('jobs/delete.html', job=job, form=form)

    if request.method == 'POST':
        print("POST request for job delete")
        if form.validate_on_submit():
            
            if job.resume_file:
                delete_file(job.resume_file, "Resumes")
            if job.job_description_file:
                delete_file(job.job_description_file, "Job_Descriptions")
            if job.cover_letter_file:
                delete_file(job.cover_letter_file, "Cover_Letters")

            db.session.delete(job)
            db.session.commit()
            flash('Job deleted successfully!', 'success')
        else:
            print("Form validation failed. Errors:", form.errors)
            flash('Error deleting job!', 'error')
        return redirect('/')

    return render_template('jobs/delete.html', job=job, form=form)

def delete_file(file_name, folder):
    file_folder = os.path.join(current_app.config['FILE_STORAGE_PATH'], folder)
    file_path = os.path.join(file_folder, file_name)

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"File {file_name} deleted successfully from {folder} folder.")
        except Exception as e:
            print(f"Error deleting file {file_name} from {folder} folder: {str(e)}")

@jobs_bp.route('/<int:job_id>/file-cards', methods=['GET', 'POST'])
def file_cards(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('jobs/file_cards_partial.html', job=job)

def process_file_upload(file, folder_name):
    """Process file upload with validation and return unique filename or error response"""
    # Validate file type
    allowed_extensions = {'pdf', 'docx', 'doc', 'tex'}
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if file_ext not in allowed_extensions:
        return jsonify({'error': f'Invalid file type for {file.filename}. Only PDF and document files allowed!'}), 400
    
    # Generate unique filename and save file
    original_filename = secure_filename(file.filename)
    unique_filename = generate_unique_filename(original_filename)
    
    # Create full file path
    file_path = os.path.join(current_app.config['FILE_STORAGE_PATH'], folder_name, unique_filename)
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # Save the file
        file.save(file_path)
        return unique_filename
    except Exception as e:
        return jsonify({'error': f'Error uploading {file.filename}: {str(e)}'}), 500

def generate_unique_filename(original_filename):
    """Generate a unique filename while preserving the extension"""
    # Get file extension
    _, ext = os.path.splitext(original_filename)
    # Generate unique name using UUID
    unique_name = str(uuid.uuid4()) + ext
    return unique_name