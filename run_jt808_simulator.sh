#!/bin/bash
# Run the JT808 simulator pointing to the MQTT adapter

echo "Running JT808 simulator..."
python3 tools/jt808_simulator.py --host 127.0.0.1 --port 8081 "$@"
