from app import app
import os
import logging
from services.protocol808 import start_protocol_server
import threading

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    # Start 808 protocol server in a separate thread
    protocol_thread = threading.Thread(target=start_protocol_server)
    protocol_thread.daemon = True
    protocol_thread.start()
    
    logger.info("Starting Pet Tracking API server")
    # Run the Flask application
    app.run(host="0.0.0.0", port=5000, debug=True)
