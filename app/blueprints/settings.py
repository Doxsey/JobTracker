from flask import Blueprint, jsonify, render_template, request, send_file, url_for, flash, current_app
from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField, TextAreaField, DecimalField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed
from app.models import Job, Settings, JobActivityTypes
from werkzeug.utils import secure_filename
from datetime import datetime
import os

settings_bp = Blueprint('settings', __name__)

def allowed_file(filename):
    allowed_extensions = {'pdf', 'doc', 'docx', 'tex'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


class SettingsForm(FlaskForm):
    key = StringField('Key', validators=[DataRequired()])
    value = StringField('Value', validators=[DataRequired()])
    submit = SubmitField('Save Settings')

@settings_bp.route('/', methods=['GET', 'POST'])
def index():
    current_settings = Settings.query.all()
    return render_template('settings/index.html', current_settings=current_settings)

@settings_bp.route('/api/update', methods=['POST'])
def update_setting():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400
    
    key = data.get('key')
    value = data.get('value')
    
    if not key or not value:
        return jsonify({'error': 'Key and value are required'}), 400
    
    setting = Settings.query.filter_by(key=key).first()
    
    if setting:
        setting.value = value
    else:
        setting = Settings(key=key, value=value)
        db.session.add(setting)
    
    db.session.commit()
    
    return jsonify({'message': 'Setting updated successfully'}), 200

@settings_bp.route('/api/upload_default_resume', methods=['POST'])
def upload_default_resume():
    if 'default_resume_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['default_resume_file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        _, ext = os.path.splitext(file.filename)

        filename = f"default_resume{ext}"
        file.save(os.path.join(current_app.config['FILE_STORAGE_PATH'], 'Resumes', filename))
        flash('Default resume uploaded successfully!', 'success')
        
        # Optionally, you can update the Settings table with the new resume file path
        setting = Settings.query.filter_by(key='default_resume').first()
        if setting:
            setting.value = filename
        else:
            setting = Settings(key='default_resume', value=filename)
            db.session.add(setting)
        db.session.commit()

        return jsonify({'success': True}), 200

    return jsonify({'error': 'Invalid file type'}), 400

@settings_bp.route('/api/download_default_resume', methods=['GET'])
def download_default_resume():
    resume_path = os.path.join(current_app.config['FILE_STORAGE_PATH'], 'Resumes', 'default_resume.pdf')
    if os.path.exists(resume_path):
        return send_file(resume_path, as_attachment=True)
    return jsonify({'error': 'Default resume not found'}), 404


@settings_bp.route('/api/delete_default_resume', methods=['DELETE'])
def delete_default_resume():
    resume_path = os.path.join(current_app.config['FILE_STORAGE_PATH'], 'Resumes', 'default_resume.pdf')
    if os.path.exists(resume_path):
        os.remove(resume_path)
        flash('Default resume deleted successfully!', 'success')
        
        # Optionally, remove the setting from the database
        setting = Settings.query.filter_by(key='default_resume').first()
        if setting:
            db.session.delete(setting)
            db.session.commit()
        
        return jsonify({'success': True}), 200
    return jsonify({'error': 'Default resume not found'}), 404