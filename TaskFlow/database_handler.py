from .app import db
from .models import User, Task
from sqlalchemy import func, and_, or_, case
from datetime import datetime, timedelta
import logging

class DatabaseHandler:
    """Database handler class following SOLID principles for database operations"""
    
    def __init__(self):
        self.db = db
    
    # User operations
    def create_user(self, username, email, password):
        """Create a new user"""
        try:
            user = User(username=username, email=email, password=password)
            self.db.session.add(user)
            self.db.session.commit()
            logging.info(f"User created successfully: {username}")
            return user
        except Exception as e:
            self.db.session.rollback()
            logging.error(f"Error creating user: {str(e)}")
            raise e
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        return User.query.get(user_id)
    
    def get_user_by_username(self, username):
        """Get user by username"""
        return User.query.filter_by(username=username).first()
    
    def get_user_by_email(self, email):
        """Get user by email"""
        return User.query.filter_by(email=email).first()
    
    def get_all_users(self):
        """Get all users"""
        return User.query.all()
    
    def update_user(self, user_id, **kwargs):
        """Update user information"""
        try:
            user = self.get_user_by_id(user_id)
            if user:
                for key, value in kwargs.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                user.updated_at = datetime.utcnow()
                self.db.session.commit()
                logging.info(f"User updated successfully: {user.username}")
                return user
            return None
        except Exception as e:
            self.db.session.rollback()
            logging.error(f"Error updating user: {str(e)}")
            raise e
    
    def delete_user(self, user_id):
        """Delete user and all associated tasks"""
        try:
            user = self.get_user_by_id(user_id)
            if user:
                self.db.session.delete(user)
                self.db.session.commit()
                logging.info(f"User deleted successfully: {user.username}")
                return True
            return False
        except Exception as e:
            self.db.session.rollback()
            logging.error(f"Error deleting user: {str(e)}")
            raise e
    
    # Task operations
    def create_task(self, title, description, user_id, priority='medium', due_date=None):
        """Create a new task"""
        try:
            task = Task(
                title=title,
                description=description,
                user_id=user_id,
                priority=priority,
                due_date=due_date
            )
            self.db.session.add(task)
            self.db.session.commit()
            logging.info(f"Task created successfully: {title}")
            return task
        except Exception as e:
            self.db.session.rollback()
            logging.error(f"Error creating task: {str(e)}")
            raise e
    
    def get_task_by_id(self, task_id):
        """Get task by ID"""
        return Task.query.get(task_id)
    
    def get_tasks_by_user(self, user_id, status=None, priority=None):
        """Get tasks for a specific user with optional filters"""
        query = Task.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        if priority:
            query = query.filter_by(priority=priority)
        
        return query.order_by(Task.created_at.desc()).all()
    
    def get_all_tasks(self):
        """Get all tasks"""
        return Task.query.order_by(Task.created_at.desc()).all()
    
    def update_task(self, task_id, **kwargs):
        """Update task information"""
        try:
            task = self.get_task_by_id(task_id)
            if task:
                for key, value in kwargs.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                task.updated_at = datetime.utcnow()
                
                # Set completed_at if status is changed to completed
                if 'status' in kwargs and kwargs['status'] == 'completed':
                    task.completed_at = datetime.utcnow()
                elif 'status' in kwargs and kwargs['status'] != 'completed':
                    task.completed_at = None
                
                self.db.session.commit()
                logging.info(f"Task updated successfully: {task.title}")
                return task
            return None
        except Exception as e:
            self.db.session.rollback()
            logging.error(f"Error updating task: {str(e)}")
            raise e
    
    def delete_task(self, task_id):
        """Delete task"""
        try:
            task = self.get_task_by_id(task_id)
            if task:
                self.db.session.delete(task)
                self.db.session.commit()
                logging.info(f"Task deleted successfully: {task.title}")
                return True
            return False
        except Exception as e:
            self.db.session.rollback()
            logging.error(f"Error deleting task: {str(e)}")
            raise e
    
    # Complex queries with JOIN and GROUP BY
    def get_user_task_statistics(self):
        """Get task statistics grouped by user using JOIN and GROUP BY"""
        results = self.db.session.query(
            User.id,
            User.username,
            User.email,
            func.count(Task.id).label('total_tasks'),
            func.sum(case((Task.status == 'completed', 1), else_=0)).label('completed_tasks'),
            func.sum(case((Task.status == 'pending', 1), else_=0)).label('pending_tasks'),
            func.sum(case((Task.status == 'in_progress', 1), else_=0)).label('in_progress_tasks')
        ).outerjoin(Task).group_by(User.id, User.username, User.email).all()
        
        return [
            {
                'user_id': result.id,
                'username': result.username,
                'email': result.email,
                'total_tasks': result.total_tasks or 0,
                'completed_tasks': result.completed_tasks or 0,
                'pending_tasks': result.pending_tasks or 0,
                'in_progress_tasks': result.in_progress_tasks or 0
            }
            for result in results
        ]
    
    def get_task_priority_statistics(self, user_id=None):
        """Get task statistics grouped by priority"""
        query = self.db.session.query(
            Task.priority,
            func.count(Task.id).label('count'),
            func.sum(case((Task.status == 'completed', 1), else_=0)).label('completed'),
            func.sum(case((Task.status == 'pending', 1), else_=0)).label('pending'),
            func.sum(case((Task.status == 'in_progress', 1), else_=0)).label('in_progress')
        )
        
        if user_id:
            query = query.filter(Task.user_id == user_id)
        
        results = query.group_by(Task.priority).all()
        
        return [
            {
                'priority': result.priority,
                'count': result.count,
                'completed': result.completed or 0,
                'pending': result.pending or 0,
                'in_progress': result.in_progress or 0
            }
            for result in results
        ]
    
    def get_overdue_tasks(self, user_id=None):
        """Get overdue tasks using complex WHERE conditions"""
        query = Task.query.filter(
            and_(
                Task.due_date < datetime.utcnow(),
                Task.status != 'completed'
            )
        )
        
        if user_id:
            query = query.filter(Task.user_id == user_id)
        
        return query.join(User).order_by(Task.due_date).all()
    
    def get_tasks_due_soon(self, days=7, user_id=None):
        """Get tasks due within specified days"""
        future_date = datetime.utcnow() + timedelta(days=days)
        
        query = Task.query.filter(
            and_(
                Task.due_date <= future_date,
                Task.due_date >= datetime.utcnow(),
                Task.status != 'completed'
            )
        )
        
        if user_id:
            query = query.filter(Task.user_id == user_id)
        
        return query.join(User).order_by(Task.due_date).all()
    
    def search_tasks(self, search_term, user_id=None):
        """Search tasks by title or description"""
        search_pattern = f"%{search_term}%"
        
        query = Task.query.filter(
            or_(
                Task.title.ilike(search_pattern),
                Task.description.ilike(search_pattern)
            )
        )
        
        if user_id:
            query = query.filter(Task.user_id == user_id)
        
        return query.join(User).order_by(Task.updated_at.desc()).all()
    
    def get_recent_activity(self, user_id=None, limit=10):
        """Get recent task activity (created or updated)"""
        query = Task.query
        
        if user_id:
            query = query.filter(Task.user_id == user_id)
        
        return query.join(User).order_by(Task.updated_at.desc()).limit(limit).all()
