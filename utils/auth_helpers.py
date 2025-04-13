import functools
import logging
from flask import request, jsonify, Response
from flask_jwt_extended import jwt_required, verify_jwt_in_request
from utils.error_handlers import handle_error

# Set up logging
logger = logging.getLogger(__name__)

def jwt_required_except_options(fn):
    """Decorator that skips JWT verification for OPTIONS requests but applies it for all others."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        # Log request details for debugging
        route = request.endpoint or 'unknown'
        logger.debug(f"JWT decorator for {route} - Method: {request.method}, Path: {request.path}")
        logger.debug(f"Request headers: {dict(request.headers)}")
        
        if request.method == 'OPTIONS':
            # For OPTIONS requests, return an empty response with appropriate CORS headers
            response = jsonify({"status": "ok"})
            
            # Add CORS headers explicitly to ensure they're present
            origin = request.headers.get('Origin', '*')
            response.headers.add('Access-Control-Allow-Origin', origin)
            response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            response.headers.add('Access-Control-Max-Age', '86400')  # 24 hours
            
            # Log the response headers
            logger.info(f"OPTIONS Response Headers for {route}: {dict(response.headers)}")
            
            return response
        else:
            # For non-OPTIONS requests, verify JWT and then call the function
            try:
                verify_jwt_in_request()
                result = fn(*args, **kwargs)
                
                # If the result is a Response object, ensure it has CORS headers
                if isinstance(result, Response):
                    origin = request.headers.get('Origin')
                    if origin:
                        result.headers.add('Access-Control-Allow-Origin', origin)
                        result.headers.add('Access-Control-Allow-Credentials', 'true')
                        logger.debug(f"Added CORS headers to response for {route}")
                
                return result
                
            except Exception as e:
                logger.error(f"JWT verification failed for {route}: {str(e)}")
                # Return a standardized sanitized error response
                return handle_error(e, status_code=401, 
                                   user_message="Authentication required. Please log in to access this resource.")
    return wrapper