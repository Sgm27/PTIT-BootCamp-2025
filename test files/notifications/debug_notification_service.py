#!/usr/bin/env python3
"""
Debug script to test NotificationDBService directly
"""
import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.db_config import get_db
from db.models import User, Notification, NotificationType
from db.db_services.notification_service import NotificationDBService

def debug_notification_service():
    """Debug NotificationDBService directly"""
    
    print("=== Debugging NotificationDBService ===\n")
    
    try:
        # 1. Check database connection and data
        print("1. Checking database directly...")
        with get_db() as session:
            # Check elderly user
            elderly_user = session.query(User).filter(User.email == "son123@gmail.com").first()
            if elderly_user:
                print(f"✅ Elderly user found: {elderly_user.full_name} (ID: {elderly_user.id})")
                
                # Check notifications directly
                notifications = session.query(Notification).filter(
                    Notification.user_id == elderly_user.id
                ).all()
                print(f"✅ Found {len(notifications)} notifications in database directly")
                
                for notif in notifications:
                    status = "COMPLETED" if notif.is_sent else "PENDING"
                    print(f"  - {notif.title} ({notif.notification_type}) - {notif.scheduled_at} - {status}")
            else:
                print("❌ Elderly user not found")
                return
        
        # 2. Test NotificationDBService
        print("\n2. Testing NotificationDBService...")
        notification_service = NotificationDBService()
        
        # Test get_user_notifications
        print("Testing get_user_notifications...")
        try:
            # This should work since we're in the same process
            import asyncio
            
            async def test_service():
                notifications = await notification_service.get_user_notifications(
                    user_id=str(elderly_user.id),
                    limit=100
                )
                print(f"✅ Service returned {len(notifications)} notifications")
                
                for notif in notifications:
                    status = "COMPLETED" if notif.is_sent else "PENDING"
                    print(f"  - {notif.title} ({notif.notification_type}) - {notif.scheduled_at} - {status}")
                
                return notifications
            
            # Run the async function
            notifications = asyncio.run(test_service())
            
        except Exception as e:
            print(f"❌ Error testing service: {e}")
            import traceback
            traceback.print_exc()
        
        # 3. Test raw SQL query
        print("\n3. Testing raw SQL query...")
        try:
            import psycopg2
            from db.db_config import DB_CONFIG
            
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            
            # Query notifications directly
            cur.execute("""
                SELECT id, title, notification_type, scheduled_at, is_sent, category
                FROM notifications 
                WHERE user_id = %s
                ORDER BY scheduled_at
            """, (str(elderly_user.id),))
            
            raw_notifications = cur.fetchall()
            print(f"✅ Raw SQL found {len(raw_notifications)} notifications")
            
            for notif in raw_notifications:
                notif_id, title, notif_type, scheduled_at, is_sent, category = notif
                status = "COMPLETED" if is_sent else "PENDING"
                print(f"  - {title} ({notif_type}) - {scheduled_at} - {status} - {category}")
            
            cur.close()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error with raw SQL: {e}")
            import traceback
            traceback.print_exc()
        
        # 4. Check enum mapping
        print("\n4. Checking enum mapping...")
        try:
            with get_db() as session:
                # Try to query with specific enum value
                medicine_notifications = session.query(Notification).filter(
                    and_(
                        Notification.user_id == elderly_user.id,
                        Notification.notification_type == NotificationType.MEDICINE_REMINDER
                    )
                ).all()
                
                print(f"✅ Found {len(medicine_notifications)} medicine notifications with enum")
                
                for notif in medicine_notifications:
                    status = "COMPLETED" if notif.is_sent else "PENDING"
                    print(f"  - {notif.title} ({notif.notification_type}) - {notif.scheduled_at} - {status}")
                
        except Exception as e:
            print(f"❌ Error with enum query: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n=== Debug Summary ===")
        print("If the service returns empty results but raw SQL works, there's")
        print("a mismatch between SQLAlchemy models and database schema.")
        
    except Exception as e:
        print(f"❌ Error in debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Import required modules
    from sqlalchemy import and_
    
    debug_notification_service() 