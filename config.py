import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Flask app configuration
class Config:
    # Secret key for session management
    SECRET_KEY = os.environ.get("SESSION_SECRET", "dev-secret-key")
    
    # Database configuration - using SQLite for development
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///pet_tracker.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Google OAuth configuration
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
    
    # API rate limiting
    RATELIMIT_DEFAULT = "100/hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # 808 Protocol configuration
    PROTOCOL_808_PORT = os.environ.get("PROTOCOL_808_PORT", 8080)
    
    # Application constants
    PET_TYPES = ["Dog", "Cat", "Bird", "Other"]
    
    # REST API settings
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
