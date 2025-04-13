from flask import Blueprint, request, jsonify, redirect, url_for, current_app
from flask_login import current_user, login_user, logout_user, login_required
from app import db, limiter
from models import User
import os
import json
import requests
import traceback
import urllib.parse
import platform
from oauthlib.oauth2 import WebApplicationClient
import logging
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from utils.auth_helpers import jwt_required_except_options
# Needed for local development only - allows OAuth over HTTP
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Create blueprint
auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

# Google OAuth setup
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

def get_google_client():
    return WebApplicationClient(current_app.config['GOOGLE_CLIENT_ID'])

@auth_bp.route('/login_info', methods=['GET', 'OPTIONS'])
def login_info():
    """Return information about Google login configuration"""
    # Handle OPTIONS request explicitly for better CORS support
    if request.method == 'OPTIONS':
        return handle_options_request()
        
    DEV_REDIRECT_URL = f'https://{os.environ.get("REPLIT_DEV_DOMAIN", "localhost:5000")}/api/auth/callback'
    
    # Check if Google OAuth is configured
    google_client_id = current_app.config['GOOGLE_CLIENT_ID']
    google_client_secret = current_app.config['GOOGLE_CLIENT_SECRET']
    
    setup_info = {
        "googleConfigured": bool(google_client_id and google_client_secret),
        "message": "To make Google authentication work:",
        "steps": [
            "1. Go to https://console.cloud.google.com/apis/credentials",
            "2. Create a new OAuth 2.0 Client ID",
            f"3. Add {DEV_REDIRECT_URL} to Authorized redirect URIs"
        ],
        "documentation": "https://docs.replit.com/additional-resources/google-auth-in-flask#set-up-your-oauth-app--client"
    }
    
    # Add debug information in development
    if os.environ.get('FLASK_ENV') != 'production':
        setup_info['debug'] = {
            'client_id_set': bool(google_client_id),
            'client_secret_set': bool(google_client_secret),
            'env_client_id_set': 'GOOGLE_OAUTH_CLIENT_ID' in os.environ,
            'env_client_secret_set': 'GOOGLE_OAUTH_CLIENT_SECRET' in os.environ,
            'request_origin': request.headers.get('Origin', 'Not provided'),
            'cors_enabled': True
        }
    
    response = jsonify(setup_info)
    
    # Ensure CORS headers are present
    origin = request.headers.get('Origin')
    if origin:
        # If origin is provided, ensure it's allowed
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Credentials', 'true')
    
    # Log the response headers for debugging
    logger.info(f"Login Info Response Headers: {dict(response.headers)}")
    
    return response

@auth_bp.route('/login', methods=['GET', 'OPTIONS'])
@limiter.limit("10/minute", methods=['GET'])
def login():
    """Initiate the Google OAuth flow"""
    # Log detailed request information for debugging
    logger.info(f"Login Request - Host: {request.host}, Path: {request.path}, Method: {request.method}")
    logger.info(f"Login Request - Headers: {dict(request.headers)}")
    
    # Check if Google OAuth is configured
    if not current_app.config['GOOGLE_CLIENT_ID'] or not current_app.config['GOOGLE_CLIENT_SECRET']:
        logger.error("Google OAuth not configured - missing client ID or secret")
        return jsonify({"error": "Google OAuth not configured"}), 500
    
    client = get_google_client()
    logger.info("Google client created successfully")
    
    # Get Google's OAuth 2.0 endpoints
    try:
        # Fetch Google's discovery document
        discovery_response = requests.get(GOOGLE_DISCOVERY_URL)
        if discovery_response.status_code != 200:
            logger.error(f"Failed to get Google discovery document: {discovery_response.status_code}")
            return jsonify({"error": "Could not connect to Google services"}), 500
            
        google_provider_cfg = discovery_response.json()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
        logger.info(f"Using Google authorization endpoint: {authorization_endpoint}")
        
        # Determine environment for callback URL
        is_local = "localhost" in request.host or "127.0.0.1" in request.host
        logger.info(f"Environment - Host: {request.host}, Is local: {is_local}")
        
        # Set the correct callback URL based on environment
        if is_local:
            # For local development, use this callback URL consistently
            callback_url = "http://localhost:5000/api/auth/callback"
            
            # Debug
            logger.info(f"Using local environment callback URL: {callback_url}")
        else:
            # For production environment (Replit)
            replit_domain = os.environ.get("REPLIT_DEV_DOMAIN", "")
            if replit_domain:
                callback_url = f"https://{replit_domain}/api/auth/callback"
                logger.info(f"Using Replit domain callback URL: {callback_url}")
            else:
                # Fallback to a more reliable URL construction
                host = request.host
                protocol = "https" if not "localhost" in host else "http"
                callback_url = f"{protocol}://{host}/api/auth/callback"
                logger.info(f"Using fallback callback URL: {callback_url}")
            
        logger.info(f"Using callback URL: {callback_url}")
        
        # Prepare the authorization request URI
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=callback_url,
            scope=["openid", "email", "profile"],
        )
        
        logger.info(f"Redirecting to Google: {request_uri}")
        
        # Direct redirect to Google OAuth
        return redirect(request_uri)
    except Exception as e:
        logger.error(f"Error initiating Google OAuth flow: {str(e)}")
        logger.error(f"Error details: {traceback.format_exc()}")
        
        # If this is an API call expecting JSON, return JSON error
        if 'application/json' in request.headers.get('Accept', ''):
            return jsonify({"error": "Failed to initiate login process"}), 500
            
        # Otherwise redirect to frontend with error
        return redirect(f"/login?error={urllib.parse.quote('Failed to initiate login process')}")

