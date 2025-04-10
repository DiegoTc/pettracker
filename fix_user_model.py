from app import app, db
from sqlalchemy import inspect, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_role_column():
    """Ensure the role column exists in the user table"""
    with app.app_context():
        # Get database inspector
        inspector = inspect(db.engine)
        
        # Check if role column exists
        columns = [col['name'] for col in inspector.get_columns('user')]
        logger.info(f"Found columns in user table: {columns}")
        
        # If role column doesn't exist, add it
        if 'role' not in columns:
            logger.info("Role column doesn't exist, adding it...")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE \"user\" ADD COLUMN role VARCHAR(20) DEFAULT 'user' NOT NULL"))
                conn.commit()
            logger.info("Role column added successfully")
        else:
            logger.info("Role column already exists")
        
        # Refresh SQLAlchemy metadata
        logger.info("Refreshing SQLAlchemy metadata")
        db.Model.metadata.reflect(db.engine)
        
        # Verify the column now exists and is accessible
        try:
            from models import User
            # Create a test query that should access the role column
            user = User.query.filter_by(role='user').first()
            logger.info(f"Successfully queried using role column: {user}")
        except Exception as e:
            logger.error(f"Error trying to access role column: {str(e)}")

if __name__ == "__main__":
    ensure_role_column()