#!/usr/bin/env python3
"""
API Testing Tool

This script demonstrates the API by creating sample data and testing
the device location simulation.

Usage:
    python test_api.py --jwt <your_jwt_token>
"""

import argparse
import json
import logging
import random
import sys
import time
from datetime import datetime
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('api_tester')

class APITester:
    """Test the Pet Tracking API"""
    
    def __init__(self, base_url='http://localhost:5000/api', jwt_token=None):
        self.base_url = base_url
        self.jwt_token = jwt_token
        self.session = requests.Session()
        if jwt_token:
            self.session.headers.update({
                'Authorization': f'Bearer {jwt_token}'
            })
        
        logger.info(f"API tester initialized with base URL: {base_url}")
    
    def get_user_info(self):
        """Get current user information"""
        response = self.session.get(f"{self.base_url}/auth/user")
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to get user info: {response.status_code} - {response.text}")
            return None
    
    def create_pet(self, name, pet_type, breed=None, color=None):
        """Create a new pet"""
        data = {
            "name": name,
            "pet_type": pet_type
        }
        
        if breed:
            data["breed"] = breed
        if color:
            data["color"] = color
            
        response = self.session.post(f"{self.base_url}/pets", json=data)
        if response.status_code == 201:
            return response.json()
        else:
            logger.error(f"Failed to create pet: {response.status_code} - {response.text}")
            return None
    
    def create_device(self, name, device_type="GPS Tracker"):
        """Register a new device"""
        data = {
            "name": name,
            "device_type": device_type
        }
        
        response = self.session.post(f"{self.base_url}/devices", json=data)
        if response.status_code == 201:
            return response.json()
        else:
            logger.error(f"Failed to create device: {response.status_code} - {response.text}")
            return None
    
    def assign_device_to_pet(self, device_id, pet_id):
        """Assign a device to a pet"""
        response = self.session.post(f"{self.base_url}/devices/{device_id}/assign/{pet_id}")
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to assign device to pet: {response.status_code} - {response.text}")
            return None
    
    def simulate_location(self, device_id, lat, lon, speed=None, heading=None, battery_level=None):
        """Simulate a device location update"""
        data = {
            "device_id": device_id,
            "latitude": lat,
            "longitude": lon
        }
        
        if speed is not None:
            data["speed"] = speed
        if heading is not None:
            data["heading"] = heading
        if battery_level is not None:
            data["battery_level"] = battery_level
            
        response = self.session.post(f"{self.base_url}/locations/simulate", json=data)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to simulate location: {response.status_code} - {response.text}")
            return None
    
    def simulate_trip(self, device_id, start_lat, start_lon, steps=10, interval=5):
        """Simulate a trip with multiple location updates"""
        lat = start_lat
        lon = start_lon
        battery = 100.0
        
        for i in range(steps):
            # Move in a small random direction
            lat += random.uniform(-0.001, 0.001)
            lon += random.uniform(-0.001, 0.001)
            
            # Decrease battery level slightly
            battery -= random.uniform(0, 0.5)
            
            # Generate random speed and heading
            speed = random.uniform(0, 5.0)
            heading = random.uniform(0, 360.0)
            
            logger.info(f"Simulating location {i+1}/{steps}: lat={lat:.6f}, lon={lon:.6f}")
            result = self.simulate_location(
                device_id, lat, lon, 
                speed=speed, 
                heading=heading,
                battery_level=battery
            )
            
            if result:
                logger.info(f"Location recorded successfully")
            else:
                logger.error(f"Failed to record location {i+1}")
                
            if i < steps - 1:
                time.sleep(interval)
    
    def get_pet_locations(self, pet_id):
        """Get location history for a pet"""
        response = self.session.get(f"{self.base_url}/locations/pet/{pet_id}")
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to get pet locations: {response.status_code} - {response.text}")
            return None
    
    def run_demo(self):
        """Run a full demo of the API"""
        # Get user info
        user = self.get_user_info()
        if not user:
            logger.error("Cannot continue demo without valid user")
            return False
        
        logger.info(f"Logged in as user: {user.get('username')} ({user.get('email')})")
        
        # Create a pet
        pet_name = f"Buddy {datetime.now().strftime('%H%M%S')}"
        pet = self.create_pet(pet_name, "Dog", breed="Golden Retriever", color="Golden")
        if not pet:
            logger.error("Cannot continue demo without created pet")
            return False
            
        logger.info(f"Created pet: {pet['name']} (ID: {pet['id']})")
        
        # Create a device
        device_name = f"GPS Collar {datetime.now().strftime('%H%M%S')}"
        device = self.create_device(device_name)
        if not device:
            logger.error("Cannot continue demo without created device")
            return False
            
        logger.info(f"Created device: {device['name']} (ID: {device['id']}, Device ID: {device['device_id']})")
        
        # Assign device to pet
        assignment = self.assign_device_to_pet(device['id'], pet['id'])
        if not assignment:
            logger.error("Failed to assign device to pet")
            return False
            
        logger.info(f"Assigned device {device['device_id']} to pet {pet['name']}")
        
        # Simulate a trip
        logger.info(f"Simulating trip for device {device['device_id']}...")
        self.simulate_trip(device['device_id'], 37.7749, -122.4194, steps=5, interval=2)
        
        # Get location history
        locations = self.get_pet_locations(pet['id'])
        if locations:
            logger.info(f"Retrieved {len(locations)} location records for pet {pet['name']}")
            for location in locations[:3]:  # Show the first 3
                logger.info(f"  {location['timestamp']}: ({location['latitude']:.6f}, {location['longitude']:.6f})")
            if len(locations) > 3:
                logger.info(f"  ... and {len(locations) - 3} more locations")
        
        logger.info("Demo completed successfully")
        return True

def get_dev_token():
    """Get a development token for testing"""
    try:
        response = requests.get("http://localhost:5000/api/auth/dev-token")
        if response.status_code == 200:
            return response.json().get("token")
        else:
            logger.error(f"Failed to get dev token: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error getting dev token: {str(e)}")
        return None

def main():
    """Main function to run the API test"""
    parser = argparse.ArgumentParser(description='Pet Tracking API Tester')
    parser.add_argument('--jwt', help='JWT token for authorization')
    parser.add_argument('--url', default='http://localhost:5000/api', help='Base URL of the API')
    parser.add_argument('--dev', action='store_true', help='Use development token')
    
    args = parser.parse_args()
    
    # Get token
    jwt_token = None
    if args.jwt:
        jwt_token = args.jwt
    elif args.dev:
        logger.info("Getting development token...")
        jwt_token = get_dev_token()
        if not jwt_token:
            logger.error("Could not get development token")
            return 1
        
    if not jwt_token:
        logger.error("No JWT token provided. Use --jwt or --dev option")
        return 1
    
    # Run tester
    tester = APITester(args.url, jwt_token)
    success = tester.run_demo()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())