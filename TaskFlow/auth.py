from flask_login import LoginManager
from .models import User
from email_validator import validate_email, EmailNotValidError # <-- THIS LINE IS THE FIX
from .app import app

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))

class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
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
        """Validate user registration data"""
        errors = []
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            errors.append('Username already exists')
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            errors.append('Email already exists')

        # Use a robust library for email validation
        try:
            validate_email(email)
        except EmailNotValidError as e:
            errors.append(str(e))
        
        # Validate password
        if len(password) < 8:
            errors.append('Password must be at least 8 characters long')
        
        # Check password confirmation
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        # Validate username
        if len(username) < 3:
            errors.append('Username must be at least 3 characters long')
        
        return errors
    
    @staticmethod
    def is_safe_url(target):
        """Check if the target URL is safe for redirection"""
        return target and not target.startswith('http')