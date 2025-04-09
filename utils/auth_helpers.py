import functools
from flask import request, jsonify
from flask_jwt_extended import jwt_required, verify_jwt_in_request

def jwt_required_except_options(fn):
    """Decorator that skips JWT verification for OPTIONS requests but applies it for all others."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if request.method == 'OPTIONS':
            # For OPTIONS requests, return an empty response with appropriate CORS headers
            # Return a proper OPTIONS response with CORS headers
            response = jsonify({})
            response.status_code = 200
            # The flask-cors extension will add the required headers
            return response
        else:
            # For non-OPTIONS requests, verify JWT and then call the function
            verify_jwt_in_request()
            return fn(*args, **kwargs)
    return wrapper