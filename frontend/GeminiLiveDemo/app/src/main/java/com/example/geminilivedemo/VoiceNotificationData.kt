package com.example.geminilivedemo

/**
 * Data class for voice notification responses from the backend
 */
data class VoiceNotificationData(
    val success: Boolean,
    val message: String,
    val notificationText: String,
    val audioBase64: String?,
    val audioFormat: String,
    val timestamp: String,
    val service: String
)
