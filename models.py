from app import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
import uuid

class User(UserMixin, db.Model):
    """User model for authentication and profile information"""
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    profile_picture = db.Column(db.String(256))
    role = db.Column(db.String(20), default='user', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_moderator(self):
        return self.role == 'moderator'
    
    # Relationships
    pets = db.relationship('Pet', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    devices = db.relationship('Device', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    @hybrid_property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

class Pet(db.Model):
    """Pet model containing pet information"""
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    pet_type = db.Column(db.String(32), nullable=False)
    breed = db.Column(db.String(64))
    color = db.Column(db.String(32))
    birthdate = db.Column(db.Date, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    devices = db.relationship('Device', backref='pet', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Pet {self.name}>'
    
    def to_dict(self):
        """Convert object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'pet_type': self.pet_type,
            'breed': self.breed,
            'color': self.color,
            'birthdate': self.birthdate.isoformat() if self.birthdate else None,
            'weight': self.weight,
            'description': self.description,
            'image_url': self.image_url,
            'owner_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

class Device(db.Model):
    """Device model for tracking devices"""
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(64))
    device_type = db.Column(db.String(32))
    serial_number = db.Column(db.String(64), unique=True)
    imei = db.Column(db.String(32), unique=True)
    firmware_version = db.Column(db.String(32))
    battery_level = db.Column(db.Float, default=100.0)
    is_active = db.Column(db.Boolean, default=True)
    last_ping = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=True)
    
    # Relationships
    locations = db.relationship('Location', backref='device', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Device {self.device_id}>'
    
    @staticmethod
    def generate_device_id():
        """Generate a unique device ID"""
        return str(uuid.uuid4())
    
    def to_dict(self):
        """Convert object to dictionary"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'name': self.name,
            'device_type': self.device_type,
            'serial_number': self.serial_number,
            'imei': self.imei,
            'firmware_version': self.firmware_version,
            'battery_level': self.battery_level,
            'is_active': self.is_active,
            'last_ping': self.last_ping.isoformat() if self.last_ping else None,
            'user_id': self.user_id,
            'pet_id': self.pet_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Location(db.Model):
    """Location model for device location history"""
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    altitude = db.Column(db.Float)
    speed = db.Column(db.Float)
    heading = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    accuracy = db.Column(db.Float)
    battery_level = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # NOTE: Pet-specific data fields are not stored in the database
    # They are published to MQTT topics for real-time use
    # These fields were causing database errors because the table doesn't have these columns
    # activity_level = db.Column(db.Float)  # 0-100% representing pet's activity
    # health_flags = db.Column(db.Integer)  # Bit flags for various health indicators
    # temperature = db.Column(db.Float)     # Pet body temperature in Celsius
    
    # Foreign Keys
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    
    def __repr__(self):
        return f'<Location ({self.latitude}, {self.longitude}) @ {self.timestamp}>'
    
    def to_dict(self):
        """Convert object to dictionary"""
        data = {
            'id': self.id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
            'speed': self.speed,
            'heading': self.heading,
            'timestamp': self.timestamp.isoformat(),
            'accuracy': self.accuracy,
            'battery_level': self.battery_level,
            'device_id': self.device_id,
            'created_at': self.created_at.isoformat()
        }
        
        # NOTE: Pet-specific data (activity_level, health_flags, temperature) 
        # has been removed as it's no longer stored in the database
        # Instead, it's published to MQTT topics for real-time use by clients
            
        return data
