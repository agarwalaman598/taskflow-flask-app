from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
import logging

from app import app
from database_handler import DatabaseHandler
from auth import AuthHandler
from models import User, Task

# Initialize handlers
db_handler = DatabaseHandler()
auth_handler = AuthHandler()

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        errors = auth_handler.validate_registration_data(username, email, password, confirm_password)
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('register.html')
        
        try:
            user = db_handler.create_user(username, email, password)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        
        except Exception as e:
            logging.error(f"Registration error: {str(e)}")
            flash('Registration failed. Please try again.', 'danger')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = bool(request.form.get('remember_me'))
        
        user = auth_handler.authenticate_user(username, password)
        
        if user:
            login_user(user, remember=remember_me)
            
            next_page = request.args.get('next')
            if next_page and auth_handler.is_safe_url(next_page):
                return redirect(next_page)
            
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_stats = current_user.get_task_stats()
    recent_tasks = db_handler.get_tasks_by_user(current_user.id)[:5]
    overdue_tasks = db_handler.get_overdue_tasks(current_user.id)
    due_soon_tasks = db_handler.get_tasks_due_soon(7, current_user.id)
    priority_stats = db_handler.get_task_priority_statistics(current_user.id)
    
    return render_template('dashboard.html',
                         user_stats=user_stats,
                         recent_tasks=recent_tasks,
                         overdue_tasks=overdue_tasks,
                         due_soon_tasks=due_soon_tasks,
                         priority_stats=priority_stats)

@app.route('/tasks')
@login_required
def tasks():
    status_filter = request.args.get('status')
    priority_filter = request.args.get('priority')
    search_term = request.args.get('search')
    
    if search_term:
        user_tasks = db_handler.search_tasks(search_term, current_user.id)
    else:
        user_tasks = db_handler.get_tasks_by_user(current_user.id, status_filter, priority_filter)
    
    return render_template('tasks.html', 
                         tasks=user_tasks,
                         current_status=status_filter,
                         current_priority=priority_filter,
                         search_term=search_term)

@app.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        priority = request.form.get('priority', 'medium')
        due_date_str = request.form.get('due_date')
        
        if not title:
            flash('Task title is required', 'danger')
            return render_template('create_task.html')
        
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid due date format', 'danger')
                return render_template('create_task.html')
        
        try:
            task = db_handler.create_task(
                title=title, description=description, user_id=current_user.id,
                priority=priority, due_date=due_date
            )
            flash('Task created successfully!', 'success')
            return redirect(url_for('tasks'))
        except Exception as e:
            logging.error(f"Error creating task: {str(e)}")
            flash('Failed to create task. Please try again.', 'danger')
    
    return render_template('create_task.html')

