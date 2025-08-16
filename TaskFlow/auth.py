from flask_login import LoginManager
from .models import User
from .app import app

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class AuthenticationError(Exception):
    pass

class AuthHandler:
    """Authentication handler following SOLID principles"""
    
    @staticmethod
    def authenticate_user(username, password):
        """Authenticate user with username and password"""
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            return user
        
        return None
    
     
    @staticmethod
    def validate_registration_data(username, email, password, confirm_password):
        errors = []
        
        if len(username) < 3:
            errors.append('Username must be at least 3 characters long')
        if User.query.filter_by(username=username).first():
            errors.append('Username already exists')
        
        if User.query.filter_by(email=email).first():
            errors.append('Email already exists')
        
        # *** FIX: Use a robust library for email validation ***
        try:
            validate_email(email)
        except EmailNotValidError as e:
            errors.append(str(e))
        
        if len(password) < 8:
            errors.append('Password must be at least 8 characters long')
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        return errors
    
    @staticmethod
    def is_safe_url(target):
        """Check if the target URL is safe for redirection"""
        # Basic implementation - in production, you might want more sophisticated checks
        return target and not target.startswith('http')
