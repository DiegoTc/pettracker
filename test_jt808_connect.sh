#!/bin/bash

# This script runs a simple JT808 simulator test with correct port configuration

# Start the MQTT protocol adapter on port 8081
echo "Starting MQTT Protocol Adapter on port 8081..."
python run_mqtt_adapter.py --protocol-port=8081 --mqtt-host=127.0.0.1 --mqtt-port=1883 --debug &
ADAPTER_PID=$!

# Wait for adapter to start
sleep 2

# Start a single JT808 device simulator pointing to port 8081
echo "Starting JT808 simulator to connect to port 8081..."
python tools/jt808_simulator.py --server=127.0.0.1 --port=8081 --debug

# Clean up when done
echo "Cleaning up..."
kill $ADAPTER_PID 2>/dev/null