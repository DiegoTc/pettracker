import socket
import threading
import logging
import json
import time
import struct
import binascii
from datetime import datetime
from app import db
from models import Device, Location
import re
import binascii
from flask import current_app

logger = logging.getLogger(__name__)

class Protocol808Parser:
    """
    Parser for the 808 GPS protocol commonly used in pet/vehicle tracking devices
    
    The 808 protocol typically includes:
    - Header: Start markers and device identifiers
    - Command: Type of message (position, status, alarm)
    - Data: GPS coordinates, time, speed, etc.
    - Footer: End markers and checksums
    """
    
    # Common message types in 808 protocol
    MESSAGE_TYPES = {
        "BP00": "Heartbeat",
        "BP01": "Login",
        "BP02": "GPS",
        "BP03": "Status",
        "BP04": "Alarm",
        "BP05": "Terminal",
        "BP06": "Message",
        "BP07": "Command Response"
    }
    
    @staticmethod
    def parse_message(raw_data):
        """Parse raw 808 protocol data into structured information"""
        try:
            # Convert bytes to string if needed
            if isinstance(raw_data, bytes):
                data_str = raw_data.decode('utf-8', errors='ignore')
            else:
                data_str = raw_data
                
            logger.debug(f"Parsing 808 message: {data_str}")
            
            # Basic validation - check if it looks like a 808 message
            if not (data_str.startswith("*") and data_str.endswith("#")):
                logger.warning(f"Invalid 808 message format: {data_str}")
                return None
                
            # Extract device ID - typically follows the start marker
            # Format: *ID,IMEI:123456789012345,command,data#
            match = re.search(r'\*(?:ID|HQ),([^,]+)', data_str)
            if not match:
                logger.warning(f"Could not extract device ID from message: {data_str}")
                return None
                
            device_id = match.group(1)
            # Handle IMEI format
            if "IMEI:" in device_id:
                device_id = device_id.split("IMEI:")[1]
            
            # Try to identify message type
            message_type = None
            for cmd, desc in Protocol808Parser.MESSAGE_TYPES.items():
                if cmd in data_str:
                    message_type = cmd
                    break
            
            # Parse GPS data if it's a location message
            location_data = None
            if "BP02" in data_str or "GPS" in data_str or re.search(r'[A|V],(\d+\.\d+)[N|S],(\d+\.\d+)[E|W]', data_str):
                location_data = Protocol808Parser._parse_gps_data(data_str)
            
            # Parse status data
            status_data = {}
            
            # Battery level is often in the status part (e.g., BAT:75%)
            bat_match = re.search(r'BAT:(\d+)%', data_str)
            if bat_match:
                status_data['battery_level'] = float(bat_match.group(1))
            
            return {
                "device_id": device_id,
                "raw_message": data_str,
                "message_type": message_type,
                "timestamp": datetime.utcnow(),
                "location": location_data,
                "status": status_data
            }
        
        except Exception as e:
            logger.error(f"Error parsing 808 message: {str(e)}", exc_info=True)
            return None
    
    @staticmethod
    def _parse_gps_data(data_str):
        """Extract GPS coordinates from a 808 protocol message"""
        try:
            # Try to match standard GPS format (A=valid, V=invalid)
            # Format: A,latitude,N/S,longitude,E/W,speed,heading,date,magnetic,variation,E/W
            gps_match = re.search(r'([A|V]),(\d+\.\d+)([N|S]),(\d+\.\d+)([E|W]),(\d+\.\d+),(\d+\.\d+)', data_str)
            
            if gps_match:
                valid = gps_match.group(1) == "A"
                latitude = float(gps_match.group(2))
                if gps_match.group(3) == "S":
                    latitude = -latitude
                
                longitude = float(gps_match.group(4))
                if gps_match.group(5) == "W":
                    longitude = -longitude
                
                speed = float(gps_match.group(6))
                heading = float(gps_match.group(7))
                
                # Try to extract timestamp
                date_match = re.search(r'(\d{2})(\d{2})(\d{2})', data_str)
                timestamp = None
                if date_match:
                    # Note: This assumes YY/MM/DD format, might need adjustment
                    year = 2000 + int(date_match.group(1))
                    month = int(date_match.group(2))
                    day = int(date_match.group(3))
                    timestamp = datetime(year, month, day)
                else:
                    timestamp = datetime.utcnow()
                
                return {
                    "valid": valid,
                    "latitude": latitude,
                    "longitude": longitude,
                    "speed": speed,
                    "heading": heading,
                    "timestamp": timestamp
                }
            
            # Alternative format checking
            alt_match = re.search(r'lat:(\d+\.\d+),long:(\d+\.\d+),speed:(\d+\.\d+)', data_str, re.IGNORECASE)
            if alt_match:
                latitude = float(alt_match.group(1))
                longitude = float(alt_match.group(2))
                speed = float(alt_match.group(3))
                
                return {
                    "valid": True,
                    "latitude": latitude,
                    "longitude": longitude,
                    "speed": speed,
                    "heading": 0.0,  # Default if not available
                    "timestamp": datetime.utcnow()
                }
            
            logger.warning(f"Could not parse GPS data from message: {data_str}")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing GPS data: {str(e)}", exc_info=True)
            return None
    
    @staticmethod
    def create_response(device_id, command, status="OK"):
        """Create a response message in 808 protocol format"""
        # Basic response format: *ID,IMEI,command,status#
        response = f"*ID,{device_id},{command},{status}#"
        return response.encode('utf-8')


