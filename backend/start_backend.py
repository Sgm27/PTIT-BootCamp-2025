#!/usr/bin/env python3
"""
Backend Server Startup Script
Starts the AI Healthcare Assistant API server with proper configuration
"""

import os
import sys
import subprocess
import time
import signal
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        logger.info("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.info("Please install dependencies: pip install -r requirements.txt")
        return False

def check_database():
    """Check database connection"""
    try:
        from db.db_config import check_database_connection
        if check_database_connection():
            logger.info("✅ Database connection successful")
            return True
        else:
            logger.error("❌ Database connection failed")
            return False
    except Exception as e:
        logger.error(f"❌ Database check failed: {e}")
        return False

def start_server():
    """Start the backend server"""
    try:
        logger.info("🚀 Starting AI Healthcare Assistant API Server...")
        
        # Check dependencies
        if not check_dependencies():
            return False
        
        # Check database
        if not check_database():
            logger.warning("⚠️ Database not available - server will run in file-based mode")
        
        # Start server
        cmd = [sys.executable, "run_server.py"]
        logger.info(f"Running: {' '.join(cmd)}")
        
        process = subprocess.Popen(cmd, cwd=Path(__file__).parent)
        
        # Wait for server to start
        time.sleep(3)
        
        if process.poll() is None:
            logger.info("✅ Server started successfully")
            logger.info("🌐 API available at: http://localhost:8000")
            logger.info("📚 Documentation at: http://localhost:8000/docs")
            logger.info("❤️ Health check at: http://localhost:8000/health")
            logger.info("Press Ctrl+C to stop the server")
            
            try:
                process.wait()
            except KeyboardInterrupt:
                logger.info("🛑 Shutting down server...")
                process.terminate()
                process.wait()
                logger.info("✅ Server stopped")
            
            return True
        else:
            logger.error("❌ Server failed to start")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error starting server: {e}")
        return False

def main():
    """Main function"""
    logger.info("=" * 60)
    logger.info("🏥 AI Healthcare Assistant - Backend Server")
    logger.info("=" * 60)
    
    success = start_server()
    
    if success:
        logger.info("🎉 Server startup completed successfully")
    else:
        logger.error("💥 Server startup failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
