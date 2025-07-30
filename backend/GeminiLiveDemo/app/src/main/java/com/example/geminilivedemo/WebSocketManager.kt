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
    
    fun setCallback(callback: WebSocketCallback) {
        this.callback = callback
    }
    
    fun isConnected(): Boolean {
        return isConnected && webSocket?.isOpen == true
    }
    
    fun connect() {
        Log.d("WebSocketManager", "Connecting to: ${Constants.URL}")
        webSocket = object : WebSocketClient(URI(Constants.URL)) {
            override fun onOpen(handshakedata: ServerHandshake?) {
                Log.d("WebSocketManager", "Connected")
                isConnected = true
                callback?.onConnected()
                sendInitialSetupMessage()
            }

            override fun onMessage(message: String?) {
                Log.d("WebSocketManager", "Message Received: $message")
                receiveMessage(message)
            }

            override fun onClose(code: Int, reason: String?, remote: Boolean) {
                Log.d("WebSocketManager", "Connection Closed: $reason")
                isConnected = false
                callback?.onDisconnected()
            }

            override fun onError(ex: Exception?) {
                Log.e("WebSocketManager", "Error: ${ex?.message}")
                isConnected = false
                callback?.onError(ex)
            }
        }
        webSocket?.connect()
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

        val messageData = JSONObject(message)
        val response = Response(messageData)
        callback?.onMessageReceived(response)
    }
    
    fun isWebSocketConnected(): Boolean = isConnected
    
    fun disconnect() {
        webSocket?.close()
        isConnected = false
    }
}
