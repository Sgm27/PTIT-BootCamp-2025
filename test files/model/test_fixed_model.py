#!/usr/bin/env python3
"""
Test script to verify the fixed Notification model
"""
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.db_config import get_db
from db.models import User, Notification

def test_fixed_model():
    """Test if the fixed model can query notifications"""
    
    print("=== Testing Fixed Notification Model ===\n")
    
    try:
        with get_db() as session:
            # Check elderly user
            elderly_user = session.query(User).filter(User.email == "son123@gmail.com").first()
            if elderly_user:
                print(f"✅ Elderly user found: {elderly_user.full_name} (ID: {elderly_user.id})")
                
                # Try to query notifications with fixed model
                notifications = session.query(Notification).filter(
                    Notification.user_id == elderly_user.id
                ).all()
                
                print(f"✅ Successfully queried {len(notifications)} notifications!")
                
                for notif in notifications:
                    status = "COMPLETED" if notif.is_sent else "PENDING"
                    print(f"  - {notif.title} ({notif.notification_type}) - {notif.scheduled_at} - {status}")
                
                return True
            else:
                print("❌ Elderly user not found")
                return False
                
    except Exception as e:
        print(f"❌ Error testing fixed model: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fixed_model()
    if success:
        print("\n🎉 Model fix successful! SQLAlchemy can now query notifications.")
        print("The API should now return the correct schedule data.")
    else:
        print("\n❌ Model fix failed. Need to investigate further.") 