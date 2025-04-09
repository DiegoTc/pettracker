#!/bin/bash
# Start the MQTT system with all required components

echo "Starting MQTT broker..."
pkill mosquitto 2>/dev/null
sleep 1
mosquitto -c mosquitto.conf -d
if [ $? -ne 0 ]; then
  echo "Failed to start MQTT broker"
  exit 1
fi
echo "MQTT broker started successfully"

echo "Starting MQTT adapter..."
pkill -f run_mqtt_adapter.py 2>/dev/null
sleep 1
python3 run_mqtt_adapter.py --protocol-port 8081 --mqtt-host 127.0.0.1 --debug &
if [ $? -ne 0 ]; then
  echo "Failed to start MQTT adapter"
  exit 1
fi
echo "MQTT adapter started successfully"

echo "MQTT system is now running:"
echo "- MQTT broker: 127.0.0.1:1883"
echo "- MQTT adapter: 0.0.0.0:8081"
echo ""
echo "You can now run the simulator with:"
echo "python3 tools/jt808_simulator.py --host 127.0.0.1 --port 8081"
echo ""
echo "Or run the full system test with:"
echo "python3 test_mqtt_system.py --with-simulator"
echo ""
echo "Press Ctrl+C to stop all components"

# Wait for user to press Ctrl+C
trap "pkill mosquitto; pkill -f run_mqtt_adapter.py; echo 'MQTT system stopped'" INT
wait
