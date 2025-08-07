"""
Enhanced server startup script with database integration and better logging
"""
import uvicorn
import logging
import sys
import os
from pathlib import Path

# Fix Windows UTF-8 encoding issue
if sys.platform == "win32":
    # Set environment variable for UTF-8 output
    os.environ["PYTHONIOENCODING"] = "utf-8"
    # Reconfigure stdout and stderr for UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

# Configure logging with UTF-8 support
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('server.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# Import database components
try:
    from db.db_config import init_database, check_database_connection
    from db.db_services import (
        UserService, ConversationService, HealthService,
        MedicineDBService, NotificationDBService, MemoirDBService,
        SessionDBService
    )
    DATABASE_AVAILABLE = True
    logger.info("Database modules loaded successfully")
except ImportError as e:
    DATABASE_AVAILABLE = False
    logger.warning(f"Database modules not available: {e}")
    logger.warning("Server will run in file-based mode")

def initialize_database():
    """Initialize database connection and create tables"""
    if not DATABASE_AVAILABLE:
        logger.info("Database not available - skipping database initialization")
        return False
    
    try:
        logger.info("Initializing database connection...")
        
        # Check database connection
        if not check_database_connection():
            logger.error("Failed to connect to database")
            return False
        
        logger.info("Database connection successful")
        
        # Initialize database tables
        logger.info("Creating database tables...")
        init_database()
        logger.info("Database tables created successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def run_server():
    """Run the server with enhanced configuration."""
    try:
        logger.info("=== AI Healthcare Assistant API Server ===")
        logger.info("Starting server initialization...")
        
        # Initialize database
        db_status = initialize_database()
        
        logger.info("Server Configuration:")
        logger.info("  🌐 WebSocket endpoint: /gemini-live")
        logger.info("  ❤️ Health check: /health")
        logger.info("  📚 API documentation: /docs")
        logger.info("  🗄️ Database: " + ("✅ Connected" if db_status else "❌ File-based mode"))
        logger.info("  🎭 Memoir extraction: INTEGRATED & ON-DISCONNECT")
        logger.info("     - Auto extraction: DISABLED")
        logger.info("     - Trigger: ON CLIENT DISCONNECT ONLY")
        logger.info("     - Mode: Full conversation processing")
        logger.info("     - Storage: " + ("Database" if db_status else "File (my_life_stories.txt)"))
        
        if DATABASE_AVAILABLE and db_status:
            logger.info("🎯 Features enabled:")
            logger.info("  ✅ User Management (Elderly + Family)")
            logger.info("  ✅ Conversation History (Database)")
            logger.info("  ✅ Health Records & Vital Signs")
            logger.info("  ✅ Medicine Management & Scanning")
            logger.info("  ✅ Smart Notifications & Reminders")
            logger.info("  ✅ Life Memoir Extraction & Storage")
            logger.info("  ✅ Session Management")
            logger.info("  ✅ Family Relationship Management")
        else:
            logger.warning("⚠️ Running in limited mode - some features disabled")
        
        logger.info("Starting server...")
        
        uvicorn.run(
            "backend:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True,
            ws_ping_interval=20,  # Ping every 20 seconds
            ws_ping_timeout=15,   # Wait 15 seconds for pong
            ws_max_size=16777216, # 16MB max message size
            ws_max_queue=64,      # Message queue size
            timeout_keep_alive=65, # Keep alive timeout
            h11_max_incomplete_event_size=65536, # Increased for large audio chunks
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_server()
