from flask import Blueprint, request, jsonify, redirect, url_for, current_app
from flask_login import current_user, login_user, logout_user, login_required
from app import db, limiter
from models import User
import os
import json
import requests
from oauthlib.oauth2 import WebApplicationClient
import logging
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import os
# Needed for local development only - allows OAuth over HTTP
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Create blueprint
auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

# Google OAuth setup
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

def get_google_client():
    return WebApplicationClient(current_app.config['GOOGLE_CLIENT_ID'])

@auth_bp.route('/login_info', methods=['GET'])
def login_info():
    """Return information about Google login configuration"""
    DEV_REDIRECT_URL = f'https://{os.environ.get("REPLIT_DEV_DOMAIN", "localhost:5000")}/api/auth/callback'
    
    setup_info = {
        "message": "To make Google authentication work:",
        "steps": [
            "1. Go to https://console.cloud.google.com/apis/credentials",
            "2. Create a new OAuth 2.0 Client ID",
            f"3. Add {DEV_REDIRECT_URL} to Authorized redirect URIs"
        ],
        "documentation": "https://docs.replit.com/additional-resources/google-auth-in-flask#set-up-your-oauth-app--client"
    }
    
    return jsonify(setup_info)

@auth_bp.route('/login', methods=['GET'])
@limiter.limit("10/minute")
def login():
    """Initiate the Google OAuth flow"""
    # Check if Google OAuth is configured
    if not current_app.config['GOOGLE_CLIENT_ID'] or not current_app.config['GOOGLE_CLIENT_SECRET']:
        return jsonify({"error": "Google OAuth not configured"}), 500
    
    client = get_google_client()
    
    # Get Google's OAuth 2.0 endpoints
    try:
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
        
        # Build redirect URL for Google login
        # Get the exact redirect URL to use in production and development
        is_local = "localhost" in request.host or "127.0.0.1" in request.host
        
        # Print domain for debugging
        logger.info(f"Current host: {request.host}, Is local: {is_local}")
        
        # For development, the URL should always exactly match what's in Google Console
        # Instead of programmatically building it, let's use a consistent URL
        if is_local:
            # This should exactly match what's in your Google OAuth settings
            callback_url = "http://localhost:5000/api/auth/callback"
        else:
            # For production environment (Replit)
            replit_domain = os.environ.get("REPLIT_DEV_DOMAIN", "")
            if replit_domain:
                callback_url = f"https://{replit_domain}/api/auth/callback"
            else:
                # Fallback to generated URL for other production environments
                callback_url = request.base_url.replace("http://", "https://").replace("/login", "/callback")
            
        logger.info(f"Using callback URL: {callback_url}")
        
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=callback_url,
            scope=["openid", "email", "profile"],
        )
        
        return jsonify({"redirect_url": request_uri})
    except Exception as e:
        logger.error(f"Error initiating Google OAuth flow: {str(e)}")
        return jsonify({"error": "Failed to initiate login process"}), 500

