from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db, limiter
from models import Pet
from flask_jwt_extended import get_jwt_identity
from utils.auth_helpers import jwt_required_except_options
import logging
from datetime import datetime

pets_bp = Blueprint('pets', __name__)
logger = logging.getLogger(__name__)

@pets_bp.route('/', methods=['GET', 'OPTIONS'])
@jwt_required_except_options
@limiter.limit("60/minute")
def get_pets():
    """Get pets based on user role"""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    
    # Admin can see all pets
    if user.is_admin:
        pets = Pet.query.all()
    else:
        # Regular users see only their pets
        pets = Pet.query.filter_by(user_id=user_id).all()
    
    # Convert user_id to int since JWT identity is stored as string
    user_id = int(user_id)
    
    # Get optional query parameters for filtering
    pet_type = request.args.get('type')
    
    # Create base query
    query = Pet.query.filter_by(user_id=user_id)
    
    # Apply filters if provided
    if pet_type:
        query = query.filter_by(pet_type=pet_type)
    
    # Execute query and return results
    pets = query.all()
    return jsonify([pet.to_dict() for pet in pets])

@pets_bp.route('/<int:pet_id>', methods=['GET', 'OPTIONS'])
@jwt_required_except_options
def get_pet(pet_id):
    """Get a specific pet by id"""
    user_id = int(get_jwt_identity())
    
    pet = Pet.query.filter_by(id=pet_id, user_id=user_id).first()
    if not pet:
        return jsonify({"error": "Pet not found"}), 404
    
    return jsonify(pet.to_dict())

@pets_bp.route('/', methods=['POST', 'OPTIONS'])
@jwt_required_except_options
@limiter.limit("20/minute")
def create_pet():
    """Create a new pet"""
    user_id = int(get_jwt_identity())
    
    # Get request data
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Validate required fields
    if 'name' not in data or 'pet_type' not in data:
        return jsonify({"error": "Name and pet_type are required"}), 400
    
    # Parse birthdate if provided
    birthdate = None
    if 'birthdate' in data and data['birthdate']:
        try:
            birthdate = datetime.strptime(data['birthdate'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid birthdate format. Use YYYY-MM-DD."}), 400
    
    # Create new pet
    pet = Pet(
        name=data['name'],
        pet_type=data['pet_type'],
        breed=data.get('breed'),
        color=data.get('color'),
        birthdate=birthdate,
        weight=data.get('weight'),
        description=data.get('description'),
        image_url=data.get('image_url'),
        user_id=user_id
    )
    
    # Save to database
    try:
        db.session.add(pet)
        db.session.commit()
        logger.info(f"Created pet {pet.id} for user {user_id}")
        return jsonify(pet.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating pet: {str(e)}")
        return jsonify({"error": "Failed to create pet"}), 500

@pets_bp.route('/<int:pet_id>', methods=['PUT', 'OPTIONS'])
@jwt_required_except_options
def update_pet(pet_id):
    """Update an existing pet"""
    user_id = int(get_jwt_identity())
    
    # Find the pet
    pet = Pet.query.filter_by(id=pet_id, user_id=user_id).first()
    if not pet:
        return jsonify({"error": "Pet not found"}), 404
    
    # Get request data
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Update fields
    if 'name' in data:
        pet.name = data['name']
    if 'pet_type' in data:
        pet.pet_type = data['pet_type']
    if 'breed' in data:
        pet.breed = data['breed']
    if 'color' in data:
        pet.color = data['color']
    if 'birthdate' in data:
        if data['birthdate']:
            try:
                pet.birthdate = datetime.strptime(data['birthdate'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"error": "Invalid birthdate format. Use YYYY-MM-DD."}), 400
        else:
            pet.birthdate = None
    if 'weight' in data:
        pet.weight = data['weight']
    if 'description' in data:
        pet.description = data['description']
    if 'image_url' in data:
        pet.image_url = data['image_url']
    
    # Update timestamp
    pet.updated_at = datetime.utcnow()
    
    # Save to database
    try:
        db.session.commit()
        logger.info(f"Updated pet {pet_id}")
        return jsonify(pet.to_dict())
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating pet: {str(e)}")
        return jsonify({"error": "Failed to update pet"}), 500

@pets_bp.route('/<int:pet_id>', methods=['DELETE', 'OPTIONS'])
@jwt_required_except_options
def delete_pet(pet_id):
    """Delete a pet"""
    user_id = int(get_jwt_identity())
    
    # Find the pet
    pet = Pet.query.filter_by(id=pet_id, user_id=user_id).first()
    if not pet:
        return jsonify({"error": "Pet not found"}), 404
    
    # Delete the pet
    try:
        db.session.delete(pet)
        db.session.commit()
        logger.info(f"Deleted pet {pet_id}")
        return jsonify({"message": "Pet deleted successfully"})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting pet: {str(e)}")
        return jsonify({"error": "Failed to delete pet"}), 500
