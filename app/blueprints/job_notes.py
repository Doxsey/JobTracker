from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DecimalField
from wtforms.validators import DataRequired
from app.models import Job

job_notes_bp = Blueprint('job_notes', __name__)