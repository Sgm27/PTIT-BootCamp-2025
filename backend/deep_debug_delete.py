#!/usr/bin/env python3
"""
Deep debug for delete notification issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.db_services.notification_service import NotificationDBService
from db.db_config import get_db
from db.models import Notification
import asyncio

async def deep_debug_delete():
    """Deep debug the delete notification issue"""
    
    print("=== Deep Debug Delete Notification ===")
    
    # Test notification ID
    notification_id = "776fcfd6-62f0-47bc-a200-a81ba52b429f"
    
    try:
        print(f"1. Initial check - notification exists?")
        
        # Check directly with database
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
        
        print(f"\n3. Verification after service delete...")
        
        # Check again directly
        with get_db() as db:
            notification_after = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            
            if notification_after:
                print(f"   ❌ Still exists: {notification_after.title}")
                print(f"   - ID: {notification_after.id}")
                print(f"   - User ID: {notification_after.id}")
            else:
                print(f"   ✅ Successfully deleted!")
        
        print(f"\n4. Testing direct database delete...")
        
        # Test direct database delete
        with get_db() as db:
            notification_direct = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            
            if notification_direct:
                print(f"   Found for direct delete: {notification_direct.title}")
                
                # Delete directly
                db.delete(notification_direct)
                db.commit()
                print(f"   Direct delete committed")
                
                # Verify
                notification_verify = db.query(Notification).filter(
                    Notification.id == notification_id
                ).first()
                
                if notification_verify:
                    print(f"   ❌ Still exists after direct delete!")
                else:
                    print(f"   ✅ Direct delete successful!")
            else:
                print(f"   No notification found for direct delete")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(deep_debug_delete()) 