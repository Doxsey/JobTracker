from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField, TextAreaField, DecimalField
from wtforms.validators import DataRequired
from app.models import Job, JobActivities, JobActivityTypes
from datetime import datetime
import json

job_activities_bp = Blueprint('job_activities', __name__)

@job_activities_bp.route('/<int:job_id>/create', methods=['GET', 'POST'])
def create(job_id):

    job = Job.query.get_or_404(job_id)
    job_activity_types = JobActivityTypes.query.all()
    job_activity_types_list = [(type.activity_type) for type in job_activity_types]

    return render_template('job_activities/create.html', job=job, job_activity_types_list=job_activity_types_list)

@job_activities_bp.route('api/create', methods=['POST'])
def add():
    data = request.get_json()
    print(f"Received data: {data}")
    print(f"Type of data: {type(data)}")
    if not data:
        return jsonify({'error': 'No input data provided'}), 400
    
    try:
        # Adjust field names as needed to match your JobActivities model
        job_id = data['job_id']
        activity_type = data.get('activity_type')
        activity_date_str = data.get('activity_date')
        activity_brief = data.get('activity_brief')
        activity_date = None
        if activity_date_str:
            try:
                activity_date = datetime.strptime(activity_date_str, "%Y-%m-%d")
            except ValueError:
                return jsonify({'error': 'Invalid activity_date format. Use ISO 8601 format.'}), 400
        
        job = Job.query.get(job_id)
        if not job:
            return jsonify({'error': f'Job with job_id: {job_id} not found'}), 400
        
        activity_json_data = data.get('activity_json_data', {})
        if not isinstance(activity_json_data, dict):
            try:
                activity_json_data = json.loads(activity_json_data)
            except Exception:
                return jsonify({'error': 'activity_json_data must be a valid JSON object'}), 400
        
        print(f"Type of activity_json_data: {type(activity_json_data)}")

        # Remove 'activity_type' from activity_json_data if present
        if 'activity_type' in activity_json_data:
            activity_json_data.pop('activity_type')
        if 'activity_date' in activity_json_data:
            activity_json_data.pop('activity_date')

        new_activity = JobActivities(
            job_id=job_id,
            activity_date=activity_date,
            activity_type=activity_type,
            activity_brief=activity_brief,
            activity_json_data=activity_json_data
        
        )

        print(f"Adding new activity: {new_activity}")

        db.session.add(new_activity)
        db.session.commit()

        response_data = {
                    'message': 'Job activity added successfully',
                    'job_activity_id': new_activity.id,
                    'job_id': job_id,
                }

        return jsonify(response_data), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500