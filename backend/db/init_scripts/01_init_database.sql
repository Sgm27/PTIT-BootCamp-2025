-- Healthcare AI Database Initialization Script
-- This script sets up the PostgreSQL database with proper extensions and configurations

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Set up database encoding and locale
-- (This should already be set during database creation)

-- Create custom types for better data validation
DO $$ BEGIN
    -- User types
    CREATE TYPE user_type_enum AS ENUM ('elderly', 'family');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    -- Relationship types  
    CREATE TYPE relationship_type_enum AS ENUM ('child', 'grandchild', 'spouse', 'sibling', 'relative', 'caregiver');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    -- Notification types
    CREATE TYPE notification_type_enum AS ENUM ('medicine_reminder', 'appointment_reminder', 'health_check', 'emergency', 'custom');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    -- Health status
    CREATE TYPE health_status_enum AS ENUM ('excellent', 'good', 'fair', 'poor');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    -- Conversation roles
    CREATE TYPE conversation_role_enum AS ENUM ('user', 'assistant', 'system');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create indexes for better performance (will be created automatically by SQLAlchemy)
-- But we can add some custom ones here for optimization

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to generate session handles
CREATE OR REPLACE FUNCTION generate_session_handle()
RETURNS TEXT AS $$
BEGIN
    RETURN encode(gen_random_bytes(32), 'base64');
END;
$$ language 'plpgsql';

-- Function for full text search on Vietnamese text
CREATE OR REPLACE FUNCTION vietnamese_unaccent(text)
RETURNS TEXT AS $$
BEGIN
    -- This is a simplified version - you might want to enhance it
    -- for better Vietnamese text handling
    RETURN lower(unaccent($1));
END;
$$ language 'plpgsql' IMMUTABLE;

-- Create a function to check user permissions
CREATE OR REPLACE FUNCTION check_family_permission(
    p_elderly_user_id UUID,
    p_family_member_id UUID,
    p_permission_type TEXT
) RETURNS BOOLEAN AS $$
DECLARE
    has_permission BOOLEAN := FALSE;
BEGIN
    SELECT 
        CASE 
            WHEN p_permission_type = 'view_health' THEN fr.can_view_health_data
            WHEN p_permission_type = 'receive_notifications' THEN fr.can_receive_notifications
            WHEN p_permission_type = 'manage_medications' THEN fr.can_manage_medications
            WHEN p_permission_type = 'schedule_appointments' THEN fr.can_schedule_appointments
            ELSE FALSE
        END INTO has_permission
    FROM family_relationships fr
    JOIN elderly_profiles ep ON fr.elderly_id = ep.id
    JOIN family_profiles fp ON fr.family_member_id = fp.id
    WHERE ep.user_id = p_elderly_user_id 
    AND fp.user_id = p_family_member_id
    AND fr.is_active = TRUE;
    
    RETURN COALESCE(has_permission, FALSE);
END;
$$ language 'plpgsql';

-- Drop tables if exist to ensure clean init
-- BEGIN CLEAN INIT SECTION
-- Drop dependent views first
DROP VIEW IF EXISTS user_summary CASCADE;
DROP VIEW IF EXISTS active_sessions CASCADE;
DROP VIEW IF EXISTS health_alerts CASCADE;

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS system_settings CASCADE;
DROP TABLE IF EXISTS user_sessions CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS medication_logs CASCADE;
DROP TABLE IF EXISTS medicine_records CASCADE;
DROP TABLE IF EXISTS health_records CASCADE;
DROP TABLE IF EXISTS life_memoirs CASCADE;
DROP TABLE IF EXISTS conversation_messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS family_relationships CASCADE;
DROP TABLE IF EXISTS family_profiles CASCADE;
DROP TABLE IF EXISTS elderly_profiles CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create tables

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_type user_type_enum NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(10),
    avatar_url TEXT,
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100) DEFAULT 'Vietnam',
    password_hash VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    preferred_language VARCHAR(10) DEFAULT 'vi',
    timezone VARCHAR(50) DEFAULT 'Asia/Ho_Chi_Minh',
    notification_settings JSON DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS elderly_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    medical_conditions TEXT[],
    current_medications JSON DEFAULT '{}',
    allergies TEXT[],
    emergency_contact VARCHAR(20),
    doctor_info JSON DEFAULT '{}',
    care_level VARCHAR(20) DEFAULT 'independent',
    mobility_status VARCHAR(20),
    cognitive_status VARCHAR(20),
    emergency_contacts JSON DEFAULT '[]',
    medical_insurance JSON DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS family_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    occupation VARCHAR(100),
    workplace VARCHAR(255),
    is_primary_caregiver BOOLEAN DEFAULT FALSE,
    care_responsibilities TEXT[],
    availability_schedule JSON DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS family_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    elderly_id UUID REFERENCES elderly_profiles(id) ON DELETE CASCADE,
    family_member_id UUID REFERENCES family_profiles(id) ON DELETE CASCADE,
    relationship_type relationship_type_enum NOT NULL,
    can_view_health_data BOOLEAN DEFAULT TRUE,
    can_receive_notifications BOOLEAN DEFAULT TRUE,
    can_manage_medications BOOLEAN DEFAULT FALSE,
    can_schedule_appointments BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255),
    title VARCHAR(255),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    total_messages INTEGER DEFAULT 0,
    conversation_summary TEXT,
    topics_discussed TEXT[]
);

