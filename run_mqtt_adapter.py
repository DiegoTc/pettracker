#!/usr/bin/env python3
"""
Run the JT/T 808 to MQTT Protocol Adapter

This script starts a TCP server that listens for JT/T 808 protocol messages from
GPS tracking devices, parses them according to the protocol specification, and
publishes the data to an MQTT broker.

Production Configuration:
- In production, this adapter listens on port 808 (pettrack.com:808)
- Physical devices should be configured to connect to pettrack.com:808
- The standard port 808 is reserved for this specific protocol
"""

import argparse
import logging
import os
import signal
import sys
import threading
import time

from services.mqtt_adapter import MQTTClient, ProtocolAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mqtt_adapter.log')
    ]
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='JT/T 808 to MQTT Protocol Adapter')
    
    parser.add_argument(
        '--protocol-host',
        default=os.environ.get('PROTOCOL_HOST', '0.0.0.0'),
        help='Host to bind the protocol server to (default: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--protocol-port',
        type=int,
        default=int(os.environ.get('PROTOCOL_PORT', 808)),
        help='Port to listen on for protocol messages (default: 808 for production, use 8081 for development)'
    )
    
    parser.add_argument(
        '--mqtt-host',
        default=os.environ.get('MQTT_HOST', '127.0.0.1'),
        help='MQTT broker host (default: 127.0.0.1)'
    )
    
    parser.add_argument(
        '--mqtt-port',
        type=int,
        default=int(os.environ.get('MQTT_PORT', 1883)),
        help='MQTT broker port (default: 1883)'
    )
    
    parser.add_argument(
        '--mqtt-username',
        default=os.environ.get('MQTT_USERNAME', None),
        help='MQTT broker username'
    )
    
    parser.add_argument(
        '--mqtt-password',
        default=os.environ.get('MQTT_PASSWORD', None),
        help='MQTT broker password'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--simulator',
        action='store_true',
        help='Enable built-in simulator mode to generate sample JT/T 808 messages for testing'
    )
    
    parser.add_argument(
        '--simulator-device-count',
        type=int,
        default=1,
        help='Number of virtual devices to simulate (default: 1)'
    )
    
    parser.add_argument(
        '--simulator-interval',
        type=int,
        default=10,
        help='Interval between simulated location updates in seconds (default: 10)'
    )
    
    return parser.parse_args()


def main():
    """Main entry point for the adapter"""
    args = parse_arguments()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.info("Debug logging enabled")
    
    # Set environment variables for MQTT credentials if provided
    if args.mqtt_username:
        os.environ['MQTT_USERNAME'] = args.mqtt_username
    if args.mqtt_password:
        os.environ['MQTT_PASSWORD'] = args.mqtt_password
    
    logger.info(f"Starting JT/T 808 to MQTT Protocol Adapter")
    logger.info(f"Protocol server listening on {args.protocol_host}:{args.protocol_port}")
    logger.info(f"Connecting to MQTT broker at {args.mqtt_host}:{args.mqtt_port}")
    
    # Create MQTT client
    mqtt_client = MQTTClient(
        broker_host=args.mqtt_host,
        broker_port=args.mqtt_port,
        client_id="jt808_mqtt_adapter"
    )
    
    # Create and start the protocol adapter
    adapter = ProtocolAdapter(
        host=args.protocol_host,
        port=args.protocol_port,
        mqtt_client=mqtt_client
    )
    
    # Handle graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Shutting down adapter...")
        adapter.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start the adapter in a try-except block to handle any startup errors
    try:
        # Start the adapter in a background thread
        adapter_thread = threading.Thread(target=adapter.start)
        adapter_thread.daemon = True
        adapter_thread.start()
        logger.info("Protocol adapter started successfully")
        
        # If simulator mode is enabled, start simulated devices
        if args.simulator:
            from tools.jt808_simulator import JT808DeviceSimulator
            
            logger.info(f"Starting built-in simulator with {args.simulator_device_count} virtual devices")
            logger.info(f"Location updates will be sent every {args.simulator_interval} seconds")
            
            # Create and start simulated devices
            simulators = []
            for i in range(args.simulator_device_count):
                device_id = f"SIM{i+1:03d}"
                simulator = JT808DeviceSimulator(
                    server_host='127.0.0.1',  # Connect to the local adapter
                    server_port=args.protocol_port,
                    device_id=device_id,
                    initial_latitude=37.7749 + (i * 0.01),  # Slightly offset each device
                    initial_longitude=-122.4194 + (i * 0.01),
                    move_randomly=True
                )
                
                # Connect and register the device
                if simulator.connect():
                    if simulator.send_registration():
                        logger.info(f"Simulated device {device_id} registered successfully")
                        simulators.append(simulator)
                    else:
                        logger.error(f"Failed to register simulated device {device_id}")
                else:
                    logger.error(f"Failed to connect simulated device {device_id}")
            
            # Main simulation loop for all connected devices
            while simulators and adapter.running:
                # Send location updates and heartbeats
                for simulator in simulators:
                    try:
                        simulator.send_location()
                        logger.debug(f"Sent location update from {simulator.device_id}")
                    except Exception as e:
                        logger.error(f"Error sending location from {simulator.device_id}: {str(e)}")
                
                # Wait for the configured interval
                time.sleep(args.simulator_interval)
        else:
            # If no simulator, just keep the main process running
            while adapter.running:
                time.sleep(1)
                
    except Exception as e:
        logger.error(f"Error in adapter: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())