class JT808Parser:
    """
    Parser for the JT/T 808 protocol commonly used in GPS tracking devices
    
    The JT808 protocol typically includes:
    - Header: Start and end markers (0x7e), message ID, attributes, phone number, etc.
    - Body: Message content specific to the message type
    - Checksum: XOR of all bytes excluding start/end markers
    """
    
    # Common message types in JT808 protocol
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
    
    @staticmethod
    def parse_message(data):
        """
        Decodes a JT/T 808 message.

        Args:
            data: The raw byte string received from the socket.

        Returns:
            A dictionary containing the decoded message, or None on error.
        """
        try:
            # 1. Unescape the data (reverse the 0x7d 0x02, 0x7d 0x01 escapes)
            unescaped_data = bytearray()
            i = 0
            while i < len(data):
                if data[i] == 0x7d:
                    if i + 1 < len(data):
                        if data[i + 1] == 0x02:
                            unescaped_data.append(0x7e)
                            i += 2
                            continue
                        elif data[i + 1] == 0x01:
                            unescaped_data.append(0x7d)
                            i += 2
                            continue
                    # Handle the case where 0x7d is at the end of the data
                    unescaped_data.append(data[i])
                    i += 1
                else:
                    unescaped_data.append(data[i])
                    i += 1
            data = bytes(unescaped_data)

            # 2. Verify start and end flags (0x7e)
            if data[0] != 0x7e or data[-1] != 0x7e:
                logger.warning("Invalid JT808 message: Missing start or end flags")
                return None

            # 3. Extract header (first 12 bytes, or 14 if sub-package)
            # Message ID, Body Length, Phone Number, Serial Number
            header_format = '>HH6sH'
            header_size = struct.calcsize(header_format)

            # Check if it is a subpackage.
            body_length_field = struct.unpack('>H', data[2:4])[0]
            is_subpackage = (body_length_field >> 13) & 0x01

            if is_subpackage:
                # Total packages, package serial number
                header_format += '>HH'
                header_size = struct.calcsize(header_format)

            header_data = struct.unpack(header_format, data[1:header_size+1])  # Skip start flag at index 0
            message_id = header_data[0]
            body_length = header_data[1] & 0x1FFF  # Get the lower 13 bits for body length
            phone_number = header_data[2].decode('ascii', errors='ignore').strip()
            serial_number = header_data[3]

            if is_subpackage:
                total_packages = header_data[4]
                package_number = header_data[5]
            else:
                total_packages = None
                package_number = None

            # 4. Extract body and checksum
            body = data[header_size+1 : header_size + 1 + body_length]  # Skip the start flag (1 byte)

            # 5. Verify checksum
            received_checksum = data[header_size + 1 + body_length]
            calculated_checksum = 0
            for b in data[1 : header_size + 1 + body_length]:  # Checksum excludes start/end flags
                calculated_checksum ^= b

            if received_checksum != calculated_checksum:
                logger.warning(f"Checksum mismatch. Received: {received_checksum}, Calculated: {calculated_checksum}")
                return None

            # 6. Decode message body based on message ID
            decoded_body = None
            location_data = None
            
            if message_id == 0x0200:  # Location Information Report
                decoded_body = JT808Parser._decode_location_information_report(body)
                location_data = decoded_body  # For consistency with Protocol808Parser return format
            elif message_id == 0x0002:  # Heartbeat
                decoded_body = "Heartbeat"  # Empty body
            else:
                decoded_body = f"Unsupported message type: 0x{message_id:04X}"
                logger.info(f"Received unsupported JT808 message type: 0x{message_id:04X}")

            # 7. Construct and return the full message in a format compatible with our existing system
            return {
                "device_id": phone_number,  # Use phone number as device ID
                "raw_message": binascii.hexlify(data).decode('ascii'),  # For debugging
                "message_type": JT808Parser.MESSAGE_TYPES.get(message_id, f"Unknown (0x{message_id:04X})"),
                "timestamp": datetime.utcnow(),
                "location": location_data,
                "status": {},  # Will be populated if status data is available
                "jt808_data": {  # Store the original JT808 message details
                    "message_id": message_id,
                    "serial_number": serial_number,
                    "is_subpackage": is_subpackage,
                    "total_packages": total_packages,
                    "package_number": package_number
                }
            }

        except Exception as e:
            logger.error(f"Error parsing JT808 message: {str(e)}", exc_info=True)
            return None
    
    @staticmethod
    def _decode_location_information_report(body):
        """Decodes a location information report (0x0200) message body."""
        try:
            # Based on the JT808 spec, this should be:
            # Alarm (4 bytes) + Status (4 bytes) + Latitude (4 bytes) + Longitude (4 bytes) + 
            # Altitude (2 bytes) + Speed (2 bytes) + Direction (2 bytes) + 
            # Time (6 bytes BCD) + Additional data (variable)
            format_string = '>IIiiHHH6s'
            min_size = struct.calcsize(format_string)
            
            if len(body) < min_size:
                logger.warning(f"Location body too short: {len(body)} bytes, expected at least {min_size}")
                return None
                
            main_data = struct.unpack(format_string, body[:min_size])
            
            alarm = main_data[0]
            status = main_data[1]
            latitude = main_data[2] / 1000000.0  # Convert from integer (millionths of a degree)
            longitude = main_data[3] / 1000000.0  # Convert from integer (millionths of a degree)
            altitude = main_data[4]  # In meters
            speed = main_data[5] / 10.0  # Convert from 0.1 km/h to km/h
            direction = main_data[6]  # In degrees, 0-359
            time_bcd = main_data[7]  # BCD encoded time (YYMMDDhhmmss)
            
            # Convert BCD time to datetime
            time_hex = binascii.hexlify(time_bcd).decode('ascii')
            year = 2000 + int(time_hex[0:2])
            month = int(time_hex[2:4])
            day = int(time_hex[4:6])
            hour = int(time_hex[6:8])
            minute = int(time_hex[8:10])
            second = int(time_hex[10:12])
            timestamp = datetime(year, month, day, hour, minute, second)
            
            # Check validity based on status bit 1 (0=invalid, 1=valid)
            valid = bool((status >> 1) & 0x01)
            
            # Extract battery level and other additional data if available
            battery_level = None
            additional_data = {}
            
            # Store the alarm and status in additional data for reference
            additional_data['alarm'] = alarm
            additional_data['status'] = status
            
            # Process additional data fields if present
            remaining_data = body[min_size:]
            while remaining_data:
                if len(remaining_data) < 2:
                    break  # Not enough data for ID and length
                    
                additional_id = remaining_data[0]
                additional_length = remaining_data[1]
                
                if len(remaining_data) < 2 + additional_length:
                    break  # Not enough data for the content
                    
                additional_content = remaining_data[2:2+additional_length]
                
                # Process known additional data types
                if additional_id == 0x01:  # Mileage
                    if additional_length == 4:
                        mileage = struct.unpack('>I', additional_content)[0] / 10.0  # In km
                        additional_data['mileage'] = mileage
                        
                elif additional_id == 0x02:  # Fuel level
                    if additional_length == 2:
                        fuel = struct.unpack('>H', additional_content)[0] / 10.0  # In liters
                        additional_data['fuel_level'] = fuel
                        
                elif additional_id == 0x03:  # Speed from additional source
                    if additional_length == 2:
                        extra_speed = struct.unpack('>H', additional_content)[0] / 10.0  # In km/h
                        additional_data['additional_speed'] = extra_speed
                        
                elif additional_id == 0x04:  # Vehicle signal status
                    if additional_length == 4:
                        signal_status = struct.unpack('>I', additional_content)[0]
                        additional_data['signal_status'] = signal_status
                        
                elif additional_id == 0x11:  # Phone signal strength
                    if additional_length == 1:
                        signal_strength = struct.unpack('>B', additional_content)[0]
                        additional_data['signal_strength'] = signal_strength
                        
                elif additional_id == 0x30:  # Battery level (custom/pet device specific)
                    if additional_length == 1:
                        battery_level = struct.unpack('>B', additional_content)[0]  # In percentage
                        additional_data['battery_level'] = battery_level
                
                # Move to next additional data field
                remaining_data = remaining_data[2+additional_length:]
            
            # Return location data in a format consistent with Protocol808Parser
            location_data = {
                "valid": valid,
                "latitude": latitude,
                "longitude": longitude,
                "altitude": altitude,
                "speed": speed,
                "heading": direction,
                "timestamp": timestamp,
                "additional_data": additional_data
            }
            
            if battery_level is not None:
                location_data["battery_level"] = battery_level
                
            return location_data
            
        except Exception as e:
            logger.error(f"Error decoding JT808 location information report: {str(e)}", exc_info=True)
            return None
    
    @staticmethod
    def create_response(phone_number, message_id, serial_number, result=0):
        """
        Create a general response message in JT808 protocol format (0x8001)
        
        Args:
            phone_number: The phone number (device ID) to respond to
            message_id: The message ID being responded to
            serial_number: The serial number of the message being responded to
            result: Result code (0=success, 1=failure, 2=message error, 3=not supported)
            
        Returns:
            Bytes containing the encoded response message
        """
        try:
            # 1. Prepare response body (response message ID, serial number, result)
            body = struct.pack('>HHB', serial_number, message_id, result)
            body_length = len(body)
            
            # 2. Prepare header (message ID 0x8001, body length, phone number, serial number)
            msg_id = 0x8001
            msg_attributes = body_length & 0x1FFF  # Lower 13 bits for body length
            
            # Get a new serial number for the response
            resp_serial = serial_number  # Using the same serial number for simplicity
            
            # Format phone number as bytes, padded to 6 bytes
            if isinstance(phone_number, str):
                phone_bytes = phone_number.encode('ascii')
                # Ensure it's exactly 6 bytes (pad with zeros if needed)
                if len(phone_bytes) < 6:
                    phone_bytes = phone_bytes.ljust(6, b'\x00')
                elif len(phone_bytes) > 6:
                    phone_bytes = phone_bytes[:6]
            else:
                # If it's already bytes, ensure it's the right length
                phone_bytes = phone_number
                if len(phone_bytes) < 6:
                    phone_bytes = phone_bytes.ljust(6, b'\x00')
                elif len(phone_bytes) > 6:
                    phone_bytes = phone_bytes[:6]
            
            header = struct.pack('>HH6sH', msg_id, msg_attributes, phone_bytes, resp_serial)
            
            # 3. Calculate checksum (XOR of all bytes in header and body)
            checksum = 0
            for b in header + body:
                checksum ^= b
            
            # 4. Assemble the full message (start flag + header + body + checksum + end flag)
            message = bytearray()
            message.append(0x7e)  # Start flag
            message.extend(header)
            message.extend(body)
            message.append(checksum)
            message.append(0x7e)  # End flag
            
            # 5. Escape special bytes (0x7e -> 0x7d, 0x02 and 0x7d -> 0x7d, 0x01)
            escaped_message = bytearray()
            for b in message[1:-1]:  # Skip the start and end flags
                if b == 0x7e:
                    escaped_message.extend([0x7d, 0x02])
                elif b == 0x7d:
                    escaped_message.extend([0x7d, 0x01])
                else:
                    escaped_message.append(b)
            
            # Add back the start and end flags
            final_message = bytearray()
            final_message.append(0x7e)
            final_message.extend(escaped_message)
            final_message.append(0x7e)
            
            return bytes(final_message)
            
        except Exception as e:
            logger.error(f"Error creating JT808 response: {str(e)}", exc_info=True)
            return None


