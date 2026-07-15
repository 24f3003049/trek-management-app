
import os
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# Base directory 
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Database aur login setup 
db = SQLAlchemy()
login_manager = LoginManager()

# Config class - app ka configuration 
class Config:
    SECRET_KEY = "trekking-management-secret-key"
    # Database path - SQLite
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "database", "trekking.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
