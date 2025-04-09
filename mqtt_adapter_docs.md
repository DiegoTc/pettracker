# MQTT Protocol Adapter

The system includes a modular MQTT adapter that translates JT/T 808 protocol messages to MQTT for more flexible integrations:

## Features
- Listens for incoming JT/T 808 protocol messages on TCP port 8081 (configurable)
- Parses messages according to the protocol specification, handling byte unescaping and checksum verification
- Extracts and transforms device data into structured JSON
- Publishes data to an MQTT broker on topics like `devices/{device_id}/location`
- Supports all standard JT/T 808 message types plus pet-specific extensions
- Manages device registration and authentication flows

## Testing the MQTT Adapter

The easiest way to test the adapter is with the all-in-one test script:

```bash
# Start all components (MQTT broker, adapter, and subscriber)
python test_mqtt_system.py

# To also start a simulator automatically
python test_mqtt_system.py --with-simulator
```

For more details, see the comprehensive [MQTT Adapter Testing Guide](MQTT_ADAPTER_GUIDE.md).

## Running the MQTT Adapter Manually

1. **Start the MQTT broker**:
   ```bash
   # Start Mosquitto with the provided configuration
   mosquitto -c mosquitto.conf
   ```

2. **Run the adapter**:
   ```bash
   # Start the JT/T 808 to MQTT adapter (on port 8081 to avoid conflict)
   python run_mqtt_adapter.py --protocol-port 8081
   ```

3. **Monitor messages** (optional):
   ```bash
   # Subscribe to all device topics
   python tools/mqtt_subscriber.py
   ```

4. **Test with a simulated device**:
   ```bash
   # Run the JT808 device simulator
   python tools/jt808_simulator.py --port 8081
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
