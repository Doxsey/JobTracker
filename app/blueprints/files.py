from flask import Blueprint, send_from_directory, abort, request, redirect, url_for, flash, jsonify, current_app
from app import db
from app.models import Job
import os, json

files_bp = Blueprint('files', __name__)

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

@files_bp.route('/<int:job_id>/<file_type>')
def download_file(job_id, file_type):
    print(f"Request to download file of type: {file_type} for job ID: {job_id}")
    job = Job.query.get(job_id)
    if not job:
        flash('File not found.', 'danger')
        return redirect(url_for('main.index'))

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

@files_bp.route('/delete', methods=['POST'])
def delete_file():
    is_json_request = request.is_json or request.content_type == 'application/json'
    if is_json_request:
        try:
            data = request.get_json()

            print(f"Received JSON data for file deletion: {data}")

            job_id = data.get('job_id')
            file_name = data.get('file_name')

            job = Job.query.get(job_id)

            if not job:
                return jsonify({'error': 'Job not found.'}), 400
            
            if file_name == job.resume_file:
                job.resume_file = None
                file_config = file_types['resume']
            elif file_name == job.job_description_file:
                job.job_description_file = None
                file_config = file_types['job_description']
            elif file_name == job.cover_letter_file:
                job.cover_letter_file = None
                file_config = file_types['cover_letter']
            else:
                return jsonify({'error': 'File not found in job.'}), 400

            db.session.commit()
            file_folder = os.path.join(current_app.config['FILE_STORAGE_PATH'], file_config['folder'])
            file_path = os.path.join(file_folder, file_name)

            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    return jsonify({'error': f'Error deleting file from drive: {str(e)}'}), 400
            
            response = {
                'success': True,
                'message': 'File deleted successfully.',
                'job_id': job_id,
                'file_name': file_name
            }

            return jsonify(response), 200

        except json.JSONDecodeError:
                return jsonify({'error': 'Invalid JSON data'}), 400
        except Exception as e:
            print(f"Error creating job via API: {e}")
            db.session.rollback()
            return jsonify({'error': 'Error updating job'}), 500
    else:
        flash('Invalid request format. Please use JSON.', 'danger')
        return redirect(request.referrer or url_for('main.index'))
