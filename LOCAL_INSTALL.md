# Local Installation Guide

This guide will help you set up and run the Pet Tracking System on your local machine.

## Prerequisites

- Python 3.11 or higher
- Node.js 16 or higher (for frontend)
- PostgreSQL (or SQLite for development)
- Mosquitto MQTT broker (for MQTT adapter)

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd pet-tracking-system
```

## Step 2: Python Environment Setup

### Create a Virtual Environment

```bash
# Linux/macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Install Python Dependencies

Install the following dependencies:

```bash
pip install Flask Flask-Cors Flask-JWT-Extended Flask-Limiter Flask-Login Flask-SQLAlchemy 
pip install gunicorn paho-mqtt psycopg2-binary python-dotenv requests oauthlib 
pip install SQLAlchemy email-validator
```

The required versions from our Replit environment are:

- email-validator>=2.2.0
- flask>=3.1.0
- flask-cors>=5.0.1
- flask-jwt-extended>=4.7.1
- flask-limiter>=3.12
- flask-login>=0.6.3
- flask-sqlalchemy>=3.1.1
- gunicorn>=23.0.0
- oauthlib>=3.2.2
- paho-mqtt>=2.1.0
- psycopg2-binary>=2.9.10
- python-dotenv>=1.0.0
- requests>=2.32.3
- sqlalchemy>=2.0.40

## Step 3: Frontend Setup

```bash
cd frontend
npm install
```

Create a `.env` file in the frontend directory:

```
VITE_API_URL=http://localhost:5000
```

## Step 4: Database Setup

For PostgreSQL:

```bash
# Create a database
createdb pet_tracker

# Set the environment variable
export DATABASE_URL=postgresql://username:password@localhost/pet_tracker
```

For SQLite (easier for development):

```bash
export DATABASE_URL=sqlite:///pet_tracker.db
```

## Step 5: Environment Variables

Create a `.env` file in the project root with:

```
# Database
DATABASE_URL=postgresql://username:password@localhost/pet_tracker
# or for SQLite: DATABASE_URL=sqlite:///pet_tracker.db

# Session secret (change this to something secure)
SESSION_SECRET=your-secret-key-here

# Google OAuth (if using Google authentication)
GOOGLE_OAUTH_CLIENT_ID=your-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret

# Protocol server port
PROTOCOL_808_PORT=8080
```

## Step 6: Run the Application

### Start the Backend

```bash
# From the project root
python main.py
```

The backend will be available at http://localhost:5000

### Start the Frontend (Development Mode)

```bash
# From the frontend directory
npm run dev
```

The frontend will be available at http://localhost:3000

## Step 7: Running the MQTT Adapter (Optional)

If you want to use the MQTT adapter for device communication:

### Install Mosquitto MQTT Broker

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install mosquitto mosquitto-clients
```

**macOS**:
```bash
brew install mosquitto
```

**Windows**:
Download from: https://mosquitto.org/download/

### Configure Mosquitto

Create a `mosquitto.conf` file with:
```
listener 1883
allow_anonymous true
```

### Start the MQTT System

```bash
# Start Mosquitto
mosquitto -c mosquitto.conf -d

# Start the MQTT adapter
python run_mqtt_adapter.py --protocol-port 8081 --mqtt-host 127.0.0.1
```

Or use our helper script:
```bash
./start_mqtt_testing.sh
```

## Step 8: Testing the System

### Test with Simulated Devices

```bash
# Run the JT808 simulator
python tools/jt808_simulator.py --host 127.0.0.1 --port 8081
```

Or use our helper script:
```bash
./run_jt808_simulator.sh
```

### Full MQTT System Test

```bash
python test_mqtt_system.py --with-simulator
```

## Ports Used by the System

- **Backend API**: http://localhost:5000
- **Frontend**: http://localhost:3000
- **Protocol Server**: Port 8080 (808 Protocol)
- **MQTT Adapter**: Port 8081 (JT808 Protocol)
- **MQTT Broker**: Port 1883

## Troubleshooting

### CORS Issues

If you encounter CORS issues with the frontend connecting to the backend:
1. Check that your frontend's `.env` file has `VITE_API_URL` set correctly
2. Make sure the backend is running and accessible

### Database Connection Issues

If you have trouble connecting to PostgreSQL:
1. Verify PostgreSQL is running
2. Check your DATABASE_URL environment variable
3. For testing, you can switch to SQLite by changing the DATABASE_URL

### Protocol Server or MQTT Issues

If devices aren't connecting or sending data:
1. Check that the protocol server is running on the correct port
2. Verify there are no port conflicts
3. Check firewall settings that might block incoming connections