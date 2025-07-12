import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24).hex()
    APP_FOLDER = os.environ.get('APP_FOLDER') or os.path.join(os.path.expanduser('~'), 'JobTracker')
    LOCAL_TIMEZONE = os.environ.get('LOCAL_TIMEZONE', 'America/Chicago')
    
    # Database configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # GitHub configuration
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
    GITHUB_REPO = os.environ.get('GITHUB_REPO')  # Format: "username/repository"
    GITHUB_BASE_BRANCH = os.environ.get('GITHUB_BASE_BRANCH', 'main')

    # rclone configuration for cloud backups
    RCLONE_CONFIG_PATH = os.environ.get('RCLONE_CONFIG_PATH')  # Optional: custom rclone config path
    RCLONE_DEFAULT_REMOTE = os.environ.get('RCLONE_DEFAULT_REMOTE')  # Optional: default remote to use
    RCLONE_BACKUP_PATH = os.environ.get('RCLONE_BACKUP_PATH', 'job-tracker-backups')  # Path on remote storage
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f'sqlite:///{self.APP_FOLDER}/app.db'
    
    @property
    def FILE_STORAGE_PATH(self):
        return f'{self.APP_FOLDER}/JobTrackerFiles'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    # Override to ensure production has secure secret
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for production!")

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}