@auth_bp.route('/callback', methods=['GET'])
def callback():
    """Handle the Google OAuth callback"""
    # Check if Google OAuth is configured
    if not current_app.config['GOOGLE_CLIENT_ID'] or not current_app.config['GOOGLE_CLIENT_SECRET']:
        return jsonify({"error": "Google OAuth not configured"}), 500
    
    # Get authorization code from the callback
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Authorization code missing"}), 400
    
    client = get_google_client()
    
    try:
        # Get Google's OAuth 2.0 endpoints
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg["token_endpoint"]
        
        # Prepare and send token request
        is_local = "localhost" in request.host or "127.0.0.1" in request.host
        
        # Print domain for debugging
        logger.info(f"Callback - Current host: {request.host}, Is local: {is_local}")
        
        if is_local:
            # For local development, use the exact same URL as in login method
            auth_response = request.url
            redirect_url = "http://localhost:5000/api/auth/callback"
        else:
            # For production
            auth_response = request.url.replace("http://", "https://")
            
            # For Replit environments
            replit_domain = os.environ.get("REPLIT_DEV_DOMAIN", "")
            if replit_domain:
                redirect_url = f"https://{replit_domain}/api/auth/callback"
            else:
                redirect_url = request.base_url.replace("http://", "https://")
            
        logger.info(f"Callback - Using redirect URL for token request: {redirect_url}")
        
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=auth_response,
            redirect_url=redirect_url,
            code=code,
        )
        
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(current_app.config['GOOGLE_CLIENT_ID'], current_app.config['GOOGLE_CLIENT_SECRET']),
        )
        
        # Parse the token response
        client.parse_request_body_response(json.dumps(token_response.json()))
        
        # Get user info from Google
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        
        userinfo = userinfo_response.json()
        
        # Verify user info
        if not userinfo.get("email_verified"):
            return jsonify({"error": "User email not verified by Google"}), 400
        
        # Get user data
        email = userinfo["email"]
        username = email.split("@")[0]  # Use email prefix as username
        name = userinfo.get("name")
        picture = userinfo.get("picture")
        
        # Find or create user
        user = User.query.filter_by(email=email).first()
        if not user:
            # Try to extract first name and last name
            first_name = userinfo.get("given_name", "")
            last_name = userinfo.get("family_name", "")
            
            # Create new user
            user = User(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                profile_picture=picture
            )
            db.session.add(user)
            db.session.commit()
        
        # Update last login time
        user.last_login = db.func.now()
        db.session.commit()
        
        # Login the user
        login_user(user)
        
        # Create JWT token - Convert user.id to string to prevent "Subject must be a string" error
        access_token = create_access_token(identity=str(user.id))
        
        # Check if this is a browser flow or API call
        request_accepts_json = request.headers.get('Accept', '').startswith('application/json')
        redirect_param = request.args.get('redirect_to_frontend', 'true').lower() == 'true'
        
        if request_accepts_json and not redirect_param:
            # Return JSON for API clients
            return jsonify({
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "profile_picture": user.profile_picture
                },
                "access_token": access_token
            })
        else:
            # Redirect to frontend with token as URL parameter for browser flow
            is_local = "localhost" in request.host or "127.0.0.1" in request.host
            
            if is_local:
                frontend_url = "http://localhost:3000"
            else:
                # For production environments, use the same domain with a different port
                replit_domain = os.environ.get("REPLIT_DEV_DOMAIN", "")
                if replit_domain:
                    frontend_url = f"https://{replit_domain}" 
                else:
                    frontend_url = request.url_root.replace("http://", "https://")
            
            redirect_url = f"{frontend_url}/auth/callback?token={access_token}"
            logger.info(f"Redirecting to frontend: {redirect_url}")
            return redirect(redirect_url)
    
    except Exception as e:
        logger.error(f"Error in Google OAuth callback: {str(e)}")
        return jsonify({"error": "Authentication failed"}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout the current user"""
    logout_user()
    return jsonify({"message": "Logout successful"})

@auth_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    """Get current user information"""
    user_id = get_jwt_identity()
    # Convert to int if needed, since we stored it as a string in the token
    if isinstance(user_id, str) and user_id.isdigit():
        user_id = int(user_id)
    
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "profile_picture": user.profile_picture,
        "pets_count": user.pets.count(),
        "devices_count": user.devices.count()
    })

@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    if current_user.is_authenticated:
        # Create a JWT token for API access
        access_token = create_access_token(identity=str(current_user.id))
        
        return jsonify({
            "authenticated": True,
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "username": current_user.username
            },
            "access_token": access_token
        })
    else:
        return jsonify({"authenticated": False})

# Development/testing only endpoint - should be removed in production
@auth_bp.route('/dev-token', methods=['GET'])
def get_dev_token():
    """Get a development token for testing - NOT FOR PRODUCTION USE"""
    # Creating a token for testing purposes in any environment
    # Create a test user if it doesn't exist
    test_email = "test@example.com"
    test_user = User.query.filter_by(email=test_email).first()
    
    if not test_user:
        test_user = User(
            email=test_email,
            username="testuser",
            first_name="Test",
            last_name="User"
        )
        db.session.add(test_user)
        db.session.commit()
        logger.info(f"Created test user: {test_email}")
    
    # Create JWT token for the test user - make sure to convert id to string
    access_token = create_access_token(identity=str(test_user.id))
    
    return jsonify({
        "message": "Development token generated",
        "user_id": test_user.id,
        "access_token": access_token,
        "token": access_token  # Added for compatibility with test_api.py
    })
