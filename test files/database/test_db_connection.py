#!/usr/bin/env python3
"""
Test database connection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.db_config import get_db, engine
from db.models import Notification
from sqlalchemy.orm import sessionmaker

def test_db_connection():
    """Test database connection"""
    
    print("=== Testing Database Connection ===")
    
    # Test notification ID
    notification_id = "adfcaa97-3471-4112-adce-366f7c18cf2e"
    
    try:
        print(f"1. Testing get_db() context manager...")
        
        # Test with get_db() context manager
        with get_db() as db:
            notification = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            
            if notification:
                print(f"   ✅ Found with get_db(): {notification.title}")
            else:
                print(f"   ❌ Not found with get_db()")
                return
        
        print(f"\n2. Testing direct session...")
        
        # Test with direct session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            notification = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            
            if notification:
                print(f"   ✅ Found with direct session: {notification.title}")
            else:
                print(f"   ❌ Not found with direct session")
                return
                
        finally:
            db.close()
        
        print(f"\n3. Testing delete with get_db()...")
        
        # Test delete with get_db()
        with get_db() as db:
            notification = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            
            if notification:
                print(f"   Found for deletion: {notification.title}")
                
                # Delete
                db.delete(notification)
                db.commit()
                print(f"   Deleted with get_db()")
                
                # Verify
                notification_verify = db.query(Notification).filter(
                    Notification.id == notification_id
                ).first()
                
                if notification_verify:
                    print(f"   ❌ Still exists after get_db() delete")
                else:
                    print(f"   ✅ Successfully deleted with get_db()")
            else:
                print(f"   No notification found for deletion")
        
        print(f"\n4. Testing delete with direct session...")
        
        # Test delete with direct session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            notification = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            
            if notification:
                print(f"   Found for deletion: {notification.title}")
                
                # Delete
                db.delete(notification)
                db.commit()
                print(f"   Deleted with direct session")
                
                # Verify
                notification_verify = db.query(Notification).filter(
                    Notification.id == notification_id
                ).first()
                
                if notification_verify:
                    print(f"   ❌ Still exists after direct session delete")
                else:
                    print(f"   ✅ Successfully deleted with direct session")
            else:
                print(f"   No notification found for deletion")
                
        finally:
            db.close()
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_db_connection() 