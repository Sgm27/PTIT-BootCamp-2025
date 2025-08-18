#!/usr/bin/env python3
"""
Test database service directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.db_services.notification_service import NotificationDBService
from db.db_config import get_db
from db.models import Notification

def test_db_service():
    """Test database service directly"""
    
    print("=== Testing Database Service Directly ===")
    
    # Test notification ID
    notification_id = "27f31895-7e79-4f3d-9ac3-a3c0411859f8"
    
    try:
        print(f"1. Checking notification: {notification_id}")
        
        # Check if exists
        with get_db() as db:
            notification = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            
            if notification:
                print(f"   ✅ Found: {notification.title}")
                print(f"   - ID: {notification.id}")
                print(f"   - User ID: {notification.user_id}")
                print(f"   - Created: {notification.created_at}")
            else:
                print(f"   ❌ Not found")
                return
        
        print(f"\n2. Testing service layer delete...")
        
        # Test with service layer
        notification_service = NotificationDBService()
        
        # Try to delete
        success = notification_service.delete_notification(notification_id)
        print(f"   Service delete result: {success}")
        
        print(f"\n3. Verifying deletion...")
        
        # Check again directly
        with get_db() as db:
            notification_after = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            
            if notification_after:
                print(f"   ❌ Still exists: {notification_after.title}")
                print(f"   - ID: {notification_after.id}")
                print(f"   - User ID: {notification_after.user_id}")
            else:
                print(f"   ✅ Successfully deleted!")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_db_service() 