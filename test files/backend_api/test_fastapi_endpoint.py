#!/usr/bin/env python3
"""
Test FastAPI endpoint with test client
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.testclient import TestClient
from api_services.schedule_service import add_schedule_endpoints
from db.db_services.notification_service import NotificationDBService

def test_fastapi_endpoint():
    """Test FastAPI endpoint with test client"""
    
    print("=== Testing FastAPI Endpoint with Test Client ===")
    
    try:
        # Create test app
        app = FastAPI()
        
        # Initialize services
        notification_db_service = NotificationDBService()
        
        # Add endpoints
        add_schedule_endpoints(app, notification_db_service, None, None)
        
        # Create test client
        client = TestClient(app)
        
        # Test notification ID
        notification_id = "adfcaa97-3471-4112-adce-366f7c18cf2e"
        user_id = "dd8d892b-fa77-4a71-9520-71baf601c3ba"
        
        print(f"1. Testing delete endpoint with:")
        print(f"   - Notification ID: {notification_id}")
        print(f"   - User ID: {user_id}")
        
        # Test delete endpoint
        response = client.delete(f"/api/schedules/{notification_id}?user_id={user_id}")
        
        print(f"\n2. Delete endpoint response:")
        print(f"   - Status: {response.status_code}")
        print(f"   - Body: {response.json()}")
        
        if response.status_code == 200:
            print(f"   ✅ Delete endpoint returned success")
        else:
            print(f"   ❌ Delete endpoint failed")
            return
        
        print(f"\n3. Checking if notification still exists...")
        
        # Check if notification still exists
        from db.db_config import get_db
        from db.models import Notification
        
        with get_db() as db:
            notification_after = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            
            if notification_after:
                print(f"   ❌ Still exists: {notification_after.title}")
                print(f"   - ID: {notification_after.id}")
                print(f"   - User ID: {notification_after.user_id}")
            else:
                print(f"   ✅ Successfully deleted!")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fastapi_endpoint() 