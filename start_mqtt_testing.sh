#!/bin/bash
# Start the MQTT testing environment

# Create persistence directory for Mosquitto
mkdir -p /tmp/mosquitto

# Start Mosquitto MQTT broker in the background
echo "Starting MQTT broker..."
mosquitto -c mosquitto.conf &
MOSQUITTO_PID=$!

# Wait for broker to start
sleep 2

# Start the Protocol Adapter in the background
echo "Starting JT/T 808 to MQTT Protocol Adapter..."
python run_mqtt_adapter.py --debug --protocol-port 8081 --protocol-port 8081 &
ADAPTER_PID=$!

# Wait for adapter to start
sleep 2

# Start the MQTT Subscriber to monitor messages
echo "Starting MQTT Subscriber..."
python tools/mqtt_subscriber.py --debug &
SUBSCRIBER_PID=$!

# Wait for subscriber to start
sleep 2

echo "All components started. Press Ctrl+C to stop."
echo "Mosquitto PID: $MOSQUITTO_PID"
echo "Adapter PID: $ADAPTER_PID"
echo "Subscriber PID: $SUBSCRIBER_PID"
echo ""
echo "You can now run the JT808 simulator with:"
echo "python tools/jt808_simulator.py"
echo ""

# Handle termination
function cleanup {
    echo "Stopping all components..."
    kill $SUBSCRIBER_PID 2>/dev/null
    kill $ADAPTER_PID 2>/dev/null
    kill $MOSQUITTO_PID 2>/dev/null
    echo "Done."
    exit 0
}

trap cleanup SIGINT SIGTERM

# Keep script running
while true; do
    sleep 1
done
