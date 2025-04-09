#!/usr/bin/env python3
"""
Test the MQTT adapter with the JT808 simulator in a single script
"""

import logging
import subprocess
import sys
import time
import threading
import os
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProcessManager:
    """Manage external processes for testing"""
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.stop_flag = threading.Event()
    
    def start_process(self, command: str, name: str) -> Optional[subprocess.Popen]:
        """Start a process and add it to the managed list"""
        try:
            logger.info(f"Starting {name}...")
            process = subprocess.Popen(
                command, 
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            self.processes.append(process)
            
            # Start a thread to read output
            threading.Thread(
                target=self._read_output,
                args=(process, name),
                daemon=True
            ).start()
            
            return process
        except Exception as e:
            logger.error(f"Failed to start {name}: {e}")
            return None
    
    def _read_output(self, process: subprocess.Popen, name: str) -> None:
        """Read and log output from a process"""
        try:
            for line in iter(process.stdout.readline, ''):
                if self.stop_flag.is_set():
                    break
                if line:
                    logger.info(f"{name}: {line.rstrip()}")
        except Exception as e:
            if not self.stop_flag.is_set():
                logger.error(f"Error reading output from {name}: {e}")
    
    def stop_all(self) -> None:
        """Stop all managed processes"""
        self.stop_flag.set()
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                logger.error(f"Error stopping process: {e}")
        
        self.processes = []
        logger.info("All processes stopped")

def main():
    """Run the MQTT test system"""
    # Create process manager
    manager = ProcessManager()
    
    try:
        # Create mosquitto config if it doesn't exist
        if not os.path.exists("mosquitto.conf"):
            with open("mosquitto.conf", "w") as f:
                f.write("""
# Basic configuration
pid_file /tmp/mosquitto.pid
persistence false
allow_anonymous true
log_dest stdout
log_type all
connection_messages true
listener 1883
                """)
        
        # Start the MQTT broker
        broker = manager.start_process(
            "mosquitto -c mosquitto.conf", 
            "MQTT Broker"
        )
        if not broker:
            return 1
        
        # Wait for broker to start
        time.sleep(2)
        
        # Start the protocol adapter
        adapter = manager.start_process(
            "python run_mqtt_adapter.py --debug --protocol-port 8081",
            "Protocol Adapter"
        )
        if not adapter:
            return 1
        
        # Wait for adapter to start
        time.sleep(2)
        
        # Start the MQTT subscriber
        subscriber = manager.start_process(
            "python tools/mqtt_subscriber.py --debug",
            "MQTT Subscriber"
        )
        if not subscriber:
            return 1
        
        # Wait for subscriber to start
        time.sleep(2)
        
        # Print information for the user
        print("\n")
        print("=" * 80)
        print("MQTT Test System Running".center(80))
        print("=" * 80)
        print("\nComponents:")
        print("  * MQTT Broker (Mosquitto) - running on port 1883")
        print("  * JT/T 808 Protocol Adapter - listening on port 8081")
        print("  * MQTT Subscriber - monitoring all device topics")
        print("\nYou can now run the JT808 simulator to test the system:")
        print("  python tools/jt808_simulator.py --port 8081 --interval 5")
        print("\nPress Ctrl+C to stop all components")
        print("=" * 80)
        
        # Start simulator if requested
        if "--with-simulator" in sys.argv:
            simulator = manager.start_process(
                "python tools/jt808_simulator.py --port 8081 --interval 5",
                "JT808 Simulator"
            )
            if not simulator:
                return 1
        
        # Keep the script running
        while True:
            time.sleep(1)
        
    except KeyboardInterrupt:
        print("\nStopping all components...")
    
    finally:
        # Stop all processes
        manager.stop_all()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())