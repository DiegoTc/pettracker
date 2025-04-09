"""
MQTT Client module for publishing device data to MQTT broker.
"""

import json
import logging
import os
from typing import Dict, Any

import paho.mqtt.client as mqtt

# Configure logging
logger = logging.getLogger(__name__)


class MQTTClient:
    """
    MQTT Client for publishing pet tracking data.
    
    This client handles connecting to an MQTT broker and publishing
    messages from tracking devices to appropriate topics.
    """
    
    def __init__(self, 
                broker_host: str = "localhost", 
                broker_port: int = 1883,
                client_id: str = "pet_tracker_adapter"):
        """
        Initialize the MQTT client.
        
        Args:
            broker_host: MQTT broker hostname or IP address
            broker_port: MQTT broker port
            client_id: Client ID for connecting to the broker
        """
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client_id = client_id
        self.client = mqtt.Client(client_id=client_id, clean_session=True, protocol=mqtt.MQTTv311)
        
        # Set up handlers
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        
        # Track connection status
        self.connected = False
        
        # Configure authentication if needed
        mqtt_username = os.environ.get("MQTT_USERNAME")
        mqtt_password = os.environ.get("MQTT_PASSWORD")
        
        if mqtt_username and mqtt_password:
            self.client.username_pw_set(mqtt_username, mqtt_password)
    
    def connect(self) -> bool:
        """
        Connect to the MQTT broker.
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        try:
            logger.info(f"Connecting to MQTT broker at {self.broker_host}:{self.broker_port}")
            self.client.connect(self.broker_host, self.broker_port)
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the MQTT broker."""
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("Disconnected from MQTT broker")
    
    def publish_device_data(self, device_id: str, data_type: str, payload: Dict[str, Any]) -> bool:
        """
        Publish device data to the MQTT broker.
        
        Args:
            device_id: Identifier for the device (IMEI or other unique ID)
            data_type: Type of data (location, status, etc.)
            payload: Dictionary containing the data to publish
            
        Returns:
            bool: True if message was published successfully, False otherwise
        """
        if not self.connected:
            logger.warning("Not connected to MQTT broker. Attempting reconnection...")
            self.connect()
            if not self.connected:
                logger.error("Failed to reconnect to MQTT broker")
                return False
        
        topic = f"devices/{device_id}/{data_type}"
        try:
            message = json.dumps(payload)
            result = self.client.publish(topic, message, qos=1)
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                logger.error(f"Failed to publish message to {topic}: {mqtt.error_string(result.rc)}")
                return False
            
            logger.debug(f"Published message to {topic}: {message}")
            return True
        except Exception as e:
            logger.error(f"Error publishing message to {topic}: {e}")
            return False
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when the client connects to the broker."""
        if rc == 0:
            self.connected = True
            logger.info("Connected to MQTT broker")
        else:
            self.connected = False
            logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects from the broker."""
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected disconnection from MQTT broker: {rc}")
        else:
            logger.info("Disconnected from MQTT broker")
    
    def _on_publish(self, client, userdata, mid):
        """Callback for when a message is published."""
        logger.debug(f"Message published (id: {mid})")