# Local Setup Guide

This guide will help you set up and run the Pet Tracking System on your local machine.

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher (for frontend)
- PostgreSQL (or use SQLite for development)
- Mosquitto MQTT broker (for MQTT adapter)

## Backend Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd pet-tracking-system
```

### 2. Create and activate a virtual environment

```bash
# For Linux/macOS
python -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Here are the required packages for the backend:
```
Flask==2.3.3
Flask-Cors==4.0.0
Flask-JWT-Extended==4.5.3
Flask-Limiter==3.5.0
Flask-Login==0.6.2
Flask-SQLAlchemy==3.1.1
SQLAlchemy==2.0.23
gunicorn==21.2.0
paho-mqtt==2.2.1
psycopg2-binary==2.9.9
python-dotenv==1.0.0
email-validator==2.1.0
requests==2.31.0
oauthlib==3.2.2
```

### 4. Set up environment variables

Create a `.env` file in the root directory:

```
# Database
DATABASE_URL=postgresql://username:password@localhost/pet_tracker
# or for SQLite
# DATABASE_URL=sqlite:///pet_tracker.db

# Session secret
SESSION_SECRET=your-secret-key

# Google OAuth (if using)
GOOGLE_OAUTH_CLIENT_ID=your-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret

# Protocol server port
PROTOCOL_808_PORT=8080
```

### 5. Initialize the database

```bash
flask db init
flask db migrate
flask db upgrade
```

Or simply run the application, which will create the tables:

```bash
python main.py
```

## Frontend Setup

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 2. Create a `.env` file for the frontend:

```
VITE_API_URL=http://localhost:5000
```

### 3. Start the development server

```bash
npm run dev
```

## MQTT Adapter Setup

### 1. Install Mosquitto MQTT broker

**For Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install mosquitto mosquitto-clients
```

**For macOS:**
```bash
brew install mosquitto
```

**For Windows:**
Download from: https://mosquitto.org/download/

### 2. Configure Mosquitto

Create or modify `mosquitto.conf`:
```
listener 1883
allow_anonymous true
```

### 3. Start the MQTT system

Use the provided script:
```bash
./start_mqtt_testing.sh
```

Or start components manually:
```bash
# Start Mosquitto
mosquitto -c mosquitto.conf -d

# Start the MQTT adapter
python run_mqtt_adapter.py --protocol-port 8081 --mqtt-host 127.0.0.1
```

## Running the Complete System

1. Start the backend:
   ```bash
   python main.py
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Start the MQTT adapter system:
   ```bash
   ./start_mqtt_testing.sh
   ```

## Testing

### Run the simulator:

```bash
python tools/jt808_simulator.py --host 127.0.0.1 --port 8081
```

Or use the helper script:
```bash
./run_jt808_simulator.sh
```

### Run the full MQTT system test:

```bash
python test_mqtt_system.py --with-simulator
```

## Accessing the Application

- Backend API: http://localhost:5000
- Frontend application: http://localhost:3000
- Protocol server: Port 8080
- MQTT adapter: Port 8081
- MQTT broker: Port 1883

## Troubleshooting

### Common Issues

1. **Port conflicts**: Make sure no other applications are using ports 5000, 3000, 8080, 8081, or 1883.

2. **Database connection issues**: Verify PostgreSQL is running and your connection string is correct.

3. **MQTT connection issues**: Ensure Mosquitto is running and accepting connections.

4. **CORS issues**: Check that your frontend is connecting to the correct backend URL.

5. **Missing environment variables**: Ensure all required environment variables are set in your `.env` file.

### Logs

- Backend logs: Visible in the terminal where you run the Flask application
- MQTT adapter logs: Check `mqtt_adapter.log`
- Mosquitto logs: Vary by platform, but often in `/var/log/mosquitto/`