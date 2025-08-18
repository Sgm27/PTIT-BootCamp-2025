"""
Test script to check backend connection and fix issues
"""
import requests
import time
import subprocess
import sys
import os
import signal
import threading
from pathlib import Path

class BackendTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.server_process = None
        self.test_results = []
        
    def log(self, message, level="INFO"):
        """Log message with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_endpoint(self, endpoint, expected_status=200):
        """Test a specific endpoint"""
        try:
            url = f"{self.base_url}{endpoint}"
            self.log(f"Testing endpoint: {url}")
            
            response = requests.get(url, timeout=10)
            status = response.status_code
            
            if status == expected_status:
                self.log(f"✅ {endpoint} - Status: {status}", "SUCCESS")
                self.test_results.append(f"✅ {endpoint}")
                return True
            else:
                self.log(f"❌ {endpoint} - Expected: {expected_status}, Got: {status}", "ERROR")
                self.test_results.append(f"❌ {endpoint} (Status: {status})")
                return False
                
        except requests.exceptions.ConnectionError:
            self.log(f"❌ {endpoint} - Connection refused (server not running)", "ERROR")
            self.test_results.append(f"❌ {endpoint} (Connection refused)")
            return False
        except Exception as e:
            self.log(f"❌ {endpoint} - Error: {e}", "ERROR")
            self.test_results.append(f"❌ {endpoint} (Error: {e})")
            return False
    
    def start_server(self, method="simple"):
        """Start the backend server"""
        try:
            self.log(f"Starting backend server using method: {method}")
            
            if method == "simple":
                script_path = "run_server_simple.py"
            elif method == "original":
                script_path = "run_server.py"
            else:
                script_path = "run_server.py"
            
            # Check if script exists
            if not os.path.exists(script_path):
                self.log(f"Script {script_path} not found!", "ERROR")
                return False
            
            # Start server in background
            self.log(f"Executing: python {script_path}")
            self.server_process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a bit for server to start
            time.sleep(5)
            
            # Check if process is still running
            if self.server_process.poll() is None:
                self.log("✅ Server process started successfully", "SUCCESS")
                return True
            else:
                stdout, stderr = self.server_process.communicate()
                self.log(f"❌ Server failed to start", "ERROR")
                self.log(f"STDOUT: {stdout}", "DEBUG")
                self.log(f"STDERR: {stderr}", "DEBUG")
                return False
                
        except Exception as e:
            self.log(f"Error starting server: {e}", "ERROR")
            return False
    
    def stop_server(self):
        """Stop the backend server"""
        if self.server_process:
            try:
                self.log("Stopping server...")
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                self.log("✅ Server stopped", "SUCCESS")
            except subprocess.TimeoutExpired:
                self.log("Force killing server...", "WARNING")
                self.server_process.kill()
            except Exception as e:
                self.log(f"Error stopping server: {e}", "ERROR")
    
    def run_tests(self):
        """Run all tests"""
        self.log("=== Starting Backend Connection Tests ===")
        
        # Test 1: Check if server is running
        self.log("Test 1: Checking if server is running...")
        if not self.test_endpoint("/"):
            self.log("Server not running, attempting to start...", "WARNING")
            
            # Try to start server
            if not self.start_server("simple"):
                self.log("Failed to start server with simple method, trying original...", "WARNING")
                if not self.start_server("original"):
                    self.log("All server start methods failed!", "ERROR")
                    return False
            
            # Wait for server to fully start
            time.sleep(10)
            
            # Test again
            if not self.test_endpoint("/"):
                self.log("Server still not responding after start!", "ERROR")
                return False
        
        # Test 2: Health check
        self.log("Test 2: Testing health endpoint...")
        self.test_endpoint("/health")
        
        # Test 3: API docs
        self.log("Test 3: Testing API documentation...")
        self.test_endpoint("/docs")
        
        # Test 4: WebSocket status
        self.log("Test 4: Testing WebSocket status...")
        self.test_endpoint("/api/websocket/status")
        
        # Test 5: Services status
        self.log("Test 5: Testing services status...")
        self.test_endpoint("/api/services/status")
        
        # Print summary
        self.log("=== Test Results Summary ===")
        for result in self.test_results:
            print(f"  {result}")
        
        success_count = len([r for r in self.test_results if r.startswith("✅")])
        total_count = len(self.test_results)
        
        self.log(f"Tests passed: {success_count}/{total_count}", "SUMMARY")
        
        if success_count == total_count:
            self.log("🎉 All tests passed! Backend is working correctly.", "SUCCESS")
            return True
        else:
            self.log("⚠️ Some tests failed. Backend has issues.", "WARNING")
            return False
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_server()

def main():
    """Main function"""
    tester = BackendTester()
    
    try:
        # Run tests
        success = tester.run_tests()
        
        if success:
            print("\n🎉 Backend is working! You can now access:")
            print("  🌐 Main API: http://localhost:8000")
            print("  📚 API Docs: http://localhost:8000/docs")
            print("  ❤️ Health: http://localhost:8000/health")
            print("  🔌 WebSocket: ws://localhost:8000/gemini-live")
        else:
            print("\n❌ Backend has issues. Check the logs above.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main() 