package com.example.geminilivedemo.data

object ApiConfig {
    
    // Environment Configuration - Changed to production to use deployed backend
    private const val ENVIRONMENT = "production" // "development" | "production" | "local"
    
    // Production Configuration (Backend API deployed on domain)
    private const val PROD_BASE_URL = "https://backend-bootcamp.sonktx.online/"
    private const val PROD_WS_URL = "wss://backend-bootcamp.sonktx.online/gemini-live"
    
    // Development Configuration (Backend API on domain, not EC2 direct)
    private const val DEV_BASE_URL = "https://backend-bootcamp.sonktx.online/"
    private const val DEV_WS_URL = "wss://backend-bootcamp.sonktx.online/gemini-live"
    
    // Local Development (for emulator/device testing with local backend)
    private const val LOCAL_BASE_URL = "http://10.0.2.2:8000/" // Emulator
    private const val LOCAL_WS_URL = "ws://10.0.2.2:8000/gemini-live"
    
    // Current API Configuration
    val BASE_URL: String = when (ENVIRONMENT) {
        "production" -> PROD_BASE_URL
        "development" -> DEV_BASE_URL
        "local" -> LOCAL_BASE_URL
        else -> PROD_BASE_URL
    }
    
    val WEBSOCKET_URL: String = when (ENVIRONMENT) {
        "production" -> PROD_WS_URL
        "development" -> DEV_WS_URL
        "local" -> LOCAL_WS_URL
        else -> PROD_WS_URL
    }
    
    // API Endpoints
    object Endpoints {
        const val AUTH_LOGIN = "api/auth/login"
        const val AUTH_REGISTER = "api/auth/register"
        const val AUTH_PROFILE = "api/auth/profile/{user_id}"
        const val AUTH_CREATE_RELATIONSHIP = "api/auth/create-relationship"
        const val AUTH_FAMILY_MEMBERS = "api/auth/family-members/{elderly_user_id}"
        const val AUTH_ELDERLY_PATIENTS = "api/auth/elderly-patients/{family_user_id}"
        
        // Conversation endpoints
        const val CONVERSATIONS = "api/conversations/{user_id}"
        const val CONVERSATION_DETAIL = "api/conversations/{user_id}/{conversation_id}"
        const val CONVERSATION_SEARCH = "api/conversations/{user_id}/search"
        
        // Memoir endpoints
        const val MEMOIRS = "api/memoirs/{user_id}"
        const val MEMOIR_DETAIL = "api/memoirs/{user_id}/{memoir_id}"
        const val MEMOIR_SEARCH = "api/memoirs/{user_id}/search"
        const val MEMOIR_TIMELINE = "api/memoirs/{user_id}/timeline"
        const val MEMOIR_EXPORT = "api/memoirs/{user_id}/export"
        
        // User stats
        const val USER_STATS = "api/users/{user_id}/stats"
        
        // Medicine analysis
        const val ANALYZE_MEDICINE = "api/analyze-medicine-gemini"
        
        // Voice notification
        const val VOICE_NOTIFICATION = "api/generate-voice-notification"
        
        // Schedule endpoints
        const val CREATE_SCHEDULE = "api/schedules/create"
        const val GET_USER_SCHEDULES = "api/schedules/{user_id}"
        const val UPDATE_SCHEDULE = "api/schedules/{schedule_id}"
        const val DELETE_SCHEDULE = "api/schedules/{schedule_id}"
        const val MARK_SCHEDULE_COMPLETE = "api/schedules/{schedule_id}/complete"
    }
    
    // Database Configuration (EC2 AWS - chỉ dùng cho backend, không dùng trực tiếp từ Android)
    object Database {
        const val HOST = "13.215.139.225"  // EC2 AWS - chỉ backend connect
        const val PORT = 5432
        const val NAME = "healthcare_ai"
        const val USER = "postgres"
        const val PASSWORD = "postgres"
    }
    
    // Environment Info
    fun getEnvironmentInfo(): String {
        return """
            Environment: $ENVIRONMENT
            API Base URL: $BASE_URL
            WebSocket URL: $WEBSOCKET_URL
            Note: Database (${Database.HOST}:${Database.PORT}) chỉ backend kết nối trực tiếp
        """.trimIndent()
    }
    
    // Check if production
    fun isProduction(): Boolean = ENVIRONMENT == "production"
    
    // Check if development
    fun isDevelopment(): Boolean = ENVIRONMENT == "development"
    
    // Check if local
    fun isLocal(): Boolean = ENVIRONMENT == "local"
} 