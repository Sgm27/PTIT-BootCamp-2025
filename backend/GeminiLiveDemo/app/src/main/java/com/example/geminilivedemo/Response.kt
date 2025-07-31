package com.example.geminilivedemo

import org.json.JSONObject
import org.json.JSONArray

class Response(data: JSONObject) {
    var text: String? = null
    var audioData: String? = null
    var notifications: List<Notification>? = null
    var notificationResponse: String? = null

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
}
