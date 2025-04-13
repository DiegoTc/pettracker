"""
Script to add the 'role' column to the user table if it doesn't exist
Run this script locally to fix your database schema
"""
from sqlalchemy import inspect, text
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_role_column(db_url=None):
    """Add the role column to the user table if it doesn't exist"""
    # Import here to avoid circular imports
    from sqlalchemy import create_engine
    
    # Use provided database URL or get from environment
    if not db_url:
        db_url = os.environ.get("DATABASE_URL")
        if not db_url:
            logger.error("No database URL provided or found in DATABASE_URL environment variable")
            return False
    
    logger.info(f"Connecting to database...")
    
    try:
        # Create engine
        engine = create_engine(db_url)
        
        # Get database inspector
        inspector = inspect(engine)
        
        # Check if role column exists
        columns = [col['name'] for col in inspector.get_columns('user')]
        logger.info(f"Found columns in user table: {columns}")
        
        # If role column doesn't exist, add it
        if 'role' not in columns:
            logger.info("Role column doesn't exist, adding it...")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE \"user\" ADD COLUMN role VARCHAR(20) DEFAULT 'user' NOT NULL"))
                conn.commit()
            logger.info("Role column added successfully")
            
            # Verify the column was added
            inspector = inspect(engine)
            new_columns = [col['name'] for col in inspector.get_columns('user')]
            if 'role' in new_columns:
                logger.info("Verified: role column is now present in the user table")
                return True
            else:
                logger.error("Failed to add role column - column not found after adding")
                return False
        else:
            logger.info("Role column already exists")
            return True
            
    except Exception as e:
        logger.error(f"Error adding role column: {str(e)}")
        return False

if __name__ == "__main__":
    # Run the function
    print("This script will add the 'role' column to your user table if it doesn't exist.")
    print("Enter your database URL (or press Enter to use DATABASE_URL environment variable):")
    db_url = input().strip()
    
    if db_url:
        result = add_role_column(db_url)
    else:
        result = add_role_column()
        
    if result:
        print("\nSUCCESS: Role column has been added or already exists in your database!")
    else:
        print("\nFAILED: There was an error adding the role column. Check the logs for details.")