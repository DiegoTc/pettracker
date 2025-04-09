#!/usr/bin/env python3
"""
JT808 Device Simulator

This script simulates a GPS tracking device using the JT/T 808 protocol.
It connects to a protocol server and sends location messages at regular intervals.
"""

import argparse
import binascii
import datetime
import logging
import random
import socket
import struct
import sys
import time
from typing import Any, Dict, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JT808DeviceSimulator:
    """
    Simulator for a JT/T 808 protocol compatible device.
    
    This class creates and sends JT/T 808 protocol messages to a server,
    simulating a GPS tracking device.
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
                 server_host: str = "localhost", 
                 server_port: int = 8080,
                 device_id: str = None,
                 manufacturer_id: str = "PETTR",
                 terminal_model: str = "PT100",
                 initial_latitude: float = 37.7749,
                 initial_longitude: float = -122.4194,
                 move_randomly: bool = True):
        """
        Initialize the JT808 device simulator.
        
        Args:
            server_host: Protocol server hostname or IP
            server_port: Protocol server port
            device_id: Device ID (phone number in JT808 terms)
            manufacturer_id: Manufacturer identifier (5 chars)
            terminal_model: Terminal model identifier (20 chars max)
            initial_latitude: Starting latitude
            initial_longitude: Starting longitude
            move_randomly: Whether to simulate random movement
        """
        self.server_host = server_host
        self.server_port = server_port
        
        # Generate a random device ID if none provided
        if device_id is None:
            device_id = ''.join([str(random.randint(0, 9)) for _ in range(12)])
        self.device_id = device_id
        
        # Make sure manufacturer ID is exactly 5 chars
        self.manufacturer_id = manufacturer_id[:5].ljust(5)
        
        # Make sure terminal model is at most 20 chars
        self.terminal_model = terminal_model[:20].ljust(20)
        
        # Terminal unique ID
        self.terminal_id = f'SIM{random.randint(10000, 99999):05d}'
        
        # Current position
        self.latitude = initial_latitude
        self.longitude = initial_longitude
        self.altitude = 10.0 + random.random() * 20.0
        self.speed = 0.0
        self.heading = random.randint(0, 359)
        
        # Current battery level and other pet-specific metrics
        self.battery_level = 100.0
        self.activity_level = 50.0
        self.health_flags = 0
        self.temperature = 37.5  # Normal pet temperature in Celsius
        
        # Message sequence number
        self.seq_num = 0
        
        # Connection state
        self.socket = None
        self.connected = False
        self.registered = False
        self.authenticated = False
        
        # Movement simulation
        self.move_randomly = move_randomly
    
    def connect(self) -> bool:
        """
        Connect to the protocol server.
        
        Returns:
            bool: True if connected successfully, False otherwise
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            self.connected = True
            logger.info(f"Connected to server at {self.server_host}:{self.server_port}")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self.connected = False
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the protocol server."""
        if self.socket:
            self.socket.close()
            self.socket = None
        self.connected = False
        self.registered = False
        self.authenticated = False
        logger.info("Disconnected from server")
    
    def send_registration(self) -> bool:
        """
        Send a registration message to the server.
        
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.connected:
            logger.warning("Not connected to server")
            return False
        
        # Create registration message
        msg = self._create_registration_message()
        
        # Send the message
        try:
            self.socket.send(msg)
            logger.info(f"Sent registration message for device {self.device_id}")
            
            # Wait for response
            response = self._wait_for_response()
            if response:
                msg_id = response.get('msg_id')
                if msg_id == 0x8100:  # Registration response
                    result = response.get('result', 0xFF)
                    if result == 0:
                        self.registered = True
                        logger.info("Registration successful")
                        return True
                    else:
                        logger.warning(f"Registration failed with result code: {result}")
            
            return False
        except Exception as e:
            logger.error(f"Error sending registration: {e}")
            return False
    
    def send_authentication(self, auth_code: str) -> bool:
        """
        Send an authentication message to the server.
        
        Args:
            auth_code: Authentication code to send
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.connected:
            logger.warning("Not connected to server")
            return False
        
        # Create authentication message
        msg = self._create_authentication_message(auth_code)
        
        # Send the message
        try:
            self.socket.send(msg)
            logger.info(f"Sent authentication message for device {self.device_id}")
            
            # Wait for response
            response = self._wait_for_response()
            if response:
                msg_id = response.get('msg_id')
                if msg_id == 0x8001:  # General response
                    result = response.get('result', 0xFF)
                    if result == 0:
                        self.authenticated = True
                        logger.info("Authentication successful")
                        return True
                    else:
                        logger.warning(f"Authentication failed with result code: {result}")
            
            return False
        except Exception as e:
            logger.error(f"Error sending authentication: {e}")
            return False
    
    def send_heartbeat(self) -> bool:
        """
        Send a heartbeat message to the server.
        
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.connected:
            logger.warning("Not connected to server")
            return False
        
        # Create heartbeat message
        msg = self._create_heartbeat_message()
        
        # Send the message
        try:
            self.socket.send(msg)
            logger.debug(f"Sent heartbeat message for device {self.device_id}")
            return True
        except Exception as e:
            logger.error(f"Error sending heartbeat: {e}")
            return False
    
    def send_location(self) -> bool:
        """
        Send a location message to the server.
        
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.connected:
            logger.warning("Not connected to server")
            return False
        
        # Update battery level (slowly decrease)
        self.battery_level = max(0.0, self.battery_level - random.random() * 0.1)
        
        # Simulate pet activity level (random changes)
        self.activity_level = max(0.0, min(100.0, self.activity_level + random.uniform(-5.0, 5.0)))
        
        # Simulate pet temperature (normal with small variations)
        self.temperature = max(35.0, min(40.0, self.temperature + random.uniform(-0.1, 0.1)))
        
        # Update position if movement simulation is enabled
        if self.move_randomly:
            self._simulate_movement()
        
        # Create location message
        msg = self._create_location_message()
        
        # Send the message
        try:
            self.socket.send(msg)
            logger.info(f"Sent location message for device {self.device_id}: "
                        f"({self.latitude:.6f}, {self.longitude:.6f}), "
                        f"battery: {self.battery_level:.1f}%, "
                        f"activity: {self.activity_level:.1f}%, "
                        f"temp: {self.temperature:.1f}°C")
            return True
        except Exception as e:
            logger.error(f"Error sending location: {e}")
            return False
    
    def _simulate_movement(self) -> None:
        """Simulate random movement by updating position."""
        # Simulate a pet walking around
        # Calculate new position based on heading and speed
        self.heading = (self.heading + random.randint(-20, 20)) % 360
        self.speed = max(0.0, min(5.0, self.speed + random.uniform(-0.5, 0.5)))
        
        # Calculate new position (very simple approximation)
        self.latitude += math.sin(math.radians(self.heading)) * self.speed * 0.00001
        self.longitude += math.cos(math.radians(self.heading)) * self.speed * 0.00001
        
        # Update altitude
        self.altitude = max(0.0, min(100.0, self.altitude + random.uniform(-1.0, 1.0)))
    
    def _create_registration_message(self) -> bytes:
        """
        Create a terminal registration message (0x0100).
        
        Returns:
            bytes: Encoded JT808 message
        """
        self.seq_num = (self.seq_num + 1) % 0xFFFF
        
        # Message ID: 0x0100 (Terminal Registration)
        msg_id_bytes = struct.pack('>H', 0x0100)
        
        # Message body:
        # - Province ID (2 bytes): 0
        # - City ID (2 bytes): 0
        # - Manufacturer ID (5 bytes): ASCII
        # - Terminal model (20 bytes): ASCII
        # - Terminal ID (7 bytes): ASCII
        # - License plate color (1 byte): 0 (no license plate)
        # - License plate: Empty
        body = struct.pack('>HH', 0, 0)
        body += self.manufacturer_id.encode('ascii')
        body += self.terminal_model.encode('ascii')
        body += self.terminal_id.encode('ascii').ljust(7, b'\x00')
        body += struct.pack('B', 0)  # No license plate
        
        # Message properties: body length
        msg_props_bytes = struct.pack('>H', len(body))
        
        # Phone number (device ID): convert to BCD
        phone_bytes = bytearray(6)
        for i in range(min(len(self.device_id), 12)):
            if i % 2 == 0:
                phone_bytes[i // 2] = (int(self.device_id[i]) << 4)
            else:
                phone_bytes[i // 2] |= int(self.device_id[i])
        
        # Message serial number
        serial_bytes = struct.pack('>H', self.seq_num)
        
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
    
    def _create_authentication_message(self, auth_code: str) -> bytes:
        """
        Create a terminal authentication message (0x0102).
        
        Args:
            auth_code: Authentication code string
            
        Returns:
            bytes: Encoded JT808 message
        """
        self.seq_num = (self.seq_num + 1) % 0xFFFF
        
        # Message ID: 0x0102 (Terminal Authentication)
        msg_id_bytes = struct.pack('>H', 0x0102)
        
        # Message body is just the authentication code as ASCII
        body = auth_code.encode('ascii')
        
        # Message properties: body length
        msg_props_bytes = struct.pack('>H', len(body))
        
        # Phone number (device ID): convert to BCD
        phone_bytes = bytearray(6)
        for i in range(min(len(self.device_id), 12)):
            if i % 2 == 0:
                phone_bytes[i // 2] = (int(self.device_id[i]) << 4)
            else:
                phone_bytes[i // 2] |= int(self.device_id[i])
        
        # Message serial number
        serial_bytes = struct.pack('>H', self.seq_num)
        
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
    
    def _create_heartbeat_message(self) -> bytes:
        """
        Create a heartbeat message (0x0002).
        
        Returns:
            bytes: Encoded JT808 message
        """
        self.seq_num = (self.seq_num + 1) % 0xFFFF
        
        # Message ID: 0x0002 (Heartbeat)
        msg_id_bytes = struct.pack('>H', 0x0002)
        
        # Message body is empty for heartbeat
        body = b''
        
        # Message properties: body length
        msg_props_bytes = struct.pack('>H', len(body))
        
        # Phone number (device ID): convert to BCD
        phone_bytes = bytearray(6)
        for i in range(min(len(self.device_id), 12)):
            if i % 2 == 0:
                phone_bytes[i // 2] = (int(self.device_id[i]) << 4)
            else:
                phone_bytes[i // 2] |= int(self.device_id[i])
        
        # Message serial number
        serial_bytes = struct.pack('>H', self.seq_num)
        
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
    
    def _create_location_message(self) -> bytes:
        """
        Create a location message (0x0200).
        
        Returns:
            bytes: Encoded JT808 message
        """
        self.seq_num = (self.seq_num + 1) % 0xFFFF
        
        # Message ID: 0x0200 (Location)
        msg_id_bytes = struct.pack('>H', 0x0200)
        
        # Message body:
        # - Alarm flag (4 bytes): 0
        # - Status (4 bytes): 0 (ACC off, not positioned)
        # - Latitude (4 bytes): degrees * 1,000,000
        # - Longitude (4 bytes): degrees * 1,000,000
        # - Altitude (2 bytes): meters
        # - Speed (2 bytes): 0.1 km/h
        # - Direction (2 bytes): 0-359 degrees
        # - Time (6 bytes): BCD YY-MM-DD-HH-MM-SS
        
        # Status flags (bit 0: ACC, bit 1: positioned, etc.)
        status = 0
        status |= 0x02  # Bit 1: Positioned
        if self.latitude < 0:
            status |= 0x04  # Bit 2: South latitude
        if self.longitude < 0:
            status |= 0x08  # Bit 3: West longitude
        if self.speed > 0:
            status |= 0x10  # Bit 4: Moving
        
        # Convert latitude/longitude to JT808 format (absolute value * 1,000,000)
        lat_int = int(abs(self.latitude) * 1000000)
        lon_int = int(abs(self.longitude) * 1000000)
        
        # Convert speed to 0.1 km/h
        speed_int = int(self.speed * 10)
        
        # Get current time as BCD
        now = datetime.datetime.now()
        year = now.year % 100
        month = now.month
        day = now.day
        hour = now.hour
        minute = now.minute
        second = now.second
        
        # Convert time to BCD format
        time_bytes = bytearray(6)
        time_bytes[0] = ((year // 10) << 4) | (year % 10)
        time_bytes[1] = ((month // 10) << 4) | (month % 10)
        time_bytes[2] = ((day // 10) << 4) | (day % 10)
        time_bytes[3] = ((hour // 10) << 4) | (hour % 10)
        time_bytes[4] = ((minute // 10) << 4) | (minute % 10)
        time_bytes[5] = ((second // 10) << 4) | (second % 10)
        
        # Put together the base location data
        body = struct.pack('>IIIIHHH', 0, status, lat_int, lon_int, 
                          int(self.altitude), speed_int, int(self.heading))
        body += bytes(time_bytes)
        
        # Additional location data elements:
        
        # 0xE0: Battery level (0-100%)
        body += struct.pack('BB', 0xE0, 1)  # ID, length
        body += struct.pack('B', int(self.battery_level))
        
        # 0xE1: Activity level (0-100%)
        body += struct.pack('BB', 0xE1, 1)  # ID, length
        body += struct.pack('B', int(self.activity_level))
        
        # 0xE2: Health flags (bit flags)
        body += struct.pack('BB', 0xE2, 2)  # ID, length
        body += struct.pack('>H', self.health_flags)
        
        # 0xE3: Temperature (celsius x 10)
        body += struct.pack('BB', 0xE3, 2)  # ID, length
        body += struct.pack('>H', int(self.temperature * 10))
        
        # Message properties: body length
        msg_props_bytes = struct.pack('>H', len(body))
        
        # Phone number (device ID): convert to BCD
        phone_bytes = bytearray(6)
        for i in range(min(len(self.device_id), 12)):
            if i % 2 == 0:
                phone_bytes[i // 2] = (int(self.device_id[i]) << 4)
            else:
                phone_bytes[i // 2] |= int(self.device_id[i])
        
        # Message serial number
        serial_bytes = struct.pack('>H', self.seq_num)
        
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
    
    def _wait_for_response(self, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
        """
        Wait for a response from the server.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            Parsed response message or None on timeout/error
        """
        if not self.socket:
            return None
        
        # Set socket timeout
        self.socket.settimeout(timeout)
        
        try:
            # Read response
            buffer = bytearray()
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    data = self.socket.recv(1024)
                    if not data:
                        logger.warning("Connection closed by server")
                        return None
                    
                    buffer.extend(data)
                    
                    # Look for complete message (0x7e...0x7e)
                    start_idx = buffer.find(b'\x7e')
                    if start_idx != -1:
                        end_idx = buffer.find(b'\x7e', start_idx + 1)
                        if end_idx != -1:
                            # Extract message
                            message = buffer[start_idx:end_idx+1]
                            
                            # Unescape the message
                            unescaped = self._unescape_message(message)
                            
                            # Parse response
                            return self._parse_response(unescaped)
                except socket.timeout:
                    continue
            
            logger.warning("Timeout waiting for response")
            return None
        
        except Exception as e:
            logger.error(f"Error waiting for response: {e}")
            return None
        finally:
            # Reset socket timeout
            self.socket.settimeout(None)
    
    def _unescape_message(self, message: bytes) -> bytes:
        """
        Unescape a JT/T 808 message.
        
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
    
    def _parse_response(self, data: bytes) -> Optional[Dict[str, Any]]:
        """
        Parse a response from the server.
        
        Args:
            data: Response message bytes (without start/end markers)
            
        Returns:
            Parsed response or None on error
        """
        try:
            if len(data) < 12:  # Minimum header size
                logger.warning(f"Response too short: {len(data)} bytes")
                return None
            
            # Parse header
            msg_id = struct.unpack('>H', data[0:2])[0]
            msg_props = struct.unpack('>H', data[2:4])[0]
            
            # Extract message properties
            msg_length = msg_props & 0x03FF  # First 10 bits
            
            # Phone number (device ID) - 6 bytes BCD
            phone_bytes = data[4:10]
            phone_number = ''.join([f'{b:02x}' for b in phone_bytes]).upper()
            
            # Message serial number - 2 bytes
            msg_serial = struct.unpack('>H', data[10:12])[0]
            
            result = {
                'msg_id': msg_id,
                'msg_props': msg_props,
                'msg_length': msg_length,
                'phone_number': phone_number,
                'msg_serial': msg_serial,
                'msg_type': self.MESSAGE_TYPES.get(msg_id, 'Unknown')
            }
            
            # Message body (without checksum)
            body = data[12:-1]
            
            # Parse response body based on message type
            if msg_id == 0x8001:  # Platform general response
                if len(body) >= 5:
                    resp_serial = struct.unpack('>H', body[0:2])[0]
                    resp_msg_id = struct.unpack('>H', body[2:4])[0]
                    resp_result = body[4]
                    
                    result['response_serial'] = resp_serial
                    result['response_msg_id'] = resp_msg_id
                    result['result'] = resp_result
            
            elif msg_id == 0x8100:  # Terminal registration response
                if len(body) >= 3:
                    resp_serial = struct.unpack('>H', body[0:2])[0]
                    resp_result = body[2]
                    
                    result['response_serial'] = resp_serial
                    result['result'] = resp_result
                    
                    if resp_result == 0 and len(body) > 3:
                        auth_code = body[3:].decode('ascii')
                        result['auth_code'] = auth_code
            
            logger.debug(f"Parsed response: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return None


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='JT808 Device Simulator')
    
    parser.add_argument(
        '--server',
        default='localhost',
        help='Protocol server hostname or IP (default: localhost)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='Protocol server port (default: 8080)'
    )
    
    parser.add_argument(
        '--device-id',
        default=None,
        help='Device ID (12-digit number, random if not specified)'
    )
    
    parser.add_argument(
        '--latitude',
        type=float,
        default=37.7749,
        help='Initial latitude (default: 37.7749)'
    )
    
    parser.add_argument(
        '--longitude',
        type=float,
        default=-122.4194,
        help='Initial longitude (default: -122.4194)'
    )
    
    parser.add_argument(
        '--interval',
        type=float,
        default=10.0,
        help='Interval between messages in seconds (default: 10.0)'
    )
    
    parser.add_argument(
        '--no-movement',
        action='store_true',
        help='Disable random movement simulation'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    return parser.parse_args()


def main():
    """Main entry point for the simulator"""
    args = parse_arguments()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create simulator
    device = JT808DeviceSimulator(
        server_host=args.server,
        server_port=args.port,
        device_id=args.device_id,
        initial_latitude=args.latitude,
        initial_longitude=args.longitude,
        move_randomly=not args.no_movement
    )
    
    logger.info(f"Starting JT808 Device Simulator (ID: {device.device_id})")
    logger.info(f"Connecting to server at {args.server}:{args.port}")
    
    try:
        # Connect to server
        if not device.connect():
            logger.error("Failed to connect to server")
            return 1
        
        # Register device
        if not device.send_registration():
            logger.error("Failed to register device")
            device.disconnect()
            return 1
        
        # Main simulation loop
        try:
            heartbeat_counter = 0
            while True:
                # Send location update
                device.send_location()
                
                # Send heartbeat every 6th message
                heartbeat_counter += 1
                if heartbeat_counter >= 6:
                    device.send_heartbeat()
                    heartbeat_counter = 0
                
                # Wait for next interval
                time.sleep(args.interval)
                
        except KeyboardInterrupt:
            logger.info("Simulation stopped by user")
        
        # Disconnect
        device.disconnect()
        
    except Exception as e:
        logger.error(f"Error in simulator: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    # Fix missing math module import
    import math
    sys.exit(main())