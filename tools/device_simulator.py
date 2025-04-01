#!/usr/bin/env python3
"""
808 Protocol Device Simulator

This script simulates a GPS tracking device that communicates using the 808 protocol.
It can be used for testing the pet tracking system without a physical device.

Usage:
    python device_simulator.py --device-id <device_id> --imei <imei> --interval <seconds>

Example:
    python device_simulator.py --device-id 9c96e35f-1339-4e32-8ee4-65904ca55df1 --imei 123456789012345 --interval 10
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
        # Format: ##,imei:IMEI,A,date_time,device_id,*checksum##
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        message = f"##,imei:{self.imei},BP01,{timestamp},{self.device_id},*FF##"
        response = self._send_message(message)
        logger.info(f"Login response: {response}")
    
    def send_heartbeat(self):
        """Send a heartbeat message to the server"""
        if not self.connected and not self.connect():
            return False
            
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        message = f"##,imei:{self.imei},BP00,{timestamp},{self.device_id},{self.battery_level},*FF##"
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
        
        # Format: ##,imei:IMEI,BP02,timestamp,device_id,lat,lon,altitude,speed,heading,bat_level,*checksum##
        message = (f"##,imei:{self.imei},BP02,{timestamp},{self.device_id},"
                   f"{self.latitude:.6f},{self.longitude:.6f},{self.altitude:.1f},"
                   f"{self.speed:.1f},{self.heading:.1f},{self.battery_level:.1f},*FF##")
        
        response = self._send_message(message)
        logger.info(f"Location sent: lat={self.latitude:.6f}, lon={self.longitude:.6f}, speed={self.speed:.1f}, battery={self.battery_level:.1f}")
        logger.debug(f"Location response: {response}")
        return True
    
    def _send_message(self, message):
        """Send a message to the server and receive response"""
        try:
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

def signal_handler(sig, frame):
    """Handle interrupt signal"""
    global running
    logger.info("Received interrupt signal, shutting down...")
    running = False

def main():
    """Main function to run simulator from command line"""
    # Set up argument parser
    parser = argparse.ArgumentParser(description='808 Protocol GPS Device Simulator')
    parser.add_argument('--device-id', required=True, help='Device identifier')
    parser.add_argument('--imei', default='123456789012345', help='Device IMEI number')
    parser.add_argument('--host', default='localhost', help='Protocol 808 server host')
    parser.add_argument('--port', type=int, default=8080, help='Protocol 808 server port')
    parser.add_argument('--interval', type=int, default=5, help='Interval between location updates in seconds')
    parser.add_argument('--duration', type=int, default=0, 
                        help='Duration of simulation in seconds (0 for continuous)')
    parser.add_argument('--latitude', type=float, default=37.7749, help='Starting latitude')
    parser.add_argument('--longitude', type=float, default=-122.4194, help='Starting longitude')
    
    args = parser.parse_args()
    
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create and run simulator
    simulator = GPS808Simulator(args.device_id, args.imei, args.host, args.port)
    simulator.latitude = args.latitude
    simulator.longitude = args.longitude
    
    if args.duration > 0:
        simulator.simulate_trip(args.duration, args.interval)
    else:
        simulator.simulate_continuous(args.interval)

if __name__ == "__main__":
    main()