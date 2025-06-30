from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField, TextAreaField, DecimalField
from wtforms.validators import DataRequired
from app.models import Job, JobActivities, JobActivityTypes

select_activity_bp = Blueprint('select_activity', __name__)

@select_activity_bp.route('/search')
def search():
    query = request.args.get('q', '').lower()
    job_activity_types = JobActivityTypes.query.all()
    activity_type_choices = [(type.id, type.activity_type) for type in job_activity_types]

    return jsonify(activity_type_choices)

