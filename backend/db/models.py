"""
Database Models for Healthcare AI Application
Supporting elderly users and their family members
"""
import uuid
from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, DateTime, Text, Boolean, 
    ForeignKey, JSON, Enum, Float, Date, LargeBinary
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from db.db_config import Base

# Enums for better data integrity
class UserType(enum.Enum):
    ELDERLY = "elderly"        # Người già sử dụng app
    FAMILY_MEMBER = "family"   # Con cháu của người già

class RelationshipType(enum.Enum):
    CHILD = "child"           # Con
    GRANDCHILD = "grandchild" # Cháu
    SPOUSE = "spouse"         # Vợ/chồng
    SIBLING = "sibling"       # Anh/chị/em
    RELATIVE = "relative"     # Họ hàng khác
    CAREGIVER = "caregiver"   # Người chăm sóc

class NotificationType(enum.Enum):
    MEDICINE_REMINDER = "medicine_reminder"
    APPOINTMENT_REMINDER = "appointment_reminder"
    HEALTH_CHECK = "health_check"
    EMERGENCY = "emergency"
    CUSTOM = "custom"

class HealthStatus(enum.Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

class ConversationRole(enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

# User Models
class User(Base):
    """Base user model supporting both elderly users and family members"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_type = Column(Enum(UserType), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    phone = Column(String(20), unique=True, nullable=True)
    full_name = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)
    avatar_url = Column(Text, nullable=True)
    
    # Address information
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), default="Vietnam")
    
    # Account settings
    password_hash = Column(String(255), nullable=True)  # For authentication
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)
    
    # Preferences
    preferred_language = Column(String(10), default="vi")
    timezone = Column(String(50), default="Asia/Ho_Chi_Minh")
    notification_settings = Column(JSON, default={})
    
    # Relationships
    elderly_profiles = relationship("ElderlyProfile", back_populates="user", cascade="all, delete-orphan")
    family_profiles = relationship("FamilyProfile", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    health_records = relationship("HealthRecord", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

class ElderlyProfile(Base):
    """Extended profile for elderly users"""
    __tablename__ = "elderly_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Health information
    medical_conditions = Column(ARRAY(String), default=[])
    current_medications = Column(JSON, default={})
    allergies = Column(ARRAY(String), default=[])
    emergency_contact = Column(String(20), nullable=True)
    doctor_info = Column(JSON, default={})
    
    # Care preferences
    care_level = Column(String(20), default="independent")  # independent, assisted, supervised
    mobility_status = Column(String(20), nullable=True)
    cognitive_status = Column(String(20), nullable=True)
    
    # Emergency information
    emergency_contacts = Column(JSON, default=[])
    medical_insurance = Column(JSON, default={})
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="elderly_profiles")
    family_relationships = relationship("FamilyRelationship", foreign_keys="FamilyRelationship.elderly_id", back_populates="elderly_user")

class FamilyProfile(Base):
    """Extended profile for family members"""
    __tablename__ = "family_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Family member specific info
    occupation = Column(String(100), nullable=True)
    workplace = Column(String(255), nullable=True)
    
    # Care involvement
    is_primary_caregiver = Column(Boolean, default=False)
    care_responsibilities = Column(ARRAY(String), default=[])
    availability_schedule = Column(JSON, default={})
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="family_profiles")
    family_relationships = relationship("FamilyRelationship", foreign_keys="FamilyRelationship.family_member_id", back_populates="family_member")

class FamilyRelationship(Base):
    """Defines relationships between elderly users and family members"""
    __tablename__ = "family_relationships"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    elderly_id = Column(UUID(as_uuid=True), ForeignKey("elderly_profiles.id"), nullable=False)
    family_member_id = Column(UUID(as_uuid=True), ForeignKey("family_profiles.id"), nullable=False)
    relationship_type = Column(Enum(RelationshipType), nullable=False)
    
    # Permissions and access levels
    can_view_health_data = Column(Boolean, default=True)
    can_receive_notifications = Column(Boolean, default=True)
    can_manage_medications = Column(Boolean, default=False)
    can_schedule_appointments = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    elderly_user = relationship("ElderlyProfile", foreign_keys=[elderly_id], back_populates="family_relationships")
    family_member = relationship("FamilyProfile", foreign_keys=[family_member_id], back_populates="family_relationships")

# Conversation and Memory Models
class Conversation(Base):
    """Store all conversations with the AI assistant"""
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_id = Column(String(255), nullable=True)  # For WebSocket sessions
    
    title = Column(String(255), nullable=True)
    started_at = Column(DateTime, default=func.now())
    ended_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Conversation metadata
    total_messages = Column(Integer, default=0)
    conversation_summary = Column(Text, nullable=True)
    topics_discussed = Column(ARRAY(String), default=[])
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan")
    memoirs = relationship("LifeMemoir", back_populates="conversation")

class ConversationMessage(Base):
    """Individual messages within conversations"""
    __tablename__ = "conversation_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    
    role = Column(Enum(ConversationRole), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    
    # Message metadata
    message_order = Column(Integer, nullable=False)
    has_audio = Column(Boolean, default=False)
    audio_file_path = Column(String(500), nullable=True)
    processing_time_ms = Column(Float, nullable=True)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

class LifeMemoir(Base):
    """Extracted life stories and important memories"""
    __tablename__ = "life_memoirs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    date_of_memory = Column(Date, nullable=True)
    extracted_at = Column(DateTime, default=func.now())
    
    # Categorization
    categories = Column(ARRAY(String), default=[])  # e.g., ["family", "war", "work"]
    people_mentioned = Column(ARRAY(String), default=[])
    places_mentioned = Column(ARRAY(String), default=[])
    time_period = Column(String(50), nullable=True)  # e.g., "1960s", "childhood"
    
    # Quality metrics
    emotional_tone = Column(String(20), nullable=True)  # positive, negative, neutral, mixed
    importance_score = Column(Float, default=0.0)  # 0-1 scale
    
    # Relationships
    user = relationship("User")
    conversation = relationship("Conversation", back_populates="memoirs")

# Health and Medicine Models
class HealthRecord(Base):
    """Health data and monitoring records"""
    __tablename__ = "health_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    recorded_at = Column(DateTime, default=func.now())
    record_type = Column(String(50), nullable=False)  # vital_signs, symptom, medication, appointment
    
    # Vital signs
    blood_pressure_systolic = Column(Integer, nullable=True)
    blood_pressure_diastolic = Column(Integer, nullable=True)
    heart_rate = Column(Integer, nullable=True)
    temperature = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    blood_sugar = Column(Float, nullable=True)
    
    # General health data
    symptoms = Column(ARRAY(String), default=[])
    pain_level = Column(Integer, nullable=True)  # 1-10 scale
    mood = Column(String(20), nullable=True)
    energy_level = Column(String(20), nullable=True)
    sleep_quality = Column(String(20), nullable=True)
    appetite = Column(String(20), nullable=True)
    
    # Additional notes
    notes = Column(Text, nullable=True)
    recorded_by = Column(String(50), default="user")  # user, family, doctor, ai_assistant
    
    # Relationships
    user = relationship("User", back_populates="health_records")

class MedicineRecord(Base):
    """Medicine information and prescriptions"""
    __tablename__ = "medicine_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Medicine information
    medicine_name = Column(String(255), nullable=False)
    generic_name = Column(String(255), nullable=True)
    dosage = Column(String(100), nullable=False)
    frequency = Column(String(100), nullable=False)  # "2 times daily", "every 8 hours"
    
    # Schedule
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Instructions
    instructions = Column(Text, nullable=True)
    side_effects = Column(ARRAY(String), default=[])
    contraindications = Column(ARRAY(String), default=[])
    
    # Prescription details
    prescribed_by = Column(String(255), nullable=True)
    prescription_date = Column(Date, nullable=True)
    pharmacy = Column(String(255), nullable=True)
    
    # AI scan data
    scan_image_path = Column(String(500), nullable=True)
    scan_confidence = Column(Float, nullable=True)
    scan_result = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    medication_logs = relationship("MedicationLog", back_populates="medicine", cascade="all, delete-orphan")

class MedicationLog(Base):
    """Log of medication intake"""
    __tablename__ = "medication_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    medicine_id = Column(UUID(as_uuid=True), ForeignKey("medicine_records.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    scheduled_time = Column(DateTime, nullable=False)
    actual_time = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False)  # taken, missed, delayed, skipped
    
    # Additional info
    notes = Column(Text, nullable=True)
    side_effects_experienced = Column(ARRAY(String), default=[])
    logged_by = Column(String(50), default="user")  # user, family, caregiver
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    medicine = relationship("MedicineRecord", back_populates="medication_logs")
    user = relationship("User")

# Notification Models
class Notification(Base):
    """System notifications and reminders"""
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    notification_type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Scheduling
    scheduled_at = Column(DateTime, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    is_sent = Column(Boolean, default=False)
    is_read = Column(Boolean, default=False)
    
    # Voice notification
    has_voice = Column(Boolean, default=False)
    voice_file_path = Column(String(500), nullable=True)
    voice_generated_at = Column(DateTime, nullable=True)
    
    # Metadata
    priority = Column(String(10), default="normal")  # low, normal, high, urgent
    category = Column(String(50), nullable=True)
    related_record_id = Column(UUID(as_uuid=True), nullable=True)  # Link to medicine, appointment, etc.
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notifications")

# Session Management
class UserSession(Base):
    """Manage user sessions for WebSocket connections"""
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    session_handle = Column(String(255), nullable=False, unique=True)
    websocket_session_id = Column(String(255), nullable=True)
    
    started_at = Column(DateTime, default=func.now())
    last_activity = Column(DateTime, default=func.now())
    ended_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Session metadata
    device_info = Column(JSON, default={})
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User")

# System Configuration
class SystemSettings(Base):
    """System-wide configuration settings"""
    __tablename__ = "system_settings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    setting_key = Column(String(100), nullable=False, unique=True)
    setting_value = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    updated_by = Column(String(255), nullable=True)

# Audit Log
class AuditLog(Base):
    """System audit trail"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    action = Column(String(100), nullable=False)
    table_name = Column(String(100), nullable=True)
    record_id = Column(UUID(as_uuid=True), nullable=True)
    
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    
    timestamp = Column(DateTime, default=func.now())
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User") 