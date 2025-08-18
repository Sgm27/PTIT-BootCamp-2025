#!/usr/bin/env python3
"""
Simple test for delete notification
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.db_config import get_db
from db.models import Notification
import uuid

def test_simple_delete():
    """Test simple delete without service layer"""
    
    print("=== Simple Delete Test ===")
    
    # Test notification ID
    notification_id = "f5978776-c780-4c12-b22d-71b81a6d5737"
    
    try:
        print(f"1. Checking notification: {notification_id}")
        
        with get_db() as db:
            # Check if exists
            notification = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            
            if notification:
                print(f"   ✅ Found: {notification.title}")
                print(f"   - User ID: {notification.user_id}")
                print(f"   - Created: {notification.created_at}")
            else:
                print(f"   ❌ Not found")
                return
            
            print(f"\n2. Attempting delete...")
            
            # Try to delete
            db.delete(notification)
            print(f"   Object marked for deletion")
            
            # Commit
            db.commit()
            print(f"   Transaction committed")
            
            print(f"\n3. Verifying deletion...")
            
            # Check again
            notification_after = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            
            if notification_after:
                print(f"   ❌ Still exists: {notification_after.title}")
            else:
                print(f"   ✅ Successfully deleted!")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_delete() 