class Protocol808Server:
    """
    TCP server that listens for both 808 and JT808 protocol messages from tracking devices
    """
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.clients = {}
        self.parser_808 = Protocol808Parser()
        self.parser_jt808 = JT808Parser()
    
    def start(self):
        """Start the dual-protocol server (supporting both 808 and JT808)"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            logger.info(f"Protocol server started on {self.host}:{self.port} (supporting 808 and JT808 protocols)")
            
            while self.running:
                try:
                    client_socket, addr = self.server_socket.accept()
                    logger.info(f"New connection from {addr}")
                    
                    # Start a new thread to handle this client
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except (socket.error, IOError) as e:
                    if self.running:
                        logger.error(f"Socket error: {str(e)}", exc_info=True)
                    break
                except Exception as e:
                    logger.error(f"Unexpected error in 808 server: {str(e)}", exc_info=True)
        
        except Exception as e:
            logger.error(f"Error starting 808 server: {str(e)}", exc_info=True)
        finally:
            if self.server_socket:
                self.server_socket.close()
    
    def stop(self):
        """Stop the protocol server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        logger.info("Protocol server stopped (808/JT808)")
    
    def handle_client(self, client_socket, addr):
        """Handle communication with a connected tracking device"""
        client_id = None
        protocol_type = None  # 'jt808' or '808'
        
        try:
            while self.running:
                # Receive data from the client
                data = client_socket.recv(1024)
                if not data:
                    logger.info(f"Client {addr} disconnected")
                    break
                
                # Determine protocol type if not already known
                if not protocol_type:
                    # Check if it's JT808 protocol (starts with 0x7e)
                    if data and len(data) > 0 and data[0] == 0x7e:
                        protocol_type = 'jt808'
                        logger.info(f"Client {addr} using JT808 protocol")
                    # Check if it's 808 protocol (starts with *ID or *HQ)
                    elif data and len(data) > 3 and data[0:1] == b'*':
                        protocol_type = '808'
                        logger.info(f"Client {addr} using 808 protocol")
                    else:
                        # Log the first few bytes for debugging
                        hex_data = binascii.hexlify(data[:20] if len(data) > 20 else data).decode('ascii')
                        logger.warning(f"Unable to determine protocol type from data: {hex_data}...")
                        protocol_type = '808'  # Default to 808 protocol
                
                # Parse the received message based on protocol type
                message = None
                if protocol_type == 'jt808':
                    message = self.parser_jt808.parse_message(data)
                else:  # Default to 808 protocol
                    message = self.parser_808.parse_message(data)
                
                if not message:
                    # Log the message in hex format for debugging
                    hex_data = binascii.hexlify(data[:50] if len(data) > 50 else data).decode('ascii')
                    logger.warning(f"Failed to parse message from {addr} using {protocol_type} protocol: {hex_data}...")
                    continue
                
                # Store client ID for future reference
                client_id = message.get("device_id")
                if client_id:
                    self.clients[client_id] = client_socket
                
                # Process the message
                self.process_message(message)
                
                # Send acknowledgment back to the device based on protocol
                if protocol_type == 'jt808' and 'jt808_data' in message:
                    jt_data = message['jt808_data']
                    ack = self.parser_jt808.create_response(
                        client_id, 
                        jt_data['message_id'], 
                        jt_data['serial_number']
                    )
                    if ack:
                        client_socket.send(ack)
                else:
                    ack = self.parser_808.create_response(client_id, "ACK", "OK")
                    client_socket.send(ack)
        
        except socket.error as e:
            logger.error(f"Socket error with client {addr}: {str(e)}")
        except Exception as e:
            logger.error(f"Error handling client {addr}: {str(e)}", exc_info=True)
        finally:
            # Clean up
            client_socket.close()
            if client_id and client_id in self.clients:
                del self.clients[client_id]
            logger.info(f"Connection closed with {addr}")
    
    def process_message(self, message):
        """Process a parsed protocol message (both 808 and JT808)"""
        try:
            device_id = message.get("device_id")
            if not device_id:
                logger.warning("Message missing device_id, cannot process")
                return
            
            # Import app for app context
            from app import app
            
            # Find the device in the database
            with app.app_context():
                device = Device.query.filter_by(device_id=device_id).first()
                
                if not device:
                    # Try to find by IMEI
                    device = Device.query.filter_by(imei=device_id).first()
                
                if not device:
                    logger.warning(f"Device not found in database: {device_id}")
                    return
                
                # Update device last ping time
                device.last_ping = datetime.utcnow()
                
                # Update battery level if available in status data
                if message.get("status") and "battery_level" in message["status"]:
                    device.battery_level = message["status"]["battery_level"]
                
                # Process location data if available
                location_data = message.get("location")
                if location_data and location_data.get("valid"):
                    # For JT808 devices, battery level might be in location data
                    if "battery_level" in location_data and device.battery_level != location_data["battery_level"]:
                        device.battery_level = location_data["battery_level"]
                        logger.info(f"Updated battery level for device {device_id}: {device.battery_level}%")
                    
                    # If location has additional data, log it
                    if "additional_data" in location_data:
                        logger.debug(f"Additional data for device {device_id}: {location_data['additional_data']}")
                    
                    # Create new location record
                    location = Location(
                        device_id=device.id,
                        latitude=location_data["latitude"],
                        longitude=location_data["longitude"],
                        speed=location_data.get("speed"),
                        heading=location_data.get("heading"),
                        altitude=location_data.get("altitude"),
                        timestamp=location_data.get("timestamp", datetime.utcnow()),
                        battery_level=device.battery_level,
                        accuracy=location_data.get("accuracy")
                    )
                    
                    db.session.add(location)
                    
                    # Log the protocol type
                    protocol_type = "JT808" if "jt808_data" in message else "808"
                    logger.info(f"Recorded location for device {device_id} ({protocol_type}): " 
                              f"({location_data['latitude']}, {location_data['longitude']})")
                
                # Commit changes to database
                db.session.commit()
                logger.info(f"Processed message from device {device_id}")
        
        except Exception as e:
            try:
                db.session.rollback()
            except:
                pass
            logger.error(f"Error processing message: {str(e)}", exc_info=True)


# Singleton instance of the server
_server_instance = None

def get_server_instance():
    """Get the singleton instance of the protocol server (supports both 808 and JT808)"""
    global _server_instance
    if _server_instance is None:
        # Try to get port from current_app if in app context
        try:
            port = current_app.config.get('PROTOCOL_808_PORT', 8080)
        except RuntimeError:
            # Outside app context, use default port
            from config import Config
            port = int(Config.PROTOCOL_808_PORT)
            
        logger.info(f"Initializing dual-protocol server (808/JT808) on port {port}")
        _server_instance = Protocol808Server(port=port)
    return _server_instance

def start_protocol_server():
    """Start the protocol server in the background (handles both 808 and JT808 protocols)"""
    server = get_server_instance()
    # Start in a new thread to avoid blocking
    thread = threading.Thread(target=server.start)
    thread.daemon = True
    thread.start()
    return thread

def stop_protocol_server():
    """Stop the protocol server"""
    global _server_instance
    if _server_instance:
        _server_instance.stop()
        _server_instance = None
