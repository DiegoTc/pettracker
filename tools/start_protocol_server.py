#!/usr/bin/env python3
"""
Protocol 808 Server Standalone Starter

This script runs the 808 Protocol server without starting the full Flask application.
It's useful for testing device simulators when you don't need the web API.

Usage:
    python start_protocol_server.py
"""

import os
import sys
import logging
import time
import threading
import signal

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('protocol_server')

# Create a event to signal when script should exit
shutdown_event = threading.Event()

def signal_handler(sig, frame):
    """Handle interrupt signal"""
    logger.info(f"Received signal {sig}, shutting down...")
    shutdown_event.set()

def main():
    """Main function to start the 808 protocol server standalone"""
    # Import here to avoid circular imports
    from services.protocol808 import start_protocol_server, stop_protocol_server
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        logger.info("Starting 808 Protocol server...")
        server_thread = start_protocol_server()
        
        logger.info("Server started, press Ctrl+C to stop")
        
        # Keep running until shutdown signal
        while not shutdown_event.is_set():
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"Error running server: {str(e)}")
    finally:
        logger.info("Stopping 808 Protocol server...")
        stop_protocol_server()
        logger.info("Server stopped")

if __name__ == "__main__":
    main()