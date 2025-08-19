package com.example.geminilivedemo

import android.app.Service
import android.content.Intent
import android.os.IBinder
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import android.media.AudioAttributes
import android.media.AudioFocusRequest
import android.media.AudioManager as SysAudioManager
import android.util.Log
import com.example.geminilivedemo.data.ScheduleManager
import com.example.geminilivedemo.data.Schedule
import kotlinx.coroutines.*
import java.util.*

class VoiceNotificationService : Service() {
    
    private val serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private lateinit var textToSpeech: TextToSpeech
    private lateinit var scheduleManager: ScheduleManager
    private lateinit var systemAudioManager: SysAudioManager
    private var audioFocusRequest: AudioFocusRequest? = null
    
    companion object {
        private const val TAG = "VoiceNotificationService"
        
        fun startService(context: android.content.Context) {
            val intent = Intent(context, VoiceNotificationService::class.java)
            context.startService(intent)
        }
        
        fun stopService(context: android.content.Context) {
            val intent = Intent(context, VoiceNotificationService::class.java)
            context.stopService(intent)
        }
    }
    
    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "VoiceNotificationService created")
        
        scheduleManager = ScheduleManager(this)
        systemAudioManager = getSystemService(AUDIO_SERVICE) as SysAudioManager
        initializeTextToSpeech()
        
        // Start monitoring schedules
        startScheduleMonitoring()
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.d(TAG, "VoiceNotificationService started")
        return START_STICKY
    }
    
    override fun onBind(intent: Intent?): IBinder? = null
    
    override fun onDestroy() {
        super.onDestroy()
        Log.d(TAG, "VoiceNotificationService destroyed")
        
        textToSpeech.shutdown()
        serviceScope.cancel()
        abandonAudioFocus()
    }
    
    private fun initializeTextToSpeech() {
        textToSpeech = TextToSpeech(this) { status ->
            if (status == TextToSpeech.SUCCESS) {
                val result = textToSpeech.setLanguage(Locale("vi"))
                if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                    Log.w(TAG, "Vietnamese language not supported, using default")
                    textToSpeech.language = Locale.getDefault()
                }
                Log.d(TAG, "TextToSpeech initialized successfully")
                textToSpeech.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
                    override fun onStart(utteranceId: String?) {
                        GlobalPlaybackState.isPlaying = true
                        Log.d(TAG, "TTS onStart: $utteranceId")
                    }

                    override fun onDone(utteranceId: String?) {
                        Log.d(TAG, "TTS onDone: $utteranceId")
                        GlobalPlaybackState.isPlaying = false
                        abandonAudioFocus()
                    }

                    @Deprecated("Deprecated in Java")
                    override fun onError(utteranceId: String?) {
                        Log.w(TAG, "TTS onError: $utteranceId")
                        GlobalPlaybackState.isPlaying = false
                        abandonAudioFocus()
                    }

                    override fun onError(utteranceId: String?, errorCode: Int) {
                        Log.w(TAG, "TTS onError($errorCode): $utteranceId")
                        GlobalPlaybackState.isPlaying = false
                        abandonAudioFocus()
                    }
                })
            } else {
                Log.e(TAG, "TextToSpeech initialization failed")
            }
        }
    }
    
    private fun startScheduleMonitoring() {
        serviceScope.launch {
            while (isActive) {
                try {
                    // Check for upcoming schedules every minute
                    checkUpcomingSchedules()
                    delay(60000) // 1 minute
                } catch (e: Exception) {
                    Log.e(TAG, "Error in schedule monitoring: ${e.message}", e)
                    delay(60000) // Wait 1 minute before retrying
                }
            }
        }
    }
    
    private suspend fun checkUpcomingSchedules() {
        try {
            // For now, check schedules for a default elderly user
            // In a real app, this would be determined by the current user
            val elderlyId = "default_elderly"
            val upcomingSchedules = scheduleManager.getUpcomingSchedules(elderlyId, 10)
            
            val now = System.currentTimeMillis() / 1000
            val fiveMinutesFromNow = now + 300 // 5 minutes
            
            upcomingSchedules.forEach { schedule ->
                // Check if schedule is within the next 5 minutes
                if (schedule.scheduledAt <= fiveMinutesFromNow && schedule.scheduledAt > now) {
                    val timeUntilSchedule = schedule.scheduledAt - now
                    
                    when {
                        timeUntilSchedule <= 60 -> { // Within 1 minute
                            sendImmediateVoiceNotification(schedule)
                        }
                        timeUntilSchedule <= 300 -> { // Within 5 minutes
                            sendAdvanceVoiceNotification(schedule, timeUntilSchedule)
                        }
                    }
                }
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "Error checking upcoming schedules: ${e.message}", e)
        }
    }
    
    private fun sendImmediateVoiceNotification(schedule: Schedule) {
        if (GlobalPlaybackState.isPlaying) {
            Log.d(TAG, "Another audio is playing, skipping immediate TTS to avoid overlap")
            return
        }
        requestAudioFocus()
        GlobalPlaybackState.isPlaying = true
        val notificationText = "Đã đến giờ: ${schedule.title}. ${schedule.message}"
        
        textToSpeech.speak(
            notificationText,
            TextToSpeech.QUEUE_FLUSH,
            null,
            "schedule_notification_${schedule.id}"
        )
        
        Log.d(TAG, "Sent immediate voice notification: $notificationText")
        
        // Mark as completed after sending
        serviceScope.launch {
            scheduleManager.markScheduleComplete(schedule.id ?: "")
        }
    }
    
    private fun sendAdvanceVoiceNotification(schedule: Schedule, timeUntilSchedule: Long) {
        if (GlobalPlaybackState.isPlaying) {
            Log.d(TAG, "Another audio is playing, skipping advance TTS to avoid overlap")
            return
        }
        requestAudioFocus()
        GlobalPlaybackState.isPlaying = true
        val minutes = timeUntilSchedule / 60
        val notificationText = "Nhắc nhở: ${schedule.title} sẽ diễn ra trong $minutes phút nữa. ${schedule.message}"
        
        textToSpeech.speak(
            notificationText,
            TextToSpeech.QUEUE_FLUSH,
            null,
            "schedule_advance_${schedule.id}"
        )
        
        Log.d(TAG, "Sent advance voice notification: $notificationText")
    }
    
    // Public method to send custom voice notification
    fun sendCustomVoiceNotification(title: String, message: String) {
        if (GlobalPlaybackState.isPlaying) {
            Log.d(TAG, "Another audio is playing, skipping custom TTS to avoid overlap")
            return
        }
        requestAudioFocus()
        GlobalPlaybackState.isPlaying = true
        val notificationText = "$title. $message"
        
        textToSpeech.speak(
            notificationText,
            TextToSpeech.QUEUE_FLUSH,
            null,
            "custom_notification_${System.currentTimeMillis()}"
        )
        
        Log.d(TAG, "Sent custom voice notification: $notificationText")
    }
    
    // Method to test voice notification
    fun testVoiceNotification() {
        if (GlobalPlaybackState.isPlaying) {
            Log.d(TAG, "Another audio is playing, skipping test TTS to avoid overlap")
            return
        }
        requestAudioFocus()
        GlobalPlaybackState.isPlaying = true
        val testText = "Xin chào! Đây là thông báo thử nghiệm từ ứng dụng Kết nối yêu thương."
        
        textToSpeech.speak(
            testText,
            TextToSpeech.QUEUE_FLUSH,
            null,
            "test_notification"
        )
        
        Log.d(TAG, "Sent test voice notification")
    }

    private fun requestAudioFocus() {
        try {
            val attributes = AudioAttributes.Builder()
                .setUsage(AudioAttributes.USAGE_ASSISTANCE_ACCESSIBILITY)
                .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                .build()
            audioFocusRequest = AudioFocusRequest.Builder(SysAudioManager.AUDIOFOCUS_GAIN_TRANSIENT_MAY_DUCK)
                .setAudioAttributes(attributes)
                .setAcceptsDelayedFocusGain(false)
                .setOnAudioFocusChangeListener { /* no-op */ }
                .build()
            val result = systemAudioManager.requestAudioFocus(audioFocusRequest!!)
            Log.d(TAG, "Audio focus request result: $result")
        } catch (e: Exception) {
            Log.w(TAG, "Failed to request audio focus", e)
        }
    }

    private fun abandonAudioFocus() {
        try {
            audioFocusRequest?.let {
                systemAudioManager.abandonAudioFocusRequest(it)
            }
        } catch (e: Exception) {
            Log.w(TAG, "Failed to abandon audio focus", e)
        }
    }
} 