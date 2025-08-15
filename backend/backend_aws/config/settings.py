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
    OPENAI_TEXT_MODEL: str = "gpt-4o-mini"
    
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
    SESSION_TIMEOUT_SECONDS: int = 60
    
    def __init__(self):
        """Validate required environment variables."""
        if not self.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")


# Global settings instance
settings = Settings()
