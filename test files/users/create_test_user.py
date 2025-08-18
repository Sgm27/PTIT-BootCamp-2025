#!/usr/bin/env python3
"""
Script để tạo test user trong database cho connection testing
"""
import uuid
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test user UUID - same as used in test script
TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440000"

def create_test_user():
    """Create test user in database"""
    try:
        from db.db_config import get_db
        from db.models import User, UserType
        
        with get_db() as db:
            # Check if test user already exists
            existing_user = db.query(User).filter(User.id == TEST_USER_ID).first()
            
            if existing_user:
                logger.info(f"Test user already exists: {existing_user.full_name}")
                return TEST_USER_ID
            
            # Create new test user
            test_user = User(
                id=uuid.UUID(TEST_USER_ID),
                user_type=UserType.ELDERLY,
                email="test@connection.stability",
                phone="0123456789",
                full_name="Test User for Connection Stability",
                date_of_birth=datetime(1950, 1, 1).date(),
                gender="other",
                address="Test Address",
                city="Test City",
                country="Vietnam",
                is_active=True,
                preferred_language="vi",
                timezone="Asia/Ho_Chi_Minh",
                notification_settings={}
            )
            
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            logger.info(f"✅ Test user created successfully: {test_user.full_name}")
            logger.info(f"   ID: {test_user.id}")
            logger.info(f"   Email: {test_user.email}")
            logger.info(f"   Phone: {test_user.phone}")
            
            return str(test_user.id)
            
    except Exception as e:
        logger.error(f"❌ Failed to create test user: {e}")
        return None

def main():
    """Main function"""
    logger.info("🔧 Creating test user for connection stability testing...")
    
    user_id = create_test_user()
    
    if user_id:
        logger.info("✅ Test user setup completed successfully")
        logger.info(f"   Test User ID: {user_id}")
        logger.info("   You can now run connection stability tests")
    else:
        logger.error("❌ Failed to setup test user")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 