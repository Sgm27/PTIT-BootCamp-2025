#!/usr/bin/env python3
"""
Transfer all schedules to user with email son123@gmail.com
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Database Configuration
DB_CONFIG = {
    'host': '13.215.139.225',
    'port': 5432,
    'database': 'healthcare_ai',
    'user': 'postgres',
    'password': 'postgres'
}

def get_user_by_email(email: str):
    """Get user by email"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("SELECT id, email, full_name FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        
        conn.close()
        return user
    except Exception as e:
        print(f"❌ Error getting user by email: {e}")
        return None

def get_all_schedules():
    """Get all schedules from database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT id, user_id, title, message, scheduled_at, notification_type, 
                   category, priority, has_voice, is_sent, is_read, created_at
            FROM notifications 
            WHERE notification_type IN ('medicine_reminder', 'appointment_reminder', 'health_check', 'custom')
            ORDER BY created_at DESC
        """)
        schedules = cur.fetchall()
        
        conn.close()
        return schedules
    except Exception as e:
        print(f"❌ Error getting schedules: {e}")
        return []

def transfer_schedules_to_user(target_user_id: str):
    """Transfer all schedules to target user"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Get all schedules
        schedules = get_all_schedules()
        print(f"📋 Found {len(schedules)} schedules to transfer")
        
        if not schedules:
            print("❌ No schedules found to transfer")
            return False
        
        # Update all schedules to target user
        updated_count = 0
        for schedule in schedules:
            try:
                cur.execute("""
                    UPDATE notifications 
                    SET user_id = %s
                    WHERE id = %s
                """, (target_user_id, schedule['id']))
                updated_count += 1
                print(f"✅ Transferred schedule: {schedule['title']}")
            except Exception as e:
                print(f"❌ Error transferring schedule {schedule['id']}: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"🎉 Successfully transferred {updated_count} schedules to user {target_user_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error transferring schedules: {e}")
        return False

def verify_transfer(target_user_id: str):
    """Verify that schedules were transferred correctly"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Count schedules for target user
        cur.execute("""
            SELECT COUNT(*) as count
            FROM notifications 
            WHERE user_id = %s AND notification_type IN ('medicine_reminder', 'appointment_reminder', 'health_check', 'custom')
        """, (target_user_id,))
        result = cur.fetchone()
        target_user_count = result['count']
        
        # Count total schedules
        cur.execute("""
            SELECT COUNT(*) as count
            FROM notifications 
            WHERE notification_type IN ('medicine_reminder', 'appointment_reminder', 'health_check', 'custom')
        """)
        result = cur.fetchone()
        total_count = result['count']
        
        # Get sample schedules for target user
        cur.execute("""
            SELECT id, title, scheduled_at, notification_type, category
            FROM notifications 
            WHERE user_id = %s AND notification_type IN ('medicine_reminder', 'appointment_reminder', 'health_check', 'custom')
            ORDER BY created_at DESC
            LIMIT 5
        """, (target_user_id,))
        sample_schedules = cur.fetchall()
        
        conn.close()
        
        print(f"\n📊 Transfer Verification:")
        print(f"   - Total schedules in system: {total_count}")
        print(f"   - Schedules for target user: {target_user_count}")
        
        if target_user_count > 0:
            print(f"\n📋 Sample schedules for target user:")
            for schedule in sample_schedules:
                print(f"   - {schedule['title']} ({schedule['notification_type']}) - {schedule['scheduled_at']}")
        
        return target_user_count == total_count
        
    except Exception as e:
        print(f"❌ Error verifying transfer: {e}")
        return False

def main():
    """Main function"""
    print("🔄 Schedule Transfer Script")
    print("=" * 50)
    
    # Get target user
    target_email = "son123@gmail.com"
    target_user = get_user_by_email(target_email)
    
    if not target_user:
        print(f"❌ User with email {target_email} not found")
        print("Creating user...")
        
        # Create user if not exists
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO users (email, full_name, user_type, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (target_email, "Son User", "elderly", datetime.now(), datetime.now()))
            
            target_user_id = cur.fetchone()[0]
            conn.commit()
            conn.close()
            
            print(f"✅ Created user with ID: {target_user_id}")
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            return
    else:
        target_user_id = target_user['id']
        print(f"✅ Found user: {target_user['full_name']} (ID: {target_user_id})")
    
    # Get current schedules
    current_schedules = get_all_schedules()
    print(f"\n📋 Current schedules in database: {len(current_schedules)}")
    
    if current_schedules:
        print("Sample current schedules:")
        for i, schedule in enumerate(current_schedules[:3], 1):
            print(f"   {i}. {schedule['title']} (User: {schedule['user_id']})")
    
    # Confirm transfer
    print(f"\n🔄 Ready to transfer all schedules to user {target_user_id}")
    print("This will update all schedule notifications to belong to the target user.")
    
    # Perform transfer
    if transfer_schedules_to_user(target_user_id):
        # Verify transfer
        if verify_transfer(target_user_id):
            print("\n🎉 Transfer completed successfully!")
            print(f"All schedules now belong to user: {target_email}")
        else:
            print("\n⚠️ Transfer may have had issues. Please verify manually.")
    else:
        print("\n❌ Transfer failed!")

if __name__ == "__main__":
    main() 