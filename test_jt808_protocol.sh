#!/bin/bash
# This script sets up and tests the JT/T 808 Protocol server with the simulator

echo "====================================================="
echo "Testing JT/T 808 Protocol Adapter with Simulator"
echo "====================================================="

# First, check if mosquitto is running
if ! pgrep mosquitto > /dev/null; then
    echo "Starting Mosquitto MQTT broker..."
    mosquitto -c mosquitto.conf -d
    sleep 2
else
    echo "Mosquitto broker is already running."
fi

# Start MQTT adapter on port 8081
echo "Starting JT/T 808 Protocol Adapter on port 8081..."
python run_mqtt_adapter.py --protocol-port=8081 --mqtt-host=127.0.0.1 --mqtt-port=1883 --debug &
ADAPTER_PID=$!

# Wait for adapter to initialize
echo "Waiting for adapter to initialize..."
sleep 3

# Start MQTT subscriber
echo "Starting MQTT subscriber to monitor messages..."
python tools/mqtt_subscriber.py --debug &
SUBSCRIBER_PID=$!

# Wait for subscriber to initialize
sleep 2

# Start simulator
echo "Starting JT/T 808 device simulator..."
python tools/simulate_808_devices.py --host=localhost --port=8081 --count=1 --interval=5 --debug

# Manual cleanup
echo "Press Ctrl+C to stop the test"

# Wait for user to terminate
wait $ADAPTER_PID

# Cleanup
kill $ADAPTER_PID 2>/dev/null
kill $SUBSCRIBER_PID 2>/dev/null