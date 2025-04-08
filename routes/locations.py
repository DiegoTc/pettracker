from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db, limiter
from models import Location, Device, Pet
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime, timedelta
from sqlalchemy import desc

locations_bp = Blueprint('locations', __name__)
logger = logging.getLogger(__name__)

@locations_bp.route('/device/<int:device_id>', methods=['GET'])
@jwt_required()
@limiter.limit("120/minute")
def get_device_locations(device_id):
    """Get location history for a specific device"""
    user_id = int(get_jwt_identity())
    
    # Find the device
    device = Device.query.filter_by(id=device_id, user_id=user_id).first()
    if not device:
        return jsonify({"error": "Device not found"}), 404
    
    # Get query parameters for filtering
    limit = request.args.get('limit', default=100, type=int)
    hours = request.args.get('hours', default=24, type=int)
    since = request.args.get('since', type=str)
    
    # Create base query
    query = Location.query.filter_by(device_id=device.id)
    
    # Apply time filter
    if since:
        try:
            since_time = datetime.fromisoformat(since)
            query = query.filter(Location.timestamp >= since_time)
        except ValueError:
            return jsonify({"error": "Invalid 'since' parameter format. Use ISO format."}), 400
    else:
        # Default to last N hours
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        query = query.filter(Location.timestamp >= time_threshold)
    
    # Order by timestamp and limit results
    locations = query.order_by(desc(Location.timestamp)).limit(limit).all()
    
    return jsonify([location.to_dict() for location in locations])

@locations_bp.route('/pet/<int:pet_id>', methods=['GET'])
@jwt_required()
@limiter.limit("120/minute")
def get_pet_locations(pet_id):
    """Get location history for a specific pet"""
    user_id = int(get_jwt_identity())
    
    # Find the pet
    pet = Pet.query.filter_by(id=pet_id, user_id=user_id).first()
    if not pet:
        return jsonify({"error": "Pet not found"}), 404
    
    # Find the pet's device
    device = Device.query.filter_by(pet_id=pet.id).first()
    if not device:
        return jsonify({"error": "No device assigned to this pet"}), 404
    
    # Get query parameters for filtering
    limit = request.args.get('limit', default=100, type=int)
    hours = request.args.get('hours', default=24, type=int)
    since = request.args.get('since', type=str)
    
    # Create base query
    query = Location.query.filter_by(device_id=device.id)
    
    # Apply time filter
    if since:
        try:
            since_time = datetime.fromisoformat(since)
            query = query.filter(Location.timestamp >= since_time)
        except ValueError:
            return jsonify({"error": "Invalid 'since' parameter format. Use ISO format."}), 400
    else:
        # Default to last N hours
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        query = query.filter(Location.timestamp >= time_threshold)
    
    # Order by timestamp and limit results
    locations = query.order_by(desc(Location.timestamp)).limit(limit).all()
    
    return jsonify({
        "pet": pet.to_dict(),
        "device": device.to_dict(),
        "locations": [location.to_dict() for location in locations]
    })

@locations_bp.route('/latest/device/<int:device_id>', methods=['GET'])
@jwt_required()
def get_device_latest_location(device_id):
    """Get the latest location for a specific device"""
    user_id = int(get_jwt_identity())
    
    # Find the device
    device = Device.query.filter_by(id=device_id, user_id=user_id).first()
    if not device:
        return jsonify({"error": "Device not found"}), 404
    
    # Get the latest location
    location = Location.query.filter_by(device_id=device.id).order_by(desc(Location.timestamp)).first()
    
    if not location:
        return jsonify({"error": "No location data available for this device"}), 404
    
    return jsonify({
        "device": device.to_dict(),
        "location": location.to_dict()
    })

@locations_bp.route('/latest/pet/<int:pet_id>', methods=['GET'])
@jwt_required()
def get_pet_latest_location(pet_id):
    """Get the latest location for a specific pet"""
    user_id = int(get_jwt_identity())
    
    # Find the pet
    pet = Pet.query.filter_by(id=pet_id, user_id=user_id).first()
    if not pet:
        return jsonify({"error": "Pet not found"}), 404
    
    # Find the pet's device
    device = Device.query.filter_by(pet_id=pet.id).first()
    if not device:
        return jsonify({"error": "No device assigned to this pet"}), 404
    
    # Get the latest location
    location = Location.query.filter_by(device_id=device.id).order_by(desc(Location.timestamp)).first()
    
    if not location:
        return jsonify({"error": "No location data available for this pet"}), 404
    
    return jsonify({
        "pet": pet.to_dict(),
        "device": device.to_dict(),
        "location": location.to_dict()
    })

