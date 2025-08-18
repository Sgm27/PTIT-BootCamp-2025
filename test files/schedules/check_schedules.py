#!/usr/bin/env python3
"""
Script to check schedules in database
"""
from db.db_config import get_db
from db.models import Notification, User

def check_schedules():
    with get_db() as session:
        try:
            # Check elderly user
            elderly_user = session.query(User).filter(User.email == "son123@gmail.com").first()
            if elderly_user:
                print(f"Elderly User: {elderly_user.full_name} (ID: {elderly_user.id})")
                
                # Check notifications for this user
                notifications = session.query(Notification).filter(
                    Notification.user_id == elderly_user.id
                ).all()
                
                print(f"Found {len(notifications)} notifications:")
                for notif in notifications:
                    print(f"  - {notif.title} ({notif.notification_type}) - {notif.scheduled_at} - Sent: {notif.is_sent}")
            else:
                print("Elderly user not found")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_schedules() 