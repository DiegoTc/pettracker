import socket
import threading
import logging
import json
import time
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


class Protocol808Server:
    """
    TCP server that listens for 808 protocol messages from tracking devices
    """
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.clients = {}
        self.parser = Protocol808Parser()
    
    def start(self):
        """Start the 808 protocol server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            logger.info(f"808 Protocol server started on {self.host}:{self.port}")
            
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
        """Stop the 808 protocol server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        logger.info("808 Protocol server stopped")
    
    def handle_client(self, client_socket, addr):
        """Handle communication with a connected tracking device"""
        client_id = None
        
        try:
            while self.running:
                # Receive data from the client
                data = client_socket.recv(1024)
                if not data:
                    logger.info(f"Client {addr} disconnected")
                    break
                
                # Parse the received message
                message = self.parser.parse_message(data)
                if not message:
                    logger.warning(f"Failed to parse message from {addr}: {data}")
                    continue
                
                # Store client ID for future reference
                client_id = message.get("device_id")
                if client_id:
                    self.clients[client_id] = client_socket
                
                # Process the message
                self.process_message(message)
                
                # Send acknowledgment back to the device
                ack = self.parser.create_response(client_id, "ACK", "OK")
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
        """Process a parsed 808 protocol message"""
        try:
            device_id = message.get("device_id")
            if not device_id:
                logger.warning("Message missing device_id, cannot process")
                return
            
            # Find the device in the database
            with db.app.app_context():
                device = Device.query.filter_by(device_id=device_id).first()
                
                if not device:
                    # Try to find by IMEI
                    device = Device.query.filter_by(imei=device_id).first()
                
                if not device:
                    logger.warning(f"Device not found in database: {device_id}")
                    return
                
                # Update device last ping time
                device.last_ping = datetime.utcnow()
                
                # Update battery level if available
                if message.get("status") and "battery_level" in message["status"]:
                    device.battery_level = message["status"]["battery_level"]
                
                # Process location data if available
                location_data = message.get("location")
                if location_data and location_data.get("valid"):
                    # Create new location record
                    location = Location(
                        device_id=device.id,
                        latitude=location_data["latitude"],
                        longitude=location_data["longitude"],
                        speed=location_data.get("speed"),
                        heading=location_data.get("heading"),
                        timestamp=location_data.get("timestamp", datetime.utcnow()),
                        battery_level=device.battery_level
                    )
                    
                    db.session.add(location)
                
                # Commit changes to database
                db.session.commit()
                logger.info(f"Processed message from device {device_id}")
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error processing message: {str(e)}", exc_info=True)


# Singleton instance of the server
_server_instance = None

def get_server_instance():
    """Get the singleton instance of the 808 protocol server"""
    global _server_instance
    if _server_instance is None:
        port = current_app.config.get('PROTOCOL_808_PORT', 8080)
        _server_instance = Protocol808Server(port=port)
    return _server_instance

def start_protocol_server():
    """Start the 808 protocol server in the background"""
    server = get_server_instance()
    server.start()

def stop_protocol_server():
    """Stop the 808 protocol server"""
    global _server_instance
    if _server_instance:
        _server_instance.stop()
        _server_instance = None
