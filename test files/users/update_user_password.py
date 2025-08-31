#!/usr/bin/env python3
"""
Script to update password for user with email son123@gmail.com
"""
import sys
import os
import hashlib

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'backend')
sys.path.append(backend_path)

try:
    from db.db_config import get_db
    from db.models import User
    from sqlalchemy.orm import sessionmaker
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def update_user_password():
    """Update password for user with email son123@gmail.com"""
    email = "son123@gmail.com"
    new_password = "12345678"
    
    try:
        # Get database session
        with get_db() as db:
            # Find user by email
            print(f"Searching for user with email: {email}")
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                print(f"❌ User with email {email} not found!")
                return False
            
            print(f"✅ Found user: {user.full_name} (ID: {user.id})")
            print(f"Current password hash: {user.password_hash}")
            
            # Hash the new password
            new_password_hash = hash_password(new_password)
            print(f"New password hash: {new_password_hash}")
            
            # Update the password
            user.password_hash = new_password_hash
            db.commit()
            
            print(f"✅ Successfully updated password for user {email}")
            print(f"New password: {new_password}")
            return True
            
    except Exception as e:
        print(f"❌ Error updating password: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔐 Updating user password...")
    print("=" * 50)
    
    success = update_user_password()
    
    print("=" * 50)
    if success:
        print("🎉 Password update completed successfully!")
    else:
        print("💥 Password update failed!")
        sys.exit(1) 