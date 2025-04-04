# Pet Tracking System

A comprehensive multiplatform pet tracking platform that supports Google authentication, device tracking via 808 protocol, and provides a robust backend API for cross-platform pet monitoring.

## Features

- **Google OAuth Authentication**: Secure user login and management
- **Pet Management**: Create, update, view, and delete pets
- **Device Management**: Register GPS trackers and assign them to pets
- **Location Tracking**: Real-time tracking using the 808 protocol
- **RESTful API**: Backend support for web, Android, and iOS clients
- **Interactive Map**: Visualize pet locations in real-time
- **Device Simulator**: Test without physical hardware

## System Architecture

The system consists of several components:

1. **Backend API**: Flask application providing RESTful endpoints
2. **Protocol808 Service**: TCP server for communicating with GPS devices
3. **Device Simulator**: Tool for simulating GPS device data
4. **Web Frontend**: Simple interface for managing pets and devices

## Local Development Setup (Step-by-Step)

### Prerequisites

- Python 3.10 or higher
- PostgreSQL database
- Google Cloud Platform account (for OAuth)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/pet-tracking-system.git
cd pet-tracking-system
```

### 2. Create Virtual Environment and Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install all required packages
pip install email-validator Flask Flask-Cors Flask-JWT-Extended Flask-Limiter Flask-Login Flask-SQLAlchemy gunicorn oauthlib psycopg2-binary requests SQLAlchemy python-dotenv
```

Required packages:
- email-validator
- Flask
- Flask-Cors
- Flask-JWT-Extended
- Flask-Limiter
- Flask-Login
- Flask-SQLAlchemy
- gunicorn
- oauthlib
- psycopg2-binary
- requests
- SQLAlchemy
- python-dotenv

### 3. Set Up PostgreSQL Database

```bash
# Create database
createdb pet_tracker

# Alternative with psql
psql
CREATE DATABASE pet_tracker;
\q
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```
# Database configuration
DATABASE_URL=postgresql://username:password@localhost/pet_tracker

# Google OAuth credentials (required for login)
GOOGLE_OAUTH_CLIENT_ID=your_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret_here

# Session security
SESSION_SECRET=generate_a_secure_random_key_here

# 808 Protocol server port (optional)
PROTOCOL_808_PORT=8080
```

### 5. Initialize the Database

```bash
# Run directly with:
flask db upgrade

# Or if that doesn't work, try with Python explicitly:
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 6. Start the Application

```bash
# Using gunicorn (recommended for production-like environment)
gunicorn --bind 0.0.0.0:5000 --reload main:app

# Or run directly with Python
python main.py
```

The application will be available at http://localhost:5000

## Google OAuth Setup

To enable Google authentication, you need to create OAuth credentials:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Credentials"
4. Click "Create Credentials" > "OAuth client ID"
5. Select "Web application" as the application type
6. Add your domain to the "Authorized JavaScript origins"
   - For local development: `http://localhost:5000`
7. Add the callback URL to "Authorized redirect URIs"
   - For local development: `http://localhost:5000/api/auth/callback`
8. Click "Create" and note your Client ID and Client Secret
9. Update your `.env` file with these credentials

## Testing Without Physical Hardware

### Option 1: Running the 808 Protocol Server and Device Simulator

For the most realistic testing experience, run the Protocol Server and Device Simulator:

1. **Start the application normally** (this will automatically start the 808 Protocol Server)

2. **Register a device through the web interface**
   - Go to http://localhost:5000 in your browser
   - Login with Google
   - Create a pet
   - Register a device
   - Note the device ID (shown in the device details)

3. **Run the device simulator in a separate terminal**

```bash
# Activate your virtual environment if needed
source venv/bin/activate

# Run the simulator
python tools/device_simulator.py --device-id your_device_id_here --interval 5
```

Additional options:
- `--duration 300`: Run for 5 minutes then exit
- `--latitude 37.7749 --longitude -122.4194`: Set starting position
- `--imei 123456789012345`: Set device IMEI (not required for testing)

## Local Testing Without Google OAuth

During development, you may want to test the API without setting up Google OAuth credentials. The system provides a development token endpoint for this purpose.

### Option 1: Using the Development Token Endpoint

The application includes a special endpoint that generates a JWT token for testing:

```bash
# Get a development token
curl -X GET http://localhost:5000/api/auth/dev-token
```

This will:
1. Create a test user with email "test@example.com" if it doesn't exist
2. Generate a JWT token for this user
3. Return the token that you can use to authenticate API requests

