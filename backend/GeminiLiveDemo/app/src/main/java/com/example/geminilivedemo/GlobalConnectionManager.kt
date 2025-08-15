package com.example.geminilivedemo

import android.app.Activity
import android.content.Context
import android.util.Log
import java.util.concurrent.ConcurrentHashMap

/**
 * GlobalConnectionManager - Quản lý WebSocket connection toàn cục
 * Đảm bảo connection được duy trì khi chuyển giữa các Activity
 */
class GlobalConnectionManager private constructor() {
    
    companion object {
        @Volatile
        private var INSTANCE: GlobalConnectionManager? = null
        
        fun getInstance(): GlobalConnectionManager {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: GlobalConnectionManager().also { INSTANCE = it }
            }
        }
    }
    
    private var webSocketManager: WebSocketManager? = null
    private var audioManager: AudioManager? = null
    private var serviceManager: ServiceManager? = null
    private var voiceNotificationManager: VoiceNotificationManager? = null
    
    // Theo dõi các Activity đang hoạt động
    private val activeActivities = ConcurrentHashMap<String, Activity>()
    private var currentActivity: Activity? = null
    private var isAppInBackground = false
    private var isBackgroundServiceRunning = false
    
    // Callback để thông báo trạng thái connection
    interface ConnectionStateCallback {
        fun onConnectionStateChanged(isConnected: Boolean)
        fun onChatAvailabilityChanged(isChatAvailable: Boolean)
    }
    
    private val callbacks = mutableSetOf<ConnectionStateCallback>()
    
    fun initialize(context: Context) {
        if (webSocketManager == null) {
            Log.d("GlobalConnectionManager", "Initializing managers")
            webSocketManager = WebSocketManager()
            audioManager = AudioManager(context)
            serviceManager = ServiceManager(context)
            voiceNotificationManager = VoiceNotificationManager(context)
        }
    }
    
    fun registerCallback(callback: ConnectionStateCallback) {
        callbacks.add(callback)
    }
    
    fun unregisterCallback(callback: ConnectionStateCallback) {
        callbacks.remove(callback)
    }
    
    fun registerActivity(activity: Activity) {
        val activityName = activity::class.java.simpleName
        Log.d("GlobalConnectionManager", "Registering activity: $activityName")
        
        activeActivities[activityName] = activity
        currentActivity = activity
        isAppInBackground = false
        
        // Nếu đây là MainActivity hoặc MedicineInfoActivity, cho phép chat và duy trì connection
        val isChatAvailable = activity is MainActivity || activity is MedicineInfoActivity
        notifyChatAvailabilityChanged(isChatAvailable)
        
        // Đảm bảo kết nối khi ở MainActivity hoặc MedicineInfoActivity
        if (activity is MainActivity || activity is MedicineInfoActivity) {
            ensureConnection()
        }
    }
    
    fun unregisterActivity(activity: Activity) {
        val activityName = activity::class.java.simpleName
        Log.d("GlobalConnectionManager", "Unregistering activity: $activityName")
        
        activeActivities.remove(activityName)
        
        if (currentActivity == activity) {
            currentActivity = null
        }
        
        // Nếu không còn Activity nào active, app đi background
        if (activeActivities.isEmpty()) {
            Log.d("GlobalConnectionManager", "App going to background")
            isAppInBackground = true
            handleAppGoingBackground()
        }
    }
    
    fun onActivityPaused(activity: Activity) {
        val activityName = activity::class.java.simpleName
        Log.d("GlobalConnectionManager", "Activity paused: $activityName")
        
        // Chỉ disable chat, không disconnect
        if (activity is MainActivity) {
            notifyChatAvailabilityChanged(false)
        }
    }
    
    fun onActivityResumed(activity: Activity) {
        val activityName = activity::class.java.simpleName
        Log.d("GlobalConnectionManager", "Activity resumed: $activityName")
        
        currentActivity = activity
        isAppInBackground = false
        
        // Enable chat nếu là MainActivity hoặc MedicineInfoActivity
        val isChatAvailable = activity is MainActivity || activity is MedicineInfoActivity
        notifyChatAvailabilityChanged(isChatAvailable)
        
        // Đảm bảo kết nối khi ở MainActivity hoặc MedicineInfoActivity
        if (activity is MainActivity || activity is MedicineInfoActivity) {
            ensureConnection()
        }
    }
    
    private fun ensureConnection() {
        webSocketManager?.let { wsManager ->
            if (!wsManager.isConnected()) {
                Log.d("GlobalConnectionManager", "Ensuring WebSocket connection")
                wsManager.connect()
            }
            notifyConnectionStateChanged(wsManager.isConnected())
        }
    }
    
    private fun handleAppGoingBackground() {
        Log.d("GlobalConnectionManager", "Handling app going to background")
        
        // Resume background service nếu có
        if (isBackgroundServiceRunning) {
            serviceManager?.resumeListeningService()
            
            // Delay disconnect để service có thời gian reconnect
            android.os.Handler(android.os.Looper.getMainLooper()).postDelayed({
                if (isAppInBackground) {
                    Log.d("GlobalConnectionManager", "Disconnecting WebSocket - app in background")
                    webSocketManager?.disconnect()
                    notifyConnectionStateChanged(false)
                }
            }, 1000)
        } else {
            // Không có background service, disconnect ngay
            webSocketManager?.disconnect()
            notifyConnectionStateChanged(false)
        }
    }
    
    fun handleAppComingForeground() {
        Log.d("GlobalConnectionManager", "Handling app coming to foreground")
        isAppInBackground = false
        
        // Pause background service
        if (isBackgroundServiceRunning) {
            serviceManager?.pauseListeningService()
        }
        
        // Reconnect WebSocket khi MainActivity hoặc MedicineInfoActivity là activity hiện tại
        if (currentActivity is MainActivity || currentActivity is MedicineInfoActivity) {
            ensureConnection()
        }
    }
    
    private fun notifyConnectionStateChanged(isConnected: Boolean) {
        callbacks.forEach { it.onConnectionStateChanged(isConnected) }
    }
    
    private fun notifyChatAvailabilityChanged(isChatAvailable: Boolean) {
        callbacks.forEach { it.onChatAvailabilityChanged(isChatAvailable) }
    }
    
    // Getters cho các manager
    fun getWebSocketManager(): WebSocketManager? = webSocketManager
    fun getAudioManager(): AudioManager? = audioManager
    fun getServiceManager(): ServiceManager? = serviceManager
    fun getVoiceNotificationManager(): VoiceNotificationManager? = voiceNotificationManager
    
    fun setBackgroundServiceRunning(isRunning: Boolean) {
        isBackgroundServiceRunning = isRunning
    }
    
    fun isBackgroundServiceRunning(): Boolean = isBackgroundServiceRunning
    
    fun getCurrentActivity(): Activity? = currentActivity
    
    fun isChatAvailable(): Boolean {
        return (currentActivity is MainActivity || currentActivity is MedicineInfoActivity) && !isAppInBackground
    }
    
    fun cleanup() {
        Log.d("GlobalConnectionManager", "Cleaning up GlobalConnectionManager")
        webSocketManager?.disconnect()
        audioManager?.cleanup()
        voiceNotificationManager?.cleanup()
        callbacks.clear()
        activeActivities.clear()
    }
} 