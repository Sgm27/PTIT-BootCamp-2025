package com.example.geminilivedemo

import android.util.Log
import org.json.JSONObject

/**
 * Manager for handling voice notification requests through WebSocket
 */
class VoiceNotificationWebSocketManager(private val webSocketManager: WebSocketManager) {
    
    interface VoiceNotificationWebSocketCallback {
        fun onVoiceNotificationReceived(voiceData: VoiceNotificationData)
        fun onVoiceNotificationError(error: String)
    }
    
    private var callback: VoiceNotificationWebSocketCallback? = null
    private var lastRequestTime = 0L
    private val requestCooldownMs = 1000L // 1 second cooldown between requests
    
    fun setCallback(callback: VoiceNotificationWebSocketCallback) {
        this.callback = callback
    }
    
    /**
     * Request voice notification generation through WebSocket
     */
    fun requestVoiceNotification(text: String, type: String = "info") {
        // Check cooldown to prevent duplicate requests
        val currentTime = System.currentTimeMillis()
        if (currentTime - lastRequestTime < requestCooldownMs) {
            Log.w("VoiceNotificationWebSocket", "Request cooldown active, ignoring duplicate request")
            return
        }
        lastRequestTime = currentTime
        
        if (!webSocketManager.isConnected()) {
            Log.w("VoiceNotificationWebSocket", "WebSocket not connected, cannot request voice notification")
            callback?.onVoiceNotificationError("WebSocket not connected")
            return
        }
        
        try {
            Log.d("VoiceNotificationWebSocket", "Requesting voice notification for: $text")
            
            val payload = JSONObject()
            val voiceNotificationRequest = JSONObject()
            voiceNotificationRequest.put("action", "generate_voice_notification")
            voiceNotificationRequest.put("text", text)
            voiceNotificationRequest.put("type", type)
            
            payload.put("voice_notification_request", voiceNotificationRequest)
            
            // Send through existing WebSocket connection
            webSocketManager.sendRawMessage(payload.toString())
            
        } catch (e: Exception) {
            Log.e("VoiceNotificationWebSocket", "Error sending voice notification request: ${e.message}")
            callback?.onVoiceNotificationError("Error sending request: ${e.message}")
        }
    }
    
    /**
     * Request emergency voice notification
     */
    fun requestEmergencyVoiceNotification(text: String) {
        requestVoiceNotification(text, "emergency")
    }
    
    /**
     * Handle voice notification response from WebSocket
     */
    fun handleVoiceNotificationResponse(response: Response) {
        response.voiceNotificationData?.let { voiceData ->
            Log.d("VoiceNotificationWebSocket", "Received voice notification response: ${voiceData.notificationText}")
            
            if (voiceData.success && voiceData.audioBase64 != null) {
                Log.d("VoiceNotificationWebSocket", "Voice notification generated successfully, calling callback")
                callback?.onVoiceNotificationReceived(voiceData)
            } else {
                Log.e("VoiceNotificationWebSocket", "Voice notification failed: ${voiceData.message}")
                callback?.onVoiceNotificationError("Voice notification failed: ${voiceData.message}")
            }
        }
    }
}
