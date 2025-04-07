#!/usr/bin/env python3
"""
Device Protocol Simulator

This script simulates a GPS tracking device that communicates using either the 808 protocol 
or the JT808 protocol. It can be used for testing the pet tracking system without a physical device.

Usage:
    python device_simulator.py --device-id <device_id> --imei <imei> --interval <seconds> [--protocol <protocol>]

Protocol options:
    - 808 (default): Traditional 808 protocol format
    - jt808: Chinese JT/T 808 protocol format

Examples:
    python device_simulator.py --device-id 9c96e35f-1339-4e32-8ee4-65904ca55df1 --imei 123456789012345 --interval 10
    python device_simulator.py --device-id 9c96e35f --imei 123456789012345 --interval 5 --protocol jt808
"""

import socket
import time
import random
import argparse
import logging
import sys
import threading
import signal
import math
import struct
import binascii
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('device_simulator')

# Flag for graceful shutdown
running = True

class GPS808Simulator:
    """Simulates a GPS device using the 808 protocol"""
    
    def __init__(self, device_id, imei, server_host='localhost', server_port=8080):
        self.device_id = device_id
        self.imei = imei
        self.server_host = server_host
        self.server_port = server_port
        self.sock = None
        self.connected = False
        
        # Starting position (San Francisco)
        self.latitude = 37.7749
        self.longitude = -122.4194
        self.altitude = 10.0
        self.speed = 0.0
        self.heading = 0.0
        self.battery_level = 100.0
        
        logger.info(f"Initialized device simulator with ID: {device_id}, IMEI: {imei}")
        
    def connect(self):
        """Connect to the 808 protocol server"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.server_host, self.server_port))
            self.connected = True
            logger.info(f"Connected to server at {self.server_host}:{self.server_port}")
            
            # Send login message
            self._send_login()
            return True
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            self.connected = False
            return False
            
    def disconnect(self):
        """Disconnect from the server"""
        if self.sock:
            try:
                self.sock.close()
                logger.info("Disconnected from server")
            except:
                pass
            self.sock = None
            self.connected = False
    
    def _send_login(self):
        """Send a login message to the server"""
        # Format: *ID,IMEI:123456789012345,BP01,timestamp,device_id#
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        message = f"*ID,IMEI:{self.imei},BP01,{timestamp},{self.device_id}#"
        response = self._send_message(message)
        logger.info(f"Login response: {response}")
    
    def send_heartbeat(self):
        """Send a heartbeat message to the server"""
        if not self.connected and not self.connect():
            return False
            
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        message = f"*ID,IMEI:{self.imei},BP00,{timestamp},{self.device_id},{self.battery_level}#"
        response = self._send_message(message)
        logger.info(f"Heartbeat response: {response}")
        return True
    
    def send_location(self):
        """Send a GPS location message to the server"""
        if not self.connected and not self.connect():
            return False
            
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Slightly move position for simulation
        self._update_position()
        
        # Format: *ID,IMEI:123456789012345,BP02,timestamp,device_id,lat,lon,altitude,speed,heading,bat_level#
        message = (f"*ID,IMEI:{self.imei},BP02,{timestamp},{self.device_id},"
                   f"{self.latitude:.6f},{self.longitude:.6f},{self.altitude:.1f},"
                   f"{self.speed:.1f},{self.heading:.1f},{self.battery_level:.1f}#")
        
        response = self._send_message(message)
        logger.info(f"Location sent: lat={self.latitude:.6f}, lon={self.longitude:.6f}, speed={self.speed:.1f}, battery={self.battery_level:.1f}")
        logger.debug(f"Location response: {response}")
        return True
    
    def _send_message(self, message):
        """Send a message to the server and receive response"""
        try:
            if self.sock is None:
                logger.error("Socket is not connected")
                self.connected = False
                return None
                
            self.sock.sendall(message.encode())
            # Wait for response
            response = self.sock.recv(1024).decode().strip()
            return response
        except Exception as e:
            logger.error(f"Communication error: {str(e)}")
            self.connected = False
            return None
    
    def _update_position(self):
        """Update position for simulation"""
        # Random walk with some direction persistence
        if random.random() < 0.1:  # 10% chance to change direction
            self.heading = random.uniform(0, 360)
        
        # Randomly update speed
        if random.random() < 0.2:  # 20% chance to change speed
            self.speed = random.uniform(0, 5.0)  # Speed in m/s
        
        # Convert degrees to radians
        heading_rad = math.radians(self.heading)
        
        # Calculate distance moved (in degrees)
        # Roughly 111km per degree of latitude, speed is in m/s
        # This gives a realistic movement based on speed
        distance = self.speed * 0.00001  # Convert to degrees
        
        # Update position
        self.latitude += distance * math.cos(heading_rad)
        self.longitude += distance * math.sin(heading_rad) / math.cos(math.radians(self.latitude))
        
        # Add some randomness to altitude
        self.altitude += random.uniform(-0.5, 0.5)
        
        # Decrease battery level slowly
        self.battery_level -= random.uniform(0, 0.05)
        if self.battery_level < 0:
            self.battery_level = 0.0
    
    def simulate_trip(self, duration_seconds, interval_seconds):
        """Simulate a trip by sending location data at regular intervals"""
        end_time = time.time() + duration_seconds
        
        try:
            if not self.connect():
                logger.error("Failed to connect for trip simulation")
                return False
            
            logger.info(f"Starting trip simulation for {duration_seconds} seconds")
            
            while time.time() < end_time and running:
                self.send_location()
                time.sleep(interval_seconds)
                
                # Send heartbeat occasionally
                if random.random() < 0.2:  # 20% chance
                    self.send_heartbeat()
                    
            logger.info("Trip simulation completed")
            self.disconnect()
            return True
            
        except KeyboardInterrupt:
            logger.info("Trip simulation interrupted")
            self.disconnect()
            return False
        except Exception as e:
            logger.error(f"Error during trip simulation: {str(e)}")
            self.disconnect()
            return False
    
    def simulate_continuous(self, interval_seconds):
        """Continuously simulate device activity until stopped"""
        try:
            if not self.connect():
                logger.error("Failed to connect for continuous simulation")
                return False
            
            logger.info(f"Starting continuous simulation with {interval_seconds} second intervals")
            
            heartbeat_counter = 0
            
            while running:
                self.send_location()
                
                # Send heartbeat every 5 location updates
                heartbeat_counter += 1
                if heartbeat_counter >= 5:
                    self.send_heartbeat()
                    heartbeat_counter = 0
                
                time.sleep(interval_seconds)
                    
        except KeyboardInterrupt:
            logger.info("Continuous simulation interrupted")
            return False
        except Exception as e:
            logger.error(f"Error during continuous simulation: {str(e)}")
            return False
        finally:
            self.disconnect()

class JT808Simulator:
    """Simulates a GPS device using the JT/T 808 protocol"""
    
    def __init__(self, device_id, imei, server_host='localhost', server_port=8080):
        # In JT808, phone_number is used as the device identifier
        # We'll use the provided device_id as the phone number
        self.phone_number = device_id.replace('-', '').ljust(11, '0')[:11]  # Ensure it's 11 digits
        self.imei = imei
        self.server_host = server_host
        self.server_port = server_port
        self.sock = None
        self.connected = False
        self.serial_number = 1  # Message serial number, increments with each message
        self.authenticated = False
        
        # Starting position (San Francisco)
        self.latitude = 37.7749
        self.longitude = -122.4194
        self.altitude = 10.0
        self.speed = 0.0
        self.heading = 0.0
        self.battery_level = 100.0
        
        logger.info(f"Initialized JT808 device simulator with phone: {self.phone_number}, IMEI: {imei}")
        
    def connect(self):
        """Connect to the 808 protocol server"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.server_host, self.server_port))
            self.connected = True
            logger.info(f"Connected to server at {self.server_host}:{self.server_port}")
            
            # Send terminal registration message
            self._send_registration()
            return True
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            self.connected = False
            return False
            
    def disconnect(self):
        """Disconnect from the server"""
        if self.sock:
            try:
                self.sock.close()
                logger.info("Disconnected from server")
            except:
                pass
            self.sock = None
            self.connected = False
    
    def _send_registration(self):
        """Send a terminal registration message (0x0100)"""
        # Create registration message
        msg_id = 0x0100  # Terminal Registration
        provincial_id = 1  # Beijing
        city_id = 1  # Beijing City
        manufacturer_id = "PET01"  # Pet tracker manufacturer
        terminal_model = "MODEL1-GPS"  # Device model
        terminal_id = self.imei[-7:]  # Last 7 digits of IMEI
        plate_color = 0  # No license plate
        plate_number = "PET" + self.phone_number[-4:]  # Pet name/number
        
        # Pack the body data
        body = struct.pack(
            '>HH5s20s7sB',
            provincial_id,
            city_id,
            manufacturer_id.encode().ljust(5, b'\x00'),
            terminal_model.encode().ljust(20, b'\x00'),
            terminal_id.encode().ljust(7, b'\x00'),
            plate_color
        )
        
        # Add plate number if available
        if plate_number:
            try:
                body += plate_number.encode('gbk')
            except:
                body += plate_number.encode('ascii')
        
        # Send the message and process response
        response = self._send_jt808_message(msg_id, body)
        
        # Process response - should be a 0x8100 Terminal Registration Response
        if response and len(response) >= 12:  # Minimum response size
            try:
                # Extract message ID from the response (should be 0x8100)
                resp_msg_id = struct.unpack('>H', response[1:3])[0]
                
                if resp_msg_id == 0x8100:
                    logger.info("Registration successful")
                    
                    # Extract authentication code and save it
                    resp_body_offset = 13  # 1(start flag) + 12(header)
                    resp_result = response[resp_body_offset + 2]  # Skip response serial
                    
                    if resp_result == 0:  # Success
                        self.authenticated = True
                        # Extract auth code (variable length ASCII)
                        auth_code = response[resp_body_offset+3:-2].decode('ascii', errors='ignore').strip('\x00')
                        logger.info(f"Received authentication code: {auth_code}")
                        
                        # Send authentication message with the received code
                        self._send_authentication(auth_code)
                    else:
                        logger.warning(f"Registration failed with result code: {resp_result}")
                else:
                    logger.warning(f"Unexpected response message ID: 0x{resp_msg_id:04X}")
            except Exception as e:
                logger.error(f"Error processing registration response: {str(e)}")
                
        return response
    
    def _send_authentication(self, auth_code):
        """Send a terminal authentication message (0x0102)"""
        msg_id = 0x0102  # Terminal Authentication
        body = auth_code.encode('ascii')
        
        response = self._send_jt808_message(msg_id, body)
        
        # Check if response indicates successful authentication
        if response and len(response) >= 15:  # Minimum size for a general response
            try:
                resp_msg_id = struct.unpack('>H', response[1:3])[0]
                
                if resp_msg_id == 0x8001:  # General Response
                    resp_body_offset = 13  # 1(start flag) + 12(header)
                    resp_serial = struct.unpack('>H', response[resp_body_offset:resp_body_offset+2])[0]
                    resp_msg = struct.unpack('>H', response[resp_body_offset+2:resp_body_offset+4])[0]
                    resp_result = response[resp_body_offset+4]
                    
                    if resp_msg == 0x0102 and resp_result == 0:
                        logger.info("Authentication successful")
                        self.authenticated = True
                    else:
                        logger.warning(f"Authentication failed: result={resp_result}")
                else:
                    logger.warning(f"Unexpected response message ID: 0x{resp_msg_id:04X}")
            except Exception as e:
                logger.error(f"Error processing authentication response: {str(e)}")
                
        return response
        
    def send_heartbeat(self):
        """Send a heartbeat message (0x0002)"""
        if not self.connected and not self.connect():
            return False
            
        if not self.authenticated:
            logger.warning("Not authenticated, skipping heartbeat")
            return False
            
        msg_id = 0x0002  # Heartbeat
        body = b''  # Empty body for heartbeat
        
        response = self._send_jt808_message(msg_id, body)
        logger.info("Heartbeat sent")
        return response is not None
    
    def send_location(self):
        """Send a GPS location message (0x0200)"""
        if not self.connected and not self.connect():
            return False
            
        if not self.authenticated:
            logger.warning("Not authenticated, skipping location update")
            return False
            
        # Update position
        self._update_position()
        
        # Message ID for Location Information Report
        msg_id = 0x0200
        
        # Pack the message body according to JT808 protocol
        # Alarm (4 bytes) + Status (4 bytes) + Latitude (4 bytes) + Longitude (4 bytes) + 
        # Altitude (2 bytes) + Speed (2 bytes) + Direction (2 bytes) + 
        # Time (6 bytes BCD) + Additional data
        
        # Alarm: 0 (no alarm)
        alarm = 0
        
        # Status: Bit 1 set (position valid)
        status = 0x02  # Bit 1 set - position is valid
        
        # Convert position to JT808 format (integer, millionths of a degree)
        lat_int = int(self.latitude * 1000000)
        lon_int = int(self.longitude * 1000000)
        
        # Altitude in meters (integer)
        alt_int = int(self.altitude)
        
        # Speed in 0.1 km/h (integer)
        speed_int = int(self.speed * 36)  # Convert m/s to 0.1 km/h
        
        # Direction in degrees (0-359)
        dir_int = int(self.heading) % 360
        
        # Time as BCD (YYMMDDhhmmss)
        # Converting each digit to BCD format
        now = datetime.now()
        year_bcd = ((now.year - 2000) // 10 << 4) | ((now.year - 2000) % 10)
        month_bcd = (now.month // 10 << 4) | (now.month % 10)
        day_bcd = (now.day // 10 << 4) | (now.day % 10)
        hour_bcd = (now.hour // 10 << 4) | (now.hour % 10)
        minute_bcd = (now.minute // 10 << 4) | (now.minute % 10)
        second_bcd = (now.second // 10 << 4) | (now.second % 10)
        
        time_bcd = bytes([
            year_bcd,
            month_bcd,
            day_bcd,
            hour_bcd,
            minute_bcd,
            second_bcd
        ])
        
        # Pack the main body
        body = struct.pack(
            '>IIiiHHH',
            alarm,          # Alarm
            status,         # Status
            lat_int,        # Latitude
            lon_int,        # Longitude
            alt_int,        # Altitude
            speed_int,      # Speed
            dir_int         # Direction
        ) + time_bcd  # Time (BCD)
        
        # Add additional data: battery level
        # ID: 0x30 (custom battery level), Length: 1, Value: battery percent
        battery_percent = int(self.battery_level)
        body += bytes([0x30, 1, battery_percent])
        
        # Send the message
        response = self._send_jt808_message(msg_id, body)
        
        logger.info(f"Location sent: lat={self.latitude:.6f}, lon={self.longitude:.6f}, speed={self.speed:.1f}, battery={self.battery_level:.1f}")
        return response is not None
    
    def _send_jt808_message(self, msg_id, body):
        """Send a JT808 format message to the server"""
        if not self.connected or self.sock is None:
            logger.warning("Not connected to server")
            return None
            
        try:
            # 1. Prepare the message components
            msg_body_len = len(body)
            
            # 2. Prepare header fields
            msg_attributes = msg_body_len & 0x1FFF  # Lower 13 bits for length
            phone_bytes = self.phone_number.encode('ascii')
            # Ensure phone number is exactly 6 bytes (right padding with zeros)
            if len(phone_bytes) < 6:
                phone_bytes = phone_bytes.ljust(6, b'\x00')
            elif len(phone_bytes) > 6:
                phone_bytes = phone_bytes[:6]
                
            # 3. Get next serial number and increment
            serial = self.serial_number
            self.serial_number = (self.serial_number + 1) % 65536  # Wrap at 16 bits
            
            # 4. Pack the header
            header = struct.pack(
                '>HH6sH',
                msg_id,            # Message ID
                msg_attributes,    # Message attributes
                phone_bytes,       # Phone number (6 bytes)
                serial             # Serial number
            )
            
            # 5. Calculate checksum (XOR of all bytes in header and body)
            checksum = 0
            for b in header + body:
                checksum ^= b
            
            # 6. Assemble the full message
            full_msg = bytearray()
            full_msg.append(0x7e)  # Start flag
            
            # 7. Escape special bytes in header and body
            for b in header + body:
                if b == 0x7e:
                    full_msg.extend([0x7d, 0x02])
                elif b == 0x7d:
                    full_msg.extend([0x7d, 0x01])
                else:
                    full_msg.append(b)
            
            # 8. Add checksum (with escaping if needed)
            if checksum == 0x7e:
                full_msg.extend([0x7d, 0x02])
            elif checksum == 0x7d:
                full_msg.extend([0x7d, 0x01])
            else:
                full_msg.append(checksum)
            
            # 9. Add end flag
            full_msg.append(0x7e)
            
            # 10. Send message and receive response
            self.sock.sendall(full_msg)
            
            # 11. Wait for response with a timeout
            self.sock.settimeout(5.0)
            try:
                response = self.sock.recv(1024)
                # Log the response in hex for debugging
                hex_resp = binascii.hexlify(response).decode('ascii')
                logger.debug(f"Response: {hex_resp}")
                return response
            except socket.timeout:
                logger.warning("Response timeout")
                return None
            finally:
                self.sock.settimeout(None)
                
        except Exception as e:
            logger.error(f"Error sending JT808 message: {str(e)}")
            self.connected = False
            return None
    
    def _update_position(self):
        """Update position for simulation"""
        # Random walk with some direction persistence
        if random.random() < 0.1:  # 10% chance to change direction
            self.heading = random.uniform(0, 360)
        
        # Randomly update speed
        if random.random() < 0.2:  # 20% chance to change speed
            self.speed = random.uniform(0, 5.0)  # Speed in m/s
        
        # Convert degrees to radians
        heading_rad = math.radians(self.heading)
        
        # Calculate distance moved (in degrees)
        # Roughly 111km per degree of latitude, speed is in m/s
        # This gives a realistic movement based on speed
        distance = self.speed * 0.00001  # Convert to degrees
        
        # Update position
        self.latitude += distance * math.cos(heading_rad)
        self.longitude += distance * math.sin(heading_rad) / math.cos(math.radians(self.latitude))
        
        # Add some randomness to altitude
        self.altitude += random.uniform(-0.5, 0.5)
        
        # Decrease battery level slowly
        self.battery_level -= random.uniform(0, 0.05)
        if self.battery_level < 0:
            self.battery_level = 0.0
    
    def simulate_trip(self, duration_seconds, interval_seconds):
        """Simulate a trip by sending location data at regular intervals"""
        end_time = time.time() + duration_seconds
        
        try:
            if not self.connect():
                logger.error("Failed to connect for trip simulation")
                return False
            
            logger.info(f"Starting JT808 trip simulation for {duration_seconds} seconds")
            
            while time.time() < end_time and running:
                self.send_location()
                time.sleep(interval_seconds)
                
                # Send heartbeat occasionally
                if random.random() < 0.2:  # 20% chance
                    self.send_heartbeat()
                    
            logger.info("Trip simulation completed")
            return True
            
        except KeyboardInterrupt:
            logger.info("Trip simulation interrupted")
            return False
        except Exception as e:
            logger.error(f"Error during trip simulation: {str(e)}")
            return False
        finally:
            self.disconnect()
    
    def simulate_continuous(self, interval_seconds):
        """Continuously simulate device activity until stopped"""
        try:
            if not self.connect():
                logger.error("Failed to connect for continuous simulation")
                return False
            
            logger.info(f"Starting JT808 continuous simulation with {interval_seconds} second intervals")
            
            heartbeat_counter = 0
            
            while running:
                self.send_location()
                
                # Send heartbeat every 5 location updates
                heartbeat_counter += 1
                if heartbeat_counter >= 5:
                    self.send_heartbeat()
                    heartbeat_counter = 0
                
                time.sleep(interval_seconds)
                    
        except KeyboardInterrupt:
            logger.info("Continuous simulation interrupted")
            return False
        except Exception as e:
            logger.error(f"Error during continuous simulation: {str(e)}")
            return False
        finally:
            self.disconnect()


def signal_handler(sig, frame):
    """Handle interrupt signal"""
    global running
    logger.info("Received interrupt signal, shutting down...")
    running = False

def main():
    """Main function to run simulator from command line"""
    # Set up argument parser
    parser = argparse.ArgumentParser(description='GPS Device Protocol Simulator')
    parser.add_argument('--device-id', required=True, help='Device identifier')
    parser.add_argument('--imei', default='123456789012345', help='Device IMEI number')
    parser.add_argument('--host', default='localhost', help='Protocol server host')
    parser.add_argument('--port', type=int, default=8080, help='Protocol server port')
    parser.add_argument('--interval', type=int, default=5, help='Interval between location updates in seconds')
    parser.add_argument('--duration', type=int, default=0, 
                        help='Duration of simulation in seconds (0 for continuous)')
    parser.add_argument('--latitude', type=float, default=37.7749, help='Starting latitude')
    parser.add_argument('--longitude', type=float, default=-122.4194, help='Starting longitude')
    parser.add_argument('--protocol', choices=['808', 'jt808'], default='808',
                        help='Protocol type: 808 (traditional) or jt808 (Chinese standard)')
    
    args = parser.parse_args()
    
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create and run simulator based on protocol choice
    if args.protocol == 'jt808':
        logger.info(f"Using JT808 protocol simulator")
        simulator = JT808Simulator(args.device_id, args.imei, args.host, args.port)
    else:
        logger.info(f"Using traditional 808 protocol simulator")
        simulator = GPS808Simulator(args.device_id, args.imei, args.host, args.port)
        
    # Set initial position
    simulator.latitude = args.latitude
    simulator.longitude = args.longitude
    
    # Run simulation
    if args.duration > 0:
        simulator.simulate_trip(args.duration, args.interval)
    else:
        simulator.simulate_continuous(args.interval)

if __name__ == "__main__":
    main()