import functools
from flask import request, jsonify
from flask_jwt_extended import jwt_required, verify_jwt_in_request

def jwt_required_except_options(fn):
    """Decorator that skips JWT verification for OPTIONS requests but applies it for all others."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if request.method == 'OPTIONS':
            # For OPTIONS requests, return an empty response with appropriate CORS headers
            # These headers will be added by the CORS extension
            return '', 200
        else:
            # For non-OPTIONS requests, verify JWT and then call the function
            verify_jwt_in_request()
            return fn(*args, **kwargs)
    return wrapper