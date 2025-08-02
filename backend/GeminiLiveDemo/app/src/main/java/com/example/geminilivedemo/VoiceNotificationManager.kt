package com.example.geminilivedemo

import android.content.Context
import android.util.Base64
import android.util.Log
import kotlinx.coroutines.*
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException

/**
 * Manager for handling voice notifications via HTTP API
 */
class VoiceNotificationManager(private val context: Context) {
    
    interface VoiceNotificationCallback {
        fun onVoiceNotificationGenerated(voiceData: VoiceNotificationData)
        fun onVoiceNotificationError(error: String)
    }
    
    private val client = OkHttpClient()
    private var callback: VoiceNotificationCallback? = null
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    fun setCallback(callback: VoiceNotificationCallback) {
        this.callback = callback
    }
    
    /**
     * Generate voice notification using the HTTP API
     */
    fun generateVoiceNotification(text: String, type: String = "info") {
        scope.launch {
            try {
                Log.d("VoiceNotificationManager", "Generating voice notification for: $text")
                
                // Prepare request body
                val requestBody = JSONObject().apply {
                    put("text", text)
                    put("type", type)
                }
                
                val request = Request.Builder()
                    .url(Constants.VOICE_NOTIFICATION_API)
                    .post(requestBody.toString().toRequestBody("application/json".toMediaType()))
                    .build()
                
                // Use synchronous call within coroutine
                val response = client.newCall(request).execute()
                response.use { res ->
                    if (res.isSuccessful) {
                        val responseBody = res.body?.string()
                        if (responseBody != null) {
                            try {
                                val jsonResponse = JSONObject(responseBody)
                                val voiceData = parseVoiceNotificationResponse(jsonResponse)
                                
                                if (voiceData != null && voiceData.success && voiceData.audioBase64 != null) {
                                    Log.d("VoiceNotificationManager", "Voice notification generated successfully")
                                    withContext(Dispatchers.Main) {
                                        callback?.onVoiceNotificationGenerated(voiceData)
                                    }
                                } else {
                                    val errorMsg = voiceData?.message ?: "Unknown error"
                                    Log.e("VoiceNotificationManager", "Voice generation failed: $errorMsg")
                                    withContext(Dispatchers.Main) {
                                        callback?.onVoiceNotificationError("Voice generation failed: $errorMsg")
                                    }
                                }
                            } catch (e: Exception) {
                                Log.e("VoiceNotificationManager", "Error parsing response: ${e.message}")
                                withContext(Dispatchers.Main) {
                                    callback?.onVoiceNotificationError("Error parsing response: ${e.message}")
                                }
                            }
                        } else {
                            Log.e("VoiceNotificationManager", "Empty response body")
                            withContext(Dispatchers.Main) {
                                callback?.onVoiceNotificationError("Empty response from server")
                            }
                        }
                    } else {
                        Log.e("VoiceNotificationManager", "API request failed with code: ${res.code}")
                        withContext(Dispatchers.Main) {
                            callback?.onVoiceNotificationError("API request failed with code: ${res.code}")
                        }
                    }
                }
                
            } catch (e: Exception) {
                Log.e("VoiceNotificationManager", "Error generating voice notification: ${e.message}")
                withContext(Dispatchers.Main) {
                    callback?.onVoiceNotificationError("Error generating voice notification: ${e.message}")
                }
            }
        }
    }
    
    /**
     * Generate emergency voice notification
     */
    fun generateEmergencyVoiceNotification(text: String) {
        generateVoiceNotification(text, "emergency")
    }
    
    /**
     * Parse voice notification response from JSON
     */
    private fun parseVoiceNotificationResponse(data: JSONObject): VoiceNotificationData? {
        return try {
            // Backend returns nested structure: { success: true, message: "", notificationText: "", audioBase64: "", ... }
            VoiceNotificationData(
                success = data.optBoolean("success", false),
                message = data.optString("message", ""),
                notificationText = data.optString("notificationText", ""),
                audioBase64 = data.optString("audioBase64"),
                audioFormat = data.optString("audioFormat", "audio/pcm"),
                timestamp = data.optString("timestamp", ""),
                service = data.optString("service", "notification_voice_service")
            )
        } catch (e: Exception) {
            Log.e("VoiceNotificationManager", "Error parsing voice notification response: ${e.message}")
            null
        }
    }
    
    /**
     * Clean up resources
     */
    fun cleanup() {
        scope.cancel()
    }
}
