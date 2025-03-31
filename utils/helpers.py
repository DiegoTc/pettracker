import json
import logging
import random
import string
from flask import current_app
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def generate_random_string(length=10):
    """Generate a random string of fixed length"""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def format_datetime(dt):
    """Format datetime object to ISO format string"""
    if dt is None:
        return None
    return dt.isoformat()

def parse_datetime(date_str):
    """Parse an ISO format date string to datetime object"""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        logger.warning(f"Failed to parse datetime: {date_str}")
        return None

def is_valid_latitude(lat):
    """Check if latitude is valid"""
    try:
        lat_float = float(lat)
        return -90 <= lat_float <= 90
    except (ValueError, TypeError):
        return False

def is_valid_longitude(lon):
    """Check if longitude is valid"""
    try:
        lon_float = float(lon)
        return -180 <= lon_float <= 180
    except (ValueError, TypeError):
        return False

def calculate_time_difference(dt1, dt2=None):
    """Calculate the time difference between two datetime objects in minutes"""
    if dt2 is None:
        dt2 = datetime.utcnow()
    
    if dt1 is None:
        return None
    
    delta = dt2 - dt1
    return delta.total_seconds() / 60

def format_timedelta(td):
    """Format timedelta to a human-readable string"""
    if td is None:
        return "N/A"
    
    total_seconds = int(td.total_seconds())
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def get_battery_status(level):
    """Get battery status based on level percentage"""
    if level is None:
        return "Unknown"
    
    if level >= 75:
        return "Good"
    elif level >= 25:
        return "Average"
    else:
        return "Low"

def format_distance(meters, system="metric"):
    """Format distance in meters to human-readable format"""
    if system == "imperial":
        # Convert to miles
        miles = meters / 1609.34
        if miles >= 10:
            return f"{miles:.1f} mi"
        elif miles >= 0.1:
            return f"{miles:.2f} mi"
        else:
            # Convert to feet
            feet = meters * 3.28084
            return f"{feet:.0f} ft"
    else:
        # Metric system
        if meters >= 1000:
            return f"{meters/1000:.2f} km"
        else:
            return f"{meters:.0f} m"

def format_speed(speed, system="metric"):
    """Format speed in m/s to km/h or mph"""
    if speed is None:
        return "N/A"
    
    if system == "imperial":
        # Convert to mph
        mph = speed * 2.23694
        return f"{mph:.1f} mph"
    else:
        # Convert to km/h
        kmh = speed * 3.6
        return f"{kmh:.1f} km/h"
