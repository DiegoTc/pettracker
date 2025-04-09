#!/usr/bin/env python3
"""
Demonstrate MQTT messages that would be sent by our adapter
"""

import json
import datetime
import random

# Simulate device data
device_id = "270225613904"
latitude = 37.7749
longitude = -122.4194
altitude = 10.5
speed = 2.3
heading = 90.0
battery_level = 85.2
activity_level = 65.8
temperature = 37.4
timestamp = datetime.datetime.now().isoformat()

# Create a location message
location_message = {
    'device_id': device_id,
    'timestamp': timestamp,
    'latitude': latitude,
    'longitude': longitude,
    'altitude': altitude,
    'speed': speed,
    'heading': heading,
    'battery_level': battery_level,
    'activity_level': activity_level,
    'temperature': temperature,
    'status': {
        'acc_on': False,
        'gps_positioned': True,
        'latitude_type': 'North',
        'longitude_type': 'West',
        'moving': True
    }
}

# Create a status message
status_message = {
    'device_id': device_id,
    'timestamp': timestamp,
    'message_type': 'heartbeat'
}

# Create a registration message
registration_message = {
    'device_id': device_id,
    'timestamp': timestamp,
    'message_type': 'registration',
    'registration_info': {
        'province_id': 0,
        'city_id': 0,
        'manufacturer_id': 'PETTR',
        'terminal_model': 'PT100',
        'terminal_id': f'SIM{random.randint(1000, 9999)}',
        'license_plate_color': 0
    }
}

# Print the messages with their topics
print("\n--- MQTT Messages Demo ---\n")

print(f"Topic: devices/{device_id}/location")
print("Payload:")
print(json.dumps(location_message, indent=2))
print("\n---\n")

print(f"Topic: devices/{device_id}/status")
print("Payload (Heartbeat):")
print(json.dumps(status_message, indent=2))
print("\n---\n")

print(f"Topic: devices/{device_id}/status")
print("Payload (Registration):")
print(json.dumps(registration_message, indent=2))

print("\n--- End of Demo ---\n")