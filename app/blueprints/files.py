from flask import Blueprint, send_from_directory, abort, request, redirect, url_for, flash, jsonify, current_app
from app import db
from werkzeug.utils import secure_filename
from app.models import Job
import os, json, uuid

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

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'csv', 'xlsx'}
ALLOWED_FILE_TYPES = {'resume_file', 'job_description_file', 'cover_letter_file'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

@files_bp.route('/upload', methods=['POST'])
def upload_file():

    try:
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file_type = request.form.get('file_type')
        if not file_type:
            return jsonify({'error': 'file_type is required'}), 400
        if file_type not in ALLOWED_FILE_TYPES:
            return jsonify({'error': f'Invalid file_type. Allowed types are: {", ".join(ALLOWED_FILE_TYPES)}'}), 400

        file = request.files['file']
        
        # Check if file was actually selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get job_id from form data
        job_id = request.form.get('job_id')
        if not job_id:
            return jsonify({'error': 'job_id is required'}), 400
        
        # Validate job exists
        job = Job.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400

        # Get the correct folder based on file_type
        folder_mapping = {
            'resume_file': 'Resumes',
            'job_description_file': 'Job_Descriptions', 
            'cover_letter_file': 'Cover_Letters'
        }
        folder_name = folder_mapping.get(file_type)

        replace_existing = request.form.get('replace_existing', 'false').lower() == 'true'
        existing_file = getattr(job, file_type, None)
        if not replace_existing:
            print(f"Checking if {file_type} already exists for job ID {job_id}")
            # Check if file already exists for the job
            if existing_file:
                return jsonify({'error': f'{file_type.replace("_", " ").title()} already exists for this job. Set replace_existing to true to overwrite.'}), 400
        else:
            if existing_file:
                file_replaced = True
                print(f"Replacing existing {file_type} for job ID {job_id}")
                # If replacing, delete the existing file from the filesystem
                file_folder = os.path.join(current_app.config['FILE_STORAGE_PATH'], folder_name)
                file_path = os.path.join(file_folder, existing_file)

                print(f"File path to delete: {file_path}")
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        return jsonify({'error': f'Error deleting file from drive: {str(e)}'}), 400


        # Validate file size
        file_size = get_file_size(file)
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': f'File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB'}), 400
        
        # Generate secure filename
        original_filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(original_filename)

        if not folder_name:
            return jsonify({'error': 'Invalid file type specified'}), 400

        upload_folder = os.path.join(current_app.config['FILE_STORAGE_PATH'], folder_name)
        # Create full file path
        file_path = os.path.join(upload_folder, unique_filename)

        try:
            # Save the file
            file.save(file_path)
            
            # Update the job record with the new filename
            setattr(job, file_type, unique_filename)
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Error uploading file: {str(e)}'}), 500


        # # Generate secure filename
        # original_filename = secure_filename(file.filename)
        # file_extension = original_filename.rsplit('.', 1)[1].lower()
        # unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # # Create upload directory
        # upload_folder = os.path.join(current_app.config['FILE_STORAGE_PATH'], 'uploads')
        # os.makedirs(upload_folder, exist_ok=True)
        
        # # Save file
        # file_path = os.path.join(upload_folder, unique_filename)
        # file.save(file_path)
        
        # Optional: Save file info to database
        # file_record = FileUpload(
        #     job_id=job_id,
        #     original_filename=original_filename,
        #     stored_filename=unique_filename,
        #     file_size=file_size,
        #     file_path=file_path
        # )
        # db.session.add(file_record)
        # db.session.commit()
        
        response = {
            'success': True,
            'message': 'File uploaded successfully',
            'job_id': int(job_id),
            'file_type': file_type,
            'original_filename': original_filename,
            'stored_filename': unique_filename,
            'file_size': file_size,
            'file_path': file_path
        }
        
        if 'file_replaced' in locals():
            response['file_replaced'] = file_replaced

        return jsonify(response), 200
        
    except Exception as e:
        print(f"Error uploading file: {e}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size(file):
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size

def generate_unique_filename(original_filename):
    """Generate a unique filename while preserving the extension"""
    # Get file extension
    _, ext = os.path.splitext(original_filename)
    # Generate unique name using UUID
    unique_name = str(uuid.uuid4()) + ext
    return unique_name


