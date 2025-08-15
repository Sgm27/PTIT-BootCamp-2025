#!/usr/bin/env python3
"""
Script để hoàn tất thông tin cho user son12345@gmail.com 
và liên kết họ với user son123@gmail.com như một thành viên gia đình
"""

import sys
import os
from datetime import date
from typing import Optional
from sqlalchemy import and_

# Thêm backend vào path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.db_services.user_service import UserService
from db.models import UserType, RelationshipType
from db.db_config import get_db
from db.models import User, ElderlyProfile, FamilyProfile, FamilyRelationship

def main():
    """Main function để hoàn tất user profile và tạo family relationship"""
    
    print("🔧 Bắt đầu hoàn tất thông tin user và tạo family relationship...")
    
    # Khởi tạo user service
    user_service = UserService()
    
    try:
        # 1. Kiểm tra user son123@gmail.com (elderly user)
        print("\n📋 Bước 1: Kiểm tra user son123@gmail.com...")
        elderly_user = user_service.get_user_by_contact(email="son123@gmail.com")
        
        if not elderly_user:
            print("❌ Không tìm thấy user son123@gmail.com")
            return False
        
        print(f"✅ Tìm thấy elderly user: {elderly_user['full_name']} (ID: {elderly_user['id']})")
        
        # 2. Kiểm tra user son12345@gmail.com
        print("\n📋 Bước 2: Kiểm tra user son12345@gmail.com...")
        family_user = user_service.get_user_by_contact(email="son12345@gmail.com")
        
        if not family_user:
            print("❌ Không tìm thấy user son12345@gmail.com, cần tạo mới...")
            family_user = create_family_user()
            if not family_user:
                print("❌ Không thể tạo user son12345@gmail.com")
                return False
        else:
            print(f"✅ Tìm thấy family user: {family_user['full_name']} (ID: {family_user['id']})")
            print(f"   Thông tin hiện tại:")
            print(f"   - Phone: {family_user.get('phone', 'N/A')}")
            print(f"   - Address: {family_user.get('address', 'N/A')}")
            print(f"   - City: {family_user.get('city', 'N/A')}")
        
        # 3. Hoàn tất thông tin cho family user nếu cần
        print("\n📋 Bước 3: Hoàn tất thông tin cho family user...")
        if not is_profile_complete(family_user):
            print("🔄 Cập nhật thông tin profile...")
            success = update_family_profile(family_user['id'])
            if not success:
                print("❌ Không thể cập nhật profile")
                return False
            print("✅ Đã cập nhật profile thành công")
        else:
            print("✅ Profile đã đầy đủ thông tin")
        
        # 4. Tạo family relationship trực tiếp trong database
        print("\n📋 Bước 4: Tạo family relationship...")
        success = create_family_relationship_direct(
            elderly_user_id=elderly_user['id'],
            family_member_id=family_user['id']
        )
        
        if success:
            print("✅ Đã tạo family relationship thành công!")
            print(f"   Elderly User: {elderly_user['full_name']} ({elderly_user['email']})")
            print(f"   Family Member: {family_user['full_name']} ({family_user['email']})")
            print(f"   Relationship: CHILD")
        else:
            print("❌ Không thể tạo family relationship")
            return False
        
        # 5. Xác nhận relationship đã được tạo
        print("\n📋 Bước 5: Xác nhận family relationship...")
        family_members = user_service.get_family_members(elderly_user['id'])
        if family_members:
            print(f"✅ Xác nhận: Elderly user có {len(family_members)} family member(s)")
            for member in family_members:
                print(f"   - {member['full_name']} ({member['email']}) - {member['relationship_type']}")
        else:
            print("⚠️  Không tìm thấy family members, có thể có vấn đề với relationship")
        
        print("\n🎉 Hoàn tất! User son12345@gmail.com đã được liên kết với son123@gmail.com")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

def create_family_user() -> Optional[dict]:
    """Tạo mới family user với email son12345@gmail.com"""
    try:
        print("🔄 Tạo mới family user...")
        
        # Tạo user với thông tin cơ bản
        user_service = UserService()
        new_user = user_service.create_user(
            user_type=UserType.FAMILY_MEMBER,
            full_name="Nguyễn Văn Sơn",
            email="son12345@gmail.com",
            phone="0987654322",  # Sử dụng số điện thoại khác
            date_of_birth=date(1990, 5, 15),
            gender="Nam",
            address="123 Đường ABC, Quận 1, TP.HCM",
            city="TP.HCM",
            country="Vietnam"
        )
        
        if new_user:
            print(f"✅ Đã tạo family user: {new_user.full_name}")
            return {
                'id': str(new_user.id),
                'full_name': new_user.full_name,
                'email': new_user.email,
                'phone': new_user.phone,
                'date_of_birth': new_user.date_of_birth,
                'gender': new_user.gender,
                'address': new_user.address,
                'city': new_user.city,
                'country': new_user.country
            }
        else:
            print("❌ Không thể tạo user")
            return None
            
    except Exception as e:
        print(f"❌ Lỗi khi tạo user: {e}")
        return None

