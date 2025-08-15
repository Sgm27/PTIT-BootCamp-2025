"""
Configuration settings for the Healthcare Assistant API
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)


class Settings:
    """Application settings."""
    
    # API Keys
    GOOGLE_API_KEY: str = os.getenv('GOOGLE_API_KEY')
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY')
    
    # Models
    GEMINI_MODEL: str = "gemini-live-2.5-flash-preview"
    OPENAI_VISION_MODEL: str = "gpt-4o"
    OPENAI_TEXT_MODEL: str = "gpt-4.1-nano"
    
    # App settings
    APP_TITLE: str = "AI Healthcare Assistant API"
    APP_DESCRIPTION: str = "Backend API for AI Healthcare Assistant with Gemini Live and Medicine Scanner"
    APP_VERSION: str = "1.0.0"
    
    # CORS settings
    CORS_ORIGINS: list = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    # Session settings
    SESSION_FILE: str = "session_handle.json"
    SESSION_TIMEOUT_SECONDS: int = 60  # 1 minute
    
    # WebSocket settings - OPTIMIZED FOR STABLE CONNECTIONS
    WEBSOCKET_PING_INTERVAL: int = 30  # Send ping every 30 seconds (increased for stability)
    WEBSOCKET_PING_TIMEOUT: int = 45   # Wait 45 seconds for pong (increased timeout)
    WEBSOCKET_CLOSE_TIMEOUT: int = 90  # Wait 90 seconds for close (increased for graceful shutdown)
    WEBSOCKET_MESSAGE_TIMEOUT: int = 3600  # 1 hour timeout for messages (increased for long sessions)
    WEBSOCKET_CONFIG_TIMEOUT: int = 600  # 10 minutes timeout for config (increased for slow connections)
    WEBSOCKET_KEEPALIVE_INTERVAL: int = 30  # Send keepalive every 30 seconds
    WEBSOCKET_CONNECTION_TIMEOUT: int = 120  # 2 minutes timeout for new connections
    
    def __init__(self):
        """Validate required environment variables."""
        if not self.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")


# Global settings instance
settings = Settings()
