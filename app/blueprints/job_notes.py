from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DecimalField
from wtforms.validators import DataRequired
from app.models import Job, JobNotes
from app.utils.html_utils import sanitize_html
from ..services.api_service import APIService
import requests
from datetime import date

job_notes_bp = Blueprint('job_notes', __name__)

class NewJobNoteForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Add Note')

class EditJobNoteForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Save Changes')

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
        return redirect(url_for('jobs.view', job_id=job_id))
    
    return render_template('job_notes/create.html', form=form, job=job)

@job_notes_bp.route('/<int:note_id>/edit', methods=['GET', 'POST'])
def edit(note_id):
    note: JobNotes = JobNotes.query.get_or_404(note_id)
    job = Job.query.get_or_404(note.job_id)
    form = EditJobNoteForm()

    if form.validate_on_submit():
        # Sanitize the updated content
        note.content = sanitize_html(form.content.data)
        db.session.commit()

        # Log the edit as an activity
        api = APIService()
        activity_data = {
            "job_id": job.id,
            "activity_type": "Note Updated",
            "activity_date": date.today().strftime("%Y-%m-%d"),
            "activity_brief": f"Job note updated",
            "activity_json_data": {
                "note_id": note.id
            }
        }
        
        try:
            response = api.create_job_activity(activity_data)
        except Exception as e:
            flash('Error logging note update activity.', 'warning')

        flash('Note updated successfully!', 'success')
        # return redirect(url_for('jobs.view', job_id=job.id))
        return redirect(request.referrer or url_for('jobs.view', job_id=job.id))
    
    elif request.method == 'GET':
        form.content.data = note.content
    
    return render_template('job_notes/edit.html', form=form, note=note, job=job)

@job_notes_bp.route('/<int:note_id>/delete', methods=['GET', 'POST'])
def delete(note_id):
    note = JobNotes.query.get_or_404(note_id)
    job = Job.query.get_or_404(note.job_id)
    
    if request.method == 'POST':
        # Log the deletion as an activity before deleting
        api = APIService()
        activity_data = {
            "job_id": job.id,
            "activity_type": "Note Deleted",
            "activity_date": date.today().strftime("%Y-%m-%d"),
            "activity_brief": f"Job note deleted",
            "activity_json_data": {
                "note_id": note.id,
                "note_preview": note.content[:100] + "..." if len(note.content) > 100 else note.content
            }
        }
        
        try:
            response = api.create_job_activity(activity_data)
        except Exception as e:
            flash('Error logging note deletion activity.', 'warning')
        
        db.session.delete(note)
        db.session.commit()
        
        flash('Note deleted successfully!', 'success')
        return redirect(url_for('jobs.view', job_id=job.id))
    
    return render_template('job_notes/delete.html', note=note, job=job)

# New API endpoint for quick delete (optional - for AJAX deletion)
@job_notes_bp.route('/api/<int:note_id>/delete', methods=['DELETE'])
def api_delete(note_id):
    note = JobNotes.query.get_or_404(note_id)
    job_id = note.job_id
    
    try:
        # Log the deletion activity
        api = APIService()
        activity_data = {
            "job_id": job_id,
            "activity_type": "Note Deleted",
            "activity_date": date.today().strftime("%Y-%m-%d"),
            "activity_brief": f"Job note deleted",
            "activity_json_data": {
                "note_id": note.id
            }
        }
        api.create_job_activity(activity_data)
        
        db.session.delete(note)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Note deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500