@locations_bp.route('/record', methods=['POST'])
def record_location():
    """Record a new location from a device (can be called by the device itself)"""
    # This endpoint is open to allow devices to send location data without authentication
    
    # Get request data
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Validate required fields
    required_fields = ['device_id', 'latitude', 'longitude', 'timestamp']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
    
    # Find the device
    device = Device.query.filter_by(device_id=data['device_id']).first()
    if not device:
        return jsonify({"error": "Device not found"}), 404
    
    # Parse timestamp
    try:
        if isinstance(data['timestamp'], str):
            timestamp = datetime.fromisoformat(data['timestamp'])
        else:
            # Assume Unix timestamp in seconds
            timestamp = datetime.fromtimestamp(data['timestamp'])
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid timestamp format"}), 400
    
    # Create new location record
    location = Location(
        device_id=device.id,
        latitude=data['latitude'],
        longitude=data['longitude'],
        altitude=data.get('altitude'),
        speed=data.get('speed'),
        heading=data.get('heading'),
        timestamp=timestamp,
        accuracy=data.get('accuracy'),
        battery_level=data.get('battery_level', device.battery_level)
    )
    
    # Update device's battery level if provided
    if 'battery_level' in data:
        device.battery_level = data['battery_level']
    
    # Update device's last ping
    device.last_ping = datetime.utcnow()
    
    # Save to database
    try:
        db.session.add(location)
        db.session.commit()
        return jsonify({"message": "Location recorded successfully", "location_id": location.id})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error recording location: {str(e)}")
        return jsonify({"error": "Failed to record location"}), 500

@locations_bp.route('/all-pets-latest', methods=['GET'])
@jwt_required()
def get_all_pets_latest_locations():
    """Get the latest location for all pets belonging to the user"""
    user_id = int(get_jwt_identity())
    
    # Get all pets belonging to the user
    pets = Pet.query.filter_by(user_id=user_id).all()
    
    result = []
    for pet in pets:
        pet_data = pet.to_dict()
        
        # Find the pet's device
        device = Device.query.filter_by(pet_id=pet.id).first()
        if device:
            pet_data['device'] = device.to_dict()
            
            # Get the latest location
            location = Location.query.filter_by(device_id=device.id).order_by(desc(Location.timestamp)).first()
            if location:
                pet_data['location'] = location.to_dict()
        
        result.append(pet_data)
    
    return jsonify(result)

@locations_bp.route('/recent', methods=['GET'])
@jwt_required()
def get_recent_locations():
    """Get recent location updates across all devices belonging to the user"""
    user_id = int(get_jwt_identity())
    
    # Get query parameters
    limit = request.args.get('limit', default=10, type=int)
    hours = request.args.get('hours', default=24, type=int)
    
    # Get all devices belonging to the user
    devices = Device.query.filter_by(user_id=user_id).all()
    
    if not devices:
        return jsonify({
            "recent": [],
            "total_count": 0
        })
    
    # Get device IDs
    device_ids = [device.id for device in devices]
    
    # Time threshold for recent locations
    time_threshold = datetime.utcnow() - timedelta(hours=hours)
    
    # Query for recent locations across all user devices
    recent_locations = (Location.query
                         .filter(Location.device_id.in_(device_ids))
                         .filter(Location.timestamp >= time_threshold)
                         .order_by(desc(Location.timestamp))
                         .limit(limit)
                         .all())
    
    # Get total count of locations in the time period
    total_count = (Location.query
                   .filter(Location.device_id.in_(device_ids))
                   .filter(Location.timestamp >= time_threshold)
                   .count())
    
    return jsonify({
        "recent": [location.to_dict() for location in recent_locations],
        "total_count": total_count
    })

@locations_bp.route('/simulate', methods=['POST'])
def simulate_device_location():
    """
    Simulate a location update from a device
    
    This endpoint is designed for testing purposes to simulate device locations
    without needing to connect through the 808 Protocol server.
    
    Example request body:
    {
        "device_id": "9c96e35f",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "altitude": 10,
        "speed": 0.5,
        "heading": 90,
        "battery_level": 95
    }
    """
    # Get request data
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Validate required fields
    required_fields = ['device_id', 'latitude', 'longitude']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
    
    # Find the device by device_id (allowing partial match to make testing easier)
    device_query = Device.query.filter(Device.device_id.like(f"%{data['device_id']}%"))
    device = device_query.first()
    
    if not device:
        return jsonify({"error": f"Device with ID containing '{data['device_id']}' not found"}), 404
    
    # Create a new location with the current timestamp
    location = Location(
        device_id=device.id,
        latitude=data['latitude'],
        longitude=data['longitude'],
        altitude=data.get('altitude'),
        speed=data.get('speed'),
        heading=data.get('heading'),
        timestamp=datetime.utcnow(),
        accuracy=data.get('accuracy'),
        battery_level=data.get('battery_level', device.battery_level)
    )
    
    # Update device battery level if provided
    if 'battery_level' in data:
        device.battery_level = data['battery_level']
    
    # Update device's last ping
    device.last_ping = datetime.utcnow()
    
    # Save to database
    try:
        db.session.add(location)
        db.session.commit()
        
        logger.info(f"Simulated location recorded for device {device.device_id}: " 
                  f"({data['latitude']}, {data['longitude']})")
        
        return jsonify({
            "message": "Location simulated successfully",
            "location_id": location.id,
            "device": device.to_dict(),
            "location": location.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error recording simulated location: {str(e)}")
        return jsonify({"error": "Failed to record location"}), 500
