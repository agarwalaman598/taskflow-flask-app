from datetime import datetime
from types import SimpleNamespace
from .app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import func, case # Make sure func and case are imported here

class User(UserMixin, db.Model):
    """User model representing application users"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with tasks
    tasks = db.relationship('Task', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, username, email, password):
        """Initialize user with hashed password"""
        self.username = username
        self.email = email
        self.set_password(password)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_task_stats(self):
        """
        Get task statistics for this user using efficient database queries.
        """
        # *** FIX: Replaced inefficient Python-side counting with database queries ***
        query = db.session.query(
            func.count(Task.id).label("total"),
            func.sum(case((Task.status == 'completed', 1), else_=0)).label("completed")
        ).filter(Task.user_id == self.id)
        
        stats = query.one()
        
        total_tasks = stats.total or 0
        completed_tasks = stats.completed or 0
        
        # Return a SimpleNamespace to allow attribute access in templates
        return SimpleNamespace(
            total=total_tasks,
            completed=completed_tasks,
            pending=total_tasks - completed_tasks
        )
    
    def to_dict(self):
        """Convert user to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'task_count': len(self.tasks)
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

class Task(db.Model):
    """Task model representing user tasks"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    priority = db.Column(db.String(10), default='medium')  # low, medium, high
    due_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Foreign key to user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __init__(self, title, description=None, user_id=None, priority='medium', due_date=None):
        """Initialize task"""
        self.title = title
        self.description = description
        self.user_id = user_id
        self.priority = priority
        self.due_date = due_date
    
    def mark_completed(self):
        """Mark task as completed"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
    
    def mark_in_progress(self):
        """Mark task as in progress"""
        self.status = 'in_progress'
        self.completed_at = None
    
    def mark_pending(self):
        """Mark task as pending"""
        self.status = 'pending'
        self.completed_at = None
    
    def is_overdue(self):
        """Check if task is overdue"""
        if self.due_date and self.status != 'completed':
            return datetime.utcnow() > self.due_date
        return False
    
    def get_priority_color(self):
        """Get color class for priority"""
        priority_colors = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger'
        }
        return priority_colors.get(self.priority, 'secondary')
    
    def get_status_color(self):
        """Get color class for status"""
        status_colors = {
            'pending': 'secondary',
            'in_progress': 'primary',
            'completed': 'success'
        }
        return status_colors.get(self.status, 'secondary')
    
    def to_dict(self):
        """Convert task to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'user_id': self.user_id,
            'is_overdue': self.is_overdue()
        }
    
    def __repr__(self):
        return f'<Task {self.title}>'

# Create indexes for better query performance
db.Index('idx_task_user_status', Task.user_id, Task.status)
db.Index('idx_task_user_priority', Task.user_id, Task.priority)
db.Index('idx_task_due_date', Task.due_date)
