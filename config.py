import os
from dotenv import load_dotenv

# Load variables from .env file into the environment
load_dotenv()


class Config:
    """
    Base configuration class.
    All settings that are shared across environments go here.
    """

    # Secret key — Flask uses this to encrypt session cookies
    # os.urandom(24) generates a random key if .env is not set
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)

    # Database URI — tells SQLAlchemy where the database is
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///eventhub.db'

    # Disable modification tracking (saves memory, not needed)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ─── Email Settings ────────────────────────────────────────
    MAIL_SERVER   = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT     = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS  = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')

    # ─── File Upload Settings ──────────────────────────────────
    # Where uploaded event images are saved
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__),
                                 'app', 'static', 'images', 'uploads')
    # Maximum upload size: 5 MB
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    # Allowed image types
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # ─── Pagination ────────────────────────────────────────────
    EVENTS_PER_PAGE = 9   # How many events show per page


class DevelopmentConfig(Config):
    """Settings used during local development."""
    DEBUG = True


class ProductionConfig(Config):
    """Settings used when deployed to a real server."""
    DEBUG = False
    # In production, use a proper database like PostgreSQL:
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


# Dictionary to select config by name
config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig
}
