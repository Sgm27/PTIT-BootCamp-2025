"""
AI Healthcare Assistant API - Restructured Backend
Main FastAPI application with separated services
"""
import datetime
import base64
import logging
from fastapi import FastAPI, WebSocket, HTTPException, UploadFile, File, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
from google import genai

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import configurations
from config.settings import settings

# Import models
from models.api_models import MedicineScanRequest, TextExtractRequest, HealthResponse

# Import services
from services.medicine_service import MedicineService
from services.text_extraction_service import TextExtractionService
from services.gemini_service import GeminiService
from services.notification_voice_service import NotificationVoiceService
from services.memoir_extraction_service import MemoirExtractionService
from services.websocket_manager import websocket_manager


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# Initialize clients
openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
gemini_client = genai.Client(api_key=settings.GOOGLE_API_KEY)

# Initialize services
medicine_service = MedicineService(openai_client)
text_extraction_service = TextExtractionService(openai_client)
gemini_service = GeminiService(gemini_client)
notification_voice_service = NotificationVoiceService(gemini_client)
memoir_extraction_service = MemoirExtractionService(openai_client)


# API Routes
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


@app.post("/api/scan-medicine", response_model=HealthResponse)
async def scan_medicine_endpoint(request: MedicineScanRequest):
    """Scan medicine from image URL or base64 string.
    
    Args:
        request: Request containing image URL or base64 string.
        
    Returns:
        HealthResponse with scan results.
        
    Raises:
        HTTPException: If scanning fails.
    """
    try:
        result = await medicine_service.scan_medicine(request.input)
        return HealthResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scan-medicine-file")
async def scan_medicine_file_endpoint(file: UploadFile = File(...)):
    """Scan medicine from uploaded image file.
    
    Args:
        file: Uploaded image file.
        
    Returns:
        HealthResponse with scan results.
        
    Raises:
        HTTPException: If scanning fails.
    """
    try:
        # Read file content
        content = await file.read()
        
        # Scan medicine using service
        result = await medicine_service.scan_from_file_content(content)
        return HealthResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/extract-memoir-info", response_model=HealthResponse)
async def extract_memoir_info_endpoint(request: TextExtractRequest):
    """Extract information from text for memoir purposes.
    
    Args:
        request: Request containing text to extract information from.
        
    Returns:
        HealthResponse with extracted information.
        
    Raises:
        HTTPException: If extraction fails.
    """
    try:
        result = await text_extraction_service.extract_info_for_memoir(request.text)
        return HealthResponse(success=True, result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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


@app.get("/api/services/status")
async def get_services_status():
    """Get status of all services.
    
    Returns:
        Dictionary containing status of all services.
    """
    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "services": {
            "medicine_service": {
                "status": "active",
                "model": medicine_service.model,
                "temperature": medicine_service.temperature
            },
            "text_extraction_service": {
                "status": "active", 
                "model": text_extraction_service.model,
                "temperature": text_extraction_service.temperature
            },
            "gemini_service": {
                "status": "active",
                "model": gemini_service.model
            },
            "notification_voice_service": {
                "status": "active",
                "model": notification_voice_service.model
            },
            "memoir_extraction_service": {
                "status": "active",
                "model": memoir_extraction_service.model,
                "temperature": memoir_extraction_service.temperature
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


@app.post("/api/memoir/extract-background")
async def start_memoir_extraction_background():
    """Start background memoir extraction from conversation history.
    
    Returns:
        Status of background task initiation.
    """
    try:
        result = memoir_extraction_service.start_background_extraction()
        return {
            "success": True,
            "message": "Background memoir extraction initiated",
            "task_status": result,
            "timestamp": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start background extraction: {str(e)}")


@app.get("/api/memoir/status")
async def get_memoir_extraction_status():
    """Get status of memoir extraction background task.
    
    Returns:
        Current status of background extraction task.
    """
    try:
        status = await memoir_extraction_service.get_background_task_status()
        return {
            "success": True,
            "task_status": status,
            "timestamp": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get extraction status: {str(e)}")


@app.get("/api/memoir/file-info")
async def get_memoir_file_info():
    """Get information about the memoir file.
    
    Returns:
        Information about memoir file including size, last modified, etc.
    """
    try:
        file_info = await memoir_extraction_service.get_memoir_file_info()
        return {
            "success": True,
            "file_info": file_info,
            "timestamp": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get file info: {str(e)}")


@app.post("/api/memoir/extract-manual")
async def extract_memoir_manual():
    """Manually extract important information from current conversation history.
    
    Returns:
        Results of memoir extraction process.
    """
    try:
        result = await memoir_extraction_service.process_conversation_history_background()
        return {
            "success": True,
            "extraction_result": result,
            "timestamp": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract memoir information: {str(e)}")


@app.get("/api/memoir/auto-settings")
async def get_memoir_auto_settings():
    """Get current auto extraction settings.
    
    Returns:
        Current auto extraction configuration.
    """
    try:
        settings_info = memoir_extraction_service.get_auto_extraction_settings()
        return {
            "success": True,
            "auto_settings": settings_info,
            "timestamp": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get auto settings: {str(e)}")


@app.post("/api/memoir/auto-settings")
async def update_memoir_auto_settings(request: dict):
    """Update auto extraction settings.
    
    Args:
        request: Request containing new threshold value.
        
    Returns:
        Status of settings update.
    """
    try:
        threshold = request.get("threshold")
        if not threshold or not isinstance(threshold, int):
            raise HTTPException(status_code=400, detail="Valid threshold number is required")
        
        result = memoir_extraction_service.update_auto_extraction_threshold(threshold)
        return {
            "success": result["success"],
            "message": result.get("message", result.get("error")),
            "settings": memoir_extraction_service.get_auto_extraction_settings(),
            "timestamp": datetime.datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update auto settings: {str(e)}")


@app.post("/api/memoir/update-conversation")
async def update_conversation_with_memoir(request: dict):
    """Update conversation history and potentially trigger auto extraction.
    
    Args:
        request: Request containing new message data.
        
    Returns:
        Status of conversation update and extraction.
    """
    try:
        # Validate required fields
        required_fields = ["role", "text"]
        for field in required_fields:
            if field not in request:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create message with timestamp
        new_message = {
            "role": request["role"],
            "text": request["text"], 
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        result = await memoir_extraction_service.update_conversation_and_extract(new_message)
        return {
            "success": result["success"],
            "message": result.get("message"),
            "conversation_info": {
                "total_messages": result.get("total_messages"),
                "auto_extract_triggered": result.get("auto_extract_triggered", False)
            },
            "timestamp": datetime.datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update conversation: {str(e)}")


# WebSocket endpoint for Gemini Live
@app.websocket("/gemini-live")
async def gemini_live_websocket(websocket: WebSocket):
    """WebSocket endpoint for Gemini Live chat with voice notification support.
    
    Args:
        websocket: WebSocket connection.
    """
    try:
        # Add connection to manager for voice notification broadcasting
        websocket_manager.add_connection(websocket)
        logger.info("WebSocket connection added to manager")
        
        # Handle Gemini Live websocket
        await gemini_service.handle_websocket_connection(websocket)
        
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close(code=4002, reason="Internal server error")
        except Exception:
            pass  # WebSocket might already be closed
    finally:
        # Remove connection from manager
        websocket_manager.remove_connection(websocket)
        logger.info("WebSocket connection removed from manager")


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return {"error": "Endpoint not found", "status_code": 404}


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    return {"error": "Internal server error", "status_code": 500}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
