# Pet Tracking System

A comprehensive multiplatform pet tracking platform that supports Google authentication, device tracking via both traditional 808 and JT/T 808 protocols, and provides a robust backend API for cross-platform pet monitoring.

## Features

- **Google OAuth Authentication**: Secure user login and management
- **Pet Management**: Create, update, view, and delete pets
- **Device Management**: Register GPS trackers and assign them to pets
- **Location Tracking**: Real-time tracking using both 808 and JT808 protocols
- **Dual Protocol Support**: Compatible with both traditional 808 protocol and Chinese JT/T 808 protocol
- **RESTful API**: Backend support for web, Android, and iOS clients
- **Interactive Map**: Visualize pet locations in real-time
- **Device Simulator**: Test without physical hardware (supports both protocols)
- **MQTT Adapter**: Transform tracking protocol messages to MQTT for flexible integrations

## Key Technologies

- Flask web framework
- PostgreSQL database
- Google OAuth authentication
- RESTful API design
- WebSocket real-time communication
- Device tracking and geofencing capabilities
- JWT authentication
- Protocol 808 and JT808 message decoding services
- MQTT integration for device data streaming

## Port Configuration

The system uses the following default port configuration:

- **Flask Backend API**: Port 5000
- **Frontend Development Server**: Port 3000
- **Protocol Server (JT/T 808)**: Port 8080 (configurable via `PROTOCOL_808_PORT`)
- **Development JT808 Simulator**: Default connects to port 8081

> **Important**: JT/T 808 protocol traditionally uses port 808 in production, but our development environment uses port 8080/8081 to avoid requiring privileged ports. If you encounter connection issues, ensure the simulator is configured to connect to the correct port.

### Testing Script

A convenience testing script is included to test the JT/T 808 protocol adapter:

```bash
# Test the JT/T 808 protocol with the correct port configuration
./test_jt808_protocol.sh
```
## Getting Started

### Prerequisites

- Python 3.11+ for the backend
- Node.js 16+ and npm for the frontend
- PostgreSQL database (or SQLite for development)
- Mosquitto MQTT broker (for MQTT adapter)

### Local Installation

For detailed instructions on setting up a local development environment, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd pet-tracking-system
   ```

2. **Create a Python virtual environment:**

   ```bash
   # Linux/macOS
   python -m venv venv
   source venv/bin/activate

   # Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Python dependencies:**

   Install the following packages:

   ```bash
   pip install Flask Flask-Cors Flask-JWT-Extended Flask-Limiter Flask-Login Flask-SQLAlchemy
   pip install gunicorn paho-mqtt psycopg2-binary python-dotenv requests oauthlib
   pip install SQLAlchemy email-validator
   ```

   Required versions (based on our Replit environment):
   ```
   email-validator>=2.2.0
   flask>=3.1.0
   flask-cors>=5.0.1
   flask-jwt-extended>=4.7.1
   flask-limiter>=3.12
   flask-login>=0.6.3
   flask-sqlalchemy>=3.1.1
   gunicorn>=23.0.0
   oauthlib>=3.2.2
   paho-mqtt>=2.1.0
   psycopg2-binary>=2.9.10
   python-dotenv>=1.0.0
   requests>=2.32.3
   sqlalchemy>=2.0.40
   ```

4. **Set up environment variables:**

   Create a `.env` file in the project root:

   ```
   # Database
   DATABASE_URL=postgresql://username:password@localhost/pet_tracker
   # or for SQLite: DATABASE_URL=sqlite:///pet_tracker.db

   # Session secret
   SESSION_SECRET=your-secret-key-here

   # Google OAuth
   GOOGLE_OAUTH_CLIENT_ID=your-client-id
   GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret

   # Protocol server port
   PROTOCOL_808_PORT=8080
   ```

5. **Set up the database:**

   For PostgreSQL:
   ```bash
   createdb pet_tracker
   ```

   For SQLite, no setup is needed; it will be created automatically.

6. **Run the application:**

   ```bash
   python main.py
   ```

### Backend Setup (Replit)

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

## Device Simulators

Multiple device simulators are included to test the pet tracking functionality:

### Single Device Simulator

```bash
# For traditional 808 protocol

# For JT/T 808 protocol

For testing with multiple devices simultaneously:

```bash
# Simulate 5 devices connecting to localhost:8081
python tools/simulate_808_devices.py --host 127.0.0.1 --port 8081 --count 5 --interval 10

# Simulate 3 devices with different movement patterns
python tools/simulate_808_devices.py --mode circular --count 3

### Built-in Simulator Mode

The protocol adapter can also run with a built-in simulator:

```bash
# Start the adapter with 3 simulated devices
python run_mqtt_adapter.py --simulator --simulator-device-count 3 --simulator-interval 10

# Or use the convenience script
./start_mqtt_adapter_with_simulator.sh --count=5

See the [MQTT Adapter Guide](MQTT_ADAPTER_GUIDE.md) for more details on the MQTT adapter.

