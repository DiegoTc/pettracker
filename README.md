# Pet Tracking System API

A comprehensive backend API for multi-platform pet tracking applications, supporting web, Android, and iOS clients.

## Features

- **User Authentication**: Secure login with Google OAuth
- **Pet Management**: Add, update, view, and delete pets
- **Device Management**: Register, configure, and assign tracking devices to pets
- **Location Tracking**: Record and retrieve real-time pet locations
- **Protocol Support**: Support for the 808 GPS protocol used by many tracking devices

## System Architecture

The system consists of:

1. **RESTful API**: A Flask-based backend API for client applications
2. **Database**: PostgreSQL for storing user, pet, device, and location data
3. **Protocol Server**: A TCP server that listens for 808 protocol messages from tracking devices

## API Endpoints

### Authentication

- `POST /api/auth/login`: Initiate Google OAuth login
- `GET /api/auth/callback`: OAuth callback endpoint
- `GET /api/auth/user`: Get current user information
- `GET /api/auth/logout`: Log out the current user

### Pets

- `GET /api/pets`: Get all pets for the current user
- `GET /api/pets/<pet_id>`: Get a specific pet
- `POST /api/pets`: Create a new pet
- `PUT /api/pets/<pet_id>`: Update a pet
- `DELETE /api/pets/<pet_id>`: Delete a pet

### Devices

- `GET /api/devices`: Get all devices for the current user
- `GET /api/devices/<device_id>`: Get a specific device
- `POST /api/devices`: Register a new device
- `PUT /api/devices/<device_id>`: Update a device
- `DELETE /api/devices/<device_id>`: Delete a device
- `POST /api/devices/<device_id>/assign/<pet_id>`: Assign a device to a pet
- `POST /api/devices/<device_id>/unassign`: Unassign a device from a pet
- `POST /api/devices/ping/<device_identifier>`: Record a device ping

### Locations

- `GET /api/locations/device/<device_id>`: Get location history for a device
- `GET /api/locations/pet/<pet_id>`: Get location history for a pet
- `GET /api/locations/latest/device/<device_id>`: Get the latest location for a device
- `GET /api/locations/latest/pet/<pet_id>`: Get the latest location for a pet
- `POST /api/locations/record`: Record a new location from a device
- `GET /api/locations/all-pets-latest`: Get the latest location for all pets

## Testing Without Physical Hardware

The system includes tools for testing without physical tracking devices:

### 1. Location Simulation API

Use the simulation API endpoint to send location updates:

```bash
# Simulate a location update
curl -X POST http://localhost:5000/api/locations/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "your-device-id",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "altitude": 10,
    "speed": 0.5,
    "heading": 90,
    "battery_level": 95
  }'
```

### 2. Device Simulator Tool

The project includes a command-line device simulator that connects to the 808 protocol server:

```bash
# Run the simulator with a registered device
python tools/device_simulator.py \
  --device-id your-device-id \
  --imei your-device-imei \
  --interval 10
```

Options:
- `--device-id`: The device ID (must be registered in the system)
- `--imei`: The IMEI number to use in messages
- `--host`: Server hostname (default: localhost)
- `--port`: Server port (default: 8080)
- `--interval`: Seconds between location updates (default: 30)
- `--duration`: Duration in seconds (default: run continuously)

## Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up the database: `flask db upgrade`
4. Configure environment variables:
   - `DATABASE_URL`: PostgreSQL connection string
   - `GOOGLE_OAUTH_CLIENT_ID`: Google OAuth client ID
   - `GOOGLE_OAUTH_CLIENT_SECRET`: Google OAuth client secret
   - `SESSION_SECRET`: Secret key for session encryption
5. Start the server: `python main.py`

## Testing the API

You can test the API using curl or any API testing tool like Postman:

```bash
# Get all pets
curl -X GET http://localhost:5000/api/pets \
  -H "Authorization: Bearer your-jwt-token"

# Create a new pet
curl -X POST http://localhost:5000/api/pets \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "name": "Fluffy",
    "pet_type": "Dog",
    "breed": "Golden Retriever"
  }'
```