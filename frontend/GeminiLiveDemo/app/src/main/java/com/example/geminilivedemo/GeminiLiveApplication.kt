package com.example.geminilivedemo

import android.app.Activity
import android.app.Application
import android.os.Bundle
import android.util.Log
import androidx.appcompat.app.AppCompatDelegate

/**
 * GeminiLiveApplication - Application class để quản lý lifecycle toàn cục
 * Theo dõi khi app thực sự đi background vs chuyển Activity
 */
class GeminiLiveApplication : Application(), Application.ActivityLifecycleCallbacks {
    
    private var activityCount = 0
    private var isAppInForeground = false
    private lateinit var globalConnectionManager: GlobalConnectionManager
    
    override fun onCreate() {
        super.onCreate()
        Log.d("GeminiLiveApplication", "Application created")
        
        // Set default theme to light mode
        AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO)
        
        // Khởi tạo GlobalConnectionManager
        globalConnectionManager = GlobalConnectionManager.getInstance()
        globalConnectionManager.initialize(this)
        
        // Đăng ký lifecycle callbacks
        registerActivityLifecycleCallbacks(this)
    }
    
    override fun onActivityCreated(activity: Activity, savedInstanceState: Bundle?) {
        Log.d("GeminiLiveApplication", "Activity created: ${activity::class.java.simpleName}")
    }
    
    override fun onActivityStarted(activity: Activity) {
        Log.d("GeminiLiveApplication", "Activity started: ${activity::class.java.simpleName}")
        
        activityCount++
        
        // App đang chuyển từ background về foreground
        if (!isAppInForeground) {
            Log.d("GeminiLiveApplication", "App coming to foreground")
            isAppInForeground = true
            globalConnectionManager.handleAppComingForeground()
        }
        
        // Đăng ký activity với GlobalConnectionManager
        globalConnectionManager.registerActivity(activity)
    }
    
    override fun onActivityResumed(activity: Activity) {
        Log.d("GeminiLiveApplication", "Activity resumed: ${activity::class.java.simpleName}")
        globalConnectionManager.onActivityResumed(activity)
    }
    
    override fun onActivityPaused(activity: Activity) {
        Log.d("GeminiLiveApplication", "Activity paused: ${activity::class.java.simpleName}")
        globalConnectionManager.onActivityPaused(activity)
    }
    
    override fun onActivityStopped(activity: Activity) {
        Log.d("GeminiLiveApplication", "Activity stopped: ${activity::class.java.simpleName}")
        
        activityCount--
        
        // Hủy đăng ký activity
        globalConnectionManager.unregisterActivity(activity)
        
        // App đang đi background (không còn activity nào visible)
        if (activityCount == 0 && isAppInForeground) {
            Log.d("GeminiLiveApplication", "App going to background")
            isAppInForeground = false
            // GlobalConnectionManager sẽ tự xử lý khi không còn activity nào active
        }
    }
    
    override fun onActivitySaveInstanceState(activity: Activity, outState: Bundle) {
        Log.d("GeminiLiveApplication", "Activity save instance state: ${activity::class.java.simpleName}")
    }
    
    override fun onActivityDestroyed(activity: Activity) {
        Log.d("GeminiLiveApplication", "Activity destroyed: ${activity::class.java.simpleName}")
    }
    
    override fun onTerminate() {
        super.onTerminate()
        Log.d("GeminiLiveApplication", "Application terminated")
        globalConnectionManager.cleanup()
        unregisterActivityLifecycleCallbacks(this)
    }
    
    fun getGlobalConnectionManager(): GlobalConnectionManager {
        return globalConnectionManager
    }
} 