CREATE TABLE IF NOT EXISTS conversation_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role conversation_role_enum NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_order INTEGER NOT NULL,
    has_audio BOOLEAN DEFAULT FALSE,
    audio_file_path VARCHAR(500),
    processing_time_ms FLOAT
);

CREATE TABLE IF NOT EXISTS life_memoirs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    date_of_memory DATE,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    categories TEXT[],
    people_mentioned TEXT[],
    places_mentioned TEXT[],
    time_period VARCHAR(50),
    emotional_tone VARCHAR(20),
    importance_score FLOAT DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS health_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    record_type VARCHAR(50) NOT NULL,
    blood_pressure_systolic INTEGER,
    blood_pressure_diastolic INTEGER,
    heart_rate INTEGER,
    temperature FLOAT,
    weight FLOAT,
    blood_sugar FLOAT,
    symptoms TEXT[],
    pain_level INTEGER,
    mood VARCHAR(20),
    energy_level VARCHAR(20),
    sleep_quality VARCHAR(20),
    appetite VARCHAR(20),
    notes TEXT,
    recorded_by VARCHAR(50) DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS medicine_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    medicine_name VARCHAR(255) NOT NULL,
    generic_name VARCHAR(255),
    dosage VARCHAR(100) NOT NULL,
    frequency VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    instructions TEXT,
    side_effects TEXT[],
    contraindications TEXT[],
    prescribed_by VARCHAR(255),
    prescription_date DATE,
    pharmacy VARCHAR(255),
    scan_image_path VARCHAR(500),
    scan_confidence FLOAT,
    scan_result JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS medication_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    medicine_id UUID REFERENCES medicine_records(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    scheduled_time TIMESTAMP NOT NULL,
    actual_time TIMESTAMP,
    status VARCHAR(20) NOT NULL,
    notes TEXT,
    side_effects_experienced TEXT[],
    logged_by VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    notification_type notification_type_enum NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    scheduled_at TIMESTAMP NOT NULL,
    sent_at TIMESTAMP,
    is_sent BOOLEAN DEFAULT FALSE,
    is_read BOOLEAN DEFAULT FALSE,
    has_voice BOOLEAN DEFAULT FALSE,
    voice_file_path VARCHAR(500),
    voice_generated_at TIMESTAMP,
    priority VARCHAR(10) DEFAULT 'normal',
    category VARCHAR(50),
    related_record_id UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_handle VARCHAR(255) NOT NULL UNIQUE,
    websocket_session_id VARCHAR(255),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    device_info JSON DEFAULT '{}',
    ip_address VARCHAR(45),
    user_agent TEXT
);

CREATE TABLE IF NOT EXISTS system_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    setting_key VARCHAR(100) NOT NULL UNIQUE,
    setting_value JSON NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(100),
    record_id UUID,
    old_values JSON,
    new_values JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT
);
-- END CLEAN INIT SECTION

-- Create system_settings table
INSERT INTO system_settings (setting_key, setting_value, description) VALUES
('app_version', '"1.0.0"', 'Current application version'),
('max_session_duration_hours', '24', 'Maximum session duration in hours'),
('notification_reminder_interval_minutes', '15', 'Default reminder interval for notifications'),
('health_alert_thresholds', '{"blood_pressure_high": {"systolic": 140, "diastolic": 90}, "blood_pressure_urgent": {"systolic": 180, "diastolic": 110}, "heart_rate_high": 100, "heart_rate_low": 60, "temperature_fever": 37.5, "temperature_high_fever": 38.5}', 'Health monitoring alert thresholds'),
('voice_notification_enabled', 'true', 'Enable voice notifications by default'),
('memoir_extraction_enabled', 'true', 'Enable automatic memoir extraction'),
('data_retention_days', '365', 'Number of days to retain old data')
ON CONFLICT (setting_key) DO NOTHING;

