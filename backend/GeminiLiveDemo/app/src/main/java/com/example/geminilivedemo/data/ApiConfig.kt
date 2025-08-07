package com.example.geminilivedemo.data

object ApiConfig {
    
    // Environment Configuration
    private const val ENVIRONMENT = "production" // "development" | "production"
    
    // Production Configuration
    private const val PROD_BASE_URL = "https://backend-bootcamp.sonktx.online/"
    private const val PROD_WS_URL = "wss://backend-bootcamp.sonktx.online/ws/"
    
    // Development Configuration
    private const val DEV_BASE_URL = "http://13.216.164.63:8000/"
    private const val DEV_WS_URL = "ws://13.216.164.63:8000/ws/"
    
    // Local Development (for emulator/device testing)
    private const val LOCAL_BASE_URL = "http://10.0.2.2:8000/" // Emulator
    private const val LOCAL_WS_URL = "ws://10.0.2.2:8000/ws/"
    
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
    }
    
    // Database Configuration (for reference)
    object Database {
        const val HOST = "13.216.164.63"
        const val PORT = 5432
        const val NAME = "healthcare_ai"
    }
    
    // Environment Info
    fun getEnvironmentInfo(): String {
        return """
            Environment: $ENVIRONMENT
            API Base URL: $BASE_URL
            WebSocket URL: $WEBSOCKET_URL
            Database Host: ${Database.HOST}:${Database.PORT}
        """.trimIndent()
    }
    
    // Check if production
    fun isProduction(): Boolean = ENVIRONMENT == "production"
    
    // Check if development
    fun isDevelopment(): Boolean = ENVIRONMENT == "development"
    
    // Check if local
    fun isLocal(): Boolean = ENVIRONMENT == "local"
} 