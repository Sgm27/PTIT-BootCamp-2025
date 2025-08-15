"""
Simple server startup script for testing
"""
import uvicorn
import logging
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_server():
    """Run the server with simple configuration."""
    try:
        logger.info("=== AI Healthcare Assistant API Server (Simple) ===")
        logger.info("Starting server...")
        logger.info("  🌐 WebSocket endpoint: /gemini-live")
        logger.info("  ❤️ Health check: /health")
        logger.info("  📚 API documentation: /docs")
        logger.info("  🔄 Auto-reload: ✅ Enabled")
        
        # Try different module paths
        module_paths = [
            "backend:app",      # When running from project root
            "run_server:app",   # When running from backend directory
            "backend:app"       # Fallback
        ]
        
        for i, module_path in enumerate(module_paths):
            try:
                logger.info(f"Trying module path: {module_path}")
                uvicorn.run(
                    module_path,
                    host="0.0.0.0",
                    port=8000,
                    reload=True,
                    log_level="info",
                    access_log=True
                )
                break  # If successful, break the loop
            except ModuleNotFoundError as e:
                logger.warning(f"Module path {module_path} failed: {e}")
                if i == len(module_paths) - 1:  # Last attempt
                    logger.error("All module paths failed!")
                    raise e
                continue
            except Exception as e:
                logger.error(f"Unexpected error with {module_path}: {e}")
                raise e
                
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        sys.exit(1)

if __name__ == "__main__":
    run_server() 