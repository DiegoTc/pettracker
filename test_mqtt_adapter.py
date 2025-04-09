#!/usr/bin/env python3
"""
Test the MQTT adapter functionality without relying on the database.

This script demonstrates the MQTT adapter with all components in a single process:
1. Starts an in-memory MQTT broker
2. Initializes the MQTT adapter
3. Simulates JT808 device messages
4. Verifies MQTT messages are published correctly
"""

import json
import logging
import os
import sys
import threading
import time
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import paho.mqtt.client as mqtt
    from services.mqtt_adapter import MQTTClient, ProtocolAdapter
    from tools.jt808_simulator import JT808DeviceSimulator
except ImportError as e:
    logger.error(f"Error importing required modules: {e}")
    logger.error("Make sure you've installed all dependencies with 'pip install paho-mqtt'")
    sys.exit(1)


class MQTTTestListener:
    """MQTT test listener to verify received messages"""
    
    def __init__(self):
        self.received_messages: List[Dict[str, Any]] = []
        self.client = mqtt.Client(client_id="test_listener")
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
    
    def connect(self, host="localhost", port=1883):
        """Connect to MQTT broker"""
        self.client.connect(host, port)
        self.client.loop_start()
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.client.loop_stop()
        self.client.disconnect()
    
    def _on_connect(self, client, userdata, flags, rc):
        """Subscribe to all device topics when connected"""
        client.subscribe("devices/#")
        logger.info("Test listener connected and subscribed to all device topics")
    
    def _on_message(self, client, userdata, msg):
        """Store received messages"""
        try:
            payload = json.loads(msg.payload)
            logger.info(f"Received message on {msg.topic}: {payload}")
            self.received_messages.append({
                "topic": msg.topic,
                "payload": payload
            })
        except json.JSONDecodeError:
            logger.warning(f"Received non-JSON message on {msg.topic}")
    
    def get_received_messages(self):
        """Get all received messages"""
        return self.received_messages


def main():
    """Run the MQTT adapter test"""
    logger.info("Starting MQTT adapter test")
    
    # Start the broker process on a different port (1884) to avoid conflicts
    broker_port = 1884
    os.system(f"mosquitto -p {broker_port} &")
    broker_pid = None
    
    try:
        # Wait for broker to start
        time.sleep(2)
        
        # Create test listener
        listener = MQTTTestListener()
        listener.connect(port=broker_port)
        
        # Create MQTT client for the adapter
        mqtt_client = MQTTClient(broker_port=broker_port)
        
        # Create and start the protocol adapter
        adapter = ProtocolAdapter(port=8081, mqtt_client=mqtt_client)
        adapter_thread = threading.Thread(target=adapter.start)
        adapter_thread.daemon = True
        adapter_thread.start()
        
        # Wait for adapter to start
        time.sleep(2)
        
        # Create and connect JT808 device simulator
        device = JT808DeviceSimulator(server_port=8081)
        if not device.connect():
            logger.error("Failed to connect simulator to adapter")
            return 1
        
        # Register the device
        if not device.send_registration():
            logger.error("Failed to register device")
            return 1
        
        # Send a heartbeat message
        device.send_heartbeat()
        
        # Send some location updates
        for _ in range(3):
            device.send_location()
            time.sleep(1)
        
        # Wait for messages to be processed
        time.sleep(2)
        
        # Get and print received messages
        messages = listener.get_received_messages()
        logger.info(f"Received {len(messages)} messages")
        
        # Verify we received at least one message
        if not messages:
            logger.error("No messages received")
            return 1
        
        # Check if we received location messages
        location_messages = [m for m in messages if '/location' in m['topic']]
        if not location_messages:
            logger.error("No location messages received")
            return 1
        
        logger.info("Test completed successfully")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        return 0
    
    finally:
        # Clean up
        if broker_pid:
            os.system(f"kill {broker_pid}")
        # Make sure all mosquitto processes are stopped
        os.system("pkill mosquitto")


if __name__ == "__main__":
    sys.exit(main())