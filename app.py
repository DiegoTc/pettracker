import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
login_manager = LoginManager()

def create_app(config_class='config.Config'):
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.secret_key = os.environ.get("SESSION_SECRET")
    
    # Enable CORS for all routes
    CORS(app)
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    
    # Import models to ensure they're registered with SQLAlchemy
    with app.app_context():
        # Import models
        from models import User, Pet, Device, Location
        
        # Create database tables
        db.create_all()
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.pets import pets_bp
    from routes.devices import devices_bp
    from routes.locations import locations_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(pets_bp, url_prefix='/api/pets')
    app.register_blueprint(devices_bp, url_prefix='/api/devices')
    app.register_blueprint(locations_bp, url_prefix='/api/locations')
    
    # Load the login manager user loader
    from models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Add a basic route for the API root
    @app.route('/')
    def index():
        return {'message': 'Pet Tracking API is running'}
    
    # Configure error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500
    
    return app

app = create_app()
