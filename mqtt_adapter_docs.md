# MQTT Adapter Implementation Notes

## Key Changes Made

1. **Port Configuration**:
   - Changed default Protocol Adapter port from 8080 to 8081 to avoid conflict with the main 808 Protocol Server
   - Updated `run_mqtt_adapter.py` to use 8081 by default

2. **MQTT Connectivity**:
   - Updated MQTT connection parameters in `mqtt_client.py` to use IP address (127.0.0.1) instead of hostname
   - Modified connection handling for more robust MQTT broker connectivity

3. **Testing Scripts**:
   - Created `start_mqtt_testing.sh` script to simplify starting all required components
   - Created `run_jt808_simulator.sh` to make it easier to run the simulator against the adapter

4. **Documentation**:
   - Added comprehensive MQTT Adapter Guide with system architecture, configuration options, and troubleshooting steps

## System Architecture

The MQTT adapter implementation consists of:

- **MQTT Broker (Mosquitto)**: Runs on port 1883
- **Protocol Adapter**: Connects to MQTT Broker and listens on port 8081 for JT808 messages
- **Simulator**: Allows testing by sending simulated JT808 messages
- **Test Scripts**: Provide easy ways to verify the system is working correctly

## Port Allocation

| Component          | Port |
|--------------------|------|
| Main Flask App     | 5000 |
| 808 Protocol Server| 8080 |
| MQTT Adapter       | 8081 |
| MQTT Broker        | 1883 |

## Next Steps & Improvements

Potential future improvements:

1. Start the MQTT adapter automatically with the main application
2. Add security features (TLS, authentication) for production use
3. Enhance the adapter to handle more message types
4. Add better error recovery and reconnection logic
5. Implement a web-based MQTT message viewer