@app.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = db_handler.get_task_by_id(task_id)
    
    if not task or task.user_id != current_user.id:
        flash('Task not found or access denied', 'danger')
        return redirect(url_for('tasks'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        status = request.form.get('status')
        priority = request.form.get('priority')
        due_date_str = request.form.get('due_date')
        
        if not title:
            flash('Task title is required', 'danger')
            return render_template('edit_task.html', task=task)
        
        # *** FIX: Handle empty date string ***
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid due date format', 'danger')
                return render_template('edit_task.html', task=task)
        
        try:
            updated_task = db_handler.update_task(
                task_id=task_id, title=title, description=description,
                status=status, priority=priority, due_date=due_date
            )
            
            if updated_task:
                flash('Task updated successfully!', 'success')
                return redirect(url_for('tasks'))
            else:
                flash('Failed to update task', 'danger')
        
        except Exception as e:
            logging.error(f"Error updating task: {str(e)}")
            flash('Failed to update task. Please try again.', 'danger')
    
    return render_template('edit_task.html', task=task)

@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = db_handler.get_task_by_id(task_id)
    
    if not task or task.user_id != current_user.id:
        flash('Task not found or access denied', 'danger')
        return redirect(url_for('tasks'))
    
    try:
        if db_handler.delete_task(task_id):
            flash('Task deleted successfully!', 'success')
        else:
            flash('Failed to delete task', 'danger')
    except Exception as e:
        logging.error(f"Error deleting task: {str(e)}")
        flash('Failed to delete task. Please try again.', 'danger')
    
    return redirect(url_for('tasks'))

@app.route('/tasks/<int:task_id>/toggle-status', methods=['POST'])
@login_required
def toggle_task_status(task_id):
    task = db_handler.get_task_by_id(task_id)
    
    if not task or task.user_id != current_user.id:
        return jsonify({'error': 'Task not found or access denied'}), 404
    
    try:
        # *** FIX: Correctly toggle any non-completed status to completed ***
        new_status = 'completed' if task.status != 'completed' else 'pending'
        updated_task = db_handler.update_task(task_id, status=new_status)
        
        if updated_task:
            return jsonify({
                'success': True,
                'new_status': new_status,
                'message': f'Task marked as {new_status.replace("_", " ")}'
            })
        else:
            return jsonify({'error': 'Failed to update task'}), 500
    
    except Exception as e:
        logging.error(f"Error toggling task status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# REST API Endpoints
@app.route('/api/tasks', methods=['GET'])
@login_required
def api_get_tasks():
    """REST API endpoint to get user tasks in JSON format"""
    try:
        # Get filter parameters
        status_filter = request.args.get('status')
        priority_filter = request.args.get('priority')
        
        # Get tasks
        tasks = db_handler.get_tasks_by_user(current_user.id, status_filter, priority_filter)
        
        # Convert to JSON format
        tasks_data = [task.to_dict() for task in tasks]
        
        return jsonify({
            'success': True,
            'tasks': tasks_data,
            'count': len(tasks_data),
            'user_id': current_user.id
        })
    
    except Exception as e:
        logging.error(f"API error getting tasks: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/tasks', methods=['POST'])
@login_required
def api_create_task():
    """REST API endpoint to create a new task"""
    try:
        data = request.get_json()
        
        if not data or not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        
        # Parse due date if provided
        due_date = None
        if data.get('due_date'):
            try:
                due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid due date format'}), 400
        
        # Create task
        task = db_handler.create_task(
            title=data['title'],
            description=data.get('description'),
            user_id=current_user.id,
            priority=data.get('priority', 'medium'),
            due_date=due_date
        )
        
        return jsonify({
            'success': True,
            'task': task.to_dict(),
            'message': 'Task created successfully'
        }), 201
    
    except Exception as e:
        logging.error(f"API error creating task: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
@login_required
def api_get_task(task_id):
    """REST API endpoint to get a specific task"""
    try:
        task = db_handler.get_task_by_id(task_id)
        
        if not task or task.user_id != current_user.id:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify({
            'success': True,
            'task': task.to_dict()
        })
    
    except Exception as e:
        logging.error(f"API error getting task: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def api_update_task(task_id):
    """REST API endpoint to update a task"""
    try:
        task = db_handler.get_task_by_id(task_id)
        
        if not task or task.user_id != current_user.id:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Parse due date if provided
        if 'due_date' in data and data['due_date']:
            try:
                data['due_date'] = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid due date format'}), 400
        
        # Update task
        updated_task = db_handler.update_task(task_id, **data)
        
        if updated_task:
            return jsonify({
                'success': True,
                'task': updated_task.to_dict(),
                'message': 'Task updated successfully'
            })
        else:
            return jsonify({'error': 'Failed to update task'}), 500
    
    except Exception as e:
        logging.error(f"API error updating task: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def api_delete_task(task_id):
    """REST API endpoint to delete a task"""
    try:
        task = db_handler.get_task_by_id(task_id)
        
        if not task or task.user_id != current_user.id:
            return jsonify({'error': 'Task not found'}), 404
        
        if db_handler.delete_task(task_id):
            return jsonify({
                'success': True,
                'message': 'Task deleted successfully'
            })
        else:
            return jsonify({'error': 'Failed to delete task'}), 500
    
    except Exception as e:
        logging.error(f"API error deleting task: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/statistics', methods=['GET'])
@login_required
def api_get_statistics():
    """REST API endpoint to get user statistics"""
    try:
        user_stats = current_user.get_task_stats()
        priority_stats = db_handler.get_task_priority_statistics(current_user.id)
        overdue_count = len(db_handler.get_overdue_tasks(current_user.id))
        due_soon_count = len(db_handler.get_tasks_due_soon(7, current_user.id))
        
        return jsonify({
            'success': True,
            'user_statistics': user_stats,
            'priority_statistics': priority_stats,
            'overdue_tasks': overdue_count,
            'tasks_due_soon': due_soon_count
        })
    
    except Exception as e:
        logging.error(f"API error getting statistics: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
