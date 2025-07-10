from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DecimalField
from wtforms.validators import DataRequired
from app.models import Job, JobNotes
from app.utils.html_utils import sanitize_html  # Add this import
from ..services.api_service import APIService
import requests
from datetime import date

job_notes_bp = Blueprint('job_notes', __name__)

class NewJobNoteForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Add Note')

@job_notes_bp.route('/<int:job_id>/create', methods=['GET', 'POST'])
def create(job_id):
    form = NewJobNoteForm()
    job = Job.query.get_or_404(job_id)

    if form.validate_on_submit():
        # Sanitize the rich text content
        sanitized_content = sanitize_html(form.content.data)
        
        new_note = JobNotes(
            job_id=job_id,
            content=sanitized_content  # Now contains sanitized HTML
        )
        db.session.add(new_note)
        db.session.commit()

        api = APIService()

        activity_data = {
            "job_id": job.id,
            "activity_type": "Note Added",
            "activity_date": date.today().strftime("%Y-%m-%d"),
            "activity_brief": f"Job note added",
            "activity_json_data": {
                "note_id": new_note.id
            }
        }
        
        try:
            response = api.create_job_activity(activity_data)
            if response.status_code != 201:
                flash('Failed to add job note activity.', 'warning')
                return render_template('job_notes/create.html', form=form, job=job)
        except Exception as e:
            flash('Error logging job note activity.', 'warning')
            return render_template('job_notes/create.html', form=form, job=job)

        flash('Note added successfully!', 'success')
        return redirect(url_for('jobs.view', job_id=job_id))  # Redirect to job view instead of home
    
    return render_template('job_notes/create.html', form=form, job=job)