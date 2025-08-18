package com.example.geminilivedemo

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import android.os.PowerManager
import android.util.Log
import androidx.core.app.NotificationCompat
import kotlinx.coroutines.*

class GeminiListeningService : Service() {
    
    companion object {
        const val CHANNEL_ID = "GeminiListeningChannel"
        const val NOTIFICATION_ID = 1
        const val ACTION_START_LISTENING = "START_LISTENING"
        const val ACTION_STOP_LISTENING = "STOP_LISTENING"
        const val ACTION_TOGGLE_LISTENING = "TOGGLE_LISTENING"
        const val ACTION_PAUSE_LISTENING = "PAUSE_LISTENING"
        const val ACTION_RESUME_LISTENING = "RESUME_LISTENING"
        const val ACTION_DISCONNECT_WEBSOCKET = "DISCONNECT_WEBSOCKET"
    }
    
    private var isListening = false
    private var isPaused = false  // New flag for pause state
    private var isPlayingResponse = false  // Keep for simple pause logic
    private var wakeLock: PowerManager.WakeLock? = null
    private var webSocketManager: WebSocketManager? = null
    private var notificationManager: NotificationManager? = null
    private var audioManager: AudioManager? = null
    private var voiceNotificationWebSocketManager: VoiceNotificationWebSocketManager? = null
    
    private val serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    override fun onCreate() {
        super.onCreate()
        Log.d("GeminiService", "Service created")
        
        createNotificationChannel()
        
        // Initialize AudioManager
        audioManager = AudioManager(this)
        audioManager?.setCallback(object : AudioManager.AudioManagerCallback {
            override fun onAudioChunkReady(base64Audio: String) {
                // Send audio chunks via WebSocket
                webSocketManager?.sendAudioChunk(base64Audio)
                Log.d("GeminiService", "Sending audio chunk via WebSocket")
            }
            
            override fun onAudioRecordingStarted() {
                Log.d("GeminiService", "Audio recording started")
            }
            
            override fun onAudioRecordingStopped() {
                Log.d("GeminiService", "Audio recording stopped")
            }
            
            override fun onAudioPlaybackStarted() {
                Log.d("GeminiService", "AI audio playback started")
                isPlayingResponse = true
            }
            
            override fun onAudioPlaybackStopped() {
                Log.d("GeminiService", "AI audio playback stopped")
                isPlayingResponse = false
            }
        })
        
        // Initialize WebSocket connection only if not paused
        if (!isPaused) {
            initializeWebSocket()
        }
        
        // Acquire wake lock to prevent CPU sleep
        val powerManager = getSystemService(Context.POWER_SERVICE) as PowerManager
        wakeLock = powerManager.newWakeLock(
            PowerManager.PARTIAL_WAKE_LOCK,
            "GeminiDemo:ListeningWakeLock"
        )
        wakeLock?.acquire()
        
        notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START_LISTENING -> startListening()
            ACTION_STOP_LISTENING -> stopListening()
            ACTION_TOGGLE_LISTENING -> toggleListening()
            ACTION_PAUSE_LISTENING -> pauseListening()
            ACTION_RESUME_LISTENING -> resumeListening()
            ACTION_DISCONNECT_WEBSOCKET -> disconnectWebSocket()
        }
        
        val notification = createNotification(isListening && !isPaused)
        startForeground(NOTIFICATION_ID, notification)
        
