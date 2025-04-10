import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
from functools import wraps

# Load environment variables from .env file
load_dotenv()

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
login_manager = LoginManager()

def create_app(config_class='config.Config'):
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.secret_key = os.environ.get("SESSION_SECRET")
    
    # Enable CORS for all routes with support for credentials
    CORS(app, 
         # Allow all routes, not just /api/*
         resources={r"/*": {"origins": ["http://localhost:3000", 
                                       f"https://{os.environ.get('REPLIT_DEV_DOMAIN', '')}", 
                                       "https://pettracker.diegotc.repl.co",
                                       "*"]}},  # Adding wildcard for testing
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization", "X-Requested-With", 
                       "Access-Control-Allow-Origin", "Access-Control-Allow-Credentials",
                       "Accept", "Origin"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
         expose_headers=["Content-Type", "Authorization"],
         max_age=600,
         automatic_options=True)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Ensure database tables match models by reflecting metadata
    with app.app_context():
        # Reflect current database schema
        Base.metadata.reflect(db.engine)
    
    # Configure JWT
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # 24 hours
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Disable CSRF protection for cookies
    app.config['JWT_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
    
    # Initialize JWT with app
    jwt.init_app(app)
    
    # We'll use utils/auth_helpers.py for our custom JWT decorator
    # This keeps our routes cleaner and more maintainable
    
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
    from routes.documentation import doc_bp
    from routes.design_proposals import design_proposals_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(pets_bp, url_prefix='/api/pets')
    app.register_blueprint(devices_bp, url_prefix='/api/devices')
    app.register_blueprint(locations_bp, url_prefix='/api/locations')
    app.register_blueprint(doc_bp, url_prefix='/docs')
    app.register_blueprint(design_proposals_bp, url_prefix='/design')
    # Frontend blueprint removed to avoid conflicts with local development
    
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