-- Create some useful views
CREATE OR REPLACE VIEW user_summary AS
SELECT 
    u.id,
    u.user_type,
    u.full_name,
    u.email,
    u.phone,
    u.created_at,
    u.last_login,
    u.is_active,
    CASE 
        WHEN u.user_type = 'elderly' THEN (
            SELECT json_build_object(
                'medical_conditions', ep.medical_conditions,
                'current_medications', ep.current_medications,
                'emergency_contact', ep.emergency_contact,
                'care_level', ep.care_level
            )
            FROM elderly_profiles ep WHERE ep.user_id = u.id
        )
        WHEN u.user_type = 'family' THEN (
            SELECT json_build_object(
                'occupation', fp.occupation,
                'is_primary_caregiver', fp.is_primary_caregiver,
                'care_responsibilities', fp.care_responsibilities
            )
            FROM family_profiles fp WHERE fp.user_id = u.id
        )
    END as profile_data
FROM users u;

-- Create view for active sessions
CREATE OR REPLACE VIEW active_sessions AS
SELECT 
    us.*,
    u.full_name as user_name,
    u.user_type
FROM user_sessions us
JOIN users u ON us.user_id = u.id
WHERE us.is_active = TRUE
AND us.last_activity > NOW() - INTERVAL '24 hours';

-- Create view for health alerts
CREATE OR REPLACE VIEW health_alerts AS
SELECT 
    hr.user_id,
    u.full_name,
    hr.recorded_at,
    hr.record_type,
    CASE 
        WHEN hr.blood_pressure_systolic >= 180 OR hr.blood_pressure_diastolic >= 110 
        THEN 'Urgent: High Blood Pressure'
        WHEN hr.blood_pressure_systolic >= 140 OR hr.blood_pressure_diastolic >= 90 
        THEN 'Warning: Elevated Blood Pressure'
        WHEN hr.heart_rate > 100 
        THEN 'Warning: High Heart Rate'
        WHEN hr.heart_rate < 60 
        THEN 'Warning: Low Heart Rate'
        WHEN hr.temperature >= 38.5 
        THEN 'Alert: High Fever'
        WHEN hr.temperature >= 37.5 
        THEN 'Warning: Fever'
        WHEN hr.blood_sugar > 250 
        THEN 'Urgent: Very High Blood Sugar'
        WHEN hr.blood_sugar < 70 
        THEN 'Urgent: Low Blood Sugar'
    END as alert_message,
    CASE 
        WHEN hr.blood_pressure_systolic >= 180 OR hr.blood_pressure_diastolic >= 110 
             OR hr.blood_sugar > 250 OR hr.blood_sugar < 70
        THEN 'urgent'
        WHEN hr.blood_pressure_systolic >= 140 OR hr.blood_pressure_diastolic >= 90 
             OR hr.heart_rate > 100 OR hr.heart_rate < 60 
             OR hr.temperature >= 37.5
        THEN 'warning'
        ELSE 'normal'
    END as severity
FROM health_records hr
JOIN users u ON hr.user_id = u.id
WHERE hr.recorded_at > NOW() - INTERVAL '7 days'
AND (
    hr.blood_pressure_systolic >= 140 OR hr.blood_pressure_diastolic >= 90 
    OR hr.heart_rate > 100 OR hr.heart_rate < 60
    OR hr.temperature >= 37.5
    OR hr.blood_sugar > 250 OR hr.blood_sugar < 70
);

-- Grant necessary permissions (adjust based on your user setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO healthcare_app;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO healthcare_app;

-- Create indexes for better performance
-- These will be created by SQLAlchemy, but we can add some custom ones

-- Index for conversation search
CREATE INDEX IF NOT EXISTS idx_conversation_messages_content_search 
ON conversation_messages USING gin(to_tsvector('english', content));

-- Index for memoir search  
CREATE INDEX IF NOT EXISTS idx_life_memoirs_content_search 
ON life_memoirs USING gin(to_tsvector('english', content));

-- Index for medicine search
CREATE INDEX IF NOT EXISTS idx_medicine_records_name_search 
ON medicine_records USING gin(to_tsvector('english', medicine_name));

-- Index for health records by date and user
CREATE INDEX IF NOT EXISTS idx_health_records_user_date 
ON health_records (user_id, recorded_at DESC);

-- Index for notifications by user and scheduled time
CREATE INDEX IF NOT EXISTS idx_notifications_user_scheduled 
ON notifications (user_id, scheduled_at, is_sent);

-- Index for active sessions
CREATE INDEX IF NOT EXISTS idx_user_sessions_active 
ON user_sessions (user_id, is_active, last_activity);

-- Success message
SELECT 'Healthcare AI Database initialized successfully!' as status; 