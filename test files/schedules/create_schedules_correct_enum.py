#!/usr/bin/env python3
"""
Script to create schedules with correct enum values (lowercase)
"""
import sys
import os
from datetime import datetime, timedelta
import uuid

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.db_config import get_db
from db.models import (
    User, UserType, ElderlyProfile, FamilyProfile, FamilyRelationship,
    Notification, NotificationType
)

def create_schedules_correct_enum():
    """Create schedules with correct enum values"""
    
    with get_db() as session:
        try:
            print("=== Creating Schedules with Correct Enum Values ===")
            
            # 1. Get elderly user
            elderly_user = session.query(User).filter(User.email == "son123@gmail.com").first()
            if not elderly_user:
                print("❌ Elderly user not found")
                return False
            
            print(f"✅ Found elderly user: {elderly_user.full_name}")
            
            # 2. Create new schedules with correct enum values (lowercase)
            print("\n=== Creating New Schedules ===")
            
            # Today's schedules (August 7th)
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Schedule 1: Uống thuốc huyết áp - 8:00 AM (COMPLETED)
            medicine_schedule_1 = Notification(
                user_id=elderly_user.id,
                notification_type="medicine_reminder",  # Use lowercase enum value
                title="Uống thuốc huyết áp",
                message="Nhớ uống thuốc huyết áp Amlodipine 5mg vào buổi sáng",
                scheduled_at=today.replace(hour=8, minute=0),
                priority="high",
                category="medicine",
                is_sent=True,  # Completed
                sent_at=today.replace(hour=8, minute=5),
                has_voice=True
            )
            session.add(medicine_schedule_1)
            print("✅ Created: Uống thuốc huyết áp (8:00 AM) - COMPLETED")
            
            # Schedule 2: Tái khám bác sĩ Tim mạch - 10:30 AM (PENDING)
            doctor_schedule = Notification(
                user_id=elderly_user.id,
                notification_type="appointment_reminder",  # Use lowercase enum value
                title="Tái khám bác sĩ Tim mạch",
                message="Cuộc hẹn tái khám với bác sĩ Nguyễn Văn A tại Bệnh viện Tim mạch",
                scheduled_at=today.replace(hour=10, minute=30),
                priority="high",
                category="appointment",
                is_sent=False,  # Pending
                has_voice=True
            )
            session.add(doctor_schedule)
            print("✅ Created: Tái khám bác sĩ Tim mạch (10:30 AM) - PENDING")
            
            # Schedule 3: Đi bộ 30 phút - 4:00 PM (PENDING)
            exercise_schedule = Notification(
                user_id=elderly_user.id,
                notification_type="health_check",  # Use lowercase enum value
                title="Đi bộ 30 phút",
                message="Vận động nhẹ nhàng để tăng cường sức khỏe tim mạch",
                scheduled_at=today.replace(hour=16, minute=0),
                priority="normal",
                category="exercise",
                is_sent=False,  # Pending
                has_voice=True
            )
            session.add(exercise_schedule)
            print("✅ Created: Đi bộ 30 phút (4:00 PM) - PENDING")
            
            # Yesterday's schedules (August 6th)
            yesterday = today - timedelta(days=1)
            
            # Schedule 4: Uống thuốc huyết áp - 8:00 AM (COMPLETED)
            medicine_schedule_2 = Notification(
                user_id=elderly_user.id,
                notification_type="medicine_reminder",  # Use lowercase enum value
                title="Uống thuốc huyết áp",
                message="Nhớ uống thuốc huyết áp Amlodipine 5mg vào buổi sáng",
                scheduled_at=yesterday.replace(hour=8, minute=0),
                priority="high",
                category="medicine",
                is_sent=True,  # Completed
                sent_at=yesterday.replace(hour=8, minute=2),
                has_voice=True
            )
            session.add(medicine_schedule_2)
            print("✅ Created: Uống thuốc huyết áp (8:00 AM) - YESTERDAY COMPLETED")
            
            # Schedule 5: Đo huyết áp - 6:00 PM (COMPLETED)
            blood_pressure_schedule = Notification(
                user_id=elderly_user.id,
                notification_type="health_check",  # Use lowercase enum value
                title="Đo huyết áp",
                message="Đo huyết áp buổi tối và ghi lại kết quả",
                scheduled_at=yesterday.replace(hour=18, minute=0),
                priority="normal",
                category="health_check",
                is_sent=True,  # Completed
                sent_at=yesterday.replace(hour=18, minute=5),
                has_voice=True
            )
            session.add(blood_pressure_schedule)
            print("✅ Created: Đo huyết áp (6:00 PM) - YESTERDAY COMPLETED")
            
            # Schedule 6: Uống thuốc tiểu đường - 7:00 PM (COMPLETED)
            diabetes_schedule = Notification(
                user_id=elderly_user.id,
                notification_type="medicine_reminder",  # Use lowercase enum value
                title="Uống thuốc tiểu đường",
                message="Nhớ uống thuốc Metformin 500mg trước bữa tối",
                scheduled_at=yesterday.replace(hour=19, minute=0),
                priority="high",
                category="medicine",
                is_sent=True,  # Completed
                sent_at=yesterday.replace(hour=19, minute=2),
                has_voice=True
            )
            session.add(diabetes_schedule)
            print("✅ Created: Uống thuốc tiểu đường (7:00 PM) - YESTERDAY COMPLETED")
            
            # Commit all changes
            session.commit()
            print("\n🎉 All schedules created successfully!")
            
            # Print summary
            print(f"\n📊 Summary:")
            print(f"   Elderly User: {elderly_user.full_name} ({elderly_user.email})")
            print(f"   Total Schedules Created: 6")
            print(f"   Today's Schedules: 3 (1 completed, 2 pending)")
            print(f"   Yesterday's Schedules: 3 (all completed)")
            
            return True
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error creating schedules: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = create_schedules_correct_enum()
    if success:
        print("\n✅ Schedules created successfully!")
        print("You can now test the family connection feature in the Android app.")
    else:
        print("\n❌ Failed to create schedules.")
        sys.exit(1) 