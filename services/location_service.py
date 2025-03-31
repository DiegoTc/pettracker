import logging
from app import db
from models import Location, Device, Pet
from datetime import datetime, timedelta
from sqlalchemy import desc, func
import json
import math

logger = logging.getLogger(__name__)

class LocationService:
    """Service for processing and analyzing location data"""
    
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """
        Calculate the distance between two points using the Haversine formula
        Returns distance in meters
        """
        # Earth's radius in meters
        R = 6371000
        
        # Convert latitude and longitude from degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Differences in coordinates
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine formula
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance
    
    @staticmethod
    def get_device_location_history(device_id, hours=24, limit=100):
        """Get location history for a device for the last N hours"""
        try:
            device = Device.query.get(device_id)
            if not device:
                return None
            
            time_threshold = datetime.utcnow() - timedelta(hours=hours)
            
            locations = Location.query.filter_by(device_id=device_id) \
                .filter(Location.timestamp >= time_threshold) \
                .order_by(desc(Location.timestamp)) \
                .limit(limit) \
                .all()
            
            return locations
        except Exception as e:
            logger.error(f"Error getting device location history: {str(e)}", exc_info=True)
            return None
    
    @staticmethod
    def get_pet_location_history(pet_id, hours=24, limit=100):
        """Get location history for a pet for the last N hours"""
        try:
            pet = Pet.query.get(pet_id)
            if not pet:
                return None
            
            # Find the pet's device
            device = Device.query.filter_by(pet_id=pet_id).first()
            if not device:
                return None
            
            return LocationService.get_device_location_history(device.id, hours, limit)
        except Exception as e:
            logger.error(f"Error getting pet location history: {str(e)}", exc_info=True)
            return None
    
    @staticmethod
    def get_latest_location(device_id):
        """Get the latest location for a device"""
        try:
            location = Location.query.filter_by(device_id=device_id) \
                .order_by(desc(Location.timestamp)) \
                .first()
            return location
        except Exception as e:
            logger.error(f"Error getting latest location: {str(e)}", exc_info=True)
            return None
    
    @staticmethod
    def calculate_distance_traveled(device_id, hours=24):
        """Calculate the total distance traveled by a device in the last N hours"""
        try:
            locations = LocationService.get_device_location_history(device_id, hours)
            if not locations or len(locations) < 2:
                return 0
            
            # Sort locations by timestamp (oldest first)
            locations.sort(key=lambda loc: loc.timestamp)
            
            # Calculate total distance
            total_distance = 0
            for i in range(1, len(locations)):
                distance = LocationService.calculate_distance(
                    locations[i-1].latitude, locations[i-1].longitude,
                    locations[i].latitude, locations[i].longitude
                )
                total_distance += distance
            
            return total_distance
        except Exception as e:
            logger.error(f"Error calculating distance traveled: {str(e)}", exc_info=True)
            return 0
    
    @staticmethod
    def check_geofence(lat, lon, center_lat, center_lon, radius):
        """
        Check if a location is within a circular geofence
        Returns True if inside, False if outside
        """
        distance = LocationService.calculate_distance(lat, lon, center_lat, center_lon)
        return distance <= radius
    
    @staticmethod
    def get_activity_stats(device_id, days=7):
        """Calculate activity statistics for a device over a period of days"""
        try:
            # Define time period
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            # Get daily distance traveled
            daily_stats = []
            current_day = start_time.date()
            end_date = end_time.date()
            
            while current_day <= end_date:
                next_day = current_day + timedelta(days=1)
                
                # Get locations for this day
                day_locations = Location.query.filter_by(device_id=device_id) \
                    .filter(Location.timestamp >= current_day) \
                    .filter(Location.timestamp < next_day) \
                    .order_by(Location.timestamp) \
                    .all()
                
                # Calculate distance for this day
                day_distance = 0
                for i in range(1, len(day_locations)):
                    distance = LocationService.calculate_distance(
                        day_locations[i-1].latitude, day_locations[i-1].longitude,
                        day_locations[i].latitude, day_locations[i].longitude
                    )
                    day_distance += distance
                
                # Get average speed for this day
                avg_speed = 0
                if day_locations:
                    speeds = [loc.speed for loc in day_locations if loc.speed is not None]
                    if speeds:
                        avg_speed = sum(speeds) / len(speeds)
                
                daily_stats.append({
                    "date": current_day.isoformat(),
                    "distance": day_distance,
                    "avg_speed": avg_speed,
                    "locations_count": len(day_locations)
                })
                
                current_day = next_day
            
            return daily_stats
        except Exception as e:
            logger.error(f"Error calculating activity stats: {str(e)}", exc_info=True)
            return []
