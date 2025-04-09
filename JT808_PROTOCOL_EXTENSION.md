# JT/T 808 Protocol Extension for Pet Tracking

## Overview

This document describes the customized JT/T 808 protocol extensions for pet tracking used in our system. The standard JT/T 808 protocol has been extended with additional data fields tailored for pet monitoring.

## Protocol Data Flow

The JT/T 808 protocol data flows through our system as follows:

1. GPS tracking devices connect to our TCP server (port 808 or 8080 in development)
2. The protocol server parses incoming binary messages according to JT/T 808 specification
3. Basic location data (coordinates, altitude, speed, etc.) is stored in the database
4. **Pet-specific extension data** is published to MQTT topics for real-time use by clients

## Pet-Specific Data Fields

The following custom data fields have been added to the standard protocol for pet tracking purposes:

| ID    | Name           | Description                              | Format           | Unit     |
|-------|----------------|------------------------------------------|------------------|----------|
| 0x31  | Activity Level | Pet activity level                       | 1-byte integer   | 0-100%   |
| 0x32  | Health Flags   | Bit flags for various health indicators  | 2-byte integer   | Bitfield |
| 0x33  | Temperature    | Pet body temperature                     | 2-byte signed    | 0.1°C    |

### Health Flags Bitfield

The health flags field (0x32) encodes several health indicators as individual bits:

- Bit 0: Temperature warning (1=warning, 0=normal)
- Bit 1: Inactivity warning (1=warning, 0=normal)
- Bit 2: Abnormal movement (1=detected, 0=normal)
- Bit 3: Potential distress (1=detected, 0=normal)
- Bits 4-15: Reserved for future use

## MQTT Topics

Pet-specific data is published to the following MQTT topics:

- `devices/{device_id}/pet_data` - Contains all pet-specific data from protocol extensions

The payload is a JSON object containing:
```json
{
  "device_id": "12345",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "timestamp": "2025-04-09T03:45:35.123456",
  "battery_level": 85.5,
  "activity_level": 72,
  "health_flags": {
    "temperature_warning": false,
    "inactivity_warning": false,
    "abnormal_movement": false,
    "potential_distress": false
  },
  "temperature": 38.1
}
```

## Implementation Notes

- The pet-specific data fields are **not stored in the database** to maintain compatibility with the standard schema
- Instead, they are published to MQTT topics for real-time consumption by frontend applications
- This approach provides maximum flexibility for handling pet-specific data without database schema changes
- Applications can subscribe to these MQTT topics to provide real-time monitoring of pet health and activity

## Testing with JT808 Simulator

The system includes a simulator for testing the pet-specific protocol extensions:

```bash
# Start the simulator with the JT/T 808 protocol
python tools/jt808_simulator.py --device-id "PETTRACKER123" --include-pet-data

# Subscribe to MQTT topics to see pet-specific data
python tools/mqtt_subscriber.py --topic "devices/+"
```