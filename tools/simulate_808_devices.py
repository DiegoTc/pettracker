#!/usr/bin/env python3
"""
JT/T 808 Device Simulator for Production Testing

This script simulates multiple JT/T 808 protocol devices connecting to 
our production endpoint (pettrack.com:808) and sending location data.

Features:
- Creates multiple virtual GPS tracking devices
- Sends registration messages
- Sends location updates with configurable frequency
- Sends heartbeat messages periodically
- Can simulate movement patterns

Usage:
    python tools/simulate_808_devices.py --host pettrack.com --port 808 --count 5 --interval 30
"""

import argparse
import logging
import random
import sys
import threading
import time
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import the JT808 simulator
try:
    from tools.jt808_simulator import JT808DeviceSimulator
except ImportError:
    logger.error("Failed to import JT808DeviceSimulator. Make sure the class is available.")
    sys.exit(1)


class DeviceSimulationManager:
    """Manages multiple simulated JT/T 808 protocol devices"""
    
    def __init__(self, 
                 server_host: str = 'pettrack.com', 
                 server_port: int = 808,
                 device_count: int = 1,
                 update_interval: int = 10,
                 simulation_mode: str = 'random'):
        """
        Initialize the simulation manager.
        
        Args:
            server_host: Host to connect the devices to (default: pettrack.com)
            server_port: Port to connect to (default: 808)
            device_count: Number of devices to simulate (default: 1)
            update_interval: Seconds between location updates (default: 10)
            simulation_mode: Movement pattern to simulate ('random', 'circular', 'fixed')
        """
        self.server_host = server_host
        self.server_port = server_port
        self.device_count = device_count
        self.update_interval = update_interval
        self.simulation_mode = simulation_mode
        
        self.simulators = []
        self.running = False
        self.threads = []
        
    def start(self):
        """Start the device simulators"""
        self.running = True
        
        # Create the devices
        logger.info(f"Creating {self.device_count} simulated JT808 devices...")
        
        # Bay Area starting locations (for more realistic and varied movement)
        base_locations = [
            (37.7749, -122.4194),  # San Francisco
            (37.8044, -122.2712),  # Oakland
            (37.3382, -121.8863),  # San Jose
            (37.5485, -121.9886),  # Fremont
            (37.6872, -122.4702),  # Pacifica
        ]
        
        for i in range(self.device_count):
            # Choose a base location (cycling through the list)
            base_lat, base_lon = base_locations[i % len(base_locations)]
            
            # Add small random offset to avoid all devices being at exactly the same location
            lat_offset = random.uniform(-0.01, 0.01)
            lon_offset = random.uniform(-0.01, 0.01)
            
            # Create a simulator with a unique device ID
            device_id = f"SIM{i+1:03d}"
            simulator = JT808DeviceSimulator(
                server_host=self.server_host,
                server_port=self.server_port,
                device_id=device_id,
                initial_latitude=base_lat + lat_offset,
                initial_longitude=base_lon + lon_offset,
                move_randomly=(self.simulation_mode == 'random')
            )
            self.simulators.append(simulator)
        
        # Connect and register all devices
        connected_simulators = []
        for simulator in self.simulators:
            try:
                if simulator.connect():
                    if simulator.send_registration():
                        logger.info(f"Device {simulator.device_id} registered successfully")
                        connected_simulators.append(simulator)
                    else:
                        logger.error(f"Failed to register device {simulator.device_id}")
                else:
                    logger.error(f"Failed to connect device {simulator.device_id}")
            except Exception as e:
                logger.error(f"Error setting up device {simulator.device_id}: {e}")
        
        # Update list with only connected simulators
        self.simulators = connected_simulators
        
        if not self.simulators:
            logger.error("No devices were successfully connected and registered")
            self.running = False
            return False
        
        # Start a thread for each simulator
        for simulator in self.simulators:
            thread = threading.Thread(
                target=self._device_loop,
                args=(simulator,)
            )
            thread.daemon = True
            thread.start()
            self.threads.append(thread)
        
        logger.info(f"Started {len(self.simulators)} device simulation threads")
        return True
    
    def _device_loop(self, simulator):
        """
        Main loop for each simulated device.
        
        Args:
            simulator: The JT808DeviceSimulator instance
        """
        heartbeat_counter = 0
        
        try:
            while self.running:
                # Send location update
                try:
                    simulator.send_location()
                    logger.debug(f"Sent location update from {simulator.device_id}")
                except Exception as e:
                    logger.error(f"Error sending location from {simulator.device_id}: {e}")
                
                # Send heartbeat every 5 cycles
                heartbeat_counter += 1
                if heartbeat_counter >= 5:
                    try:
                        simulator.send_heartbeat()
                        logger.debug(f"Sent heartbeat from {simulator.device_id}")
                    except Exception as e:
                        logger.error(f"Error sending heartbeat from {simulator.device_id}: {e}")
                    heartbeat_counter = 0
                
                # Wait for next update
                for _ in range(self.update_interval):
                    if not self.running:
                        break
                    time.sleep(1)
        
        except Exception as e:
            logger.error(f"Error in device loop for {simulator.device_id}: {e}")
        finally:
            try:
                # Try to disconnect cleanly
                simulator.disconnect()
            except:
                pass
    
    def stop(self):
        """Stop all simulated devices"""
        logger.info("Stopping device simulation...")
        self.running = False
        
        # Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=2.0)
        
        # Force disconnect any remaining simulators
        for simulator in self.simulators:
            try:
                simulator.disconnect()
            except:
                pass
        
        logger.info("Device simulation stopped")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='JT/T 808 Device Simulator for Production Testing')
    
    parser.add_argument(
        '--host',
        default='pettrack.com',
        help='Server host to connect to (default: pettrack.com)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=808,
        help='Server port to connect to (default: 808)'
    )
    
    parser.add_argument(
        '--count',
        type=int,
        default=3,
        help='Number of devices to simulate (default: 3)'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Seconds between location updates (default: 30)'
    )
    
    parser.add_argument(
        '--mode',
        choices=['random', 'circular', 'fixed'],
        default='random',
        help='Movement pattern to simulate (default: random)'
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
        logger.info("Debug logging enabled")
    
    logger.info("==========================================")
    logger.info("  JT/T 808 Protocol Device Simulator")
    logger.info("==========================================")
    logger.info(f"Target server: {args.host}:{args.port}")
    logger.info(f"Simulating {args.count} devices")
    logger.info(f"Update interval: {args.interval} seconds")
    logger.info(f"Movement mode: {args.mode}")
    logger.info("------------------------------------------")
    
    # Start simulation
    simulation = DeviceSimulationManager(
        server_host=args.host,
        server_port=args.port,
        device_count=args.count,
        update_interval=args.interval,
        simulation_mode=args.mode
    )
    
    if not simulation.start():
        logger.error("Failed to start simulation")
        return 1
    
    # Keep the main thread running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Simulation interrupted by user")
    finally:
        simulation.stop()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())