@auth_bp.route('/callback', methods=['GET', 'OPTIONS'])
def callback():
    """Handle the Google OAuth callback"""
    try:
        # Log the full request for debugging
        logger.info(f"Callback received: {request.url}")
        
        # Check if Google OAuth is configured
        if not current_app.config['GOOGLE_CLIENT_ID'] or not current_app.config['GOOGLE_CLIENT_SECRET']:
            logger.error("Google OAuth not configured")
            return jsonify({"error": "Google OAuth not configured"}), 500
        
        # Get authorization code from the callback
        code = request.args.get("code")
        if not code:
            logger.error("Authorization code missing")
            return jsonify({"error": "Authorization code missing"}), 400
        
        client = get_google_client()
        
        # Get Google's OAuth 2.0 endpoints
        google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg["token_endpoint"]
        
        # Prepare token request
        is_local = "localhost" in request.host or "127.0.0.1" in request.host
        
        # Debugging
        logger.info(f"Callback - Current host: {request.host}, Is local: {is_local}")
        
        # Simplify token request by using consistent URLs
        if is_local:
            auth_response = request.url
            redirect_url = "http://localhost:5000/api/auth/callback"
        else:
            auth_response = request.url.replace("http://", "https://")
            # For Replit environments
            replit_domain = os.environ.get("REPLIT_DEV_DOMAIN", "")
            if replit_domain:
                redirect_url = f"https://{replit_domain}/api/auth/callback"
            else:
                redirect_url = request.base_url.replace("http://", "https://")
            
        logger.info(f"Using redirect URL for token request: {redirect_url}")
        
        # Prepare and send token request
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=auth_response,
            redirect_url=redirect_url,
            code=code,
        )

        logger.info(f"Token URL: {token_url}")
        logger.info(f"Token request headers: {headers}")
        logger.info(f"Token request body: {body}")
        
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(current_app.config['GOOGLE_CLIENT_ID'], current_app.config['GOOGLE_CLIENT_SECRET']),
        )
        
        # Check token response
        if token_response.status_code != 200:
            logger.error(f"Token request failed: {token_response.status_code} {token_response.text}")
            return jsonify({"error": "Failed to obtain access token from Google"}), 500
            
        # Parse the token response
        token_data = token_response.json()
        client.parse_request_body_response(json.dumps(token_data))
        
        # Get user info from Google
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        
        # Check userinfo response
        if userinfo_response.status_code != 200:
            logger.error(f"Userinfo request failed: {userinfo_response.status_code} {userinfo_response.text}")
            return jsonify({"error": "Failed to obtain user information from Google"}), 500
            
        userinfo = userinfo_response.json()
        logger.info(f"Received user info: {userinfo}")
        
        # Verify user info - email is required
        if not userinfo.get("email"):
            logger.error("Email missing from Google response")
            return jsonify({"error": "Email information not provided by Google"}), 400
            
        # Check if email is verified (if this field exists in response)
        if "email_verified" in userinfo and not userinfo.get("email_verified"):
            logger.error("User email not verified by Google")
            return jsonify({"error": "User email not verified by Google"}), 400
        
        # Get user data
        email = userinfo["email"]
        username = email.split("@")[0]  # Use email prefix as username
        picture = userinfo.get("picture")
        
        try:
            # Find or create user
            user = User.query.filter_by(email=email).first()
            if not user:
                # Try to extract first name and last name
                first_name = userinfo.get("given_name", "")
                last_name = userinfo.get("family_name", "")
                
                # Find a unique username if needed
                base_username = username
                counter = 1
                while User.query.filter_by(username=username).first() is not None:
                    username = f"{base_username}{counter}"
                    counter += 1
                
                # Create new user
                user = User(
                    email=email,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    profile_picture=picture,
                    role="user"  # Ensure role is set
                )
                
                logger.info(f"Creating new user: {email} with username: {username}")
                db.session.add(user)
                db.session.commit()
            
            # Update last login time
            user.last_login = db.func.now()
            db.session.commit()
            
            # Login the user
            login_user(user)
            
        except Exception as db_error:
            logger.error(f"Database error while creating/updating user: {str(db_error)}")
            # Roll back transaction and return error
            db.session.rollback()
            return jsonify({"error": "Error saving user information"}), 500
        
        # Create JWT token
        access_token = create_access_token(identity=str(user.id))
        
        # Determine frontend URL with better detection
        is_local = "localhost" in request.host or "127.0.0.1" in request.host
        
        if is_local:
            # For local development
            frontend_url = "http://localhost:3000"
        else:
            # For production environments
            replit_domain = os.environ.get("REPLIT_DEV_DOMAIN", "")
            if replit_domain:
                frontend_url = f"https://{replit_domain}"
            else:
                # Fallback to request origin or host
                origin = request.headers.get('Origin')
                if origin:
                    frontend_url = origin
                else:
                    frontend_url = f"https://{request.host}"
        
        # Redirect to frontend with token
        redirect_url = f"{frontend_url}/auth/callback?token={access_token}"
        logger.info(f"Redirecting to frontend: {redirect_url}")
        
        # Add CORS headers to the redirect
        response = redirect(redirect_url)
        response.headers['Access-Control-Allow-Origin'] = frontend_url
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    except Exception as e:
        logger.error(f"Error in Google OAuth callback: {str(e)}")
        logger.error(f"Error details: {traceback.format_exc()}")
        # Only return generic error message for security
        
        try:
            # Determine if we need to redirect to frontend with error
            is_local = "localhost" in request.host or "127.0.0.1" in request.host
            
            if is_local:
                frontend_url = "http://localhost:3000"
            else:
                replit_domain = os.environ.get("REPLIT_DEV_DOMAIN", "")
                if replit_domain:
                    frontend_url = f"https://{replit_domain}"
                else:
                    frontend_url = f"https://{request.host}"
            
            # Redirect to frontend login page with error
            error_message = urllib.parse.quote("Authentication failed. Please try again.")
            redirect_url = f"{frontend_url}/login?error={error_message}"
            
            logger.info(f"Redirecting to frontend with error: {redirect_url}")
            return redirect(redirect_url)
        except Exception as redirect_error:
            # If everything fails, return a simple JSON error
            logger.error(f"Error redirecting with error: {str(redirect_error)}")
            return jsonify({
                "error": "Authentication failed. Please try again or contact support.",
                "details": "There was a problem with the authentication process."
            }), 500

