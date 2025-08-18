#!/usr/bin/env python3
"""
Script to create real schedule data for family connection feature
Creates schedules for son123@gmail.com (elder) managed by son12345@gmail.com (family)
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

def create_family_connection_data():
    """Create real schedule data for family connection feature"""
    
    with get_db() as session:
        try:
            print("=== Creating Family Connection Data ===")
            
            # 1. Create Elderly User (son123@gmail.com)
            elderly_user = session.query(User).filter(User.email == "son123@gmail.com").first()
            if not elderly_user:
                elderly_user = User(
                    user_type=UserType.ELDERLY.value,
                    email="son123@gmail.com",
                    full_name="Papa",
                    phone="0987654321",
                    is_active=True,
                    preferred_language="vi",
                    country="Vietnam"
                )
                session.add(elderly_user)
                session.commit()
                session.refresh(elderly_user)
                print(f"✅ Created elderly user: {elderly_user.full_name} ({elderly_user.email})")
            else:
                print(f"✅ Elderly user already exists: {elderly_user.full_name} ({elderly_user.email})")
            
            # 2. Create Elderly Profile
            elderly_profile = session.query(ElderlyProfile).filter(
                ElderlyProfile.user_id == elderly_user.id
            ).first()
            
            if not elderly_profile:
                elderly_profile = ElderlyProfile(
                    user_id=elderly_user.id,
                    medical_conditions=["huyết áp cao", "tiểu đường"],
                    current_medications={
                        "thuốc huyết áp": "Amlodipine 5mg",
                        "thuốc tiểu đường": "Metformin 500mg"
                    },
                    allergies=["penicillin"],
                    emergency_contact="0987654321",
                    care_level="assisted"
                )
                session.add(elderly_profile)
                session.commit()
                session.refresh(elderly_profile)
                print(f"✅ Created elderly profile for {elderly_user.full_name}")
            else:
                print(f"✅ Elderly profile already exists for {elderly_user.full_name}")
            
            # 3. Create Family User (son12345@gmail.com)
            family_user = session.query(User).filter(User.email == "son12345@gmail.com").first()
            if not family_user:
                family_user = User(
                    user_type=UserType.FAMILY_MEMBER.value,
                    email="son12345@gmail.com",
                    full_name="Con Trai",
                    phone="0123456789",
                    is_active=True,
                    preferred_language="vi",
                    country="Vietnam"
                )
                session.add(family_user)
                session.commit()
                session.refresh(family_user)
                print(f"✅ Created family user: {family_user.full_name} ({family_user.email})")
            else:
                print(f"✅ Family user already exists: {family_user.full_name} ({family_user.email})")
            
            # 4. Create Family Profile
            family_profile = session.query(FamilyProfile).filter(
                FamilyProfile.user_id == family_user.id
            ).first()
            
            if not family_profile:
                family_profile = FamilyProfile(
                    user_id=family_user.id,
                    occupation="Kỹ sư",
                    workplace="Công ty ABC",
                    is_primary_caregiver=True,
                    care_responsibilities=["quản lý thuốc", "đặt lịch khám", "theo dõi sức khỏe"],
                    availability_schedule={
                        "weekdays": "8:00-18:00",
                        "weekends": "9:00-17:00"
                    }
                )
                session.add(family_profile)
                session.commit()
                session.refresh(family_profile)
                print(f"✅ Created family profile for {family_user.full_name}")
            else:
                print(f"✅ Family profile already exists for {family_user.full_name}")
            
            # 5. Create Family Relationship
            existing_relationship = session.query(FamilyRelationship).filter(
                and_(
                    FamilyRelationship.elderly_id == elderly_profile.id,
                    FamilyRelationship.family_member_id == family_profile.id
                )
            ).first()
            
            if not existing_relationship:
                family_relationship = FamilyRelationship(
                    elderly_id=elderly_profile.id,
                    family_member_id=family_profile.id,
                    relationship_type="child",
                    can_view_health_data=True,
                    can_receive_notifications=True,
                    can_manage_medications=True,
                    can_schedule_appointments=True
                )
                session.add(family_relationship)
                session.commit()
                print(f"✅ Created family relationship between {elderly_user.full_name} and {family_user.full_name}")
            else:
                print(f"✅ Family relationship already exists between {elderly_user.full_name} and {family_user.full_name}")
            
            # 6. Create Real Schedule Data (Notifications)
            print("\n=== Creating Real Schedule Data ===")
            
            # Today's schedules (August 7th)
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Schedule 1: Uống thuốc huyết áp - 8:00 AM (COMPLETED)
            medicine_schedule_1 = session.query(Notification).filter(
                and_(
                    Notification.user_id == elderly_user.id,
                    Notification.title == "Uống thuốc huyết áp",
                    Notification.scheduled_at == today.replace(hour=8, minute=0)
                )
            ).first()
            
            if not medicine_schedule_1:
                medicine_schedule_1 = Notification(
                    user_id=elderly_user.id,
                    notification_type="MEDICINE_REMINDER",  # Use uppercase enum value
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
            else:
                print("✅ Medicine schedule 1 already exists")
            
            # Schedule 2: Tái khám bác sĩ Tim mạch - 10:30 AM (PENDING)
            doctor_schedule = session.query(Notification).filter(
                and_(
                    Notification.user_id == elderly_user.id,
                    Notification.title == "Tái khám bác sĩ Tim mạch",
                    Notification.scheduled_at == today.replace(hour=10, minute=30)
                )
            ).first()
            
            if not doctor_schedule:
                doctor_schedule = Notification(
                    user_id=elderly_user.id,
                    notification_type="APPOINTMENT_REMINDER",  # Use uppercase enum value
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
            else:
                print("✅ Doctor schedule already exists")
            
            # Schedule 3: Đi bộ 30 phút - 4:00 PM (PENDING)
            exercise_schedule = session.query(Notification).filter(
                and_(
                    Notification.user_id == elderly_user.id,
                    Notification.title == "Đi bộ 30 phút",
                    Notification.scheduled_at == today.replace(hour=16, minute=0)
                )
            ).first()
            
            if not exercise_schedule:
                exercise_schedule = Notification(
                    user_id=elderly_user.id,
                    notification_type="HEALTH_CHECK",  # Use uppercase enum value
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
            else:
                print("✅ Exercise schedule already exists")
            
            # Yesterday's schedules (August 6th)
            yesterday = today - timedelta(days=1)
            
            # Schedule 4: Uống thuốc huyết áp - 8:00 AM (COMPLETED)
            medicine_schedule_2 = session.query(Notification).filter(
                and_(
                    Notification.user_id == elderly_user.id,
                    Notification.title == "Uống thuốc huyết áp",
                    Notification.scheduled_at == yesterday.replace(hour=8, minute=0)
                )
            ).first()
            
            if not medicine_schedule_2:
                medicine_schedule_2 = Notification(
                    user_id=elderly_user.id,
                    notification_type="MEDICINE_REMINDER",  # Use uppercase enum value
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
            else:
                print("✅ Medicine schedule 2 already exists")
            
            # Schedule 5: Đo huyết áp - 6:00 PM (COMPLETED)
            blood_pressure_schedule = session.query(Notification).filter(
                and_(
                    Notification.user_id == elderly_user.id,
                    Notification.title == "Đo huyết áp",
                    Notification.scheduled_at == yesterday.replace(hour=18, minute=0)
                )
            ).first()
            
            if not blood_pressure_schedule:
                blood_pressure_schedule = Notification(
                    user_id=elderly_user.id,
                    notification_type="HEALTH_CHECK",  # Use uppercase enum value
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
            else:
                print("✅ Blood pressure schedule already exists")
            
            # Schedule 6: Uống thuốc tiểu đường - 7:00 PM (COMPLETED)
            diabetes_schedule = session.query(Notification).filter(
                and_(
                    Notification.user_id == elderly_user.id,
                    Notification.title == "Uống thuốc tiểu đường",
                    Notification.scheduled_at == yesterday.replace(hour=19, minute=0)
                )
            ).first()
            
            if not diabetes_schedule:
                diabetes_schedule = Notification(
                    user_id=elderly_user.id,
                    notification_type="MEDICINE_REMINDER",  # Use uppercase enum value
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
            else:
                print("✅ Diabetes schedule already exists")
            
            # Commit all changes
            session.commit()
            print("\n🎉 All family connection data created successfully!")
            
            # Print summary
            print(f"\n📊 Summary:")
            print(f"   Elderly User: {elderly_user.full_name} ({elderly_user.email})")
            print(f"   Family User: {family_user.full_name} ({family_user.email})")
            print(f"   Total Schedules Created: 6")
            print(f"   Today's Schedules: 3 (1 completed, 2 pending)")
            print(f"   Yesterday's Schedules: 3 (all completed)")
            
            return True
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error creating family connection data: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    # Import required modules
    from sqlalchemy import and_
    
    success = create_family_connection_data()
    if success:
        print("\n✅ Family connection data setup completed successfully!")
        print("You can now test the family connection feature in the Android app.")
    else:
        print("\n❌ Failed to setup family connection data.")
        sys.exit(1) 