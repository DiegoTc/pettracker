# Pet Tracker

A Flask-based backend API for a cross-platform pet tracking system with Google authentication and 808 protocol support.

## Features

- User authentication via Google OAuth
- Pet registration and management
- Device registration and tracking
- Real-time location tracking with 808 protocol
- Location history and statistics

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: Google OAuth 2.0
- **Rate Limiting**: Flask-Limiter
- **API Security**: JWT (JSON Web Tokens)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/DiegoTc/pettracker.git
cd pettracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export GOOGLE_OAUTH_CLIENT_ID=your_client_id
export GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret
export SESSION_SECRET=your_session_secret
export DATABASE_URL=postgresql://user:password@localhost/pet_tracker
```

4. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

5. Run the server:
```bash
flask run
```

## API Documentation

### Authentication Endpoints

- `GET /api/auth/login_info` - Get Google OAuth setup information
- `GET /api/auth/login` - Initiate Google OAuth login flow
- `GET /api/auth/callback` - Google OAuth callback endpoint
- `GET /api/auth/logout` - Logout endpoint

### Pet Endpoints

- `GET /api/pets` - Get all pets for the user
- `GET /api/pets/<pet_id>` - Get specific pet details
- `POST /api/pets` - Create a new pet
- `PUT /api/pets/<pet_id>` - Update pet information
- `DELETE /api/pets/<pet_id>` - Delete a pet

### Device Endpoints

- `GET /api/devices` - Get all devices for the user
- `GET /api/devices/<device_id>` - Get specific device details
- `POST /api/devices` - Register a new device
- `PUT /api/devices/<device_id>` - Update device information
- `DELETE /api/devices/<device_id>` - Delete a device
- `POST /api/devices/ping/<device_identifier>` - Record a device ping
- `POST /api/devices/<device_id>/assign/<pet_id>` - Assign device to a pet
- `POST /api/devices/<device_id>/unassign` - Unassign device from pet

### Location Endpoints

- `GET /api/locations/device/<device_id>` - Get location history for a device
- `GET /api/locations/pet/<pet_id>` - Get location history for a pet
- `GET /api/locations/device/<device_id>/latest` - Get latest location for a device
- `GET /api/locations/pet/<pet_id>/latest` - Get latest location for a pet
- `POST /api/locations/record` - Record a new location
- `GET /api/locations/pets/latest` - Get latest locations for all pets

## License

MIT