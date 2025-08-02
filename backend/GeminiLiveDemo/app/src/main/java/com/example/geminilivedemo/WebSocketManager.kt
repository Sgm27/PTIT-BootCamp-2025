package com.example.geminilivedemo

import android.util.Log
import android.widget.Toast
import org.java_websocket.client.WebSocketClient
import org.java_websocket.handshake.ServerHandshake
import org.json.JSONObject
import java.net.URI

class WebSocketManager {
    
    interface WebSocketCallback {
        fun onConnected()
        fun onDisconnected()
        fun onError(exception: Exception?)
                fun onMessageReceived(response: Response)
    }
    
    private var callback: WebSocketCallback? = null
    private var webSocket: WebSocketClient? = null
    private var isConnected = false
    private var shouldReconnect = true
    private val maxReconnectAttempts = 5
    private var reconnectAttempts = 0
    
    fun setCallback(callback: WebSocketCallback) {
        this.callback = callback
    }
    
    fun isConnected(): Boolean {
        return isConnected && webSocket?.isOpen == true
    }
    
    fun connect() {
        Log.d("WebSocketManager", "Connecting to: ${Constants.URL}")
        shouldReconnect = true
        reconnectAttempts = 0
        connectWebSocket()
    }
    
    private fun connectWebSocket() {
        try {
            webSocket?.close()
            webSocket = object : WebSocketClient(URI(Constants.URL)) {
                override fun onOpen(handshakedata: ServerHandshake?) {
                    Log.d("WebSocketManager", "Connected - Instance: ${this@WebSocketManager.hashCode()}")
                    isConnected = true
                    reconnectAttempts = 0
                    callback?.onConnected()
                    sendInitialSetupMessage()
                }

                override fun onMessage(message: String?) {
                    Log.d("WebSocketManager", "Message Received: $message")
                    receiveMessage(message)
                }

                override fun onClose(code: Int, reason: String?, remote: Boolean) {
                    Log.d("WebSocketManager", "Connection Closed: code=$code, reason=$reason, remote=$remote")
                    isConnected = false
                    callback?.onDisconnected()
                    
                    // Only auto-reconnect if shouldReconnect is true, within retry limit, and not a normal close
                    if (shouldReconnect && reconnectAttempts < maxReconnectAttempts && code != 1000) {
                        reconnectAttempts++
                        Log.d("WebSocketManager", "Attempting reconnection $reconnectAttempts/$maxReconnectAttempts (code: $code)")
                        
                        // Wait a bit before reconnecting
                        android.os.Handler(android.os.Looper.getMainLooper()).postDelayed({
                            if (shouldReconnect) {
                                connectWebSocket()
                            }
                        }, 2000) // 2 second delay
                    } else {
                        if (code == 1000) {
                            Log.d("WebSocketManager", "Normal connection close, no reconnection needed")
                        } else {
                            Log.w("WebSocketManager", "Max reconnection attempts reached or reconnection disabled")
                        }
                    }
                }

                override fun onError(ex: Exception?) {
                    Log.e("WebSocketManager", "Error: ${ex?.message}", ex)
                    isConnected = false
                    callback?.onError(ex)
                }
            }
            webSocket?.connect()
        } catch (e: Exception) {
            Log.e("WebSocketManager", "Failed to create WebSocket connection", e)
        }
    }
    
    private fun sendInitialSetupMessage() {
        Log.d("WebSocketManager", "Sending initial setup message")
        val setupMessage = JSONObject()
        val setup = JSONObject()
        val generationConfig = JSONObject()
        val responseModalities = org.json.JSONArray()
        responseModalities.put("AUDIO")
        generationConfig.put("response_modalities", responseModalities)
        setup.put("generation_config", generationConfig)
        setupMessage.put("setup", setup)
        webSocket?.send(setupMessage.toString())
    }
    
    fun sendVoiceMessage(b64PCM: String?, currentFrameB64: String? = null) {
        if (webSocket?.isOpen == false) {
            Log.d("WebSocketManager", "websocket not open")
            return
        }
        
        // Allow sending if we have either audio OR image
        if (b64PCM == null && currentFrameB64 == null) {
            Log.d("WebSocketManager", "No audio or image data to send")
            return
        }

        Log.d("WebSocketManager", "Sending message - Audio: ${b64PCM != null}, Image: ${currentFrameB64 != null}")

        val payload = JSONObject()
        val realtimeInput = JSONObject()
        val mediaChunks = org.json.JSONArray()
        
        // Add audio chunk if available
        b64PCM?.let { audioData ->
            val audioChunk = JSONObject()
            audioChunk.put("mime_type", "audio/pcm")
            audioChunk.put("data", audioData)
            mediaChunks.put(audioChunk)
            Log.d("WebSocketManager", "Added audio chunk")
        }

        // Add image chunk if available
        currentFrameB64?.let { imageData ->
            val imageChunk = JSONObject()
            imageChunk.put("mime_type", "image/jpeg")
            imageChunk.put("data", imageData)
            mediaChunks.put(imageChunk)
            Log.d("WebSocketManager", "Added image chunk, size: ${imageData.length}")
        }

        realtimeInput.put("media_chunks", mediaChunks)
        payload.put("realtime_input", realtimeInput)

        Log.d("WebSocketManager", "Sending payload with ${mediaChunks.length()} chunks")
        webSocket?.send(payload.toString())
    }
    
