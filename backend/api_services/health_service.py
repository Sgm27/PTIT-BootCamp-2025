"""
Health API Service
Handles health checks, system status, and service monitoring
"""
from fastapi import FastAPI
import datetime
import logging

logger = logging.getLogger(__name__)

def add_health_endpoints(app: FastAPI, services_dict: dict, settings):
    """Add health and monitoring endpoints to the FastAPI app
    
    Args:
        app: FastAPI application instance
        services_dict: Dictionary containing all service instances
        settings: Application settings
    """
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": settings.APP_TITLE, 
            "version": settings.APP_VERSION,
            "status": "running"
        }

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy", 
            "timestamp": datetime.datetime.now().isoformat(),
            "services": {
                "medicine_service": "active",
                "text_extraction_service": "active",
                "gemini_service": "active",
                "notification_voice_service": "active",
                "memoir_extraction_service": "active"
            }
        }

    @app.get("/api/services/status")
    async def get_services_status():
        """Get status of all services.
        
        Returns:
            Dictionary containing status of all services.
        """
        medicine_service = services_dict.get('medicine_service')
        text_extraction_service = services_dict.get('text_extraction_service')
        gemini_service = services_dict.get('gemini_service')
        notification_voice_service = services_dict.get('notification_voice_service')
        memoir_extraction_service = services_dict.get('memoir_extraction_service')
        
        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "services": {
                "medicine_service": {
                    "status": "active",
                    "model": getattr(medicine_service, 'model', 'unknown'),
                    "temperature": getattr(medicine_service, 'temperature', 'unknown')
                },
                "text_extraction_service": {
                    "status": "active", 
                    "model": getattr(text_extraction_service, 'model', 'unknown'),
                    "temperature": getattr(text_extraction_service, 'temperature', 'unknown')
                },
                "gemini_service": {
                    "status": "active",
                    "model": getattr(gemini_service, 'model', 'unknown')
                },
                "notification_voice_service": {
                    "status": "active",
                    "model": getattr(notification_voice_service, 'model', 'unknown')
                },
                "memoir_extraction_service": {
                    "status": "active",
                    "model": getattr(memoir_extraction_service, 'model', 'unknown'),
                    "temperature": getattr(memoir_extraction_service, 'temperature', 'unknown')
                }
            },
            "configuration": {
                "openai_model_vision": settings.OPENAI_VISION_MODEL,
                "openai_model_text": settings.OPENAI_TEXT_MODEL,
                "gemini_model": settings.GEMINI_MODEL
            },
            "websocket_settings": {
                "ping_interval": settings.WEBSOCKET_PING_INTERVAL,
                "ping_timeout": settings.WEBSOCKET_PING_TIMEOUT,
                "close_timeout": settings.WEBSOCKET_CLOSE_TIMEOUT,
                "session_timeout": settings.SESSION_TIMEOUT_SECONDS
            }
        }

    @app.get("/api/websocket/health")
    async def websocket_health_check():
        """WebSocket health check endpoint.
        
        Returns:
            WebSocket configuration and status.
        """
        return {
            "status": "healthy",
            "websocket_endpoint": "/gemini-live",
            "ping_interval_seconds": settings.WEBSOCKET_PING_INTERVAL,
            "session_timeout_seconds": settings.SESSION_TIMEOUT_SECONDS,
            "timestamp": datetime.datetime.now().isoformat()
        } 