### Option 2: Using the API Test Tool

For a quick demonstration of the API with automatic authentication:

```bash
# Get a development token and run a simple test flow
python tools/test_api.py --dev
```

This will:
1. Automatically get a development token
2. Create a test pet
3. Register a device
4. Assign the device to the pet
5. Simulate location updates
6. Retrieve and display the location history

### Option 3: Manual API Testing with curl

```bash
# Step 1: Get a development JWT token
TOKEN=$(curl -s -X GET http://localhost:5000/api/auth/dev-token | jq -r '.token')

# Step 2: Use the token to create a pet
curl -X POST http://localhost:5000/api/pets \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Buddy",
    "pet_type": "Dog",
    "breed": "Golden Retriever"
  }'

# Step 3: Create a device
DEVICE_RESPONSE=$(curl -s -X POST http://localhost:5000/api/devices \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "GPS Collar",
    "device_type": "Tracker"
  }')
DEVICE_ID=$(echo $DEVICE_RESPONSE | jq -r '.device_id')

# Step 4: Simulate a location update
curl -X POST http://localhost:5000/api/locations/simulate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "device_id": "'$DEVICE_ID'",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "battery_level": 95
  }'
```

## API Endpoints Reference

### Authentication
- `GET /api/auth/login`: Initiate Google OAuth flow
- `GET /api/auth/callback`: OAuth callback URL
- `GET /api/auth/logout`: Log out current user
- `GET /api/auth/user`: Get current user info
- `GET /api/auth/check`: Check if user is authenticated
- `GET /api/auth/dev-token`: [Development only] Get a JWT token for testing

### Pets
- `GET /api/pets`: List all pets for current user
- `POST /api/pets`: Create a new pet
- `GET /api/pets/<id>`: Get a specific pet
- `PUT /api/pets/<id>`: Update a pet
- `DELETE /api/pets/<id>`: Delete a pet

### Devices
- `GET /api/devices`: List all devices for current user
- `POST /api/devices`: Register a new device
- `GET /api/devices/<id>`: Get a specific device
- `PUT /api/devices/<id>`: Update a device
- `DELETE /api/devices/<id>`: Delete a device
- `POST /api/devices/<device_id>/assign/<pet_id>`: Assign device to pet
- `POST /api/devices/<device_id>/unassign`: Unassign device from pet
- `POST /api/devices/ping/<device_id>`: Record a device ping

### Locations
- `GET /api/locations/device/<device_id>`: Get location history for a device
- `GET /api/locations/pet/<pet_id>`: Get location history for a pet
- `GET /api/locations/device/<device_id>/latest`: Get latest location for a device
- `GET /api/locations/pet/<pet_id>/latest`: Get latest location for a pet
- `GET /api/locations/pets/latest`: Get latest location for all pets
- `POST /api/locations/simulate`: Simulate a location update (for testing)
- `POST /api/locations`: Record a new location from a device

## Troubleshooting

### Database Issues
- Ensure PostgreSQL is running: `pg_isready`
- Check connection string in `.env`
- Verify tables exist: `psql -d pet_tracker -c "\dt"`

### Authentication Issues
- Verify Google OAuth credentials
- Check that redirect URLs match exactly
- For testing, use the development token endpoint

### Testing the get_user_info() Method
If you're testing the `get_user_info()` method in `test_api.py`, make sure the Authorization header is set correctly:

```python
def get_user_info(self):
    """Get current user information"""
    # The session should already have the Authorization header set in __init__
    # But you can also manually ensure it's set:
    # headers = {"Authorization": f"Bearer {self.jwt_token}"}
    response = self.session.get(f"{self.base_url}/auth/user")
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Failed to get user info: {response.status_code} - {response.text}")
        return None
```

When initializing the APITester class, make sure to pass the JWT token:

```python
# Get the development token
token_response = requests.get("http://localhost:5000/api/auth/dev-token").json()
jwt_token = token_response.get("token")

# Create API tester with the token
tester = APITester(base_url="http://localhost:5000/api", jwt_token=jwt_token)

# Now you can get user info
user_info = tester.get_user_info()
```

### 808 Protocol Server Issues
- Check if server is running: `ps aux | grep protocol_server`
- Ensure port 8080 is not in use: `netstat -tuln | grep 8080`
- Run standalone server: `python tools/start_protocol_server.py`

## License

[MIT License](LICENSE)