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

# Import daily memoir scheduler
try:
    from services.daily_memoir_scheduler import daily_memoir_scheduler
    DAILY_MEMOIR_SCHEDULER_AVAILABLE = True
    logger.info("Daily memoir scheduler loaded successfully")
except ImportError as e:
    DAILY_MEMOIR_SCHEDULER_AVAILABLE = False
    logger.warning(f"Daily memoir scheduler not available: {e}")

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
        
        # Skip table creation - tables already exist from SQL script
        logger.info("Database tables already exist from SQL initialization script")
        # init_database()  # Commented out to avoid conflicts with existing tables
        
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def initialize_daily_memoir_scheduler():
    """Initialize and start the daily memoir extraction scheduler"""
    if not DAILY_MEMOIR_SCHEDULER_AVAILABLE:
        logger.info("Daily memoir scheduler not available - skipping scheduler initialization")
        return False
    
    if not DATABASE_AVAILABLE:
        logger.warning("Database not available - daily memoir scheduler disabled")
        return False
    
    try:
        logger.info("Starting daily memoir extraction scheduler...")
        daily_memoir_scheduler.start_scheduler()
        
        # Get scheduler status
        status = daily_memoir_scheduler.get_scheduler_status()
        if status.get("running"):
            logger.info("✅ Daily memoir scheduler started successfully")
            for job in status.get("jobs", []):
                logger.info(f"   - Job: {job['name']} | Next run: {job['next_run']}")
            return True
        else:
            logger.error("❌ Failed to start daily memoir scheduler")
            return False
            
    except Exception as e:
        logger.error(f"Failed to initialize daily memoir scheduler: {e}")
        return False

def run_server():
    """Run the server with enhanced configuration."""
    try:
        logger.info("=== AI Healthcare Assistant API Server ===")
        logger.info("Starting server initialization...")
        
        # Initialize database
        db_status = initialize_database()
        
        # Initialize daily memoir scheduler
        scheduler_status = initialize_daily_memoir_scheduler()
        
        logger.info("Server Configuration:")
        logger.info("  🌐 WebSocket endpoint: /gemini-live")
        logger.info("  ❤️ Health check: /health")
        logger.info("  📚 API documentation: /docs")
        logger.info("  🗄️ Database: " + ("✅ Connected" if db_status else "❌ File-based mode"))
        logger.info("  📅 Daily Memoir Scheduler: " + ("✅ Running" if scheduler_status else "❌ Disabled"))
        logger.info("  🎭 Memoir extraction: DAILY AUTOMATED PROCESSING")
        logger.info("     - Schedule: Daily at 23:59")
        logger.info("     - Trigger: DAILY BATCH PROCESSING")
        logger.info("     - Mode: All conversations from previous day")
        logger.info("     - Storage: " + ("Database (life_memoirs table)" if db_status else "File (my_life_stories.txt)"))
        logger.info("     - User-specific: ✅ Each user's conversations processed separately")
        
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
            reload=False,  # Tắt reload để tránh ngắt kết nối
            log_level="info",
            access_log=True,
            ws_ping_interval=30,  # Ping every 30 seconds (tăng từ 15s)
            ws_ping_timeout=45,   # Wait 45 seconds for pong (tăng từ 20s)
            ws_max_size=33554432, # 32MB max message size (tăng từ 16MB)
            ws_max_queue=128,     # Message queue size (tăng từ 64)
            timeout_keep_alive=120, # Keep alive timeout (tăng từ 65s)
            h11_max_incomplete_event_size=131072, # Increased for large audio chunks
            limit_concurrency=1000,  # Limit concurrent connections
            limit_max_requests=10000,  # Limit max requests per worker
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_server()
