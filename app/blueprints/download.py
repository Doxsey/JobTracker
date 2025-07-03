from flask import Blueprint, send_from_directory, abort, request, redirect, url_for, flash, jsonify, current_app
from app import db
from app.models import Job
import os

download_bp = Blueprint('download', __name__)

@download_bp.route('/<int:job_id>/<file_type>')
def download_file(job_id, file_type):
    job = Job.query.get(job_id)
    if not job:
        flash('File not found.', 'danger')
        return redirect(url_for('main.index'))

    # Define file type mapping
    file_types = {
        'resume': {
            'field': 'resume_file',
            'folder': 'Resumes',
            'prefix': 'Resume'
        },
        'job_description': {
            'field': 'job_description_file',
            'folder': 'Job_Descriptions',
            'prefix': 'Job-Description'
        },
        'cover_letter': {
            'field': 'cover_letter_file',
            'folder': 'Cover_Letters',
            'prefix': 'Cover-Letter'
        }
    }

    # Validate file type
    if file_type not in file_types:
        flash('Invalid file type.', 'danger')
        return redirect(request.referrer or url_for('main.index'))

    file_config = file_types[file_type]

    # Get the filename from the job model
    filename = getattr(job, file_config['field'])
    if not filename:
        flash(f'{file_config["prefix"]} file not found.', 'danger')
        return redirect(request.referrer or url_for('main.index'))



    file_folder = os.path.join(current_app.config['FILE_STORAGE_PATH'], file_config['folder'])
    file_path = os.path.join(file_folder, filename)

    print(f"Attempting to download {file_config['prefix']} file: {file_path}")

    if not os.path.exists(file_path):
        print(f"{file_config['prefix']} file does not exist")
        flash('File does not exist.', 'danger')
        return redirect(request.referrer or url_for('main.index'))

    # Create new filename with job details
    file_extension = os.path.splitext(filename)[1]
    new_filename = f"{job.company}_{job.title}_{file_config['prefix']}_{job_id}{file_extension}"

    return send_from_directory(
        file_folder, 
        filename,
        as_attachment=True,
        download_name=new_filename
    )