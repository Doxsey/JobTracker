from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DecimalField
from wtforms.validators import DataRequired
from app.models import Job, JobNotes

job_notes_bp = Blueprint('job_notes', __name__)

class NewJobNoteForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Add Note')


@job_notes_bp.route('/<int:job_id>/create', methods=['GET', 'POST'])
def create(job_id):
    form = NewJobNoteForm()

    job = Job.query.get_or_404(job_id)
    print(job.id, job.title)

    if form.validate_on_submit():
        new_note = JobNotes(
            job_id=job_id,
            content=form.content.data
        )
        db.session.add(new_note)
        db.session.commit()
        flash('Note added successfully!', 'success')
        return redirect('/')
        # return redirect(url_for('jobs.view', job_id=job_id))
    
    return render_template('job_notes/create.html', form=form, job=job)