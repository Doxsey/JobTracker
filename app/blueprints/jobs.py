from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DecimalField
from wtforms.validators import DataRequired
from app.models import Job

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
    submit = SubmitField('Add Job')
    company_website = StringField('Company Website')

# @jobs_bp.route('/')
# def index():
#     """Display all jobs"""
#     jobs = Job.query.all()
#     return render_template('jobs/index.html', jobs=jobs)

@jobs_bp.route('/create', methods=['GET', 'POST'])
def create():
    print("Creating a new job")
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
            posting_url=posting_url
        )

        try:
            db.session.add(job)
            db.session.commit()
            flash('Job created successfully!', 'success')
            print("Before redirect to index")
            return redirect('/')
            # return redirect(url_for('jobs.create'))
        except Exception as e:
            print(f"Error creating job: {e}")
            db.session.rollback()
            flash('Error creating job!', 'error')

    print("Rendering create job form")
    return render_template('jobs/create.html', form=form)