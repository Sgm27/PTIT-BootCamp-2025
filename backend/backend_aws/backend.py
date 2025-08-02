"""
AI Healthcare Assistant API - Restructured Backend
Main FastAPI application with separated services
"""
import datetime
import base64
from fastapi import FastAPI, WebSocket, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
from google import genai

# Import configurations
from config.settings import settings

# Import models
from models.api_models import MedicineScanRequest, TextExtractRequest, HealthResponse

# Import services
from services.medicine_service import MedicineService
from services.text_extraction_service import TextExtractionService
from services.gemini_service import GeminiService


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
            "gemini_service": "active"
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
            }
        },
        "configuration": {
            "openai_model_vision": settings.OPENAI_VISION_MODEL,
            "openai_model_text": settings.OPENAI_TEXT_MODEL,
            "gemini_model": settings.GEMINI_MODEL
        }
    }


# WebSocket endpoint for Gemini Live
@app.websocket("/gemini-live")
async def gemini_live_websocket(websocket: WebSocket):
    """WebSocket endpoint for Gemini Live chat.
    
    Args:
        websocket: WebSocket connection.
    """
    await gemini_service.handle_websocket_connection(websocket)


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
