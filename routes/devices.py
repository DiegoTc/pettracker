from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db, limiter
from models import Device, Pet
from flask_jwt_extended import get_jwt_identity
from utils.auth_helpers import jwt_required_except_options
from utils.error_handlers import handle_error, handle_database_error
import logging
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

devices_bp = Blueprint('devices', __name__)
logger = logging.getLogger(__name__)

@devices_bp.route('/', methods=['GET', 'OPTIONS'])
@jwt_required_except_options
@limiter.limit("60/minute")
def get_devices():
    """Get all devices belonging to the current user"""
    try:
        logger.info("get_devices() called")
        user_id = int(get_jwt_identity())
        logger.info(f"User ID from JWT: {user_id}")
        
        # Get optional query parameters for filtering
        pet_id = request.args.get('pet_id', type=int)
        is_active = request.args.get('is_active')
        
        # Create base query
        query = Device.query.filter_by(user_id=user_id)
        
        # Apply filters if provided
        if pet_id:
            query = query.filter_by(pet_id=pet_id)
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            query = query.filter_by(is_active=is_active_bool)
        
        # Execute query and return results
        devices = query.all()
        logger.info(f"Found {len(devices)} devices for user {user_id}")
        return jsonify([device.to_dict() for device in devices])
    except SQLAlchemyError as db_error:
        # Handle database errors specifically and securely
        return handle_database_error(db_error, operation="retrieving devices", 
                                    user_message="Unable to retrieve your devices. Please try again later.")
    except Exception as e:
        # Handle general errors with sanitized messages
        return handle_error(e, status_code=500,
                           user_message="An error occurred while retrieving your devices.")

@devices_bp.route('/<int:device_id>', methods=['GET', 'OPTIONS'])
@devices_bp.route('/<int:device_id>/', methods=['GET', 'OPTIONS'])  # Add route with trailing slash
@jwt_required_except_options
def get_device(device_id):
    """Get a specific device by id"""
    try:
        user_id = int(get_jwt_identity())
        
        device = Device.query.filter_by(id=device_id, user_id=user_id).first()
        if not device:
            return jsonify({"error": "Device not found"}), 404
        
        return jsonify(device.to_dict())
    except SQLAlchemyError as db_error:
        return handle_database_error(db_error, operation=f"retrieving device {device_id}", 
                                    user_message="Unable to retrieve device details. Please try again later.")
    except Exception as e:
        return handle_error(e, status_code=500,
                           user_message="An error occurred while retrieving device details.")

@devices_bp.route('/', methods=['POST', 'OPTIONS'])
@jwt_required_except_options
@limiter.limit("10/minute")
def create_device():
    """Register a new device"""
    user_id = int(get_jwt_identity())
    
    # Get request data
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Validate required fields
    if 'name' not in data:
        return jsonify({"error": "Device name is required"}), 400
    
    # Handle pet_id data type conversion and validation
    pet_id = data.get('pet_id')
    # Convert empty string to None
    if pet_id == '':
        pet_id = None
    # Validate pet_id if it's provided and not None
    elif pet_id is not None:
        try:
            # Convert to integer if it's a string
            if isinstance(pet_id, str):
                pet_id = int(pet_id)
            # Verify that the pet exists and belongs to the user
            pet = Pet.query.filter_by(id=pet_id, user_id=user_id).first()
            if not pet:
                return jsonify({"error": "Pet not found"}), 404
        except ValueError:
            # Handle case where pet_id can't be converted to an integer
            return jsonify({"error": "Invalid pet ID format"}), 400
    
    # Generate device ID if not provided
    device_id = data.get('device_id', Device.generate_device_id())
    
    # Check if device with the same ID already exists
    existing_device = Device.query.filter_by(device_id=device_id).first()
    if existing_device:
        return jsonify({"error": "Device ID already registered"}), 409
    
    # Sanitize string fields before database insertion
    serial_number = data.get('serial_number')
    if serial_number == '':
        serial_number = None
        
    imei = data.get('imei')
    if imei == '':
        imei = None
    
    # Create new device
    device = Device(
        device_id=device_id,
        name=data['name'],
        device_type=data.get('device_type', '808_tracker'),
        serial_number=serial_number,
        imei=imei,
        firmware_version=data.get('firmware_version', '1.0'),
        battery_level=data.get('battery_level', 100.0),
        is_active=data.get('is_active', True),
        user_id=user_id,
        pet_id=pet_id
    )
    
    # Save to database
    try:
        db.session.add(device)
        db.session.commit()
        logger.info(f"Created device {device.id} for user {user_id}")
        return jsonify(device.to_dict()), 201
    except SQLAlchemyError as db_error:
        db.session.rollback()
        # Capture database constraint violations, schema errors, etc.
        return handle_database_error(db_error, operation="creating device", 
                                    user_message="Unable to create device. Please try again later.")
    except Exception as e:
        db.session.rollback()
        return handle_error(e, status_code=500,
                           user_message="An error occurred while creating the device.")

