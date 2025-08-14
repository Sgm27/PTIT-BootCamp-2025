"""
API Models for the Healthcare Assistant
"""
from typing import Optional, List
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

# Conversation API Models
class ConversationCreateRequest(BaseModel):
    """Request model for creating new conversation"""
    user_id: str
    session_id: Optional[str] = None
    title: Optional[str] = None

class ConversationListResponse(BaseModel):
    """Response model for conversation list"""
    conversations: List[dict]
    total_count: int
    
class ConversationDetailResponse(BaseModel):
    """Response model for conversation detail"""
    conversation: dict
    messages: List[dict]
    
class MessageCreateRequest(BaseModel):
    """Request model for adding message to conversation"""
    conversation_id: str
    role: str  # user, assistant, system
    content: str
    has_audio: bool = False
    audio_file_path: Optional[str] = None

# Memoir API Models
class MemoirListResponse(BaseModel):
    """Response model for memoir list"""
    memoirs: List[dict]
    total_count: int
    categories: List[str]
    people: List[str]
    places: List[str]

class MemoirDetailResponse(BaseModel):
    """Response model for memoir detail"""
    memoir: dict
    
class MemoirSearchRequest(BaseModel):
    """Request model for searching memoirs"""
    query: Optional[str] = None
    categories: Optional[List[str]] = None
    time_period: Optional[str] = None
    emotional_tone: Optional[str] = None
    limit: int = 20

class MemoirExportRequest(BaseModel):
    """Request model for exporting memoirs"""
    format_type: str = "text"  # text, json, html
    user_id: str

# User profile requests
class UserStatsResponse(BaseModel):
    """Response model for user statistics"""
    conversation_stats: dict
    memoir_stats: dict
    user_info: dict

class ProfileUpdateRequest(BaseModel):
    """Request model for updating user profile"""
    full_name: str
    email: str
    phone: str
    address: str
    date_of_birth: str = None
    gender: str = None