def is_profile_complete(user: dict) -> bool:
    """Kiểm tra xem profile có đầy đủ thông tin không"""
    required_fields = ['full_name', 'phone', 'date_of_birth', 'gender', 'address', 'city']
    
    for field in required_fields:
        if not user.get(field):
            return False
    
    return True

def update_family_profile(user_id: str) -> bool:
    """Cập nhật thông tin profile cho family user"""
    try:
        with get_db() as db:
            # Cập nhật user
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # Kiểm tra xem số điện thoại mới có bị trùng không
            existing_phone = db.query(User).filter(
                and_(User.phone == "0987654322", User.id != user_id)
            ).first()
            
            if existing_phone:
                print("⚠️  Số điện thoại 0987654322 đã được sử dụng, sử dụng số khác...")
                phone_number = "0987654323"
            else:
                phone_number = "0987654322"
            
            # Cập nhật thông tin cơ bản
            user.full_name = "Nguyễn Văn Sơn"
            user.phone = phone_number
            user.date_of_birth = date(1990, 5, 15)
            user.gender = "Nam"
            user.address = "123 Đường ABC, Quận 1, TP.HCM"
            user.city = "TP.HCM"
            user.country = "Vietnam"
            user.preferred_language = "vi"
            user.timezone = "Asia/Ho_Chi_Minh"
            
            # Cập nhật family profile
            family_profile = db.query(FamilyProfile).filter(FamilyProfile.user_id == user_id).first()
            if family_profile:
                family_profile.occupation = "Kỹ sư phần mềm"
                family_profile.workplace = "Công ty ABC"
                family_profile.is_primary_caregiver = True
                family_profile.care_responsibilities = ["Quản lý thuốc", "Đặt lịch khám", "Theo dõi sức khỏe"]
                family_profile.availability_schedule = {
                    "weekdays": "8:00-18:00",
                    "weekends": "9:00-17:00",
                    "emergency": "24/7"
                }
            
            db.commit()
            print(f"✅ Đã cập nhật family profile với số điện thoại: {phone_number}")
            return True
            
    except Exception as e:
        print(f"❌ Lỗi khi cập nhật profile: {e}")
        return False

def create_family_relationship_direct(elderly_user_id: str, family_member_id: str) -> bool:
    """Tạo family relationship trực tiếp trong database bằng SQL"""
    try:
        with get_db() as db:
            # Lấy profile IDs
            elderly_profile = db.query(ElderlyProfile).filter(
                ElderlyProfile.user_id == elderly_user_id
            ).first()
            
            family_profile = db.query(FamilyProfile).filter(
                FamilyProfile.user_id == family_member_id
            ).first()
            
            if not elderly_profile or not family_profile:
                print("❌ Không tìm thấy profiles")
                return False
            
            # Kiểm tra xem relationship đã tồn tại chưa
            existing = db.query(FamilyRelationship).filter(
                and_(
                    FamilyRelationship.elderly_id == elderly_profile.id,
                    FamilyRelationship.family_member_id == family_profile.id
                )
            ).first()
            
            if existing:
                print("✅ Family relationship đã tồn tại")
                return True
            
            # Tạo relationship mới bằng SQL trực tiếp
            from sqlalchemy import text
            sql = text("""
                INSERT INTO family_relationships (
                    id, elderly_id, family_member_id, relationship_type,
                    can_view_health_data, can_receive_notifications,
                    can_manage_medications, can_schedule_appointments,
                    created_at, is_active
                ) VALUES (
                    gen_random_uuid(), :elderly_id, :family_member_id, 'CHILD',
                    :can_view_health_data, :can_receive_notifications,
                    :can_manage_medications, :can_schedule_appointments,
                    now(), :is_active
                )
            """)
            
            result = db.execute(sql, {
                'elderly_id': elderly_profile.id,
                'family_member_id': family_profile.id,
                'can_view_health_data': True,
                'can_receive_notifications': True,
                'can_manage_medications': True,
                'can_schedule_appointments': True,
                'is_active': True
            })
            
            db.commit()
            print("✅ Đã tạo family relationship thành công bằng SQL")
            return True
            
    except Exception as e:
        print(f"❌ Lỗi khi tạo family relationship: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎯 Script đã chạy thành công!")
        sys.exit(0)
    else:
        print("\n💥 Script gặp lỗi!")
        sys.exit(1) 