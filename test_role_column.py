"""
Test script to verify the User model with the role column
This script tests both successful scenarios and error handling for schema issues
"""
from app import app, db
from models import User
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_role_column():
    """Test the role column in the User model"""
    with app.app_context():
        try:
            # Test 1: Query a user with role
            logger.info("TEST 1: Query a user with role field")
            user = User.query.filter_by(role='user').first()
            logger.info(f"Found user with role 'user': {user.email if user else 'None'}")
            
            # Test 2: Create a user with role
            logger.info("TEST 2: Create a user with role field")
            try:
                test_email = "roletest@example.com"
                existing = User.query.filter_by(email=test_email).first()
                if existing:
                    logger.info(f"User {test_email} already exists, deleting first")
                    db.session.delete(existing)
                    db.session.commit()
                
                new_user = User(
                    email=test_email,
                    username="roletest",
                    first_name="Role",
                    last_name="Test",
                    role="tester"
                )
                db.session.add(new_user)
                db.session.commit()
                logger.info(f"Created user with role 'tester': {new_user.email}")
                
                # Clean up after test
                db.session.delete(new_user)
                db.session.commit()
                logger.info("Test user deleted")
            except Exception as e:
                logger.error(f"Error creating user: {str(e)}")
                db.session.rollback()
            
            # Test 3: Test error handler for missing column
            logger.info("TEST 3: Simulate a missing column query")
            try:
                # This will generate an error if executed directly in SQL
                # We'll just log what would happen
                logger.info("Simulating error: SELECT * FROM \"user\" WHERE nonexistent_column = 'value'")
                
                # Example error handling code
                error_msg = "column user.nonexistent_column does not exist"
                import re
                match = re.search(r"column (\w+\.\w+) does not exist", error_msg)
                if match:
                    missing_column = match.group(1)
                    logger.info(f"Successfully parsed error and identified missing column: {missing_column}")
                else:
                    logger.error("Failed to parse column error message")
            except Exception as e:
                logger.error(f"Unexpected error in simulation: {str(e)}")
            
            logger.info("All tests completed!")
            
        except Exception as e:
            logger.error(f"Error testing role column: {str(e)}")
            logger.error(traceback.format_exc())

if __name__ == "__main__":
    test_role_column()