@devices_bp.route('/<int:device_id>', methods=['PUT', 'OPTIONS'])
@devices_bp.route('/<int:device_id>/', methods=['PUT', 'OPTIONS'])  # Add route with trailing slash
@jwt_required_except_options
def update_device(device_id):
    """Update an existing device"""
    user_id = int(get_jwt_identity())
    
    # Find the device
    device = Device.query.filter_by(id=device_id, user_id=user_id).first()
    if not device:
        return jsonify({"error": "Device not found"}), 404
    
    # Get request data
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Handle pet_id data type conversion and validation
    pet_id = data.get('pet_id')
    
    # Convert empty string to None
    if pet_id == '':
        device.pet_id = None
    # Handle explicit unassignment
    elif pet_id == 0 or pet_id == '0':
        device.pet_id = None
    # Validate pet_id if it's provided and not None
    elif pet_id is not None:
        try:
            # Convert to integer if it's a string
            if isinstance(pet_id, str):
                pet_id = int(pet_id)
            # Verify that the pet exists and belongs to the user
            pet = Pet.query.filter_by(id=pet_id, user_id=user_id).first()
            if not pet:
                return jsonify({"error": "Pet not found"}), 404
            device.pet_id = pet_id
        except ValueError:
            # Handle case where pet_id can't be converted to an integer
            return jsonify({"error": "Invalid pet ID format"}), 400
    
    # Update fields
    if 'name' in data:
        device.name = data['name']
    if 'device_type' in data:
        device.device_type = data['device_type']
    if 'serial_number' in data:
        # Convert empty string to None
        serial_number = data['serial_number']
        if serial_number == '':
            device.serial_number = None
        else:
            device.serial_number = serial_number
    if 'imei' in data:
        # Convert empty string to None
        imei = data['imei']
        if imei == '':
            device.imei = None
        else:
            device.imei = imei
    if 'firmware_version' in data:
        device.firmware_version = data['firmware_version']
    if 'battery_level' in data:
        device.battery_level = data['battery_level']
    if 'is_active' in data:
        device.is_active = data['is_active']
    
    # Update timestamp
    device.updated_at = datetime.utcnow()
    
    # Save to database
    try:
        db.session.commit()
        logger.info(f"Updated device {device_id}")
        return jsonify(device.to_dict())
    except SQLAlchemyError as db_error:
        db.session.rollback()
        return handle_database_error(db_error, operation=f"updating device {device_id}", 
                                   user_message="Unable to update device. Please try again later.")
    except Exception as e:
        db.session.rollback()
        return handle_error(e, status_code=500,
                          user_message="An error occurred while updating the device.")

@devices_bp.route('/<int:device_id>/', methods=['DELETE', 'OPTIONS'])
@jwt_required_except_options
def delete_device(device_id):
    """Delete a device"""
    user_id = int(get_jwt_identity())
    
    logger.info(f"Delete request for device ID: {device_id} by user: {user_id}")
    
    # Find the device
    device = Device.query.filter_by(id=device_id, user_id=user_id).first()
    if not device:
        logger.warning(f"Device not found: {device_id} for user {user_id}")
        return jsonify({"error": "Device not found"}), 404
    
    # Check for locations and log them before deletion
    location_count = device.locations.count()
    logger.info(f"Device {device_id} has {location_count} location records that will be deleted")
    
    # Delete the device
    try:
        # First, explicitly delete locations associated with the device
        if location_count > 0:
            from sqlalchemy import text
            # Use parameterized query to prevent SQL injection
            db.session.execute(text("DELETE FROM location WHERE device_id = :device_id"), 
                              {"device_id": device.id})
            db.session.commit()
            logger.info(f"Deleted {location_count} location records for device {device_id}")
        
        # Now delete the device
        db.session.delete(device)
        db.session.commit()
        logger.info(f"Successfully deleted device {device_id}")
        return jsonify({"message": "Device deleted successfully"})
    except SQLAlchemyError as db_error:
        db.session.rollback()
        # Use centralized error handling to avoid leaking database details
        return handle_database_error(db_error, operation=f"deleting device {device_id}", 
                                    user_message="Unable to delete device. Please try again later.")
    except Exception as e:
        db.session.rollback()
        return handle_error(e, status_code=500,
                           user_message="An error occurred while deleting the device.")

