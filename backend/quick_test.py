"""
Quick test script for backend
"""
import requests
import time
import subprocess
import sys
import os

def test_backend():
    """Test backend connection"""
    print("=== Quick Backend Test ===")
    
    # Test 1: Check if server is running
    print("\n1. Testing if server is running...")
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"✅ Server is running! Status: {response.status_code}")
        print(f"   Response: {response.text[:100]}...")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Server not running (Connection refused)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def start_server():
    """Start the backend server"""
    print("\n2. Starting backend server...")
    
    # Check current directory
    print(f"Current directory: {os.getcwd()}")
    
    # List available scripts
    scripts = ["run_server_simple.py", "run_server.py"]
    for script in scripts:
        if os.path.exists(script):
            print(f"Found script: {script}")
    
    # Try to start with simple script first
    try:
        print("Trying to start with run_server_simple.py...")
        process = subprocess.Popen(
            [sys.executable, "run_server_simple.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Server process started")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return None

def main():
    """Main function"""
    print("Starting backend test...")
    
    # Test if server is already running
    if test_backend():
        print("\n🎉 Backend is already working!")
        return
    
    # Try to start server
    process = start_server()
    if not process:
        print("\n❌ Failed to start server")
        return
    
    # Wait for server to start
    print("\n3. Waiting for server to start...")
    time.sleep(10)
    
    # Test again
    if test_backend():
        print("\n🎉 Backend started successfully!")
        print("You can now access:")
        print("  http://localhost:8000/")
        print("  http://localhost:8000/health")
        print("  http://localhost:8000/docs")
    else:
        print("\n❌ Backend still not responding")
    
    # Cleanup
    if process:
        print("\nStopping server...")
        process.terminate()
        process.wait(timeout=5)

if __name__ == "__main__":
    main() 