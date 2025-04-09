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

### 2. Using the adapter with built-in simulator

For quick testing, you can start the adapter with its built-in simulator:

```bash
./start_mqtt_adapter_with_simulator.sh
```

This script accepts the following parameters:
- `--port=PORT` - Port for the protocol adapter (default: 8081)
- `--count=COUNT` - Number of simulated devices (default: 3)
- `--interval=SECONDS` - Interval between updates (default: 10)
- `--debug` - Enable debug logging

### 3. Using the standalone simulator

For more complex simulation scenarios, use the standalone simulator:

```bash
./start_standalone_simulator.sh
```

This script accepts the following parameters:
- `--host=HOST` - Host to connect to (default: 127.0.0.1)
- `--port=PORT` - Port to connect to (default: 8081)
- `--count=COUNT` - Number of simulated devices (default: 3)
- `--interval=SECONDS` - Interval between updates (default: 30)
- `--mode=MODE` - Movement pattern (random, circular, fixed) (default: random)
- `--debug` - Enable debug logging

### 4. Manual startup

If you need more control, you can start each component individually:

1. **Start the MQTT broker**:
   ```bash
   mosquitto -c mosquitto.conf -d
   ```

2. **Start the Protocol Adapter**:
   ```bash
   python3 run_mqtt_adapter.py --protocol-port 8081 --mqtt-host 127.0.0.1
   ```
   
   To enable the built-in simulator:
   ```bash
   python3 run_mqtt_adapter.py --protocol-port 8081 --mqtt-host 127.0.0.1 --simulator --simulator-device-count 3
   ```

3. **Run the simulator** (optional, for testing):
   ```bash
   python3 tools/jt808_simulator.py --host 127.0.0.1 --port 8081
   ```
   
   Or use the multi-device simulator:
   ```bash
   python3 tools/simulate_808_devices.py --host 127.0.0.1 --port 8081 --count 5
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
- `devices/123456789/pet_data` - Contains pet-specific data from JT808 protocol extensions

### Pet-Specific Data Topics

For JT/T 808 protocol messages that include pet-specific extension data, the system publishes to dedicated pet data topics:

```
devices/{device_id}/pet_data
```

The payload contains a JSON object with the following fields:
```json
{
  "device_id": "123456789",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "timestamp": "2025-04-09T03:45:35.123456",
  "battery_level": 85.5,
  "activity_level": 72,
  "health_flags": {
    "temperature_warning": false,
    "inactivity_warning": false,
    "abnormal_movement": false,
    "potential_distress": false
  },
  "temperature": 38.1
}
```

See `JT808_PROTOCOL_EXTENSION.md` for more details about the pet-specific protocol extensions.

## Simulation Options

The system provides multiple options for simulating device traffic:

### Built-in Simulator

The protocol adapter has a built-in simulator that can generate virtual devices directly within the adapter process:

```bash
python run_mqtt_adapter.py --simulator --simulator-device-count 3 --simulator-interval 10
```

This is the simplest method and requires no additional processes.

### Standalone Multi-Device Simulator

For more advanced simulation scenarios, use the dedicated multi-device simulator:

```bash
python tools/simulate_808_devices.py --host 127.0.0.1 --port 8081 --count 5 --mode random
```

Movement modes:
- `random` - Devices move randomly from their starting positions
- `circular` - Devices move in circular patterns
- `fixed` - Devices stay at fixed positions

### Single Device Simulator

For debugging specific protocol messages, use the single device simulator:

```bash
python tools/jt808_simulator.py --host 127.0.0.1 --port 8081
```

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
- **Simulator options**: `--simulator`, `--simulator-device-count`, `--simulator-interval`
