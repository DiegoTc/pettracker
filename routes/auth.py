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
import uuid
from oauthlib.oauth2 import WebApplicationClient
import logging
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from utils.auth_helpers import jwt_required_except_options
from sqlalchemy.exc import IntegrityError
# Needed for local development only - allows OAuth over HTTP
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Create blueprint
auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

# Set Google OAuth discovery URL
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

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
    # Handle OPTIONS request explicitly for better CORS support
    if request.method == 'OPTIONS':
        return handle_options_request()
        
    # Track the request flow for debugging
    request_id = uuid.uuid4()
    logger.info(f"[{request_id}] OAuth callback started, received URL: {request.url}")
    
    # Configuration validation at the start
    try:
        # Primary try block for the entire auth flow
        # Validate OAuth configuration first
        if not current_app.config['GOOGLE_CLIENT_ID'] or not current_app.config['GOOGLE_CLIENT_SECRET']:
            logger.error(f"[{request_id}] Google OAuth not configured - missing client ID or secret")
            return safe_error_redirect(
                error_message="Authentication service not properly configured", 
                log_message="OAuth credentials missing", 
                request_id=request_id
            )
        
        # Get authorization code from the callback
        code = request.args.get("code")
        if not code:
            logger.error(f"[{request_id}] Authorization code missing from callback")
            return safe_error_redirect(
                error_message="Invalid authentication response", 
                log_message="No authorization code in callback", 
                request_id=request_id
            )
        
        logger.info(f"[{request_id}] Authorization code received successfully")
        
        # Initialize OAuth client
        try:
            client = get_google_client()
        except Exception as client_error:
            logger.error(f"[{request_id}] Failed to initialize OAuth client: {str(client_error)}")
            return safe_error_redirect(
                error_message="Authentication setup error", 
                log_message="OAuth client initialization failed", 
                request_id=request_id
            )
        
        # 1. FETCH OAUTH CONFIGURATION
        try:
            logger.info(f"[{request_id}] Fetching Google OAuth configuration")
            discovery_response = requests.get(GOOGLE_DISCOVERY_URL, timeout=10)
            if discovery_response.status_code != 200:
                logger.error(f"[{request_id}] Failed to get Google discovery document: {discovery_response.status_code}")
                return safe_error_redirect(
                    error_message="Could not connect to authentication service",
                    log_message=f"Discovery document fetch failed with status {discovery_response.status_code}",
                    request_id=request_id
                )
                
            google_provider_cfg = discovery_response.json()
            token_endpoint = google_provider_cfg.get("token_endpoint")
            
            if not token_endpoint:
                logger.error(f"[{request_id}] Token endpoint missing from discovery document")
                return safe_error_redirect(
                    error_message="Authentication service configuration error",
                    log_message="Token endpoint missing from discovery document",
                    request_id=request_id
                )
        except requests.RequestException as req_error:
            logger.error(f"[{request_id}] Request error fetching discovery document: {str(req_error)}")
            return safe_error_redirect(
                error_message="Network error connecting to authentication service",
                log_message=f"Discovery request failed: {str(req_error)}",
                request_id=request_id
            )
        
        # 2. DETERMINE CORRECT REDIRECT URL
        # This is critical - must match exactly what was registered with Google
        frontend_url = get_frontend_url(request)
        redirect_url = get_auth_redirect_url(request)
        
        logger.info(f"[{request_id}] Environment detection - Frontend URL: {frontend_url}, Auth Redirect URL: {redirect_url}")
        
        # 3. EXCHANGE CODE FOR TOKEN
        try:
            logger.info(f"[{request_id}] Exchanging authorization code for token")
            
            # Prepare the token request
            auth_response = request.url
            if request.headers.get('X-Forwarded-Proto') == 'https' and auth_response.startswith('http:'):
                auth_response = auth_response.replace('http:', 'https:', 1)
                logger.info(f"[{request_id}] Using secure auth response URL: {auth_response}")
                
            token_url, headers, body = client.prepare_token_request(
                token_endpoint,
                authorization_response=auth_response,
                redirect_url=redirect_url,
                code=code,
            )
            
            # Sensitive information, log with care (only in development)
            if current_app.config.get('DEBUG', False):
                logger.debug(f"[{request_id}] Token request details - URL: {token_url}")
                logger.debug(f"[{request_id}] Token request headers: {sanitize_headers(headers)}")
                # Avoid logging body which may contain sensitive info
            
            # Send the token request to Google
            token_response = requests.post(
                token_url,
                headers=headers,
                data=body,
                auth=(current_app.config['GOOGLE_CLIENT_ID'], current_app.config['GOOGLE_CLIENT_SECRET']),
                timeout=10
            )
            
            # Check token response
            if token_response.status_code != 200:
                logger.error(f"[{request_id}] Token request failed: {token_response.status_code}")
                
                # More detailed logging for debugging, but don't expose to user
                if current_app.config.get('DEBUG', False):
                    logger.debug(f"[{request_id}] Token error response: {token_response.text}")
                    
                return safe_error_redirect(
                    error_message="Failed to complete authentication", 
                    log_message=f"Token request failed with status {token_response.status_code}", 
                    request_id=request_id
                )
                
            # Parse the token response
            token_data = token_response.json()
            client.parse_request_body_response(json.dumps(token_data))
            logger.info(f"[{request_id}] Token obtained successfully")
            
        except Exception as token_error:
            logger.error(f"[{request_id}] Error obtaining token: {str(token_error)}")
            return safe_error_redirect(
                error_message="Authentication process failed", 
                log_message=f"Token exchange error: {str(token_error)}", 
                request_id=request_id
            )
        
        # 4. GET USER INFO
        try:
            logger.info(f"[{request_id}] Fetching user information from Google")
            userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
            uri, headers, body = client.add_token(userinfo_endpoint)
            userinfo_response = requests.get(uri, headers=headers, data=body, timeout=10)
            
            # Check userinfo response
            if userinfo_response.status_code != 200:
                logger.error(f"[{request_id}] Userinfo request failed: {userinfo_response.status_code}")
                return safe_error_redirect(
                    error_message="Could not retrieve user information", 
                    log_message=f"Userinfo request failed with status {userinfo_response.status_code}", 
                    request_id=request_id
                )
                
            userinfo = userinfo_response.json()
            
            # Verify required user info exists
            if not userinfo.get("email"):
                logger.error(f"[{request_id}] Email missing from Google response")
                return safe_error_redirect(
                    error_message="Email information not provided", 
                    log_message="No email in userinfo response", 
                    request_id=request_id
                )
                
            # Check if email is verified (if this field exists in response)
            if "email_verified" in userinfo and not userinfo.get("email_verified"):
                logger.error(f"[{request_id}] User email not verified by Google")
                return safe_error_redirect(
                    error_message="Email not verified", 
                    log_message="User email not verified in userinfo response", 
                    request_id=request_id
                )
            
            # Extract user data
            email = userinfo["email"]
            username = email.split("@")[0]  # Use email prefix as username
            picture = userinfo.get("picture")
            first_name = userinfo.get("given_name", "")
            last_name = userinfo.get("family_name", "")
            
            logger.info(f"[{request_id}] User info obtained successfully for email: {mask_email(email)}")
            
        except Exception as userinfo_error:
            logger.error(f"[{request_id}] Error obtaining user information: {str(userinfo_error)}")
            return safe_error_redirect(
                error_message="Error retrieving user profile", 
                log_message=f"Userinfo error: {str(userinfo_error)}", 
                request_id=request_id
            )
        
        # 5. CREATE OR UPDATE USER IN DATABASE
        try:
            logger.info(f"[{request_id}] Creating or updating user in database")
            # Find or create user
            user = User.query.filter_by(email=email).first()
            
            if not user:
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
                    role="user"
                )
                
                logger.info(f"[{request_id}] Creating new user for email: {mask_email(email)}")
                db.session.add(user)
                db.session.commit()
            else:
                # Update existing user information
                user.profile_picture = picture or user.profile_picture
                user.first_name = first_name or user.first_name
                user.last_name = last_name or user.last_name
                logger.info(f"[{request_id}] Updating existing user for email: {mask_email(email)}")
            
            # Update last login time
            user.last_login = db.func.now()
            db.session.commit()
            
            # Login the user using Flask-Login
            login_user(user)
            logger.info(f"[{request_id}] User logged in successfully: ID {user.id}")
            
        except IntegrityError as integrity_error:
            # Handle database integrity errors specifically
            db.session.rollback()
            logger.error(f"[{request_id}] Database integrity error: {str(integrity_error)}")
            return safe_error_redirect(
                error_message="Account creation failed", 
                log_message=f"Database integrity error: {str(integrity_error)}", 
                request_id=request_id
            )
        except Exception as db_error:
            # Handle other database errors
            db.session.rollback()
            logger.error(f"[{request_id}] Database error: {str(db_error)}")
            return safe_error_redirect(
                error_message="Account processing error", 
                log_message=f"Database error: {str(db_error)}", 
                request_id=request_id
            )
        
        # 6. CREATE JWT TOKEN AND REDIRECT
        try:
            # Create JWT token with the user ID
            access_token = create_access_token(identity=str(user.id))
            
            # Redirect to frontend with token
            callback_url = f"{frontend_url}/auth/callback?token={access_token}"
            logger.info(f"[{request_id}] Authentication successful, redirecting to: {callback_url}")
            
            # Return redirect with CORS headers
            response = redirect(callback_url)
            response.headers['Access-Control-Allow-Origin'] = frontend_url
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response
            
        except Exception as redirect_error:
            logger.error(f"[{request_id}] Error creating JWT token or redirect: {str(redirect_error)}")
            return safe_error_redirect(
                error_message="Authentication succeeded but login failed", 
                log_message=f"JWT/Redirect error: {str(redirect_error)}", 
                request_id=request_id
            )
    
    except Exception as e:
        # Catch-all for any unhandled exceptions
        logger.error(f"[{request_id}] Unhandled error in OAuth callback: {str(e)}")
        logger.error(f"[{request_id}] Error details: {traceback.format_exc()}")
        return safe_error_redirect(
            error_message="Authentication process failed", 
            log_message=f"Unhandled error: {str(e)}", 
            request_id=request_id
        )


