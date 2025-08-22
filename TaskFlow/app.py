import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
# Use a provided session secret or fall back to a reasonable default for local dev
app.secret_key = os.environ.get("SESSION_SECRET") or os.environ.get("FLASK_SECRET") or os.urandom(24).hex()
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database from environment variables
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL") or f"sqlite:///{os.path.join(os.getcwd(), 'taskflow.db')}"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models to ensure tables are created
    from . import models  # noqa: F401
    db.create_all()
    logging.info("Database tables created successfully")