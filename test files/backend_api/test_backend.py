"""
Test script to check if backend module can be imported
"""
import sys
import os

def test_imports():
    """Test various import methods."""
    print("=== Testing Backend Module Imports ===")
    
    # Test 1: Direct import
    try:
        import backend
        print("✅ Successfully imported 'backend' module")
        print(f"   Module location: {backend.__file__}")
        print(f"   Module attributes: {dir(backend)}")
    except ImportError as e:
        print(f"❌ Failed to import 'backend' module: {e}")
    
    # Test 2: Import specific components
    try:
        from backend import app
        print("✅ Successfully imported 'backend.app'")
    except ImportError as e:
        print(f"❌ Failed to import 'backend.app': {e}")
    
    # Test 3: Check current working directory
    print(f"\n📁 Current working directory: {os.getcwd()}")
    print(f"📁 Python path: {sys.path[:3]}...")
    
    # Test 4: Check if backend.py exists
    backend_file = os.path.join(os.getcwd(), "backend.py")
    if os.path.exists(backend_file):
        print(f"✅ Found backend.py at: {backend_file}")
    else:
        print(f"❌ backend.py not found at: {backend_file}")
    
    # Test 5: Check if __init__.py exists
    init_file = os.path.join(os.getcwd(), "__init__.py")
    if os.path.exists(init_file):
        print(f"✅ Found __init__.py at: {init_file}")
    else:
        print(f"❌ __init__.py not found at: {init_file}")

if __name__ == "__main__":
    test_imports() 