#!/usr/bin/env python3
"""
Script to verify sample data has been added successfully
"""
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.db_config import get_db
from db.models import User, Conversation, ConversationMessage, LifeMemoir

TARGET_EMAIL = "son123@gmail.com"
TARGET_USER_ID = "dd8d892b-fa77-4a71-9520-71baf601c3ba"

def verify_sample_data():
    """Verify all sample data has been added"""
    
    print("=== Verifying Sample Data for son123@gmail.com ===")
    print(f"User ID: {TARGET_USER_ID}")
    print(f"Email: {TARGET_EMAIL}")
    print("=" * 50)
    
    with get_db() as session:
        try:
            # Check user exists
            user = session.query(User).filter(User.email == TARGET_EMAIL).first()
            if not user:
                print("❌ User not found!")
                return False
            
            print(f"✅ User found: {user.full_name} ({user.email})")
            
            # Check conversations
            conversations = session.query(Conversation).filter(Conversation.user_id == user.id).all()
            print(f"\n📞 Conversations: {len(conversations)}")
            for i, conv in enumerate(conversations):
                # Count messages for this conversation
                message_count = session.query(ConversationMessage).filter(
                    ConversationMessage.conversation_id == conv.id
                ).count()
                
                print(f"   {i+1}. {conv.title}")
                print(f"      - Messages: {message_count}")
                print(f"      - Started: {conv.started_at}")
                print(f"      - Summary: {conv.conversation_summary[:100]}...")
            
            # Check memoirs
            memoirs = session.query(LifeMemoir).filter(LifeMemoir.user_id == user.id).all()
            print(f"\n📖 Life Memoirs: {len(memoirs)}")
            for i, memoir in enumerate(memoirs):
                print(f"   {i+1}. {memoir.title}")
                print(f"      - Categories: {memoir.categories}")
                print(f"      - Time Period: {memoir.time_period}")
                print(f"      - Emotional Tone: {memoir.emotional_tone}")
                print(f"      - Importance Score: {memoir.importance_score}")
                print(f"      - Content: {memoir.content[:100]}...")
            
            # Check notifications (try to query directly if possible)
            try:
                # Using raw SQL since we might not have the notification model imported correctly
                result = session.execute(
                    "SELECT COUNT(*) FROM notifications WHERE user_id = %s",
                    (str(user.id),)
                )
                notification_count = result.fetchone()[0]
                print(f"\n🔔 Notifications: {notification_count}")
                
                # Get some notification details
                result = session.execute(
                    "SELECT title, scheduled_at, notification_type, category FROM notifications WHERE user_id = %s ORDER BY scheduled_at LIMIT 5",
                    (str(user.id),)
                )
                notifications = result.fetchall()
                for i, notif in enumerate(notifications):
                    print(f"   {i+1}. {notif[0]}")
                    print(f"      - Scheduled: {notif[1]}")
                    print(f"      - Type: {notif[2]}")
                    print(f"      - Category: {notif[3]}")
                    
            except Exception as e:
                print(f"⚠️  Could not check notifications: {e}")
            
            print("\n" + "=" * 50)
            print("✅ Sample data verification completed!")
            print(f"📊 Summary:")
            print(f"   - Conversations: {len(conversations)}")
            print(f"   - Total Messages: {sum(session.query(ConversationMessage).filter(ConversationMessage.conversation_id == conv.id).count() for conv in conversations)}")
            print(f"   - Life Memoirs: {len(memoirs)}")
            print(f"   - Notifications: {notification_count if 'notification_count' in locals() else 'N/A'}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error verifying sample data: {e}")
            return False

if __name__ == "__main__":
    success = verify_sample_data()
    if not success:
        print("\n❌ Sample data verification failed.")
        exit(1)
    else:
        print("\n🎉 All sample data verified successfully!")
