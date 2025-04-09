"""
Protocol Adapter for converting JT/T 808 protocol messages to MQTT.

This module handles the TCP server that listens for incoming JT/T 808 messages,
parses them according to the protocol specification, and publishes the parsed
data to an MQTT broker.
"""

import binascii
import datetime
import json
import logging
import socket
import struct
import threading
import time
from typing import Dict, Any, Optional, Tuple, List, Union

from services.mqtt_adapter.mqtt_client import MQTTClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProtocolAdapter:
    """
    Protocol adapter for JT/T 808 to MQTT conversion.
    
    This adapter runs a TCP server that listens for incoming JT/T 808 messages,
    parses them, and publishes the extracted data to an MQTT broker.
    """
    
    # JT/T 808 Message Types
    MESSAGE_TYPES = {
        0x0001: "Terminal General Response",
        0x8001: "Platform General Response",
        0x0002: "Heartbeat",
        0x0100: "Terminal Registration",
        0x8100: "Terminal Registration Response",
        0x0003: "Terminal Logout",
        0x0102: "Terminal Authentication",
        0x8103: "Set Terminal Parameters",
        0x0200: "Location Information Report",
        0x8201: "Location Information Query Response"
    }
    
    def __init__(self, 
                host: str = "0.0.0.0", 
                port: int = 8080,
                mqtt_client: Optional[MQTTClient] = None,
                mqtt_host: str = "localhost",
                mqtt_port: int = 1883):
        """
        Initialize the protocol adapter.
        
        Args:
            host: Host address to bind the TCP server to
            port: Port to listen on
            mqtt_client: Optional pre-configured MQTT client
            mqtt_host: MQTT broker host (if mqtt_client not provided)
            mqtt_port: MQTT broker port (if mqtt_client not provided)
        """
        self.host = host
        self.port = port
        self.server_socket = None
        self.is_running = False
        self.client_threads = []
        
        # Use provided MQTT client or create a new one
        if mqtt_client:
            self.mqtt_client = mqtt_client
        else:
            self.mqtt_client = MQTTClient(broker_host=mqtt_host, 
                                         broker_port=mqtt_port, 
                                         client_id="jt808_adapter")
    
    def start(self) -> None:
        """Start the protocol adapter server."""
        if self.is_running:
            logger.warning("Protocol adapter is already running")
            return
        
        # Connect to MQTT broker
        self.mqtt_client.connect()
        
        # Start TCP server
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.is_running = True
            
            logger.info(f"Protocol adapter server started on {self.host}:{self.port}")
            
            # Main server loop
            self._server_loop()
        except Exception as e:
            logger.error(f"Error starting protocol adapter: {e}")
            self.stop()
    
    def _server_loop(self) -> None:
        """Main server loop that accepts incoming connections."""
        while self.is_running:
            try:
                client_socket, addr = self.server_socket.accept()
                logger.info(f"New connection from {addr}")
                
                # Start a new thread to handle the client
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, addr)
                )
                client_thread.daemon = True
                client_thread.start()
                self.client_threads.append(client_thread)
                
                # Clean up any dead threads
                self.client_threads = [t for t in self.client_threads if t.is_alive()]
            except Exception as e:
                if self.is_running:  # Only log if not stopped intentionally
                    logger.error(f"Error in server loop: {e}")
    
    def stop(self) -> None:
        """Stop the protocol adapter server."""
        self.is_running = False
        
        # Close server socket
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
        
        # Disconnect MQTT client
        self.mqtt_client.disconnect()
        
        logger.info("Protocol adapter server stopped")
    
    def _handle_client(self, client_socket: socket.socket, addr: Tuple[str, int]) -> None:
        """
        Handle communication with a connected client.
        
        Args:
            client_socket: Socket connected to the client
            addr: Address of the client
        """
        buffer = bytearray()
        client_socket.settimeout(60)  # 60 second timeout
        
        try:
            while self.is_running:
                # Read data from socket
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        logger.info(f"Connection closed by {addr}")
                        break
                    
                    # Add data to buffer
                    buffer.extend(data)
                    
                    # Process complete messages
                    while True:
                        # Find start and end markers
                        messages = self._extract_messages(buffer)
                        if not messages:
                            break
                        
                        # Process each message
                        for msg in messages:
                            try:
                                self._process_message(msg, client_socket)
                            except Exception as e:
                                logger.error(f"Error processing message: {e}")
                
                except socket.timeout:
                    # Just a timeout, continue
                    continue
                except Exception as e:
                    logger.error(f"Error reading from socket: {e}")
                    break
        
        finally:
            client_socket.close()
            logger.info(f"Closed connection from {addr}")
    
    def _extract_messages(self, buffer: bytearray) -> List[bytes]:
        """
        Extract complete messages from the buffer.
        
        Args:
            buffer: Byte buffer containing received data
            
        Returns:
            List of complete messages extracted from the buffer
        """
        messages = []
        
        # Search for message boundaries (0x7e)
        start_idx = -1
        for i in range(len(buffer)):
            if buffer[i] == 0x7e:
                if start_idx == -1:
                    # Found start of message
                    start_idx = i
                else:
                    # Found end of message
                    end_idx = i
                    
                    # Extract the message (including start/end markers)
                    message = bytes(buffer[start_idx:end_idx+1])
                    messages.append(message)
                    
                    # Reset start index for next message
                    start_idx = -1
        
        # Remove processed messages from buffer
        if messages:
            last_msg = messages[-1]
            end_pos = buffer.find(last_msg) + len(last_msg)
            del buffer[:end_pos]
        
        return messages
    
    def _process_message(self, message: bytes, client_socket: socket.socket) -> None:
        """
        Process a complete JT/T 808 message.
        
        Args:
            message: Complete JT/T 808 message including start/end markers
            client_socket: Socket to send responses back to the device
        """
        try:
            # First, unescape the message
            unescaped_msg = self._unescape_message(message)
            
            # Parse the message header and verify checksum
            parsed_msg = self._parse_jt808_message(unescaped_msg)
            if not parsed_msg:
                logger.warning("Failed to parse message or invalid checksum")
                return
            
            # Get device identifier (phone number in JT808 protocol)
            device_id = parsed_msg.get('phone_number')
            if not device_id:
                logger.warning("Message has no device identifier")
                return
            
            # Process based on message type
            msg_type = parsed_msg.get('msg_id')
            if not msg_type:
                logger.warning("Message has no message type")
                return
            
            # Handle different message types
            if msg_type == 0x0200:  # Location report
                self._handle_location_report(parsed_msg, device_id, client_socket)
            elif msg_type == 0x0002:  # Heartbeat
                self._handle_heartbeat(parsed_msg, device_id, client_socket)
            elif msg_type == 0x0100:  # Terminal registration
                self._handle_registration(parsed_msg, device_id, client_socket)
            else:
                logger.info(f"Received message type 0x{msg_type:04x} ({self.MESSAGE_TYPES.get(msg_type, 'Unknown')})")
                # Send general response
                self._send_general_response(client_socket, device_id, msg_type, parsed_msg.get('msg_serial', 0))
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def _handle_location_report(self, msg: Dict[str, Any], device_id: str, client_socket: socket.socket) -> None:
        """
        Handle a location report message.
        
        Args:
            msg: Parsed message dictionary
            device_id: Device identifier
            client_socket: Socket to send response
        """
        if 'location' not in msg:
            logger.warning("Location message missing location data")
            return
        
        loc = msg['location']
        
        # Create a payload for MQTT
        payload = {
            'device_id': device_id,
            'timestamp': loc.get('timestamp', datetime.datetime.utcnow().isoformat()),
            'latitude': loc.get('latitude'),
            'longitude': loc.get('longitude'),
            'altitude': loc.get('altitude'),
            'speed': loc.get('speed'),
            'heading': loc.get('course'),
            'satellite_count': loc.get('satellite_count'),
            'battery_level': loc.get('battery_level'),
            'activity_level': loc.get('activity_level'),
            'temperature': loc.get('temperature'),
            'health_flags': loc.get('health_flags'),
            'raw_status': loc.get('status', 0)
        }
        
        # Status flags
        status = loc.get('status', 0)
        if status is not None:
            payload['status'] = {
                'acc_on': bool(status & 0x01),
                'gps_positioned': bool(status & 0x02),
                'latitude_type': 'South' if status & 0x04 else 'North',
                'longitude_type': 'West' if status & 0x08 else 'East',
                'moving': bool(status & 0x10),
                'vehicle_status': bool(status & 0x20),
            }
        
        # Filter out None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        # Publish to MQTT
        success = self.mqtt_client.publish_device_data(device_id, "location", payload)
        if success:
            logger.info(f"Published location data for device {device_id}")
        else:
            logger.error(f"Failed to publish location data for device {device_id}")
        
        # Send response to device
        self._send_general_response(client_socket, device_id, msg.get('msg_id'), msg.get('msg_serial', 0))
    
    def _handle_heartbeat(self, msg: Dict[str, Any], device_id: str, client_socket: socket.socket) -> None:
        """
        Handle a heartbeat message.
        
        Args:
            msg: Parsed message dictionary
            device_id: Device identifier
            client_socket: Socket to send response
        """
        # Create payload for MQTT
        payload = {
            'device_id': device_id,
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'message_type': 'heartbeat'
        }
        
        # Publish to MQTT
        success = self.mqtt_client.publish_device_data(device_id, "status", payload)
        if success:
            logger.info(f"Published heartbeat for device {device_id}")
        else:
            logger.error(f"Failed to publish heartbeat for device {device_id}")
        
        # Send response to device
        self._send_general_response(client_socket, device_id, msg.get('msg_id'), msg.get('msg_serial', 0))
    
    def _handle_registration(self, msg: Dict[str, Any], device_id: str, client_socket: socket.socket) -> None:
        """
        Handle a terminal registration message.
        
        Args:
            msg: Parsed message dictionary
            device_id: Device identifier
            client_socket: Socket to send response
        """
        # Extract registration info
        reg_info = {}
        if 'province_id' in msg:
            reg_info['province_id'] = msg['province_id']
        if 'city_id' in msg:
            reg_info['city_id'] = msg['city_id']
        if 'manufacturer_id' in msg:
            reg_info['manufacturer_id'] = msg['manufacturer_id']
        if 'terminal_model' in msg:
            reg_info['terminal_model'] = msg['terminal_model']
        if 'terminal_id' in msg:
            reg_info['terminal_id'] = msg['terminal_id']
        if 'license_plate_color' in msg:
            reg_info['license_plate_color'] = msg['license_plate_color']
        if 'license_plate' in msg:
            reg_info['license_plate'] = msg['license_plate']
        
        # Create payload for MQTT
        payload = {
            'device_id': device_id,
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'message_type': 'registration',
            'registration_info': reg_info
        }
        
        # Publish to MQTT
        success = self.mqtt_client.publish_device_data(device_id, "status", payload)
        if success:
            logger.info(f"Published registration info for device {device_id}")
        else:
            logger.error(f"Failed to publish registration info for device {device_id}")
        
        # Send registration response to device
        self._send_registration_response(client_socket, device_id, msg.get('msg_serial', 0), 0, "SUCCESS")
    
    def _send_general_response(self, client_socket: socket.socket, phone_number: str, 
                              msg_id: int, serial_number: int, result: int = 0) -> None:
        """
        Send a general response message to the device.
        
        Args:
            client_socket: Socket to send response
            phone_number: Device phone number (identifier)
            msg_id: Message ID being responded to
            serial_number: Serial number of the message being responded to
            result: Result code (0=success, 1=failure, etc.)
        """
        try:
            # Create platform general response (0x8001)
            response = self._create_general_response(phone_number, msg_id, serial_number, result)
            
            # Send the response
            client_socket.send(response)
            logger.debug(f"Sent general response to device {phone_number}")
        except Exception as e:
            logger.error(f"Error sending general response: {e}")
    
    def _send_registration_response(self, client_socket: socket.socket, phone_number: str, 
                                  serial_number: int, result: int = 0, auth_code: str = "") -> None:
        """
        Send a registration response message to the device.
        
        Args:
            client_socket: Socket to send response
            phone_number: Device phone number (identifier)
            serial_number: Serial number of the message being responded to
            result: Result code (0=success, 1=failure, etc.)
            auth_code: Authentication code for successful registration
        """
        try:
            # Create registration response (0x8100)
            response = self._create_registration_response(phone_number, serial_number, result, auth_code)
            
            # Send the response
            client_socket.send(response)
            logger.debug(f"Sent registration response to device {phone_number}")
        except Exception as e:
            logger.error(f"Error sending registration response: {e}")
    
    def _unescape_message(self, message: bytes) -> bytes:
        """
        Unescape a JT/T 808 message.
        
        In JT/T 808, 0x7d followed by 0x01 represents 0x7d,
        and 0x7d followed by 0x02 represents 0x7e.
        
        Args:
            message: Escaped message bytes
            
        Returns:
            Unescaped message bytes
        """
        # Strip start/end markers
        if message.startswith(b'\x7e') and message.endswith(b'\x7e'):
            message = message[1:-1]
        
        # Handle escape sequences
        result = bytearray()
        i = 0
        while i < len(message):
            if message[i] == 0x7d and i + 1 < len(message):
                if message[i + 1] == 0x01:
                    result.append(0x7d)
                    i += 2
                elif message[i + 1] == 0x02:
                    result.append(0x7e)
                    i += 2
                else:
                    result.append(message[i])
                    i += 1
            else:
                result.append(message[i])
                i += 1
        
        return bytes(result)
    
    def _parse_jt808_message(self, data: bytes) -> Optional[Dict[str, Any]]:
        """
        Parse a JT/T 808 message.
        
        Args:
            data: Unescaped message bytes (without start/end markers)
            
        Returns:
            Dictionary containing the parsed message, or None on error
        """
        try:
            if len(data) < 12:  # Minimum header size
                logger.warning(f"Message too short: {len(data)} bytes")
                return None
            
            # Check checksum
            if not self._verify_checksum(data):
                logger.warning("Invalid checksum")
                return None
            
            # Parse header
            msg_id = struct.unpack('>H', data[0:2])[0]
            msg_props = struct.unpack('>H', data[2:4])[0]
            
            # Extract message properties
            msg_length = msg_props & 0x03FF  # First 10 bits
            has_subpackages = bool(msg_props & 0x2000)  # 13th bit
            
            # Phone number (device ID) - 6 bytes BCD
            phone_bytes = data[4:10]
            phone_number = ''.join([f'{b:02x}' for b in phone_bytes]).upper()
            
            # Message serial number - 2 bytes
            msg_serial = struct.unpack('>H', data[10:12])[0]
            
            # Initialize result dictionary
            result = {
                'msg_id': msg_id,
                'msg_props': msg_props,
                'msg_length': msg_length,
                'has_subpackages': has_subpackages,
                'phone_number': phone_number,
                'msg_serial': msg_serial,
                'msg_type': self.MESSAGE_TYPES.get(msg_id, 'Unknown')
            }
            
            # Handle subpackage information if present
            idx = 12
            if has_subpackages:
                result['total_subpackages'] = struct.unpack('>H', data[idx:idx+2])[0]
                idx += 2
                result['subpackage_seq'] = struct.unpack('>H', data[idx:idx+2])[0]
                idx += 2
            
            # Message body (without checksum)
            body = data[idx:-1]
            
            # Process message body based on message type
            if msg_id == 0x0200:  # Location information
                self._parse_location_information(body, result)
            elif msg_id == 0x0100:  # Terminal registration
                self._parse_terminal_registration(body, result)
            elif msg_id == 0x0102:  # Terminal authentication
                result['authentication_code'] = body.decode('ascii')
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing JT808 message: {e}")
            return None
    
    def _parse_location_information(self, body: bytes, result: Dict[str, Any]) -> None:
        """
        Parse location information message body.
        
        Args:
            body: Message body bytes
            result: Dictionary to update with parsed fields
        """
        if len(body) < 28:  # Basic location info size
            logger.warning("Location message too short")
            return
        
        # Parse basic positional information
        status = struct.unpack('>I', body[0:4])[0]
        latitude = struct.unpack('>I', body[4:8])[0] / 1000000.0
        longitude = struct.unpack('>I', body[8:12])[0] / 1000000.0
        altitude = struct.unpack('>H', body[12:14])[0]
        speed = struct.unpack('>H', body[14:16])[0] / 10.0  # In km/h
        course = struct.unpack('>H', body[16:18])[0]
        
        # BCD time: YY-MM-DD-HH-MM-SS
        time_bytes = body[18:24]
        time_str = ''.join([f'{b:02x}' for b in time_bytes])
        year = int(time_str[0:2]) + 2000
        month = int(time_str[2:4])
        day = int(time_str[4:6])
        hour = int(time_str[6:8])
        minute = int(time_str[8:10])
        second = int(time_str[10:12])
        
        try:
            timestamp = datetime.datetime(year, month, day, hour, minute, second).isoformat()
        except ValueError:
            # Handle invalid dates
            timestamp = datetime.datetime.utcnow().isoformat()
            logger.warning(f"Invalid date in location message: {time_str}")
        
        location = {
            'status': status,
            'latitude': latitude,
            'longitude': longitude,
            'altitude': altitude,
            'speed': speed,
            'course': course,
            'timestamp': timestamp
        }
        
        # Parse additional data
        idx = 24
        while idx < len(body):
            if idx + 2 > len(body):
                break
            
            # Each additional item has ID (1 byte) and length (1 byte)
            item_id = body[idx]
            item_len = body[idx + 1]
            idx += 2
            
            if idx + item_len > len(body):
                break
            
            item_data = body[idx:idx+item_len]
            idx += item_len
            
            # Process additional data based on item ID
            if item_id == 0x01:  # Mileage
                location['mileage'] = struct.unpack('>I', item_data)[0] / 10.0  # In km
            elif item_id == 0x02:  # Fuel
                location['fuel'] = struct.unpack('>H', item_data)[0] / 10.0  # In liters
            elif item_id == 0x03:  # Speed from vehicle
                location['vehicle_speed'] = struct.unpack('>H', item_data)[0] / 10.0  # In km/h
            elif item_id == 0x30:  # Signal strength
                location['signal_strength'] = item_data[0]
            elif item_id == 0x31:  # GNSS satellite count
                location['satellite_count'] = item_data[0]
            
            # Custom extensions for pet tracking
            elif item_id == 0xE0:  # Battery level (0-100%)
                location['battery_level'] = item_data[0]
            elif item_id == 0xE1:  # Activity level (0-100%)
                location['activity_level'] = item_data[0]
            elif item_id == 0xE2:  # Health flags (bit flags)
                location['health_flags'] = struct.unpack('>H', item_data)[0]
            elif item_id == 0xE3:  # Temperature (celsius x 10)
                location['temperature'] = struct.unpack('>H', item_data)[0] / 10.0
        
        result['location'] = location
    
    def _parse_terminal_registration(self, body: bytes, result: Dict[str, Any]) -> None:
        """
        Parse terminal registration message body.
        
        Args:
            body: Message body bytes
            result: Dictionary to update with parsed fields
        """
        if len(body) < 37:  # Minimum registration info size
            logger.warning("Registration message too short")
            return
        
        # Province ID (2 bytes)
        result['province_id'] = struct.unpack('>H', body[0:2])[0]
        
        # City ID (2 bytes)
        result['city_id'] = struct.unpack('>H', body[2:4])[0]
        
        # Manufacturer ID (5 bytes)
        result['manufacturer_id'] = body[4:9].decode('ascii')
        
        # Terminal model (20 bytes)
        result['terminal_model'] = body[9:29].decode('ascii').rstrip('\x00')
        
        # Terminal ID (7 bytes)
        result['terminal_id'] = body[29:36].decode('ascii')
        
        # License plate color (1 byte)
        result['license_plate_color'] = body[36]
        
        # License plate (variable length)
        if len(body) > 37:
            try:
                result['license_plate'] = body[37:].decode('utf-8')
            except UnicodeDecodeError:
                # Try with GBK encoding (common in China)
                try:
                    result['license_plate'] = body[37:].decode('gbk')
                except UnicodeDecodeError:
                    result['license_plate'] = binascii.hexlify(body[37:]).decode('ascii')
    
    def _verify_checksum(self, data: bytes) -> bool:
        """
        Verify the checksum of a JT/T 808 message.
        
        The checksum is the XOR of all bytes excluding the checksum byte itself.
        
        Args:
            data: Message data including the checksum byte
            
        Returns:
            True if the checksum is valid, False otherwise
        """
        if len(data) < 2:
            return False
        
        # Extract the checksum (last byte)
        received_checksum = data[-1]
        
        # Calculate the checksum (XOR of all bytes except the last one)
        calculated_checksum = 0
        for b in data[:-1]:
            calculated_checksum ^= b
        
        return calculated_checksum == received_checksum
    
    def _create_general_response(self, phone_number: str, msg_id: int, 
                                serial_number: int, result: int = 0) -> bytes:
        """
        Create a general response message in JT808 protocol format (0x8001).
        
        Args:
            phone_number: The phone number (device ID) to respond to
            msg_id: The message ID being responded to
            serial_number: The serial number of the message being responded to
            result: Result code (0=success, 1=failure, etc.)
            
        Returns:
            Bytes containing the encoded response message
        """
        # Message ID: 0x8001 (Platform General Response)
        msg_id_bytes = struct.pack('>H', 0x8001)
        
        # Message properties: message body length = 5 bytes
        msg_props_bytes = struct.pack('>H', 5)
        
        # Phone number: 6 BCD bytes
        phone_bytes = bytearray(6)
        for i in range(min(len(phone_number), 12)):
            if i % 2 == 0:
                phone_bytes[i // 2] = (int(phone_number[i], 16) << 4)
            else:
                phone_bytes[i // 2] |= int(phone_number[i], 16)
        
        # Message serial number
        serial_bytes = struct.pack('>H', serial_number)
        
        # Message body
        # - Response serial number (2 bytes)
        # - Message ID that is being responded to (2 bytes)
        # - Result (1 byte)
        body = struct.pack('>HHB', serial_number, msg_id, result)
        
        # Calculate checksum (XOR of all header and body bytes)
        message = msg_id_bytes + msg_props_bytes + phone_bytes + serial_bytes + body
        checksum = 0
        for b in message:
            checksum ^= b
        
        # Construct the final message
        final_message = bytearray()
        final_message.append(0x7e)  # Start marker
        
        # Escape the message bytes
        for b in message:
            if b == 0x7e:
                final_message.append(0x7d)
                final_message.append(0x02)
            elif b == 0x7d:
                final_message.append(0x7d)
                final_message.append(0x01)
            else:
                final_message.append(b)
        
        # Append checksum (escaped if needed)
        if checksum == 0x7e:
            final_message.append(0x7d)
            final_message.append(0x02)
        elif checksum == 0x7d:
            final_message.append(0x7d)
            final_message.append(0x01)
        else:
            final_message.append(checksum)
        
        final_message.append(0x7e)  # End marker
        
        return bytes(final_message)
    
    def _create_registration_response(self, phone_number: str, serial_number: int, 
                                    result: int = 0, auth_code: str = "") -> bytes:
        """
        Create a terminal registration response message (0x8100).
        
        Args:
            phone_number: The phone number (device ID) to respond to
            serial_number: The serial number of the message being responded to
            result: Result code (0=success, 1=failure, etc.)
            auth_code: Authentication code string (only needed for successful registration)
            
        Returns:
            Bytes containing the encoded response message
        """
        # Message ID: 0x8100 (Terminal Registration Response)
        msg_id_bytes = struct.pack('>H', 0x8100)
        
        # Message body length: 3 + len(auth_code) if success, otherwise 3
        body_length = 3 + len(auth_code) if result == 0 and auth_code else 3
        
        # Message properties: message body length
        msg_props_bytes = struct.pack('>H', body_length)
        
        # Phone number: 6 BCD bytes
        phone_bytes = bytearray(6)
        for i in range(min(len(phone_number), 12)):
            if i % 2 == 0:
                phone_bytes[i // 2] = (int(phone_number[i], 16) << 4)
            else:
                phone_bytes[i // 2] |= int(phone_number[i], 16)
        
        # Message serial number
        serial_bytes = struct.pack('>H', serial_number)
        
        # Message body
        # - Response serial number (2 bytes)
        # - Result (1 byte)
        # - Authentication code (variable length, only if result == 0)
        body = struct.pack('>HB', serial_number, result)
        if result == 0 and auth_code:
            body += auth_code.encode('ascii')
        
        # Calculate checksum (XOR of all header and body bytes)
        message = msg_id_bytes + msg_props_bytes + phone_bytes + serial_bytes + body
        checksum = 0
        for b in message:
            checksum ^= b
        
        # Construct the final message
        final_message = bytearray()
        final_message.append(0x7e)  # Start marker
        
        # Escape the message bytes
        for b in message:
            if b == 0x7e:
                final_message.append(0x7d)
                final_message.append(0x02)
            elif b == 0x7d:
                final_message.append(0x7d)
                final_message.append(0x01)
            else:
                final_message.append(b)
        
        # Append checksum (escaped if needed)
        if checksum == 0x7e:
            final_message.append(0x7d)
            final_message.append(0x02)
        elif checksum == 0x7d:
            final_message.append(0x7d)
            final_message.append(0x01)
        else:
            final_message.append(checksum)
        
        final_message.append(0x7e)  # End marker
        
        return bytes(final_message)