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

# Reload configuration - ENABLED FOR DEVELOPMENT
RELOAD_ENABLED = True  # Enable reload for development stability
RELOAD_DIRS = [
    str(Path(__file__).parent),
    str(Path(__file__).parent / "services"),
    str(Path(__file__).parent / "api_services"),
]
# Exclude runtime data files from triggering reloads (prevents WS reconnect loops)
RELOAD_EXCLUDES = [
    "*.json",
    "*.log",
    "*.txt",
    "conversation_history.json",
    "session_handle.json",
]

# Try to import settings for consistent WebSocket tuning
try:
    from config.settings import settings as app_settings
    WS_PING_INTERVAL = app_settings.WEBSOCKET_PING_INTERVAL
    WS_PING_TIMEOUT = app_settings.WEBSOCKET_PING_TIMEOUT
except Exception:
    app_settings = None
    WS_PING_INTERVAL = 20
    WS_PING_TIMEOUT = 30

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

# Import notification scheduler
try:
    from services.notification_scheduler import notification_scheduler
    NOTIFICATION_SCHEDULER_AVAILABLE = True
    logger.info("Notification scheduler loaded successfully")
except ImportError as e:
    NOTIFICATION_SCHEDULER_AVAILABLE = False
    logger.warning(f"Notification scheduler not available: {e}")

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
    """Initialize and configure the daily memoir extraction scheduler"""
    if not DAILY_MEMOIR_SCHEDULER_AVAILABLE:
        logger.info("Daily memoir scheduler not available - skipping scheduler initialization")
        return False
    
    if not DATABASE_AVAILABLE:
        logger.warning("Database not available - daily memoir scheduler disabled")
        return False
    
    try:
        logger.info("Configuring daily memoir extraction scheduler...")
        # Configure the scheduler (jobs will be added but not started yet)
        # Add safety check before calling start_scheduler
        if hasattr(daily_memoir_scheduler, 'start_scheduler'):
            daily_memoir_scheduler.start_scheduler()
            logger.info("📅 Daily memoir scheduler configured (will start with FastAPI event loop)")
            return True
        else:
            logger.warning("Daily memoir scheduler missing start_scheduler method")
            return False
            
    except Exception as e:
        logger.error(f"Failed to configure daily memoir scheduler: {e}")
        return False

def initialize_notification_scheduler():
    """Initialize and configure the notification scheduler"""
    if not NOTIFICATION_SCHEDULER_AVAILABLE:
        logger.info("Notification scheduler not available - skipping scheduler initialization")
        return False
    
    if not DATABASE_AVAILABLE:
        logger.warning("Database not available - notification scheduler disabled")
        return False
    
    try:
        logger.info("Configuring notification scheduler...")
        # Configure the scheduler (jobs will be added but not started yet)
        # Add safety check before calling start_scheduler
        if hasattr(notification_scheduler, 'start_scheduler'):
            notification_scheduler.start_scheduler()
            logger.info("🔔 Notification scheduler configured (will start with FastAPI event loop)")
            return True
        else:
            logger.warning("Notification scheduler missing start_scheduler method")
            return False
            
    except Exception as e:
        logger.error(f"Failed to configure notification scheduler: {e}")
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
        
        # Initialize notification scheduler
        notification_scheduler_status = initialize_notification_scheduler()
        
        logger.info("Server Configuration:")
        logger.info("  🌐 WebSocket endpoint: /gemini-live")
        logger.info("  ❤️ Health check: /health")
        logger.info("  📚 API documentation: /docs")
        logger.info("  🗄️ Database: " + ("✅ Connected" if db_status else "❌ File-based mode"))
        logger.info("  📅 Daily Memoir Scheduler: " + ("✅ Configured (starts with event loop)" if scheduler_status else "❌ Disabled"))
        logger.info("  🔔 Notification Scheduler: " + ("✅ Configured (starts with event loop)" if notification_scheduler_status else "❌ Disabled"))
        logger.info("  🔄 Auto-reload: " + ("✅ Enabled" if RELOAD_ENABLED else "❌ Disabled"))
        logger.info("  🎭 Memoir extraction: DAILY AUTOMATED PROCESSING")
        logger.info("     - Schedule: Daily at 23:59")
        logger.info("     - Trigger: DAILY BATCH PROCESSING")
        logger.info("     - Mode: All conversations from previous day")
        logger.info("     - Storage: " + ("Database (life_memoirs table)" if db_status else "File (my_life_stories.txt)"))
        logger.info("     - User-specific: ✅ Each user's conversations processed separately")
        logger.info("     - Startup: Scheduler starts with FastAPI event loop")
        
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
        
        # Fix module path - use correct module reference for different run locations
        # Try different module paths based on where the script is run from
        # Try multiple module paths to be robust across working directories
        # Ensure import paths are correct for both direct run and reloader
        project_root = Path(__file__).resolve().parent.parent
        backend_dir = Path(__file__).resolve().parent
        try:
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            if str(backend_dir) not in sys.path:
                sys.path.insert(0, str(backend_dir))
            logger.info(f"sys.path updated with project_root={project_root} and backend_dir={backend_dir}")
        except Exception as e:
            logger.warning(f"Failed to update sys.path: {e}")

        module_paths = [
            "backend.backend:app",  # When running from project root
            "backend:app",          # When running from backend directory
        ]
        last_error = None
        for module_path in module_paths:
            try:
                logger.info(f"Trying ASGI app import: {module_path}")
                uvicorn_kwargs = dict(
                    host="0.0.0.0",
                    port=8000,
                    reload=RELOAD_ENABLED,
                    reload_dirs=RELOAD_DIRS,
                    log_level="info",
                    access_log=True,
                    # WebSocket stability settings - OPTIMIZED FOR LONG CONNECTIONS
                    ws_ping_interval=WS_PING_INTERVAL,
                    ws_ping_timeout=WS_PING_TIMEOUT,
                    ws_max_size=67108864, # 64MB max message size (increased for large audio/video)
                    ws_max_queue=256,     # Message queue size (increased for better buffering)
                    timeout_keep_alive=300, # Keep alive timeout 5 minutes (increased significantly)
                    h11_max_incomplete_event_size=262144, # Increased for large audio chunks
                    limit_concurrency=2000,  # Increased concurrent connections
                    limit_max_requests=50000,  # Increased max requests per worker
                    # Additional stability settings
                    timeout_graceful_shutdown=30,  # Graceful shutdown timeout
                    backlog=2048,  # Connection backlog
                )
                if RELOAD_ENABLED:
                    try:
                        uvicorn.run(
                            module_path,
                            reload_excludes=RELOAD_EXCLUDES,
                            **uvicorn_kwargs,
                        )
                    except TypeError:
                        # Older uvicorn may not support reload_excludes
                        logger.warning("reload_excludes not supported by current uvicorn version; running without excludes")
                        uvicorn.run(
                            module_path,
                            **uvicorn_kwargs,
                        )
                else:
                    uvicorn.run(
                        module_path,
                        **uvicorn_kwargs,
                    )
                return
            except ModuleNotFoundError as e:
                logger.warning(f"Failed to import '{module_path}': {e}")
                last_error = e
                continue
            except Exception as e:
                logger.error(f"Unexpected error with '{module_path}': {e}")
                last_error = e
                continue
        if last_error:
            raise last_error
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error details: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_server()