@devices_bp.route('/<string:device_identifier>/ping', methods=['POST'])
def device_ping(device_identifier):
    """Record a ping from a device (can be called by the device itself)"""
    # This endpoint is open to allow devices to ping without authentication
    
    # Find device by device_id or imei
    device = Device.query.filter(
        (Device.device_id == device_identifier) | 
        (Device.imei == device_identifier)
    ).first()
    
    if not device:
        return jsonify({"error": "Device not found"}), 404
    
    # Update last ping time
    device.last_ping = datetime.utcnow()
    
    # Update battery level if provided
    data = request.get_json() or {}
    if 'battery_level' in data:
        device.battery_level = data['battery_level']
    
    # Save to database
    try:
        db.session.commit()
        return jsonify({"message": "Ping recorded successfully"})
    except SQLAlchemyError as db_error:
        db.session.rollback()
        # Use centralized error handling for database errors
        return handle_database_error(db_error, operation=f"recording ping for device {device_identifier}", 
                                    user_message="Unable to record device ping. Please try again later.")
    except Exception as e:
        db.session.rollback()
        # Use centralized error handling for general errors
        return handle_error(e, status_code=500,
                           user_message="An error occurred while recording the device ping.")

@devices_bp.route('/<int:device_id>/assign/<int:pet_id>', methods=['POST', 'OPTIONS'])
@jwt_required_except_options
def assign_to_pet(device_id, pet_id):
    """Assign a device to a pet"""
    user_id = int(get_jwt_identity())
    
    # Find the device
    device = Device.query.filter_by(id=device_id, user_id=user_id).first()
    if not device:
        return jsonify({"error": "Device not found"}), 404
    
    # Find the pet
    pet = Pet.query.filter_by(id=pet_id, user_id=user_id).first()
    if not pet:
        return jsonify({"error": "Pet not found"}), 404
    
    # Assign device to pet
    device.pet_id = pet.id
    
    # Save to database
    try:
        db.session.commit()
        return jsonify({
            "message": f"Device {device.name} assigned to pet {pet.name}",
            "device": device.to_dict()
        })
    except SQLAlchemyError as db_error:
        db.session.rollback()
        return handle_database_error(db_error, operation=f"assigning device {device_id} to pet {pet_id}", 
                                   user_message="Unable to assign device to pet. Please try again later.")
    except Exception as e:
        db.session.rollback()
        return handle_error(e, status_code=500,
                          user_message="An error occurred while assigning the device to the pet.")

@devices_bp.route('/<int:device_id>/unassign', methods=['POST', 'OPTIONS'])
@jwt_required_except_options
def unassign_from_pet(device_id):
    """Unassign a device from a pet"""
    user_id = int(get_jwt_identity())
    
    # Find the device
    device = Device.query.filter_by(id=device_id, user_id=user_id).first()
    if not device:
        return jsonify({"error": "Device not found"}), 404
    
    # Check if device is assigned to a pet
    if device.pet_id is None:
        return jsonify({"error": "Device is not assigned to any pet"}), 400
    
    # Unassign device from pet
    device.pet_id = None
    
    # Save to database
    try:
        db.session.commit()
        return jsonify({
            "message": "Device unassigned successfully",
            "device": device.to_dict()
        })
    except SQLAlchemyError as db_error:
        db.session.rollback()
        return handle_database_error(db_error, operation=f"unassigning device {device_id}", 
                                   user_message="Unable to unassign device. Please try again later.")
    except Exception as e:
        db.session.rollback()
        return handle_error(e, status_code=500,
                          user_message="An error occurred while unassigning the device.")
