#!/usr/bin/env python3
"""
Debug script to test login functionality
"""
import hashlib
from db.db_config import get_db_session
from db.models import User
from api_services.auth_service import hash_password

def test_login():
    print("=== Testing Login Debug ===")
    
    # Test data
    email = "son123@gmail.com"
    password = "12345678"
    
    # Get database session
    session = get_db_session()
    
    try:
        # Find user
        user = session.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ User not found with email: {email}")
            return
        
        print(f"✅ User found: {user.full_name}")
        print(f"   Email: {user.email}")
        print(f"   User type: {user.user_type}")
        print(f"   Is active: {user.is_active}")
        print(f"   Password hash in DB: {user.password_hash}")
        
        # Test password hashing
        expected_hash = hash_password(password)
        print(f"   Expected hash: {expected_hash}")
        print(f"   Hash match: {user.password_hash == expected_hash}")
        
        # Test with SHA-256 directly
        sha256_hash = hashlib.sha256(password.encode()).hexdigest()
        print(f"   SHA-256 hash: {sha256_hash}")
        print(f"   SHA-256 match: {user.password_hash == sha256_hash}")
        
        if user.password_hash == expected_hash:
            print("✅ Password verification should work")
        else:
            print("❌ Password verification will fail")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    test_login() 