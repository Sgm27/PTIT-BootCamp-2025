#!/usr/bin/env python3
"""
Debug script for delete notification issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.db_services.notification_service import NotificationDBService
from db.db_config import get_db
from db.models import Notification
import asyncio

async def debug_delete():
    """Debug the delete notification issue"""
    
    print("=== Debug Delete Notification Issue ===")
    
    # Test notification ID
    notification_id = "f5978776-c780-4c12-b22d-71b81a6d5737"
    
    try:
        # Initialize service
        notification_service = NotificationDBService()
        
        print(f"1. Checking if notification exists: {notification_id}")
        
        # Check if notification exists
        notification = await notification_service.get_notification(notification_id)
        if notification:
            print(f"   ✅ Found notification: {notification.title}")
            print(f"   - ID: {notification.id}")
            print(f"   - User ID: {notification.user_id}")
            print(f"   - Title: {notification.title}")
            print(f"   - Created at: {notification.created_at}")
        else:
            print(f"   ❌ Notification not found")
            return
        
        print(f"\n2. Attempting to delete notification...")
        
        # Try to delete
        success = await notification_service.delete_notification(notification_id)
        print(f"   Delete result: {success}")
        
        print(f"\n3. Checking if notification still exists...")
        
        # Check again
        notification_after = await notification_service.get_notification(notification_id)
        if notification_after:
            print(f"   ❌ Notification still exists after deletion!")
            print(f"   - ID: {notification_after.id}")
            print(f"   - Title: {notification_after.title}")
        else:
            print(f"   ✅ Notification successfully deleted!")
        
        print(f"\n4. Checking database directly...")
        
        # Check database directly
        with get_db() as db:
            db_notification = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            
            if db_notification:
                print(f"   ❌ Found in database: {db_notification.title}")
            else:
                print(f"   ✅ Not found in database")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_delete()) 