@auth_bp.route('/logout', methods=['POST', 'OPTIONS'])
@login_required
def logout():
    """Logout the current user"""
    logout_user()
    return jsonify({"message": "Logout successful"})

@auth_bp.route('/user', methods=['GET', 'OPTIONS'])
@jwt_required_except_options
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

@auth_bp.route('/check', methods=['GET', 'OPTIONS'])
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
                "username": current_user.username,
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "role": current_user.role,
                "profile_picture": current_user.profile_picture,
                "pets_count": current_user.pets.count(),
                "devices_count": current_user.devices.count(),
                "last_login": current_user.last_login.isoformat() if current_user.last_login else None
            },
            "access_token": access_token
        })
    else:
        return jsonify({"authenticated": False})

# Helper function for CORS preflight responses
def handle_options_request():
    """Handle OPTIONS preflight request with CORS headers"""
    response = jsonify({"status": "ok"})
    # Add CORS headers
    response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Max-Age', '86400')  # 24 hours
    return response

# Simple API test endpoint that doesn't require auth
@auth_bp.route('/test', methods=['GET', 'OPTIONS'])
def test_api():
    """Test endpoint to verify API connectivity"""
    # Handle OPTIONS request explicitly for better CORS support
    if request.method == 'OPTIONS':
        return handle_options_request()
        
    from datetime import datetime
    response = jsonify({
        "status": "success",
        "message": "API is operational",
        "timestamp": datetime.utcnow().isoformat(),
        "server_info": {
            "flask_env": os.environ.get('FLASK_ENV', 'production'),
            "python_version": platform.python_version(),
            "hostname": platform.node()
        }
    })
    
    # Log the response for debugging CORS issues
    logger.info(f"Test API Response Headers: {dict(response.headers)}")
    
    return response

# Development/testing only endpoint - should be removed in production
@auth_bp.route('/dev-token', methods=['GET', 'OPTIONS'])
def get_dev_token():
    """Get a development token for testing - NOT FOR PRODUCTION USE"""
    # Handle OPTIONS request explicitly for better CORS support
    if request.method == 'OPTIONS':
        return handle_options_request()
        
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
    
    response = jsonify({
        "message": "Development token generated",
        "user_id": test_user.id,
        "access_token": access_token,
        "token": access_token  # Added for compatibility with test_api.py
    })
    
    # Ensure CORS headers are present for direct access
    origin = request.headers.get('Origin')
    if origin:
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Credentials', 'true')
    
    logger.info(f"Dev Token Response Headers: {dict(response.headers)}")
    
    return response
