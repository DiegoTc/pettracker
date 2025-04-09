#!/usr/bin/env python3
"""
MQTT Subscriber for pet tracking data.

This script subscribes to all pet tracking topics on the MQTT broker
and prints received messages.
"""

import argparse
import json
import logging
import os
import signal
import sys
import time

import paho.mqtt.client as mqtt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MQTTSubscriber:
    """
    MQTT Subscriber for pet tracking data.
    
    This class connects to an MQTT broker and subscribes to
    relevant topics for pet tracking.
    """
    
    def __init__(self, 
                host: str = "localhost", 
                port: int = 1883,
                client_id: str = "pet_tracker_subscriber",
                topics: list = None):
        """
        Initialize the MQTT subscriber.
        
        Args:
            host: MQTT broker hostname or IP
            port: MQTT broker port
            client_id: Client ID for the MQTT connection
            topics: List of topics to subscribe to (defaults to all pet tracking topics)
        """
        self.host = host
        self.port = port
        self.client_id = client_id
        self.topics = topics or ["devices/#"]
        
        # Create MQTT client
        self.client = mqtt.Client(client_id=client_id, clean_session=True)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        # Configure authentication if needed
        mqtt_username = os.environ.get("MQTT_USERNAME")
        mqtt_password = os.environ.get("MQTT_PASSWORD")
        
        if mqtt_username and mqtt_password:
            self.client.username_pw_set(mqtt_username, mqtt_password)
    
    def connect(self) -> bool:
        """
        Connect to the MQTT broker.
        
        Returns:
            bool: True if connected successfully, False otherwise
        """
        try:
            logger.info(f"Connecting to MQTT broker at {self.host}:{self.port}")
            self.client.connect(self.host, self.port)
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def start(self) -> None:
        """Start the MQTT client loop and subscribe to topics."""
        self.client.loop_start()
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Subscriber stopped by user")
        finally:
            self.stop()
    
    def stop(self) -> None:
        """Stop the MQTT client."""
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("Disconnected from MQTT broker")
    
    def _on_connect(self, client, userdata, flags, rc):
        """
        Callback for when the client connects to the broker.
        
        Args:
            client: MQTT client instance
            userdata: User data passed to the client
            flags: Response flags from the broker
            rc: Connection result code
        """
        if rc == 0:
            logger.info(f"Connected to MQTT broker at {self.host}:{self.port}")
            
            # Subscribe to all topics
            for topic in self.topics:
                logger.info(f"Subscribing to topic: {topic}")
                self.client.subscribe(topic)
        else:
            logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """
        Callback for when the client disconnects from the broker.
        
        Args:
            client: MQTT client instance
            userdata: User data passed to the client
            rc: Disconnection result code
        """
        if rc != 0:
            logger.warning(f"Unexpected disconnection from MQTT broker: {rc}")
        else:
            logger.info("Disconnected from MQTT broker")
    
    def _on_message(self, client, userdata, msg):
        """
        Callback for when a message is received from the broker.
        
        Args:
            client: MQTT client instance
            userdata: User data passed to the client
            msg: Received message
        """
        try:
            # Try to parse as JSON
            payload = json.loads(msg.payload)
            
            # Format the JSON for display
            formatted_json = json.dumps(payload, indent=2)
            
            logger.info(f"Received message on topic {msg.topic}:\n{formatted_json}")
        except json.JSONDecodeError:
            # If not JSON, just print as string
            logger.info(f"Received message on topic {msg.topic}: {msg.payload}")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='MQTT Subscriber for Pet Tracking')
    
    parser.add_argument(
        '--host',
        default='localhost',
        help='MQTT broker hostname or IP (default: localhost)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=1883,
        help='MQTT broker port (default: 1883)'
    )
    
    parser.add_argument(
        '--topic',
        action='append',
        help='Topic to subscribe to (can be specified multiple times, default: devices/#)'
    )
    
    parser.add_argument(
        '--client-id',
        default=f'pet_tracker_subscriber_{int(time.time())}',
        help='Client ID for MQTT connection (default: auto-generated)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    return parser.parse_args()


def main():
    """Main entry point for the subscriber"""
    args = parse_arguments()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create subscriber
    subscriber = MQTTSubscriber(
        host=args.host,
        port=args.port,
        client_id=args.client_id,
        topics=args.topic
    )
    
    # Handle graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Shutting down subscriber...")
        subscriber.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Connect and start subscribing
    if subscriber.connect():
        subscriber.start()
    else:
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())