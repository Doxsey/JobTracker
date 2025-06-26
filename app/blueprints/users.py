from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import User

users_bp = Blueprint('users', __name__)

@users_bp.route('/')
def index():
    """Display all users"""
    users = User.query.all()
    return render_template('users/index.html', users=users)

@users_bp.route('/create', methods=['GET', 'POST'])
def create():
    print("Creating a new user")
    """Create a new user"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return render_template('users/create.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'error')
            return render_template('users/create.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('User created successfully!', 'success')
            return redirect(url_for('users.index'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating user!', 'error')
    
    return render_template('users/create.html')

@users_bp.route('/<int:user_id>')
def view(user_id):
    """View a specific user"""
    user = User.query.get_or_404(user_id)
    return render_template('users/view.html', user=user)

@users_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
def edit(user_id):
    """Edit a user"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        is_active = 'is_active' in request.form
        
        # Check if username/email already exists (excluding current user)
        existing_user = User.query.filter(User.username == username, User.id != user_id).first()
        if existing_user:
            flash('Username already exists!', 'error')
            return render_template('users/edit.html', user=user)
        
        existing_email = User.query.filter(User.email == email, User.id != user_id).first()
        if existing_email:
            flash('Email already exists!', 'error')
            return render_template('users/edit.html', user=user)
        
        # Update user
        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.is_active = is_active
        
        try:
            db.session.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('users.view', user_id=user.id))
        except Exception as e:
            db.session.rollback()
            flash('Error updating user!', 'error')
    
    return render_template('users/edit.html', user=user)

@users_bp.route('/<int:user_id>/delete', methods=['POST'])
def delete(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting user!', 'error')
    
    return redirect(url_for('users.index'))