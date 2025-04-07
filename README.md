# Pet Tracking System

A comprehensive pet tracking and management platform that enables owners to monitor, interact with, and care for their pets through advanced technological solutions.

## Key Technologies

- Flask web framework
- PostgreSQL database
- Google OAuth authentication
- RESTful API design
- WebSocket real-time communication
- Device tracking and geofencing capabilities
- JWT authentication
- Protocol 808 and JT808 message decoding services

## Getting Started

### Prerequisites

- Python 3.10+ for the backend
- Node.js and npm for the frontend
- PostgreSQL database

### Backend Setup

1. **Start the Flask backend server**:

   ```bash
   # From the project root directory
   python -m gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```

   Or use the configured workflow:

   ```bash
   # Use the Replit workflow
   .replit
   ```

2. **Environment Variables**:

   The following environment variables are required:
   
   - `DATABASE_URL`: PostgreSQL connection string
   - `SESSION_SECRET`: Secret key for session management
   - `GOOGLE_OAUTH_CLIENT_ID`: Google OAuth client ID
   - `GOOGLE_OAUTH_CLIENT_SECRET`: Google OAuth client secret
   - `PROTOCOL_808_PORT`: Port for the 808 protocol server (default: 8080)

### Frontend Setup

#### Running Locally (Outside of Replit)

1. **Install frontend dependencies**:

   ```bash
   # Navigate to the frontend directory
   cd frontend
   
   # Install dependencies
   npm install
   ```

2. **Start the development server**:

   ```bash
   # From the frontend directory
   npm run dev
   ```

   This will start the Vue.js development server with Vite, making the frontend available at http://localhost:3000.

#### Running in Replit

To run the frontend in Replit, you'll need to:

1. Fork this repository to your local environment
2. Install the dependencies:

   ```bash
   cd frontend
   npm install
   ```

3. Build the frontend for production:

   ```bash
   npm run build
   ```

4. The built files will be in `frontend/dist` directory and can be served by the Flask backend

Note: In Replit, direct execution of the frontend development server may be restricted. For development, consider using a local environment.

## Accessing the Application

- **Backend API**: http://localhost:5000
- **Frontend**: http://localhost:3000 (when running the frontend dev server)

## Device Simulator

A GPS device simulator is included to test the pet tracking functionality:

```bash
# For traditional 808 protocol
python tools/device_simulator.py --device-id your-device-id --imei 123456789012345 --interval 5

# For JT/T 808 protocol
python tools/device_simulator.py --device-id your-device-id --imei 123456789012345 --interval 5 --protocol jt808
```

## Components

- **Frontend**: Vue.js application for user interface
- **Backend API**: Flask server with RESTful endpoints
- **Protocol Server**: TCP server handling both 808 and JT808 protocol messages from tracking devices
- **Database**: PostgreSQL for data storage

## Supported Protocols

The system supports two GPS tracking protocols:

### Traditional 808 Protocol
- Text-based protocol with command codes like BP01 (login), BP02 (GPS), etc.
- Message format: `*ID,IMEI:IMEI,command,timestamp,device_id,...#`
- Simpler string-based format popular with many basic GPS trackers
- Commands include:
  - BP00: Heartbeat
  - BP01: Login
  - BP02: GPS position update

### JT/T 808 Protocol
- Chinese national standard for GPS communication (JT/T 808-2011/2013/2019)
- Binary protocol with message IDs like 0x0100 (registration), 0x0200 (location)
- More structured binary format with proper bit fields and BCD time encoding
- Enhanced features like terminal authentication, registration, and extended data
- Key message types:
  - 0x0100: Terminal Registration
  - 0x0102: Terminal Authentication
  - 0x0200: Location Reporting
  - 0x0002: Heartbeat

### Automatic Protocol Detection
Both protocols are automatically detected by the server:
- Messages starting with `*ID` are processed as traditional 808 protocol
- Messages starting with the byte `0x7e` are processed as JT808 protocol
- This allows seamless support for mixed device fleets with no reconfiguration needed

### Protocol Server Implementation
- The protocol server runs on port 8080 (configurable via `PROTOCOL_808_PORT` environment variable)
- It listens for TCP connections from tracking devices
- Both protocol parsers maintain compatible outputs for database storage
- Device identification is consistent across protocols for unified device management