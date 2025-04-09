from flask import Blueprint, send_from_directory, render_template, jsonify, current_app
import os

design_proposals_bp = Blueprint('design_proposals', __name__)

@design_proposals_bp.route('/design-proposals/')
def index():
    """Serve the design proposals index page"""
    return send_from_directory('frontend/design-proposals', 'index.html')

@design_proposals_bp.route('/design-proposals/<path:filename>')
def files(filename):
    """Serve files from the design proposals directory"""
    return send_from_directory('frontend/design-proposals', filename)