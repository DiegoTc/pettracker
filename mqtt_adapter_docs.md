# MQTT Protocol Adapter

The system includes a modular MQTT adapter that translates JT/T 808 protocol messages to MQTT for more flexible integrations:

## Features
- Listens for incoming JT/T 808 protocol messages on TCP port 8080
- Parses messages according to the protocol specification, handling byte unescaping and checksum verification
- Extracts and transforms device data into structured JSON
- Publishes data to an MQTT broker on topics like `devices/{device_id}/location`
- Supports all standard JT/T 808 message types plus pet-specific extensions
- Manages device registration and authentication flows

## Running the MQTT Adapter

1. **Start the MQTT broker**:
   ```bash
   # Start Mosquitto with the provided configuration
   mosquitto -c mosquitto.conf
   ```

2. **Run the adapter**:
   ```bash
   # Start the JT/T 808 to MQTT adapter
   python run_mqtt_adapter.py
   ```

3. **Monitor messages** (optional):
   ```bash
   # Subscribe to all device topics
   python tools/mqtt_subscriber.py
   ```

4. **Test with a simulated device**:
   ```bash
   # Run the JT808 device simulator
   python tools/jt808_simulator.py
   ```

5. **Or use the all-in-one script**:
   ```bash
   # Start the complete testing environment (broker, adapter, subscriber)
   ./start_mqtt_testing.sh
   ```

## Configuration Options
- `--protocol-host`: Host to bind the protocol server to (default: 0.0.0.0)
- `--protocol-port`: Port to listen on for protocol messages (default: 8080)
- `--mqtt-host`: MQTT broker host (default: localhost)
- `--mqtt-port`: MQTT broker port (default: 1883)
- `--mqtt-username`: MQTT broker username (if required)
- `--mqtt-password`: MQTT broker password (if required)
- `--debug`: Enable debug logging

## MQTT Topic Structure
- `devices/{device_id}/location`: Device location updates
- `devices/{device_id}/status`: Device status updates (heartbeat, registration, etc.)

## Message Format
Location messages contain:
- Latitude, longitude, altitude
- Speed, heading
- Battery level, satellite count
- Pet-specific data: activity level, temperature, health flags
- Timestamp and status flags