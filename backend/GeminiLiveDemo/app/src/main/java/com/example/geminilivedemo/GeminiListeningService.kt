package com.example.geminilivedemo

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
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
    }
    
    private var audioRecord: AudioRecord? = null
    private var isListening = false
    private var wakeLock: PowerManager.WakeLock? = null
    private var webSocketManager: WebSocketManager? = null
    private var notificationManager: NotificationManager? = null
    private var audioManager: AudioManager? = null
    private var isAIPlaying = false
    private var appStateCheckJob: Job? = null
    
    private val serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    override fun onCreate() {
        super.onCreate()
        Log.d("GeminiService", "Service created")
        
        createNotificationChannel()
        
        // Initialize WebSocket connection
        webSocketManager = WebSocketManager()
        setupWebSocketCallbacks()
        // Chỉ kết nối WebSocket khi app ở background
        if (!MainActivity.isAppInForeground) {
            webSocketManager?.connect()
        }
        
        // Initialize AudioManager for handling AI playback state
        audioManager = AudioManager()
        setupAudioManagerCallbacks()
        
        // Acquire wake lock to prevent CPU sleep
        val powerManager = getSystemService(Context.POWER_SERVICE) as PowerManager
        wakeLock = powerManager.newWakeLock(
            PowerManager.PARTIAL_WAKE_LOCK,
            "GeminiDemo:ListeningWakeLock"
        )
        wakeLock?.acquire()
        
        notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        
        // Start monitoring app state
        startAppStateMonitoring()
    }
    
    private fun setupWebSocketCallbacks() {
        webSocketManager?.setCallback(object : WebSocketManager.WebSocketCallback {
            override fun onConnected() {
                Log.d("GeminiService", "WebSocket connected")
            }
            
            override fun onDisconnected() {
                Log.d("GeminiService", "WebSocket disconnected")
            }
            
            override fun onError(exception: Exception?) {
                Log.e("GeminiService", "WebSocket error: ${exception?.message}")
            }
            
            override fun onMessageReceived(response: Response) {
                // Handle audio response from AI - chỉ phát khi app không ở foreground
                response.audioData?.let { audioData ->
                    if (!MainActivity.isAppInForeground) {
                        audioManager?.ingestAudioChunkToPlay(audioData)
                        Log.d("GeminiService", "Playing audio in background service")
                    } else {
                        Log.d("GeminiService", "App in foreground, skipping audio playback in service")
                    }
                }
            }
        })
    }
    
    private fun setupAudioManagerCallbacks() {
        audioManager?.setCallback(object : AudioManager.AudioManagerCallback {
            override fun onAudioChunkReady(base64Audio: String) {
                // Send audio chunk through WebSocket when ready
                webSocketManager?.sendAudioChunk(base64Audio)
            }
            
            override fun onAudioRecordingStarted() {
                Log.d("GeminiService", "Audio recording started")
            }
            
            override fun onAudioRecordingStopped() {
                Log.d("GeminiService", "Audio recording stopped")
            }
            
            override fun onAudioPlaybackStarted() {
                isAIPlaying = true
                Log.d("GeminiService", "AI started playing audio - pausing recording")
            }
            
            override fun onAudioPlaybackStopped() {
                isAIPlaying = false
                Log.d("GeminiService", "AI stopped playing audio - resuming recording")
            }
        })
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START_LISTENING -> startListening()
            ACTION_STOP_LISTENING -> stopListening()
            ACTION_TOGGLE_LISTENING -> toggleListening()
        }
        
        val notification = createNotification(isListening)
        startForeground(NOTIFICATION_ID, notification)
        
        return START_STICKY // Service will be restarted if killed
    }
    
    override fun onBind(intent: Intent?): IBinder? = null
    
    override fun onDestroy() {
        super.onDestroy()
        Log.d("GeminiService", "Service destroyed")
        
        stopListening()
        wakeLock?.release()
        webSocketManager?.disconnect()
        audioManager?.cleanup()
        appStateCheckJob?.cancel()
        serviceScope.cancel()
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
        
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Gemini AI Assistant")
            .setContentText(statusText)
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
        if (isListening) return
        
        Log.d("GeminiService", "Starting listening")
        
        try {
            // Chỉ bắt đầu ghi âm khi app không ở foreground
            if (!MainActivity.isAppInForeground) {
                audioManager?.startAudioInput()
                Log.d("GeminiService", "Started audio input in background service")
            } else {
                Log.d("GeminiService", "App in foreground, not starting audio input in service")
            }
            
            isListening = true
            updateNotification()
            Log.d("GeminiService", "Listening started successfully")
        } catch (e: SecurityException) {
            Log.e("GeminiService", "Permission denied for audio recording", e)
        } catch (e: Exception) {
            Log.e("GeminiService", "Error starting listening", e)
        }
    }
    
    private fun stopListening() {
        if (!isListening) return
        
        Log.d("GeminiService", "Stopping listening")
        
        isListening = false
        
        // Use AudioManager to stop recording
        audioManager?.stopAudioInput()
        
        updateNotification()
        Log.d("GeminiService", "Listening stopped")
    }
    
    private fun toggleListening() {
        if (isListening) {
            stopListening()
        } else {
            startListening()
        }
    }
    
    private fun updateNotification() {
        val notification = createNotification(isListening)
        notificationManager?.notify(NOTIFICATION_ID, notification)
    }
    
    private fun startAppStateMonitoring() {
        appStateCheckJob = serviceScope.launch {
            var wasAppInBackground = !MainActivity.isAppInForeground
            
            while (true) {
                val isAppCurrentlyInForeground = MainActivity.isAppInForeground
                
                // App switched from foreground to background
                if (!isAppCurrentlyInForeground && !wasAppInBackground) {
                    Log.d("GeminiService", "App went to background, starting service WebSocket and audio input")
                    
                    // Đợi một chút để MainActivity ngắt kết nối trước
                    delay(1000)
                    
                    // Kết nối WebSocket cho service
                    if (webSocketManager?.isConnected() != true) {
                        webSocketManager?.connect()
                    }
                    
                    // Bắt đầu ghi âm
                    if (isListening && audioManager?.isCurrentlyRecording() != true) {
                        audioManager?.startAudioInput()
                    }
                }
                // App switched from background to foreground
                else if (isAppCurrentlyInForeground && wasAppInBackground) {
                    Log.d("GeminiService", "App came to foreground, stopping service WebSocket and audio input")
                    
                    // Ngắt kết nối WebSocket của service
                    webSocketManager?.disconnect()
                    
                    // Dừng ghi âm
                    audioManager?.stopAudioInput()
                }
                
                wasAppInBackground = !isAppCurrentlyInForeground
                delay(1000) // Check every second
            }
        }
    }
}
