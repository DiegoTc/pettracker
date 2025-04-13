"""
Secure error handling utilities for the pet tracker application.
These utilities ensure that sensitive error information is never
exposed to clients while maintaining proper logging for debugging.
"""
import logging
import traceback
import uuid
from flask import jsonify, current_app, request
from sqlalchemy.exc import SQLAlchemyError, DBAPIError

# Configure logger
logger = logging.getLogger(__name__)

# Error types that should receive specific handling
DB_ERRORS = (SQLAlchemyError, DBAPIError)


def handle_error(error, status_code=500, user_message=None, log_prefix=""):
    """
    Centralized error handler that logs detailed error information but
    returns a sanitized response to the client.
    
    Args:
        error: The exception that was raised
        status_code: HTTP status code to return (default: 500)
        user_message: Message to show to the user (default: generic error message)
        log_prefix: Optional prefix for log entries (e.g., request ID)
    
    Returns:
        A JSON response with a sanitized error message
    """
    # Generate a unique error ID for tracing
    error_id = str(uuid.uuid4())
    
    # Determine appropriate user-facing message
    if user_message is None:
        if status_code == 404:
            user_message = "The requested resource was not found."
        elif status_code == 403:
            user_message = "You don't have permission to access this resource."
        elif status_code == 401:
            user_message = "Authentication is required to access this resource."
        else:
            user_message = "An unexpected error occurred. Our team has been notified."
    
    # Format log prefix
    prefix = f"[{log_prefix}] " if log_prefix else ""
    
    # Log the detailed error with traceback for debugging
    logger.error(
        f"{prefix}Error ID: {error_id} - "
        f"Error Type: {type(error).__name__} - "
        f"Message: {str(error)}"
    )
    
    # Log detailed traceback at debug level
    logger.debug(
        f"{prefix}Error ID: {error_id} - Traceback:\n"
        f"{traceback.format_exc()}"
    )
    
    # Log additional context in development mode
    if current_app.debug:
        # Log request information for debugging
        logger.debug(
            f"{prefix}Error ID: {error_id} - Request Context:\n"
            f"URL: {request.url}\n"
            f"Method: {request.method}\n"
            f"Headers: {sanitize_headers(dict(request.headers))}\n"
            f"Args: {sanitize_data(dict(request.args))}"
        )
    
    # Return a sanitized error response to the client
    return jsonify({
        "error": {
            "status": status_code,
            "message": user_message,
            "error_id": error_id  # Include the error ID for support reference
        }
    }), status_code


def sanitize_headers(headers):
    """
    Remove sensitive information from headers for logging
    """
    if not headers:
        return {}
    
    sanitized = headers.copy()
    sensitive_keys = ['authorization', 'cookie', 'x-csrf-token']
    
    for key in headers:
        if key.lower() in sensitive_keys:
            sanitized[key] = "[REDACTED]"
    
    return sanitized


def sanitize_data(data):
    """
    Remove potentially sensitive information from request data for logging
    """
    if not data:
        return {}
    
    sanitized = data.copy()
    sensitive_keys = ['password', 'token', 'api_key', 'secret', 'auth', 'key']
    
    for key in data:
        for sensitive_key in sensitive_keys:
            if sensitive_key in key.lower():
                sanitized[key] = "[REDACTED]"
    
    return sanitized


def handle_database_error(error, operation=None, user_message=None):
    """
    Specifically handle database errors with appropriate logging
    but sanitized user responses
    
    Args:
        error: The database exception that was raised
        operation: Description of the database operation (e.g., "creating user")
        user_message: Optional custom message to the user
    
    Returns:
        A JSON response with a sanitized error message
    """
    if user_message is None:
        user_message = "A database error occurred. Please try again later."
    
    # Create a detailed log message for debugging
    log_message = f"Database error"
    if operation:
        log_message += f" during {operation}"
    
    # Log the error with full details for server-side debugging
    error_id = str(uuid.uuid4())
    
    logger.error(
        f"Error ID: {error_id} - {log_message}: "
        f"Type: {type(error).__name__}, "
        f"Error: {str(error)}"
    )
    
    # Add specific error type context
    if hasattr(error, 'orig') and error.orig is not None:
        logger.error(f"Error ID: {error_id} - Original error: {error.orig}")
    
    # Log SQL details at debug level only
    if hasattr(error, 'statement') and error.statement is not None:
        logger.debug(f"Error ID: {error_id} - SQL: {error.statement}")
    
    # Return sanitized response
    return jsonify({
        "error": {
            "status": 500,
            "message": user_message,
            "error_id": error_id  # Include ID for reference in support tickets
        }
    }), 500


def register_error_handlers(app):
    """
    Register global error handlers with the Flask application
    """
    @app.errorhandler(404)
    def not_found_error(error):
        return handle_error(error, 404)

    @app.errorhandler(500)
    def internal_error(error):
        return handle_error(error, 500)
    
    @app.errorhandler(Exception)
    def unhandled_exception(error):
        return handle_error(error, 500)
    
    @app.errorhandler(SQLAlchemyError)
    def handle_sqlalchemy_error(error):
        return handle_database_error(error)