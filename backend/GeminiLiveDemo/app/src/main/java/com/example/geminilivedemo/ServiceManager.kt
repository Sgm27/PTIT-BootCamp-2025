package com.example.geminilivedemo

import android.content.Context
import android.content.Intent
import android.os.Build

class ServiceManager(private val context: Context) {
    
    fun startListeningService() {
        val intent = Intent(context, GeminiListeningService::class.java).apply {
            action = GeminiListeningService.ACTION_START_LISTENING
        }
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            context.startForegroundService(intent)
        } else {
            context.startService(intent)
        }
    }
    
    fun stopListeningService() {
        val intent = Intent(context, GeminiListeningService::class.java).apply {
            action = GeminiListeningService.ACTION_STOP_LISTENING
        }
        context.startService(intent)
    }
    
    fun toggleListeningService() {
        val intent = Intent(context, GeminiListeningService::class.java).apply {
            action = GeminiListeningService.ACTION_TOGGLE_LISTENING
        }
        context.startService(intent)
    }
    
    fun pauseListeningService() {
        val intent = Intent(context, GeminiListeningService::class.java).apply {
            action = GeminiListeningService.ACTION_PAUSE_LISTENING
        }
        context.startService(intent)
    }
    
    fun resumeListeningService() {
        val intent = Intent(context, GeminiListeningService::class.java).apply {
            action = GeminiListeningService.ACTION_RESUME_LISTENING
        }
        context.startService(intent)
    }
    
    fun stopService() {
        val intent = Intent(context, GeminiListeningService::class.java)
        context.stopService(intent)
    }
    
    fun disconnectWebSocket() {
        val intent = Intent(context, GeminiListeningService::class.java).apply {
            action = GeminiListeningService.ACTION_DISCONNECT_WEBSOCKET
        }
        context.startService(intent)
    }
}
