import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

'''
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or 'sqlite:///project_tracker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
'''

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'project_tracker.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    UPLOADED_ATTACHMENTS_DEST = os.path.join(basedir, 'static/uploads')
    UPLOADED_ATTACHMENTS_ALLOW = ['pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx']
    
    # Flask-Login settings
    REMEMBER_COOKIE_DURATION = 3600  # 1 hour

