from flask import Blueprint, send_from_directory, abort, request, redirect, url_for, flash, jsonify, current_app
from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, TextAreaField, DecimalField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from app.models import Job
import os, uuid, json

download_bp = Blueprint('download', __name__)

@download_bp.route('/resume/<int:job_id>')
def download_resume_file(job_id):
    job = Job.query.get(job_id)
    if not job:
        flash('File not found.', 'danger')
        return redirect(url_for('main.index'))

    resume_folder = os.path.join(current_app.config['FILE_STORAGE_PATH'], "Resumes")
    file_path = os.path.join(resume_folder, job.resume_file)
    print(f"Attempting to download resume file: {file_path}")

    if not os.path.exists(file_path):
        print(f"Resume file does not exist")
        flash('File does not exist.', 'danger')
        return redirect(request.referrer or url_for('main.index'))

    new_filename = f"{job.company}_{job.title}_Resume_{job_id}.pdf"

    return send_from_directory(
        resume_folder, 
        job.resume_file,
        as_attachment=True,
        download_name=new_filename
    )