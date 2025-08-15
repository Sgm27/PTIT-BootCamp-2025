#!/usr/bin/env python3
"""
Script to restart the server with optimized settings for stable WebSocket connections
"""
import subprocess
import sys
import os
import time
import signal
import psutil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ServerManager:
    def __init__(self):
        self.server_process = None
        self.server_pid = None
        
    def find_server_process(self):
        """Find existing server process"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and any('run_server.py' in cmd for cmd in proc.info['cmdline']):
                        return proc
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return None
        except Exception as e:
            logger.error(f"Error finding server process: {e}")
            return None
    
    def stop_server(self):
        """Stop the existing server process"""
        try:
            proc = self.find_server_process()
            if proc:
                logger.info(f"🛑 Stopping existing server process (PID: {proc.pid})")
                
                # Try graceful shutdown first
                proc.terminate()
                
                # Wait for graceful shutdown
                try:
                    proc.wait(timeout=30)
                    logger.info("✅ Server stopped gracefully")
                except psutil.TimeoutExpired:
                    logger.warning("⚠️ Graceful shutdown timeout, forcing kill")
                    proc.kill()
                    proc.wait()
                    logger.info("✅ Server force killed")
                
                return True
            else:
                logger.info("ℹ️ No existing server process found")
                return True
        except Exception as e:
            logger.error(f"❌ Error stopping server: {e}")
            return False
    
    def start_server(self):
        """Start the server with optimized settings"""
        try:
            logger.info("🚀 Starting server with optimized WebSocket settings...")
            
            # Set environment variables for stability
            env = os.environ.copy()
            env['UVICORN_RELOAD'] = '0'  # Disable reload
            env['PYTHONIOENCODING'] = 'utf-8'  # Fix encoding issues
            
            # Start server process
            cmd = [sys.executable, 'backend/run_server.py']
            
            self.server_process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.server_pid = self.server_process.pid
            logger.info(f"✅ Server started with PID: {self.server_pid}")
            
            # Wait a moment for server to initialize
            time.sleep(5)
            
            # Check if server is still running
            if self.server_process.poll() is None:
                logger.info("✅ Server is running successfully")
                return True
            else:
                logger.error("❌ Server failed to start")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting server: {e}")
            return False
    
    def monitor_server(self, duration_minutes=5):
        """Monitor server for a specified duration"""
        try:
            logger.info(f"📊 Monitoring server for {duration_minutes} minutes...")
            
            start_time = time.time()
            while time.time() - start_time < duration_minutes * 60:
                if self.server_process.poll() is not None:
                    logger.error("❌ Server process has stopped unexpectedly")
                    return False
                
                # Log server status every 30 seconds
                if int(time.time() - start_time) % 30 == 0:
                    uptime = time.time() - start_time
                    logger.info(f"📈 Server uptime: {uptime:.1f}s")
                
                time.sleep(1)
            
            logger.info("✅ Server monitoring completed successfully")
            return True
            
        except KeyboardInterrupt:
            logger.info("🛑 Server monitoring interrupted by user")
            return True
        except Exception as e:
            logger.error(f"❌ Error monitoring server: {e}")
            return False
    
    def restart_server(self):
        """Restart the server with optimized settings"""
        logger.info("🔄 Starting server restart process...")
        
        # Stop existing server
        if not self.stop_server():
            logger.error("❌ Failed to stop existing server")
            return False
        
        # Wait a moment for cleanup
        time.sleep(3)
        
        # Start new server
        if not self.start_server():
            logger.error("❌ Failed to start new server")
            return False
        
        logger.info("✅ Server restart completed successfully")
        return True
    
    def show_server_info(self):
        """Show current server configuration"""
        logger.info("📋 Server Configuration:")
        logger.info("  🔄 Auto-reload: DISABLED (for stability)")
        logger.info("  🌐 WebSocket settings:")
        logger.info("    - Ping interval: 20 seconds")
        logger.info("    - Ping timeout: 30 seconds")
        logger.info("    - Keep alive: 5 minutes")
        logger.info("    - Message timeout: 30 minutes")
        logger.info("    - Max message size: 64MB")
        logger.info("    - Max queue size: 256")
        logger.info("    - Concurrent connections: 2000")
        logger.info("  📊 Connection stability features:")
        logger.info("    - Enhanced keepalive mechanism")
        logger.info("    - Improved error handling")
        logger.info("    - Graceful timeout handling")
        logger.info("    - Connection monitoring")

def main():
    """Main function"""
    manager = ServerManager()
    
    # Show server info
    manager.show_server_info()
    
    # Restart server
    if manager.restart_server():
        logger.info("🎉 Server restart successful!")
        
        # Monitor for a few minutes
        manager.monitor_server(duration_minutes=3)
        
        logger.info("💡 Server is now running with optimized settings for stable WebSocket connections")
        logger.info("🔗 You can now test the connection stability")
    else:
        logger.error("💥 Server restart failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 