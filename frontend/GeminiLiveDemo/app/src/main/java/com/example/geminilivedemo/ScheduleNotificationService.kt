package com.example.geminilivedemo

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.os.Build
import android.os.IBinder
import android.util.Log
import androidx.core.app.NotificationCompat
import com.example.geminilivedemo.data.ApiClient
import com.example.geminilivedemo.data.ApiResult
import kotlinx.coroutines.*
import java.text.SimpleDateFormat
import java.util.*
import android.app.AlarmManager
import android.app.PendingIntent
import android.content.Context
import android.content.BroadcastReceiver
import android.content.IntentFilter
import android.media.AudioManager
import android.media.MediaPlayer
import android.speech.tts.TextToSpeech
import java.util.concurrent.TimeUnit
import org.json.JSONObject
import java.util.Locale

class ScheduleNotificationService : Service() {
    
    private val serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private lateinit var textToSpeech: TextToSpeech
    private lateinit var alarmManager: AlarmManager
    private val pendingIntents = mutableMapOf<String, PendingIntent>()
    
    companion object {
        private const val TAG = "ScheduleNotificationService"
        private const val CHANNEL_ID = "schedule_notifications"
        private const val NOTIFICATION_ID = 1001
        
        fun startService(context: Context) {
            val intent = Intent(context, ScheduleNotificationService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(intent)
            } else {
                context.startService(intent)
            }
        }
        
        fun stopService(context: Context) {
            val intent = Intent(context, ScheduleNotificationService::class.java)
            context.stopService(intent)
        }
    }
    
    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "Service created")
        
        createNotificationChannel()
        initializeTextToSpeech()
        alarmManager = getSystemService(Context.ALARM_SERVICE) as AlarmManager
        
        // Start foreground service
        startForeground(NOTIFICATION_ID, createNotification("Đang theo dõi lịch trình"))
        
        // Load and schedule all notifications
        loadAndScheduleNotifications()
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.d(TAG, "Service started")
        return START_STICKY
    }
    
    override fun onBind(intent: Intent?): IBinder? = null
    
    override fun onDestroy() {
        super.onDestroy()
        Log.d(TAG, "Service destroyed")
        
        // Cancel all pending alarms
        pendingIntents.values.forEach { pendingIntent ->
            alarmManager.cancel(pendingIntent)
        }
        pendingIntents.clear()
        
        // Shutdown text to speech
        textToSpeech.shutdown()
        
        serviceScope.cancel()
    }
    
    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Lịch trình",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Thông báo lịch trình hàng ngày"
                setShowBadge(false)
            }
            
            val notificationManager = getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannel(channel)
        }
    }
    
    private fun createNotification(content: String) = NotificationCompat.Builder(this, CHANNEL_ID)
        .setContentTitle("Kết nối yêu thương")
        .setContentText(content)
        .setSmallIcon(R.drawable.baseline_schedule_24)
        .setPriority(NotificationCompat.PRIORITY_LOW)
        .setOngoing(true)
        .build()
    
    private fun initializeTextToSpeech() {
        textToSpeech = TextToSpeech(this) { status ->
            if (status == TextToSpeech.SUCCESS) {
                val result = textToSpeech.setLanguage(Locale("vi"))
                if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                    Log.w(TAG, "Vietnamese language not supported, using default")
                }
            } else {
                Log.e(TAG, "TextToSpeech initialization failed")
            }
        }
    }
    
    private fun loadAndScheduleNotifications() {
        serviceScope.launch {
            try {
                val result = ApiClient.getUserReminders()
                
                when (result) {
                    is ApiResult.Success<*> -> {
                        val response = result.data as JSONObject
                        if (response.getBoolean("success")) {
                            val remindersArray = response.getJSONArray("reminders")
                            
                            for (i in 0 until remindersArray.length()) {
                                val reminder = remindersArray.getJSONObject(i)
                                val scheduledAt = reminder.getString("scheduled_at")
                                val title = reminder.getString("title")
                                val message = reminder.getString("message")
                                val reminderId = reminder.getString("id")
                                
                                scheduleNotification(reminderId, scheduledAt, title, message)
                            }
                            
                            Log.d(TAG, "Scheduled ${remindersArray.length()} notifications")
                        }
                    }
                    is ApiResult.Error -> {
                        Log.e(TAG, "Failed to load reminders: ${result.exception.message}")
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error loading reminders: ${e.message}", e)
            }
        }
    }
    
    private fun scheduleNotification(reminderId: String, scheduledAt: String, title: String, message: String) {
        try {
            val dateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
            val scheduledTime = dateFormat.parse(scheduledAt)
            
            if (scheduledTime != null && scheduledTime.after(Date())) {
                val intent = Intent(this, ScheduleNotificationReceiver::class.java).apply {
                    action = "SCHEDULE_NOTIFICATION"
                    putExtra("reminder_id", reminderId)
                    putExtra("title", title)
                    putExtra("message", message)
                }
                
                val pendingIntent = PendingIntent.getBroadcast(
                    this,
                    reminderId.hashCode(),
                    intent,
                    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
                )
                
                pendingIntents[reminderId] = pendingIntent
                
                alarmManager.setExactAndAllowWhileIdle(
                    AlarmManager.RTC_WAKEUP,
                    scheduledTime.time,
                    pendingIntent
                )
                
                Log.d(TAG, "Scheduled notification for $title at $scheduledAt")
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error scheduling notification: ${e.message}", e)
        }
    }
    
    fun addNewSchedule(reminderId: String, scheduledAt: String, title: String, message: String) {
        scheduleNotification(reminderId, scheduledAt, title, message)
    }
    
    fun removeSchedule(reminderId: String) {
        pendingIntents[reminderId]?.let { pendingIntent ->
            alarmManager.cancel(pendingIntent)
            pendingIntents.remove(reminderId)
            Log.d(TAG, "Removed schedule: $reminderId")
        }
    }
}

class ScheduleNotificationReceiver : BroadcastReceiver() {
    
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == "SCHEDULE_NOTIFICATION") {
            val reminderId = intent.getStringExtra("reminder_id") ?: return
            val title = intent.getStringExtra("title") ?: return
            val message = intent.getStringExtra("message") ?: return
            
            Log.d("ScheduleNotification", "Received notification: $title")
            
            // Send voice notification
            sendVoiceNotification(context, title, message)
            
            // Mark as sent in database
            markNotificationAsSent(context, reminderId)
        }
    }
    
    private fun sendVoiceNotification(context: Context, title: String, message: String) {
        val notificationText = "$title. $message"
        
        // Use TextToSpeech for immediate voice feedback
        var tts: TextToSpeech? = null
        tts = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                tts?.language = Locale("vi")
                tts?.speak(notificationText, TextToSpeech.QUEUE_FLUSH, null, "schedule_notification")
                
                // Also send to backend for voice generation
                sendToBackend(context, notificationText)
            }
        }
    }
    
    private fun sendToBackend(context: Context, notificationText: String) {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val result = ApiClient.generateVoiceNotification(notificationText, "info")
                if (result is ApiResult.Success<*>) {
                    Log.d("ScheduleNotification", "Voice notification sent to backend")
                }
            } catch (e: Exception) {
                Log.e("ScheduleNotification", "Error sending to backend: ${e.message}")
            }
        }
    }
    
    private fun markNotificationAsSent(context: Context, reminderId: String) {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                // Update notification status in database
                // This would typically call an API endpoint to mark the notification as sent
                Log.d("ScheduleNotification", "Marked notification $reminderId as sent")
            } catch (e: Exception) {
                Log.e("ScheduleNotification", "Error marking notification as sent: ${e.message}")
            }
        }
    }
} 