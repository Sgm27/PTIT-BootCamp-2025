#!/usr/bin/env python3
"""
Test direct database delete
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.db_config import get_db
from db.models import Notification

def test_direct_delete():
    """Test direct database delete"""
    
    print("=== Testing Direct Database Delete ===")
    
    # Test notification ID
    notification_id = "8f660bf0-9e6b-462a-a371-70e356eedb3e"
    
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
        
        print(f"\n2. Attempting direct delete...")
        
        # Try to delete directly
        with get_db() as db:
            notification = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            
            if notification:
                print(f"   Found for deletion: {notification.title}")
                
                # Delete directly
                db.delete(notification)
                print(f"   Object marked for deletion")
                
                # Commit
                db.commit()
                print(f"   Transaction committed")
                
                # Verify immediately
                notification_verify = db.query(Notification).filter(
                    Notification.id == notification_id
                ).first()
                
                if notification_verify:
                    print(f"   ❌ Still exists after commit!")
                else:
                    print(f"   ✅ Direct delete successful!")
            else:
                print(f"   No notification found for deletion")
        
        print(f"\n3. Verifying with new session...")
        
        # Check with new session
        with get_db() as db:
            notification_after = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            
            if notification_after:
                print(f"   ❌ Still exists in new session: {notification_after.title}")
            else:
                print(f"   ✅ Not found in new session - deletion confirmed!")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_delete() 