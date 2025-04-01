from app import app
import os
import logging
from services.protocol808 import start_protocol_server, get_server_instance
import threading
import time

# Setup logging early
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def start_protocol_server_with_retry():
    """Start the 808 protocol server with retry logic in case of initial failure"""
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Starting 808 protocol server (attempt {attempt}/{max_retries})...")
            # Initialize server to configure port
            server = get_server_instance()
            logger.info(f"808 protocol server configured on port {server.port}")
            
            # Start server (this will return a thread that runs the server)
            server_thread = start_protocol_server()
            logger.info("808 protocol server started successfully")
            return server_thread
        except Exception as e:
            logger.error(f"Failed to start 808 protocol server on attempt {attempt}: {str(e)}")
            if attempt < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Maximum retries reached. Protocol server not started.")
                return None

# Start the 808 protocol server when the module is loaded
# This ensures it's started regardless of how the app is run (direct, gunicorn, etc.)
logger.info("Initializing Pet Tracking system and 808 Protocol server")
protocol_thread = start_protocol_server_with_retry()

if __name__ == "__main__":
    logger.info("Starting Pet Tracking API server in direct mode")
    # Run the Flask application
    app.run(host="0.0.0.0", port=5000, debug=True)
