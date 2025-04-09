#!/bin/bash
# Start the MQTT adapter with built-in simulator mode

# Default values
PORT=8081
DEVICE_COUNT=3
UPDATE_INTERVAL=10
DEBUG=""

# Process command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --port=*)
      PORT="${1#*=}"
      shift
      ;;
    --count=*)
      DEVICE_COUNT="${1#*=}"
      shift
      ;;
    --interval=*)
      UPDATE_INTERVAL="${1#*=}"
      shift
      ;;
    --debug)
      DEBUG="--debug"
      shift
      ;;
    *)
      echo "Unknown parameter: $1"
      echo "Usage: $0 [--port=PORT] [--count=DEVICE_COUNT] [--interval=UPDATE_INTERVAL] [--debug]"
      exit 1
      ;;
  esac
done

echo "========================================================"
echo "Starting MQTT adapter with built-in simulator"
echo "========================================================"
echo "Port: $PORT"
echo "Device count: $DEVICE_COUNT"
echo "Update interval: $UPDATE_INTERVAL seconds"
echo "Debug: ${DEBUG:=disabled}"
echo "--------------------------------------------------------"

# Start the MQTT adapter with simulator mode enabled
python run_mqtt_adapter.py \
  --protocol-port=$PORT \
  --mqtt-host=127.0.0.1 \
  --mqtt-port=1883 \
  --simulator \
  --simulator-device-count=$DEVICE_COUNT \
  --simulator-interval=$UPDATE_INTERVAL \
  $DEBUG

# Exit with the same status as the adapter
exit $?
