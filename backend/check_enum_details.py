#!/usr/bin/env python3
"""
Script để kiểm tra chi tiết về enum trong database
"""

import sys
import os
from sqlalchemy import text

# Thêm backend vào path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.db_config import get_db

def main():
    """Kiểm tra chi tiết về enum trong database"""
    
    print("🔍 Kiểm tra chi tiết về enum trong database...")
    
    try:
        with get_db() as db:
            # Kiểm tra tất cả enums
            print("\n📋 Kiểm tra tất cả enums...")
            
            result = db.execute(text("""
                SELECT 
                    t.typname as enum_name,
                    e.enumlabel as enum_value
                FROM pg_type t 
                JOIN pg_enum e ON t.oid = e.enumtypid  
                WHERE t.typname LIKE '%relationship%' OR t.typname LIKE '%type%'
                ORDER BY t.typname, e.enumsortorder;
            """))
            
            enums = result.fetchall()
            
            if enums:
                print("✅ Tìm thấy các enums:")
                current_enum = None
                for row in enums:
                    if current_enum != row.enum_name:
                        current_enum = row.enum_name
                        print(f"\n   Enum: {row.enum_name}")
                    print(f"     - {row.enum_value}")
            else:
                print("❌ Không tìm thấy enums")
            
            # Kiểm tra cấu trúc bảng family_relationships
            print("\n📋 Kiểm tra cấu trúc bảng family_relationships...")
            
            result = db.execute(text("""
                SELECT 
                    column_name,
                    data_type,
                    udt_name,
                    udt_schema
                FROM information_schema.columns 
                WHERE table_name = 'family_relationships'
                ORDER BY ordinal_position;
            """))
            
            columns = result.fetchall()
            
            if columns:
                print("✅ Cấu trúc bảng family_relationships:")
                for col in columns:
                    print(f"   - {col.column_name}: {col.data_type} ({col.udt_name}) [Schema: {col.udt_schema}]")
            
            # Kiểm tra constraint
            print("\n📋 Kiểm tra constraints...")
            
            result = db.execute(text("""
                SELECT 
                    conname as constraint_name,
                    contype as constraint_type,
                    pg_get_constraintdef(oid) as constraint_definition
                FROM pg_constraint 
                WHERE conrelid = 'family_relationships'::regclass;
            """))
            
            constraints = result.fetchall()
            
            if constraints:
                print("✅ Constraints:")
                for con in constraints:
                    print(f"   - {con.constraint_name}: {con.constraint_type}")
                    print(f"     Definition: {con.constraint_definition}")
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    main() 