    fun sendEndOfStreamMessage() {
        if (webSocket?.isOpen == true) {
            val payload = JSONObject()
            val realtimeInput = JSONObject()
            val mediaChunks = org.json.JSONArray()
            realtimeInput.put("media_chunks", mediaChunks)
            payload.put("realtime_input", realtimeInput)
            payload.put("end_of_stream", true)
            webSocket?.send(payload.toString())
        }
    }
    
    private fun receiveMessage(message: String?) {
        if (message == null) return

        try {
            val messageData = JSONObject(message)
            
            // Check if this is a voice notification broadcast
            val messageType = messageData.optString("type", "")
            if (messageType == "voice_notification_response") {
                Log.d("WebSocketManager", "Received voice notification broadcast")
                handleVoiceNotificationBroadcast(messageData)
                return
            }
            
            // Handle regular Gemini Live messages
            val response = Response(messageData)
            callback?.onMessageReceived(response)
            
        } catch (e: Exception) {
            Log.e("WebSocketManager", "Error parsing message: ${e.message}", e)
        }
    }
    
    private fun handleVoiceNotificationBroadcast(messageData: JSONObject) {
        try {
            val success = messageData.optBoolean("success", false)
            val data = messageData.optJSONObject("data")
            val isBroadcast = messageData.optBoolean("broadcast", false)
            
            if (success && data != null && isBroadcast) {
                Log.d("WebSocketManager", "Processing voice notification broadcast")
                
                // Extract voice notification data
                val notificationText = data.optString("notificationText", "")
                val audioBase64 = data.optString("audioBase64", "")
                val audioFormat = data.optString("audioFormat", "")
                val timestamp = data.optString("timestamp", "")
                val service = data.optString("service", "")
                
                Log.d("WebSocketManager", "Voice notification details:")
                Log.d("WebSocketManager", "  - Text: $notificationText")
                Log.d("WebSocketManager", "  - Format: $audioFormat")
                Log.d("WebSocketManager", "  - Service: $service")
                Log.d("WebSocketManager", "  - Timestamp: $timestamp")
                
                // Create a Response object for voice notification
                val voiceNotificationData = JSONObject()
                voiceNotificationData.put("type", "voice_notification")
                voiceNotificationData.put("notificationText", notificationText)
                voiceNotificationData.put("audioBase64", audioBase64)
                voiceNotificationData.put("audioFormat", audioFormat)
                voiceNotificationData.put("timestamp", timestamp)
                voiceNotificationData.put("service", service)
                voiceNotificationData.put("broadcast", true)
                
                val response = Response(voiceNotificationData)
                callback?.onMessageReceived(response)
                
                Log.d("WebSocketManager", "Voice notification broadcast handled successfully")
                
            } else {
                Log.w("WebSocketManager", "Invalid voice notification broadcast data")
            }
            
        } catch (e: Exception) {
            Log.e("WebSocketManager", "Error handling voice notification broadcast: ${e.message}", e)
        }
    }
    
    fun isWebSocketConnected(): Boolean = isConnected
    
    fun disconnect() {
        Log.d("WebSocketManager", "Disconnecting - Instance: ${this.hashCode()}")
        shouldReconnect = false // Disable auto-reconnect
        webSocket?.close()
        isConnected = false
    }
    
    fun requestNotifications() {
        if (webSocket?.isOpen == true) {
            Log.d("WebSocketManager", "Requesting notifications from server")
            val payload = JSONObject()
            val notificationRequest = JSONObject()
            notificationRequest.put("action", "get_notifications")
            notificationRequest.put("limit", 50)
            payload.put("notification_request", notificationRequest)
            webSocket?.send(payload.toString())
        } else {
            Log.w("WebSocketManager", "Cannot request notifications - WebSocket not connected")
        }
    }
    
    fun markNotificationAsRead(notificationId: String) {
        if (webSocket?.isOpen == true) {
            Log.d("WebSocketManager", "Marking notification as read: $notificationId")
            val payload = JSONObject()
            val notificationRequest = JSONObject()
            notificationRequest.put("action", "mark_read")
            notificationRequest.put("notification_id", notificationId)
            payload.put("notification_request", notificationRequest)
            webSocket?.send(payload.toString())
        }
    }
    
    fun sendAudioChunk(base64Audio: String) {
        sendVoiceMessage(base64Audio, null)
    }
    
    fun sendRawMessage(message: String) {
        if (webSocket?.isOpen == true) {
            Log.d("WebSocketManager", "Sending raw message: ${message.take(100)}...")
            webSocket?.send(message)
        } else {
            Log.w("WebSocketManager", "Cannot send raw message - WebSocket not connected")
        }
    }
}
