from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, TextAreaField, DecimalField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from app.models import Job
import os, uuid

jobs_bp = Blueprint('jobs', __name__)

class NewJobForm(FlaskForm):
    company = StringField('Company', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    salary_range_low = DecimalField('Salary Range Low')
    salary_range_high = DecimalField('Salary Range High')
    remote_option = StringField('Remote Option')
    posting_id = StringField('Posting ID')
    referrer = StringField('Referrer')
    referrer_posting_id = StringField('Referrer Posting ID')
    posting_url = StringField('Posting URL')
    company_website = StringField('Company Website')
    resume_file = FileField('Choose File', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'docx', 'doc', 'tex'], 
                   'Only PDF and document files allowed!')
    ])
    submit = SubmitField('Add Job')

@jobs_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        # Handle GET request - show the form
        form = NewJobForm()
        return render_template('jobs/create.html', form=form)
    
    # Handle POST request
    if request.method == 'POST':
        # Check if it's a JSON request or form submission
        is_json_request = request.is_json or request.content_type == 'application/json'
        
        if is_json_request:
            # Handle JSON API request
            try:
                data = request.get_json()
                
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
                
                # Basic validation for required fields
                if not all([company, title, description]):
                    return jsonify({'error': 'Missing required fields: company, title, description'}), 400
                
                # Check if job already exists
                if posting_id and Job.query.filter_by(posting_id=posting_id).first():
                    return jsonify({'error': 'Job posting ID already exists'}), 409
                
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
                    posting_url=posting_url
                )
                
                db.session.add(job)
                db.session.commit()
                
                return jsonify({
                    'message': 'Job created successfully',
                    'job_id': job.id  # assuming your Job model has an id field
                }), 201
                
            except Exception as e:
                print(f"Error creating job via API: {e}")
                db.session.rollback()
                return jsonify({'error': 'Error creating job'}), 500
        
        else:
            # Handle form submission (existing logic)
            form = NewJobForm()
            if form.validate_on_submit():
                print("Form submitted successfully")
                company = form.company.data
                company_website = form.company_website.data
                title = form.title.data
                description = form.description.data
                location = request.form['location']
                salary_range_low = request.form['salary_range_low']
                salary_range_high = request.form['salary_range_high']
                remote_option = request.form['remote_option']
                posting_url = request.form['posting_url']
                posting_id = request.form['posting_id']
                referrer = request.form['referrer']
                referrer_posting_id = request.form['referrer_posting_id']
                resume_file = form.resume_file.data

                if resume_file:
                    original_resume_filename = secure_filename(resume_file.filename)
                    print(f"Original resume filename: {original_resume_filename}")
                    unique_resume_filename = generate_unique_filename(original_resume_filename)
                    print(f"Unique resume filename: {unique_resume_filename}")

                    # Create full file path
                    file_path = os.path.join(current_app.config['FILE_STORAGE_PATH'], 'Resumes', unique_resume_filename)

                    try:
                        # Save the file
                        resume_file.save(file_path)
                        flash(f'File "{original_resume_filename}" uploaded successfully as "{unique_resume_filename}"!', 'success')

                        # Optional: Store mapping of original to new filename in database
                        # store_file_mapping(original_filename, unique_filename)
                        
                    except Exception as e:
                        flash(f'Error uploading file: {str(e)}', 'error')

                # Check if job already exists
                if posting_id and Job.query.filter_by(posting_id=posting_id).first():
                    flash('Job posting ID already exists!', 'error')
                    return render_template('jobs/create.html', form=form)
                
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
                    resume_file=unique_resume_filename if resume_file else None
                )
                
                try:
                    db.session.add(job)
                    db.session.commit()
                    flash('Job created successfully!', 'success')
                    print("Before redirect to index")
                    return redirect('/')
                except Exception as e:
                    print(f"Error creating job: {e}")
                    db.session.rollback()
                    flash('Error creating job!', 'error')
            
            print("Rendering create job form")
            return render_template('jobs/create.html', form=form)
        

def generate_unique_filename(original_filename):
    """Generate a unique filename while preserving the extension"""
    # Get file extension
    _, ext = os.path.splitext(original_filename)
    # Generate unique name using UUID
    unique_name = str(uuid.uuid4()) + ext
    return unique_name