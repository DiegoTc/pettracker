# MQTT Adapter Guide

This guide explains how to use the MQTT adapter and related components in the pet tracking system.

## Overview

The MQTT adapter translates JT808 protocol messages from tracking devices into MQTT messages, allowing for a more decoupled architecture. The system consists of:

1. **MQTT Broker (Mosquitto)**: Message broker that handles communication between components
2. **Protocol Adapter**: Translates JT808 protocol messages to MQTT topics
3. **Data Consumers**: Components that subscribe to device topics (like web applications, mobile apps, etc.)

## Prerequisites

- Mosquitto MQTT broker installed
- Python 3 with paho-mqtt library installed

## Running the System

### 1. Using the start script (recommended)

The easiest way to start all components is to use the provided script:

```bash
./start_mqtt_testing.sh
```

This will:
- Start the Mosquitto MQTT broker
- Start the JT/T 808 to MQTT Protocol Adapter on port 8081
- Provide instructions for running the simulator

### 2. Manual startup

If you need more control, you can start each component individually:

1. **Start the MQTT broker**:
   ```bash
   mosquitto -c mosquitto.conf -d
   ```

2. **Start the Protocol Adapter**:
   ```bash
   python3 run_mqtt_adapter.py --protocol-port 8081 --mqtt-host 127.0.0.1
   ```

3. **Run the simulator** (optional, for testing):
   ```bash
   python3 tools/jt808_simulator.py --host 127.0.0.1 --port 8081
   ```

4. **Monitor MQTT messages** (optional, for debugging):
   ```bash
   python3 tools/mqtt_subscriber.py
   ```

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐  
│                 │      │                  │      │                 │  
│  JT808 Devices  │──────►  Protocol Server │──────►  MQTT Broker    │  
│                 │ 8081 │  (Adapter)       │ 1883 │  (Mosquitto)    │  
└─────────────────┘      └──────────────────┘      └────────┬────────┘  
                                                            │
                                                            │
                                                  ┌─────────┴────────┐
                                                  │                  │
                                                  │  Subscribers     │
                                                  │  (Web App, etc.) │
                                                  └──────────────────┘
```

## MQTT Topics

The MQTT adapter publishes messages to topics in the following format:

```
devices/{device_id}/{message_type}
```

For example:
- `devices/123456789/location` - Contains location data for device 123456789
- `devices/123456789/status` - Contains status information for device 123456789

## Testing the System

You can use the provided test scripts to verify the system is working correctly:

1. **Basic functionality test**:
   ```bash
   python3 test_mqtt_adapter.py
   ```

2. **Full system test with simulator**:
   ```bash
   python3 test_mqtt_system.py --with-simulator
   ```

## Troubleshooting

### Connection Issues

1. **Port conflicts**: Ensure there are no port conflicts for 1883 (MQTT broker) and 8081 (Protocol adapter)
2. **Connectivity**: Check that all components can connect to each other (especially in networked environments)
3. **Firewall settings**: Make sure any firewall allows traffic on the necessary ports

### Message Issues

1. **Subscribe to all topics** to see what's coming through:
   ```bash
   mosquitto_sub -h localhost -t '#' -v
   ```

2. **Check adapter logs** for any errors:
   ```bash
   cat mqtt_adapter.log
   ```

## Extending the System

The MQTT adapter is designed to be extensible. To add support for new message types:

1. Update the `_parse_message` method in `protocol_adapter.py`
2. Add new message type handling in `_process_message`
3. Add any new topic structures needed

## Configuration

The system can be configured using command-line arguments or environment variables:

- **Protocol adapter port**: `--protocol-port` or `PROTOCOL_PORT` (default: 8081)
- **MQTT broker host**: `--mqtt-host` or `MQTT_HOST` (default: 127.0.0.1)
- **MQTT broker port**: `--mqtt-port` or `MQTT_PORT` (default: 1883)
- **MQTT credentials**: `--mqtt-username`, `--mqtt-password` or `MQTT_USERNAME`, `MQTT_PASSWORD`