# Helper functions for the callback handler

def safe_error_redirect(error_message="Authentication failed", log_message=None, request_id=None):
    """Create a safe redirect to the frontend with an error message"""
    try:
        # Log the detailed error for troubleshooting
        if log_message:
            logger.error(f"[{request_id}] {log_message}")
        
        # Get frontend URL based on environment
        frontend_url = get_frontend_url(request)
        
        # Create error URL with safely encoded message
        encoded_error = urllib.parse.quote(error_message)
        redirect_url = f"{frontend_url}/login?error={encoded_error}"
        
        logger.info(f"[{request_id}] Redirecting with error: {redirect_url}")
        
        # Return the redirect with appropriate CORS headers
        response = redirect(redirect_url)
        response.headers['Access-Control-Allow-Origin'] = frontend_url
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    except Exception as redirect_error:
        # If redirect fails, return a simple JSON error
        logger.error(f"[{request_id}] Error creating error redirect: {str(redirect_error)}")
        return jsonify({
            "error": "Authentication failed",
            "message": "Please try again or contact support"
        }), 500


def get_frontend_url(request):
    """Determine the frontend URL based on the environment"""
    is_local = "localhost" in request.host or "127.0.0.1" in request.host
    
    if is_local:
        # For local development
        return "http://localhost:3000"
    
    # For production environments
    replit_domain = os.environ.get("REPLIT_DEV_DOMAIN", "")
    if replit_domain:
        return f"https://{replit_domain}"
    
    # Fallback to origin header or host
    origin = request.headers.get('Origin')
    if origin:
        return origin
    
    # Last resort fallback
    return f"https://{request.host}"


