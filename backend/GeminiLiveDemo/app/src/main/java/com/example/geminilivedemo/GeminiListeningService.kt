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
import android.util.Base64
import android.util.Log
import androidx.core.app.NotificationCompat
import kotlinx.coroutines.*
import java.io.ByteArrayOutputStream

class GeminiListeningService : Service() {
    
    companion object {
        const val CHANNEL_ID = "GeminiListeningChannel"
        const val NOTIFICATION_ID = 1
        const val ACTION_START_LISTENING = "START_LISTENING"
        const val ACTION_STOP_LISTENING = "STOP_LISTENING"
        const val ACTION_TOGGLE_LISTENING = "TOGGLE_LISTENING"
        
        private const val SAMPLE_RATE = 16000
        private const val CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO
        private const val AUDIO_FORMAT = AudioFormat.ENCODING_PCM_16BIT
        private const val BUFFER_SIZE_FACTOR = 2
    }
    
    private var audioRecord: AudioRecord? = null
    private var isListening = false
    private var wakeLock: PowerManager.WakeLock? = null
    private var listeningJob: Job? = null
    private var webSocketManager: WebSocketManager? = null
    private var notificationManager: NotificationManager? = null
    
    private val serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    override fun onCreate() {
        super.onCreate()
        Log.d("GeminiService", "Service created")
        
        createNotificationChannel()
        
        // Initialize WebSocket connection
        webSocketManager = WebSocketManager()
        webSocketManager?.connect()
        
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
            val bufferSize = AudioRecord.getMinBufferSize(
                SAMPLE_RATE,
                CHANNEL_CONFIG,
                AUDIO_FORMAT
            ) * BUFFER_SIZE_FACTOR
            
            audioRecord = AudioRecord(
                MediaRecorder.AudioSource.MIC,
                SAMPLE_RATE,
                CHANNEL_CONFIG,
                AUDIO_FORMAT,
                bufferSize
            )
            
            if (audioRecord?.state == AudioRecord.STATE_INITIALIZED) {
                audioRecord?.startRecording()
                isListening = true
                
                listeningJob = serviceScope.launch {
                    startAudioCapture()
                }
                
                updateNotification()
                Log.d("GeminiService", "Listening started successfully")
            } else {
                Log.e("GeminiService", "Failed to initialize AudioRecord")
            }
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
        listeningJob?.cancel()
        
        audioRecord?.apply {
            if (state == AudioRecord.STATE_INITIALIZED) {
                stop()
            }
            release()
        }
        audioRecord = null
        
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
    
    private suspend fun startAudioCapture() {
        val audioRecord = this.audioRecord ?: return
        val buffer = ShortArray(1024)
        
        while (isListening && !Thread.currentThread().isInterrupted) {
            try {
                val readSize = audioRecord.read(buffer, 0, buffer.size)
                if (readSize > 0) {
                    // Convert to base64 and send to WebSocket
                    val base64Audio = convertToBase64(buffer, readSize)
                    webSocketManager?.sendAudioChunk(base64Audio)
                }
                
                // Small delay to prevent excessive CPU usage
                delay(50)
            } catch (e: Exception) {
                Log.e("GeminiService", "Error reading audio", e)
                break
            }
        }
    }
    
    private fun convertToBase64(audioData: ShortArray, length: Int): String {
        val byteArray = ByteArray(length * 2)
        for (i in 0 until length) {
            val value = audioData[i].toInt()
            byteArray[i * 2] = (value and 0xFF).toByte()
            byteArray[i * 2 + 1] = ((value shr 8) and 0xFF).toByte()
        }
        return Base64.encodeToString(byteArray, Base64.NO_WRAP)
    }
    
    private fun updateNotification() {
        val notification = createNotification(isListening)
        notificationManager?.notify(NOTIFICATION_ID, notification)
    }
}
