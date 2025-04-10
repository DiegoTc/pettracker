from flask import Blueprint, send_from_directory, current_app, send_file, redirect
import os

frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/', defaults={'path': ''})
@frontend_bp.route('/<path:path>')
def serve_frontend(path):
    """Serve the built Vue.js frontend"""
    # Path to the static directory
    static_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
    
    # No need to check for conflicting routes anymore since we moved the API root
    
    # Set index.html path
    index_path = os.path.join(static_folder, 'index.html')
    
    # If path is empty or doesn't have an extension, serve index.html
    if not path or '.' not in path:
        if os.path.exists(index_path):
            return send_file(index_path)
        else:
            current_app.logger.error(f"Index file not found at {index_path}")
            return {"error": "Frontend not built"}, 500
    
    # Otherwise, try to serve the static file
    file_path = os.path.join(static_folder, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_file(file_path)
    else:
        # If file not found, serve index.html for client-side routing
        if os.path.exists(index_path):
            return send_file(index_path)
        else:
            current_app.logger.error(f"Index file not found at {index_path}")
            return {"error": "Frontend not built"}, 500