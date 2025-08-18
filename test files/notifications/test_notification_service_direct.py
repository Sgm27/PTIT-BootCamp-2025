#!/usr/bin/env python3
"""
Test script to test notification service directly
"""
import asyncio
from datetime import datetime, timedelta
from db.db_services.notification_service import NotificationDBService
from db.models import NotificationType

async def test_notification_service():
    """Test notification service directly"""
    
    print("=== Test Notification Service Direct ===")
    
    try:
        # Initialize service
        notification_service = NotificationDBService()
        
        # Test data
        user_id = "6dbbe787-9645-4203-94c1-3e5b1e9ca54c"  # son123@gmail.com
        scheduled_time = datetime.now() + timedelta(hours=1)
        
        print(f"Creating notification for user: {user_id}")
        print(f"Scheduled time: {scheduled_time}")
        
        # Create notification using string directly
        notification = await notification_service.create_notification(
            user_id=user_id,
            notification_type="medicine_reminder",  # Use string directly
            title="Test Direct Service",
            message="This is a test notification created directly via service",
            scheduled_at=scheduled_time,
            priority="normal",
            category="medicine",
            has_voice=True
        )
        
        if notification:
            # Get notification info before session closes
            notification_id = str(notification.id)
            notification_title = notification.title
            notification_message = notification.message
            notification_scheduled_at = notification.scheduled_at
            notification_type = notification.notification_type
            notification_category = notification.category
            
            print(f"✅ Notification created successfully!")
            print(f"  - ID: {notification_id}")
            print(f"  - Title: {notification_title}")
            print(f"  - Message: {notification_message}")
            print(f"  - Scheduled At: {notification_scheduled_at}")
            print(f"  - Type: {notification_type}")
            print(f"  - Category: {notification_category}")
            
            # Test getting user notifications
            print(f"\nTesting get_user_notifications...")
            notifications = await notification_service.get_user_notifications(
                user_id=user_id,
                limit=10
            )
            
            print(f"Found {len(notifications)} notifications for user")
            for i, notif in enumerate(notifications):
                print(f"  {i+1}. {notif.title} - {notif.scheduled_at}")
            
            return True
        else:
            print(f"❌ Failed to create notification")
            return False
            
    except Exception as e:
        print(f"❌ Error testing notification service: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_notification_service())
    if success:
        print("\n✅ Notification service test completed successfully!")
    else:
        print("\n❌ Notification service test failed.")
        exit(1) 