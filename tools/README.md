# Simulation and Testing Tools

This directory contains various tools for simulating device connections and testing the pet tracking system.

## JT/T 808 Protocol Simulators

### 1. Single Device Simulator (`jt808_simulator.py`)

This tool simulates a single JT/T 808 protocol device connecting to the protocol adapter.

Usage:
```bash
python tools/jt808_simulator.py --host 127.0.0.1 --port 8081
```

Features:
- Connects to the protocol adapter
- Sends device registration messages
- Sends location updates with configurable frequency
- Sends heartbeat messages
- Can simulate random movement

### 2. Multi-Device Simulator (`simulate_808_devices.py`)

This tool simulates multiple JT/T 808 protocol devices connecting to the protocol adapter.

Usage:
```bash
python tools/simulate_808_devices.py --host 127.0.0.1 --port 8081 --count 5
```

Features:
- Creates multiple virtual GPS tracking devices
- Sends registration messages for each device
- Sends location updates with configurable frequency
- Sends heartbeat messages periodically
- Can simulate different movement patterns (random, circular, fixed)
- Manages multiple devices in separate threads

Options:
- `--host` - Adapter host (default: pettrack.com)
- `--port` - Adapter port (default: 808)
- `--count` - Number of devices to simulate (default: 3)
- `--interval` - Seconds between updates (default: 30)
- `--mode` - Movement pattern (random, circular, fixed) (default: random)
- `--debug` - Enable debug logging

### 3. Integrated Simulator (in `run_mqtt_adapter.py`)

The protocol adapter itself can run a built-in simulator that generates virtual device connections internally.

Usage:
```bash
python run_mqtt_adapter.py --simulator --simulator-device-count 3
```

Features:
- No separate process needed
- Creates the specified number of virtual devices
- Sends location updates at configurable intervals
- Easier to use for basic testing scenarios

## MQTT Tools

### 1. MQTT Subscriber (`mqtt_subscriber.py`)

This tool subscribes to MQTT topics and displays received messages.

Usage:
```bash
python tools/mqtt_subscriber.py
```

Options:
- `--host` - MQTT broker host (default: 127.0.0.1)
- `--port` - MQTT broker port (default: 1883)
- `--topics` - Comma-separated list of topics to subscribe to (default: all device topics)

### 2. MQTT Publisher (`mqtt_publisher.py`)

This tool can publish custom messages to MQTT topics.

Usage:
```bash
python tools/mqtt_publisher.py --topic "devices/TEST123/location" --message '{"latitude": 37.7749, "longitude": -122.4194}'
```

Options:
- `--host` - MQTT broker host (default: 127.0.0.1)
- `--port` - MQTT broker port (default: 1883)
- `--topic` - Topic to publish to
- `--message` - JSON message to publish
- `--qos` - Quality of Service level (0, 1, or 2) (default: 0)

## Helper Scripts

Several helper scripts are provided to make it easier to run the simulators:

- `start_mqtt_adapter_with_simulator.sh` - Starts the adapter with built-in simulator
- `start_standalone_simulator.sh` - Starts the standalone multi-device simulator
- `start_mqtt_testing.sh` - Sets up the complete MQTT testing environment

See the main [MQTT Adapter Guide](../MQTT_ADAPTER_GUIDE.md) for more details.
