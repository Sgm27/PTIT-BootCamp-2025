"""
Notification API Service
Handles voice notifications, broadcasting, and WebSocket communication
"""
from fastapi import FastAPI, HTTPException
import logging

logger = logging.getLogger(__name__)

def add_notification_endpoints(app: FastAPI, notification_voice_service, websocket_manager):
    """Add notification-related endpoints to the FastAPI app
    
    Args:
        app: FastAPI application instance
        notification_voice_service: Service instance for voice notifications
        websocket_manager: WebSocket manager for broadcasting
    """
    
    @app.post("/api/generate-voice-notification")
    async def generate_voice_notification_endpoint(request: dict):
        """Generate voice notification from text and broadcast to connected clients.
        
        Args:
            request: Request containing notification text and type.
            
        Returns:
            Response with voice notification data.
            
        Raises:
            HTTPException: If generation fails.
        """
        try:
            notification_text = request.get("text", "")
            notification_type = request.get("type", "info")
            
            if not notification_text:
                raise HTTPException(status_code=400, detail="Notification text is required")
            
            # Generate voice notification
            if notification_type == "emergency":
                audio_base64 = await notification_voice_service.generate_voice_notification_base64(
                    f"THÔNG BÁO KHẨN CẤP: {notification_text}"
                )
            else:
                audio_base64 = await notification_voice_service.generate_voice_notification_base64(notification_text)
            
            if audio_base64:
                response = notification_voice_service.create_notification_response(audio_base64, notification_text)
                
                # Try to broadcast to all connected WebSocket clients
                try:
                    notification_data = {
                        "message": response["message"],
                        "notificationText": response["notificationText"],
                        "audioBase64": response["audioBase64"],
                        "audioFormat": response["audioFormat"],
                        "timestamp": response["timestamp"],
                        "service": response["service"]
                    }
                    
                    await websocket_manager.broadcast_voice_notification(notification_data)
                    logger.info(f"Voice notification broadcasted to {websocket_manager.get_connection_count()} clients")
                except Exception as broadcast_error:
                    logger.error(f"Broadcast failed: {broadcast_error}")
                    # Continue anyway - API should still return the response
                
                return response
            else:
                error_response = notification_voice_service.create_error_response(
                    "Failed to generate voice notification", notification_text
                )
                raise HTTPException(status_code=500, detail=error_response["message"])
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/broadcast-voice-notification")
    async def broadcast_voice_notification_endpoint(request: dict):
        """Endpoint để test broadcast voice notification từ Python script.
        
        Args:
            request: Request containing notification text and type.
            
        Returns:
            Response with broadcast status.
        """
        try:
            notification_text = request.get("text", "")
            notification_type = request.get("type", "info")
            
            if not notification_text:
                raise HTTPException(status_code=400, detail="Notification text is required")
            
            # Generate voice notification
            if notification_type == "emergency":
                audio_base64 = await notification_voice_service.generate_voice_notification_base64(
                    f"THÔNG BÁO KHẨN CẤP: {notification_text}"
                )
            else:
                audio_base64 = await notification_voice_service.generate_voice_notification_base64(notification_text)
            
            if audio_base64:
                response = notification_voice_service.create_notification_response(audio_base64, notification_text)
                
                # Broadcast to all connected WebSocket clients
                notification_data = {
                    "message": response["message"],
                    "notificationText": response["notificationText"],
                    "audioBase64": response["audioBase64"],
                    "audioFormat": response["audioFormat"],
                    "timestamp": response["timestamp"],
                    "service": response["service"]
                }
                
                connection_count = websocket_manager.get_connection_count()
                await websocket_manager.broadcast_voice_notification(notification_data)
                
                return {
                    "success": True,
                    "message": f"Voice notification broadcasted successfully",
                    "connectionCount": connection_count,
                    "notificationText": notification_text,
                    "timestamp": response["timestamp"]
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to generate voice notification")
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) 