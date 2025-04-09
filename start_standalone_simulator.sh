#!/bin/bash
# Start the standalone JT/T 808 device simulator

# Default values
HOST="127.0.0.1"
PORT=8081
DEVICE_COUNT=3
UPDATE_INTERVAL=30
MODE="random"
DEBUG=""

# Process command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --host=*)
      HOST="${1#*=}"
      shift
      ;;
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
    --mode=*)
      MODE="${1#*=}"
      shift
      ;;
    --debug)
      DEBUG="--debug"
      shift
      ;;
    *)
      echo "Unknown parameter: $1"
      echo "Usage: $0 [--host=HOST] [--port=PORT] [--count=DEVICE_COUNT] [--interval=UPDATE_INTERVAL] [--mode=MODE] [--debug]"
      exit 1
      ;;
  esac
done

echo "========================================================"
echo "Starting JT/T 808 Device Simulator"
echo "========================================================"
echo "Target server: $HOST:$PORT"
echo "Device count: $DEVICE_COUNT"
echo "Update interval: $UPDATE_INTERVAL seconds"
echo "Movement mode: $MODE"
echo "Debug: ${DEBUG:=disabled}"
echo "--------------------------------------------------------"

# Start the standalone simulator
python tools/simulate_808_devices.py \
  --host=$HOST \
  --port=$PORT \
  --count=$DEVICE_COUNT \
  --interval=$UPDATE_INTERVAL \
  --mode=$MODE \
  $DEBUG

# Exit with the same status as the simulator
exit $?
