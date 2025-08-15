"""
API Models for the Healthcare Assistant
"""
from typing import Optional
from pydantic import BaseModel


class MedicineScanRequest(BaseModel):
    """Request model for medicine scanning."""
    input: str  # Base64 string or URL


class TextExtractRequest(BaseModel):
    """Request model for text extraction."""
    text: str


class HealthResponse(BaseModel):
    """Standard response model for health-related endpoints."""
    success: bool
    result: str
    error: Optional[str] = None


class WebSocketMessage(BaseModel):
    """WebSocket message model."""
    type: str
    data: dict
