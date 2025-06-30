from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField, TextAreaField, DecimalField
from wtforms.validators import DataRequired
from app.models import Job, JobActivities, JobActivityTypes

job_activities_bp = Blueprint('job_activities', __name__)

class NewJobActivityForm(FlaskForm):
    # activity_type = StringField('Activity Type', validators=[DataRequired()])
    activity_type = SelectField('Activity Type', coerce=int, validators=[DataRequired()])
    # activity_description = TextAreaField('Activity Description', validators=[DataRequired()])
    submit = SubmitField('Add Activity')

@job_activities_bp.route('/<int:job_id>/create', methods=['GET', 'POST'])
def create(job_id):
    form = NewJobActivityForm()

    job = Job.query.get_or_404(job_id)
    job_activity_types = JobActivityTypes.query.all()
    job_activity_types_list = [(type.activity_type) for type in job_activity_types]
    print(job_activity_types_list)
    # form.activity_type.choices = [(type.id, type.activity_type) for type in job_activity_types]

    print(f"Creating activity for Job ID: {job.id}, Title: {job.title}")

    if form.validate_on_submit():
        new_activity = JobActivities(
            job_id=job_id,
            # activity_type=form.activity_type.data,
            # activity_description=form.activity_description.data
        )
        db.session.add(new_activity)
        db.session.commit()
        flash('Activity added successfully!', 'success')
        return redirect('/')
        return redirect(url_for('jobs.view', job_id=job_id))

    return render_template('job_activities/create.html', form=form, job=job, job_activity_types_list=job_activity_types_list)