def get_auth_redirect_url(request):
    """Get the correct redirect URL for OAuth authentication"""
    is_local = "localhost" in request.host or "127.0.0.1" in request.host
    
    if is_local:
        # For local development, use the standard localhost URL
        return "http://localhost:5000/api/auth/callback"
    
    # For Replit or production environments
    replit_domain = os.environ.get("REPLIT_DEV_DOMAIN", "")
    if replit_domain:
        return f"https://{replit_domain}/api/auth/callback"
    
    # Use the base URL from the request (default to HTTPS)
    base_url = request.base_url
    if base_url.startswith('http:') and not is_local:
        base_url = base_url.replace('http:', 'https:', 1)
    
    return base_url


def sanitize_headers(headers):
    """Remove sensitive information from headers for logging"""
    if not headers:
        return {}
    
    sanitized = headers.copy()
    sensitive_keys = ['authorization', 'cookie', 'x-csrf-token']
    
    for key in headers:
        if key.lower() in sensitive_keys:
            sanitized[key] = "[REDACTED]"
    
    return sanitized


def mask_email(email):
    """Mask email address for logging to protect user privacy"""
    if not email or '@' not in email:
        return "[INVALID_EMAIL]"
    
    username, domain = email.split('@', 1)
    
    if len(username) <= 2:
        masked_username = username[0] + "*"
    else:
        masked_username = username[0] + "*" * (len(username) - 2) + username[-1]
    
    return f"{masked_username}@{domain}"

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