        return START_STICKY // Service will be restarted if killed
    }
    
    override fun onBind(intent: Intent?): IBinder? = null
    
    override fun onDestroy() {
        super.onDestroy()
        Log.d("GeminiService", "Service destroyed")
        
        stopListening()
        wakeLock?.release()
        
        // Only disconnect WebSocket if no audio is currently playing or queued
        if (audioManager?.hasAudioToPlay() == true) {
            Log.d("GeminiService", "Audio is playing or queued, keeping WebSocket alive")
        } else {
            Log.d("GeminiService", "No audio to play, disconnecting WebSocket")
            webSocketManager?.disconnect()
        }
        
        audioManager?.cleanup()
        serviceScope.cancel()
    }
    
    private fun initializeWebSocket() {
        Log.d("GeminiService", "Initializing WebSocket connection...")
        webSocketManager = WebSocketManager()
        
        // Initialize voice notification manager
        voiceNotificationWebSocketManager = VoiceNotificationWebSocketManager(webSocketManager!!)
        
        // Setup voice notification callbacks
        voiceNotificationWebSocketManager?.setCallback(object : VoiceNotificationWebSocketManager.VoiceNotificationWebSocketCallback {
            override fun onVoiceNotificationReceived(voiceData: VoiceNotificationData) {
                Log.d("GeminiService", "Voice notification received in background service: ${voiceData.notificationText}")
                
                // Pause recording to prevent feedback
                Log.d("GeminiService", "Pausing recording for voice notification")
                audioManager?.pauseRecordingForVoiceNotification()
                
                voiceData.audioBase64?.let { audioBase64 ->
                    Log.d("GeminiService", "Playing voice notification audio")
                    audioManager?.ingestAudioChunkToPlay(audioBase64)
                    
                    // Calculate estimated playback duration based on audio data length
                    val estimatedDurationMs = (audioBase64.length / 1000L + 2) * 1000L
                    val duration = estimatedDurationMs.coerceAtLeast(3000L).coerceAtMost(10000L)
                    
                    Log.d("GeminiService", "Estimated voice notification duration: ${duration}ms")
                    
                    // Resume recording after estimated playback time
                    serviceScope.launch {
                        delay(duration)
                        Log.d("GeminiService", "Resuming recording after voice notification")
                        audioManager?.resumeRecordingAfterVoiceNotification()
                    }
                }
            }
            
            override fun onVoiceNotificationError(error: String) {
                Log.e("GeminiService", "Voice notification error in background service: $error")
                // Resume recording in case of error
                Log.d("GeminiService", "Resuming recording due to voice notification error")
                audioManager?.resumeRecordingAfterVoiceNotification()
            }
        })
        
        webSocketManager?.setCallback(object : WebSocketManager.WebSocketCallback {
            override fun onConnected() {
                Log.d("GeminiService", "WebSocket connected successfully - ready for audio")
            }
            
            override fun onDisconnected() {
                Log.d("GeminiService", "WebSocket disconnected")
            }
            
            override fun onError(exception: Exception?) {
                Log.e("GeminiService", "WebSocket error: ${exception?.message}")
                // Auto-retry connection on error
                if (!isPaused) {
                    Log.d("GeminiService", "Retrying WebSocket connection in 2 seconds...")
                    serviceScope.launch {
                        delay(2000)
                        if (!isPaused) {
                            initializeWebSocket()
                        }
                    }
                }
            }
            
            override fun onMessageReceived(response: Response) {
                Log.d("GeminiService", "AI response received")
                response.text?.let { text ->
                    Log.d("GeminiService", "AI text response: $text")
                }
                response.audioData?.let { audioData ->
                    Log.d("GeminiService", "AI audio response received, playing audio")
                    // Actually play the audio using AudioManager
                    audioManager?.ingestAudioChunkToPlay(audioData)
                }
                
                // Handle voice notification responses through VoiceNotificationWebSocketManager
                response.voiceNotificationData?.let { voiceData ->
                    Log.d("GeminiService", "Received voice notification, delegating to VoiceNotificationWebSocketManager")
                    voiceNotificationWebSocketManager?.handleVoiceNotificationResponse(response)
                }
            }
        })
        webSocketManager?.connect()
    }
    
    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Gemini AI Listening",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Background AI voice assistant"
                setSound(null, null)
                enableVibration(false)
            }
            
            val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            manager.createNotificationChannel(channel)
        }
    }
    
    private fun createNotification(listening: Boolean): Notification {
        val intent = Intent(this, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent, 
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        val toggleIntent = Intent(this, GeminiListeningService::class.java).apply {
            action = ACTION_TOGGLE_LISTENING
        }
        val togglePendingIntent = PendingIntent.getService(
            this, 1, toggleIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        val stopIntent = Intent(this, GeminiListeningService::class.java).apply {
            action = ACTION_STOP_LISTENING
        }
        val stopPendingIntent = PendingIntent.getService(
            this, 2, stopIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        val statusText = if (listening) "🎤 Đang lắng nghe..." else "⏸️ Đã tạm dừng"
        val toggleText = if (listening) "Tạm dừng" else "Bắt đầu"
        
        // Show different status if paused by app
        val finalStatusText = if (isPaused) "📱 App đang hoạt động" else statusText
        
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Gemini AI Assistant")
            .setContentText(finalStatusText)
            .setSmallIcon(R.drawable.ic_mic)
            .setContentIntent(pendingIntent)
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .addAction(
                R.drawable.ic_mic,
                toggleText,
                togglePendingIntent
            )
            .addAction(
                R.drawable.ic_stop,
                "Dừng",
                stopPendingIntent
            )
            .build()
    }
    
    private fun startListening() {
        if (isListening || isPaused) return
        
        Log.d("GeminiService", "Starting listening with AudioManager")
        
        try {
            // Use AudioManager instead of direct AudioRecord
            audioManager?.startAudioInput()
            isListening = true
            
            updateNotification()
            Log.d("GeminiService", "Listening started successfully with AudioManager")
        } catch (e: Exception) {
            Log.e("GeminiService", "Error starting listening with AudioManager", e)
        }
    }
    
    private fun stopListening() {
        if (!isListening) return
        
        Log.d("GeminiService", "Stopping listening")
        
        isListening = false
        
        // Use AudioManager to stop
        audioManager?.stopAudioInput()
        
        updateNotification()
        Log.d("GeminiService", "Listening stopped")
    }
    
    private fun toggleListening() {
        if (isPaused) {
            Log.d("GeminiService", "Service is paused by app, cannot toggle")
            return
        }
        
        if (isListening) {
            stopListening()
        } else {
            startListening()
        }
    }
    
    private fun pauseListening() {
        Log.d("GeminiService", "Pausing service listening (app in foreground)")
        isPaused = true
        
        // Stop current listening immediately
        if (isListening) {
            Log.d("GeminiService", "Stopping current listening...")
            stopListening()
        }
        
        // Keep WebSocket connected to allow AI to continue playing audio
        // Only disconnect if we're truly going to background
        Log.d("GeminiService", "Keeping WebSocket connected for audio continuity")
        
        Log.d("GeminiService", "Service paused successfully (WebSocket kept alive)")
        updateNotification()
    }
    
    private fun resumeListening() {
        Log.d("GeminiService", "Resuming service listening (app in background)")
        isPaused = false
        
        // Start listening immediately, WebSocket will connect in parallel
        updateNotification()
        
        // Only initialize WebSocket if it doesn't exist
        if (webSocketManager == null) {
            Log.d("GeminiService", "Initializing WebSocket...")
            initializeWebSocket()
        } else {
            Log.d("GeminiService", "WebSocket already exists, reusing existing connection")
        }
        
        // Start audio input immediately - it can handle the case where WebSocket isn't ready yet
        serviceScope.launch {
            delay(800) // Reduced delay for faster response
            if (!isPaused && !isListening) {
                Log.d("GeminiService", "Starting audio input...")
                startListening()
            }
        }
    }
    
    private fun updateNotification() {
        val notification = createNotification(isListening && !isPaused)
        notificationManager?.notify(NOTIFICATION_ID, notification)
    }
    
    private fun disconnectWebSocket() {
        Log.d("GeminiService", "Disconnecting WebSocket (app going to background)")
        
        // Only disconnect if no audio is playing or queued
        if (audioManager?.hasAudioToPlay() == true) {
            Log.d("GeminiService", "Audio is playing or queued, keeping WebSocket alive for audio completion")
            return
        }
        
        // Disconnect WebSocket to save resources when app is truly in background
        webSocketManager?.disconnect()
        webSocketManager = null
        
        Log.d("GeminiService", "WebSocket disconnected successfully")
    }
}
