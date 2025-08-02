"""
Enhanced server startup script with better logging and error handling
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

def run_server():
    """Run the server with enhanced configuration."""
    try:
        logger.info("Starting AI Healthcare Assistant API server...")
        logger.info("WebSocket endpoint: /gemini-live")
        logger.info("Health check: /health")
        logger.info("API documentation: /docs")
        
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
