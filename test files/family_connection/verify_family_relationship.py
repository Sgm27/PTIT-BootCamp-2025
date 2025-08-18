#!/usr/bin/env python3
"""
Script để kiểm tra family relationship đã được tạo
"""

import sys
import os
from sqlalchemy import text

# Thêm backend vào path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.db_config import get_db

def main():
    """Kiểm tra family relationship đã được tạo"""
    
    print("🔍 Kiểm tra family relationship đã được tạo...")
    
    try:
        with get_db() as db:
            # Kiểm tra family relationships
            print("\n📋 Kiểm tra family relationships...")
            
            result = db.execute(text("""
                SELECT 
                    fr.id,
                    fr.relationship_type,
                    fr.can_view_health_data,
                    fr.can_receive_notifications,
                    fr.can_manage_medications,
                    fr.can_schedule_appointments,
                    fr.created_at,
                    fr.is_active,
                    e.user_id as elderly_user_id,
                    f.user_id as family_user_id
                FROM family_relationships fr
                JOIN elderly_profiles e ON fr.elderly_id = e.id
                JOIN family_profiles f ON fr.family_member_id = f.id
                ORDER BY fr.created_at DESC;
            """))
            
            relationships = result.fetchall()
            
            if relationships:
                print(f"✅ Tìm thấy {len(relationships)} family relationship(s):")
                for rel in relationships:
                    print(f"\n   Relationship ID: {rel.id}")
                    print(f"   - Type: {rel.relationship_type}")
                    print(f"   - Elderly User ID: {rel.elderly_user_id}")
                    print(f"   - Family User ID: {rel.family_user_id}")
                    print(f"   - Can view health data: {rel.can_view_health_data}")
                    print(f"   - Can receive notifications: {rel.can_receive_notifications}")
                    print(f"   - Can manage medications: {rel.can_manage_medications}")
                    print(f"   - Can schedule appointments: {rel.can_schedule_appointments}")
                    print(f"   - Created at: {rel.created_at}")
                    print(f"   - Is active: {rel.is_active}")
            else:
                print("❌ Không tìm thấy family relationships")
            
            # Kiểm tra thông tin users
            print("\n📋 Kiểm tra thông tin users...")
            
            result = db.execute(text("""
                SELECT 
                    u.id,
                    u.full_name,
                    u.email,
                    u.user_type,
                    u.phone,
                    u.address,
                    u.city
                FROM users u
                WHERE u.email IN ('son123@gmail.com', 'son12345@gmail.com')
                ORDER BY u.email;
            """))
            
            users = result.fetchall()
            
            if users:
                print("✅ Thông tin users:")
                for user in users:
                    print(f"\n   User: {user.full_name}")
                    print(f"   - ID: {user.id}")
                    print(f"   - Email: {user.email}")
                    print(f"   - Type: {user.user_type}")
                    print(f"   - Phone: {user.phone}")
                    print(f"   - Address: {user.address}")
                    print(f"   - City: {user.city}")
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    main() 