from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from models import User

def admin_required(fn):
    """Decorator to ensure the user has admin privileges"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()

        # Get user and check role
        user = User.query.get(int(user_id))
        if not user or not user.is_admin:
            return jsonify({"error": "Admin privileges required"}), 403

        return fn(*args, **kwargs)
    return wrapper

def moderator_required(fn):
    """Decorator to ensure the user has at least moderator privileges"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()

        # Get user and check role
        user = User.query.get(int(user_id))
        if not user or not (user.is_admin or user.is_moderator):
            return jsonify({"error": "Moderator privileges required"}), 403

        return fn(*args, **kwargs)
    return wrapper

def api_key_required(fn):
    """Decorator to ensure a valid API key is provided"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({"error": "API key is required"}), 401

        # Validate API key
        # Implement your API key validation logic here

        return fn(*args, **kwargs)
    return wrapper

def validate_json(schema):
    """
    Decorator to validate JSON request data against a schema
    
    Example schema:
    {
        "name": {"type": "string", "required": True},
        "age": {"type": "integer", "required": False}
    }
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Get request data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No JSON data provided"}), 400
            
            # Validate against schema
            errors = []
            for field, rules in schema.items():
                # Check required fields
                if rules.get("required", False) and field not in data:
                    errors.append(f"Field '{field}' is required")
                    continue
                
                # Skip validation if field is not present and not required
                if field not in data:
                    continue
                
                # Validate field type
                if "type" in rules:
                    if rules["type"] == "string" and not isinstance(data[field], str):
                        errors.append(f"Field '{field}' must be a string")
                    elif rules["type"] == "integer" and not isinstance(data[field], int):
                        errors.append(f"Field '{field}' must be an integer")
                    elif rules["type"] == "number" and not isinstance(data[field], (int, float)):
                        errors.append(f"Field '{field}' must be a number")
                    elif rules["type"] == "boolean" and not isinstance(data[field], bool):
                        errors.append(f"Field '{field}' must be a boolean")
                    elif rules["type"] == "array" and not isinstance(data[field], list):
                        errors.append(f"Field '{field}' must be an array")
                    elif rules["type"] == "object" and not isinstance(data[field], dict):
                        errors.append(f"Field '{field}' must be an object")
                
                # Validate minimum/maximum for numeric fields
                if isinstance(data[field], (int, float)):
                    if "minimum" in rules and data[field] < rules["minimum"]:
                        errors.append(f"Field '{field}' must be at least {rules['minimum']}")
                    if "maximum" in rules and data[field] > rules["maximum"]:
                        errors.append(f"Field '{field}' must be at most {rules['maximum']}")
                
                # Validate min/max length for strings
                if isinstance(data[field], str):
                    if "minLength" in rules and len(data[field]) < rules["minLength"]:
                        errors.append(f"Field '{field}' must be at least {rules['minLength']} characters long")
                    if "maxLength" in rules and len(data[field]) > rules["maxLength"]:
                        errors.append(f"Field '{field}' must be at most {rules['maxLength']} characters long")
                
                # Validate enum values
                if "enum" in rules and data[field] not in rules["enum"]:
                    enum_str = ", ".join([str(v) for v in rules["enum"]])
                    errors.append(f"Field '{field}' must be one of: {enum_str}")
            
            if errors:
                return jsonify({"error": "Validation failed", "details": errors}), 400
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator