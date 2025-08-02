package com.example.geminilivedemo

import org.json.JSONObject
import org.json.JSONArray

class Response(data: JSONObject) {
    var text: String? = null
    var audioData: String? = null
    var notifications: List<Notification>? = null
    var notificationResponse: String? = null
    var voiceNotificationData: VoiceNotificationData? = null

    init {
        if (data.has("text")) {
            text = data.getString("text")
        }

        if (data.has("audio")) {
            audioData = data.getString("audio")
        }
        
        // Handle notification responses
        if (data.has("type")) {
            val responseType = data.getString("type")
            when (responseType) {
                "notifications_response" -> {
                    if (data.has("notifications")) {
                        val notificationsArray = data.getJSONArray("notifications")
                        notifications = parseNotifications(notificationsArray)
                    }
                }
                "mark_read_response", "mark_all_read_response", "notification_created" -> {
                    notificationResponse = responseType
                }
                "voice_notification_response", "voice_notification" -> {
                    voiceNotificationData = parseVoiceNotificationResponse(data)
                }
            }
        }
    }
    
    private fun parseNotifications(notificationsArray: JSONArray): List<Notification> {
        val notificationList = mutableListOf<Notification>()
        for (i in 0 until notificationsArray.length()) {
            val notifJson = notificationsArray.getJSONObject(i)
            
            val notification = Notification(
                id = notifJson.getString("id"),
                title = notifJson.getString("title"),
                message = notifJson.getString("message"),
                type = NotificationType.valueOf(notifJson.getString("type").uppercase()),
                timestamp = notifJson.getLong("timestamp"),
                isRead = notifJson.getBoolean("isRead")
            )
            notificationList.add(notification)
        }
        return notificationList
    }
    
    private fun parseVoiceNotificationResponse(data: JSONObject): VoiceNotificationData? {
        return try {
            // Handle both direct voice notification data and nested data structure
            val isBroadcast = data.optBoolean("broadcast", false)
            
            if (data.has("data")) {
                // Nested structure from API response
                val responseData = data.getJSONObject("data")
                VoiceNotificationData(
                    success = data.optBoolean("success", false),
                    message = data.optString("message", ""),
                    notificationText = responseData.optString("notification_text", ""),
                    audioBase64 = responseData.optString("audio_base64"),
                    audioFormat = responseData.optString("audio_format", "audio/pcm"),
                    timestamp = responseData.optString("timestamp", ""),
                    service = responseData.optString("service", "notification_voice_service")
                )
            } else {
                // Direct structure from broadcast
                VoiceNotificationData(
                    success = true,
                    message = "Voice notification received",
                    notificationText = data.optString("notificationText", ""),
                    audioBase64 = data.optString("audioBase64"),
                    audioFormat = data.optString("audioFormat", "audio/pcm"),
                    timestamp = data.optString("timestamp", ""),
                    service = data.optString("service", "notification_voice_service")
                )
            }
        } catch (e: Exception) {
            android.util.Log.e("Response", "Error parsing voice notification response: ${e.message}")
            null
        }
    }
}
