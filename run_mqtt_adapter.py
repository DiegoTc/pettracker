#!/usr/bin/env python3
"""
Run the JT/T 808 to MQTT Protocol Adapter
"""

import argparse
import logging
import os
import signal
import sys
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
        default=int(os.environ.get('PROTOCOL_PORT', 8080)),
        help='Port to listen on for protocol messages (default: 8080)'
    )
    
    parser.add_argument(
        '--mqtt-host',
        default=os.environ.get('MQTT_HOST', 'localhost'),
        help='MQTT broker host (default: localhost)'
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
        adapter.start()
        
        # Keep the script running
        while True:
            time.sleep(1)
    except Exception as e:
        logger.error(f"Error starting adapter: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())