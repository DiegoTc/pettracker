# MQTT Adapter Testing Guide

This guide explains how to test the MQTT adapter both with and without physical tracking devices.

## Overview of Components

1. **MQTT Broker (Mosquitto)**: Handles MQTT message routing between publishers and subscribers
2. **JT/T 808 Protocol Adapter**: Listens for JT/T 808 tracking devices, parses messages, and publishes to MQTT
3. **Device Simulator**: Mimics a physical JT/T 808 GPS tracking device for testing
4. **MQTT Subscriber**: Monitors MQTT topics to verify messages are being published correctly

## Testing Without Physical Devices

### Option 1: All-in-One Test Script

The easiest way to test is with the all-in-one script that starts all components:

```bash
# Start all components including a simulator
python test_mqtt_system.py --with-simulator
```

This will:
1. Start the Mosquitto MQTT broker
2. Start the JT/T 808 Protocol Adapter
3. Start an MQTT subscriber to monitor topics
4. Start a JT/T 808 device simulator
5. Show a dashboard of all running components

Press Ctrl+C to stop all components when finished.

### Option 2: Manual Component Testing

For more control, you can start each component separately:

1. **Start the MQTT broker**:
   ```bash
   mosquitto -c mosquitto.conf
   ```

2. **Start the Protocol Adapter** (in a new terminal):
   ```bash
   python run_mqtt_adapter.py --debug --protocol-port 8081
   ```

3. **Start the MQTT Subscriber** (in a new terminal):
   ```bash
   python tools/mqtt_subscriber.py
   ```

4. **Start the JT808 Simulator** (in a new terminal):
   ```bash
   python tools/jt808_simulator.py --server-port 8081 --interval 5
   ```

You should see messages appearing in the subscriber terminal as the simulator sends data.

## Testing With Physical Devices

To test with actual JT/T 808 tracking devices:

1. **Configure Your Device**: Set your physical device to connect to your server's IP address on port 8081
   - Make sure your server allows incoming connections on port 8081
   - Ensure the device is configured to use the JT/T 808 protocol

2. **Start the Components**:
   ```bash
   # Start without the simulator
   python test_mqtt_system.py
   ```

3. **Power On Your Device**: The physical device should connect to the adapter
   - You should see registration messages in the adapter logs
   - Location updates should appear in the MQTT subscriber

4. **Check Data Flow**: Verify that the device data is flowing through the MQTT broker
   - Messages will be published to topics like: `devices/{device_id}/location`
   - Each message will contain the parsed tracking data in JSON format

## Troubleshooting

- **Connection Issues**: Make sure your firewall allows traffic on ports 8081 (JT808) and 1883 (MQTT)
- **Message Format Errors**: Check adapter logs for parsing errors if messages aren't being published
- **Device Not Registered**: Confirm your device is sending the correct identification information

## Next Steps

After verifying the adapter works correctly, you can:

1. **Create MQTT Consumers**: Develop applications that subscribe to the device topics
2. **Implement Data Processing**: Build services to process and store the location data 
3. **Configure for Production**: Set up secure authentication and TLS for MQTT communication
