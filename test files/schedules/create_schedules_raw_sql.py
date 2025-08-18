#!/usr/bin/env python3
"""
Script to create schedules using raw SQL
"""
import psycopg2
from datetime import datetime, timedelta
import uuid
from db.db_config import DB_CONFIG

def create_schedules_raw_sql():
    """Create schedules using raw SQL"""
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Get elderly user ID
        cur.execute("SELECT id FROM users WHERE email = %s", ("son123@gmail.com",))
        user_result = cur.fetchone()
        
        if not user_result:
            print("❌ Elderly user not found")
            return False
        
        elderly_user_id = user_result[0]
        print(f"✅ Found elderly user ID: {elderly_user_id}")
        
        # Delete existing notifications first
        cur.execute("DELETE FROM notifications WHERE user_id = %s", (elderly_user_id,))
        deleted_count = cur.rowcount
        print(f"🗑️ Deleted {deleted_count} existing notifications")
        
        # Today's schedules (August 7th)
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Schedule 1: Uống thuốc huyết áp - 8:00 AM (COMPLETED)
        schedule1_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO notifications (id, user_id, notification_type, title, message, 
                                     scheduled_at, sent_at, is_sent, is_read, has_voice, 
                                     priority, category, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            schedule1_id, elderly_user_id, "medicine_reminder", "Uống thuốc huyết áp",
            "Nhớ uống thuốc huyết áp Amlodipine 5mg vào buổi sáng",
            today.replace(hour=8, minute=0), today.replace(hour=8, minute=5),
            True, False, True, "high", "medicine", datetime.now()
        ))
        print("✅ Created: Uống thuốc huyết áp (8:00 AM) - COMPLETED")
        
        # Schedule 2: Tái khám bác sĩ Tim mạch - 10:30 AM (PENDING)
        schedule2_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO notifications (id, user_id, notification_type, title, message, 
                                     scheduled_at, sent_at, is_sent, is_read, has_voice, 
                                     priority, category, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            schedule2_id, elderly_user_id, "appointment_reminder", "Tái khám bác sĩ Tim mạch",
            "Cuộc hẹn tái khám với bác sĩ Nguyễn Văn A tại Bệnh viện Tim mạch",
            today.replace(hour=10, minute=30), None,
            False, False, True, "high", "appointment", datetime.now()
        ))
        print("✅ Created: Tái khám bác sĩ Tim mạch (10:30 AM) - PENDING")
        
        # Schedule 3: Đi bộ 30 phút - 4:00 PM (PENDING)
        schedule3_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO notifications (id, user_id, notification_type, title, message, 
                                     scheduled_at, sent_at, is_sent, is_read, has_voice, 
                                     priority, category, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            schedule3_id, elderly_user_id, "health_check", "Đi bộ 30 phút",
            "Vận động nhẹ nhàng để tăng cường sức khỏe tim mạch",
            today.replace(hour=16, minute=0), None,
            False, False, True, "normal", "exercise", datetime.now()
        ))
        print("✅ Created: Đi bộ 30 phút (4:00 PM) - PENDING")
        
        # Yesterday's schedules (August 6th)
        yesterday = today - timedelta(days=1)
        
        # Schedule 4: Uống thuốc huyết áp - 8:00 AM (COMPLETED)
        schedule4_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO notifications (id, user_id, notification_type, title, message, 
                                     scheduled_at, sent_at, is_sent, is_read, has_voice, 
                                     priority, category, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            schedule4_id, elderly_user_id, "medicine_reminder", "Uống thuốc huyết áp",
            "Nhớ uống thuốc huyết áp Amlodipine 5mg vào buổi sáng",
            yesterday.replace(hour=8, minute=0), yesterday.replace(hour=8, minute=2),
            True, False, True, "high", "medicine", datetime.now()
        ))
        print("✅ Created: Uống thuốc huyết áp (8:00 AM) - YESTERDAY COMPLETED")
        
        # Schedule 5: Đo huyết áp - 6:00 PM (COMPLETED)
        schedule5_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO notifications (id, user_id, notification_type, title, message, 
                                     scheduled_at, sent_at, is_sent, is_read, has_voice, 
                                     priority, category, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            schedule5_id, elderly_user_id, "health_check", "Đo huyết áp",
            "Đo huyết áp buổi tối và ghi lại kết quả",
            yesterday.replace(hour=18, minute=0), yesterday.replace(hour=18, minute=5),
            True, False, True, "normal", "health_check", datetime.now()
        ))
        print("✅ Created: Đo huyết áp (6:00 PM) - YESTERDAY COMPLETED")
        
        # Schedule 6: Uống thuốc tiểu đường - 7:00 PM (COMPLETED)
        schedule6_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO notifications (id, user_id, notification_type, title, message, 
                                     scheduled_at, sent_at, is_sent, is_read, has_voice, 
                                     priority, category, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            schedule6_id, elderly_user_id, "medicine_reminder", "Uống thuốc tiểu đường",
            "Nhớ uống thuốc Metformin 500mg trước bữa tối",
            yesterday.replace(hour=19, minute=0), yesterday.replace(hour=19, minute=2),
            True, False, True, "high", "medicine", datetime.now()
        ))
        print("✅ Created: Uống thuốc tiểu đường (7:00 PM) - YESTERDAY COMPLETED")
        
        # Commit all changes
        conn.commit()
        print("\n🎉 All schedules created successfully using raw SQL!")
        
        # Print summary
        print(f"\n📊 Summary:")
        print(f"   Elderly User ID: {elderly_user_id}")
        print(f"   Total Schedules Created: 6")
        print(f"   Today's Schedules: 3 (1 completed, 2 pending)")
        print(f"   Yesterday's Schedules: 3 (all completed)")
        
        # Close connection
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating schedules: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_schedules_raw_sql()
    if success:
        print("\n✅ Schedules created successfully using raw SQL!")
        print("You can now test the family connection feature in the Android app.")
    else:
        print("\n❌ Failed to create schedules.")
        exit(1) 