"""
Step-by-step backend test script
"""
import os
import sys
import subprocess
import time

def step1_check_files():
    """Step 1: Check if required files exist"""
    print("=== STEP 1: Checking Required Files ===")
    
    required_files = [
        "backend.py",
        "run_server.py", 
        "run_server_simple.py",
        "__init__.py",
        "config/settings.py"
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING!")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Missing {len(missing_files)} required files!")
        return False
    else:
        print("\n✅ All required files found!")
        return True

def step2_check_imports():
    """Step 2: Check if modules can be imported"""
    print("\n=== STEP 2: Testing Module Imports ===")
    
    # Test basic imports
    try:
        import config.settings
        print("✅ config.settings imported successfully")
    except Exception as e:
        print(f"❌ config.settings import failed: {e}")
        return False
    
    try:
        import models.api_models
        print("✅ models.api_models imported successfully")
    except Exception as e:
        print(f"❌ models.api_models import failed: {e}")
        return False
    
    try:
        import services.gemini_service
        print("✅ services.gemini_service imported successfully")
    except Exception as e:
        print(f"❌ services.gemini_service import failed: {e}")
        return False
    
    print("\n✅ All basic imports successful!")
    return True

def step3_test_backend_import():
    """Step 3: Test if backend.py can be imported"""
    print("\n=== STEP 3: Testing Backend Import ===")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.getcwd())
        
        # Try to import backend
        import backend
        print("✅ backend module imported successfully")
        
        # Check if app exists
        if hasattr(backend, 'app'):
            print("✅ backend.app found")
            return True
        else:
            print("❌ backend.app not found")
            return False
            
    except Exception as e:
        print(f"❌ backend import failed: {e}")
        return False

def step4_test_server_start():
    """Step 4: Test server startup"""
    print("\n=== STEP 4: Testing Server Startup ===")
    
    try:
        print("Starting server with run_server_simple.py...")
        
        # Start server process
        process = subprocess.Popen(
            [sys.executable, "run_server_simple.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit
        time.sleep(5)
        
        # Check if process is running
        if process.poll() is None:
            print("✅ Server process started successfully")
            
            # Stop the process
            process.terminate()
            process.wait(timeout=5)
            print("✅ Server process stopped")
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing server startup: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Starting Step-by-Step Backend Test")
    print("=" * 50)
    
    results = []
    
    # Step 1: Check files
    results.append(("File Check", step1_check_files()))
    
    # Step 2: Check imports
    if results[0][1]:  # Only continue if files exist
        results.append(("Module Imports", step2_check_imports()))
    else:
        results.append(("Module Imports", False))
    
    # Step 3: Test backend import
    if results[1][1]:  # Only continue if imports work
        results.append(("Backend Import", step3_test_backend_import()))
    else:
        results.append(("Backend Import", False))
    
    # Step 4: Test server startup
    if results[2][1]:  # Only continue if backend import works
        results.append(("Server Startup", step4_test_server_start()))
    else:
        results.append(("Server Startup", False))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    for step_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{step_name:20} {status}")
    
    # Overall result
    all_passed = all(result[1] for result in results)
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Backend should work correctly.")
        print("\nTo start the server, run:")
        print("  python run_server_simple.py")
        print("\nThen access:")
        print("  http://localhost:8000/")
        print("  http://localhost:8000/health")
        print("  http://localhost:8000/docs")
    else:
        print("\n❌ SOME TESTS FAILED. Backend has issues.")
        print("\nFailed steps:")
        for step_name, success in results:
            if not success:
                print(f"  - {step_name}")
        
        print("\nPlease fix the failed steps above.")

if __name__ == "__main__":
    main() 