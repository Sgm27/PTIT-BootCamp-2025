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

-- Insert default system settings
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