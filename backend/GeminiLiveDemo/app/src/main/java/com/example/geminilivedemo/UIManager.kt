package com.example.geminilivedemo

import android.content.Intent
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.Base64
import android.util.Log
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity

class UIManager(private val activity: AppCompatActivity) {
    
    interface UICallback {
        fun onCaptureButtonClicked()
        fun onMicButtonClicked()
        fun onHomeButtonClicked()
        fun onStartButtonClicked()
        fun onStopButtonClicked()
        fun onScannerButtonClicked()
        fun onNotificationButtonClicked()
        fun onProfileButtonClicked()
        fun onBackgroundServiceToggled()
        fun onHistoryButtonClicked()
    }
    
    private var callback: UICallback? = null
    
    // UI Components
    private lateinit var imageView: ImageView
    private lateinit var captureButton: FrameLayout
    private lateinit var startButton: Button
    private lateinit var stopButton: Button
    private lateinit var chatLog: TextView
    private lateinit var statusIndicator: ImageView
    private lateinit var micButton: FrameLayout
    private lateinit var homeButton: FrameLayout
    private lateinit var historyButton: FrameLayout
    private lateinit var notificationButton: FrameLayout
    private lateinit var profileButton: FrameLayout
    private lateinit var micIcon: ImageView
    private lateinit var chatLogContainer: ScrollView
    private lateinit var backgroundServiceButton: FrameLayout
    private lateinit var backgroundServiceStatus: TextView
    private lateinit var backgroundServiceIcon: ImageView
    
    // Status variables
    private var isConnected = false
    private var isSpeaking = false
    private var isAIPlaying = false
    private var isAIResponding = false
    private var isBackgroundServiceRunning = false
    
    fun setCallback(callback: UICallback) {
        this.callback = callback
    }
    
    fun initializeViews() {
        // Initialize all UI components
        imageView = activity.findViewById(R.id.imageView)
        captureButton = activity.findViewById(R.id.captureButton)
        startButton = activity.findViewById(R.id.startButton)
        stopButton = activity.findViewById(R.id.stopButton)
        chatLog = activity.findViewById(R.id.chatLog)
        statusIndicator = activity.findViewById(R.id.statusIndicator)
        micButton = activity.findViewById(R.id.micButton)
        homeButton = activity.findViewById(R.id.homeButton)
        historyButton = activity.findViewById(R.id.historyButton)
        notificationButton = activity.findViewById(R.id.notificationButton)
        profileButton = activity.findViewById(R.id.profileButton)
        micIcon = activity.findViewById(R.id.micIcon)
        chatLogContainer = activity.findViewById(R.id.chatLogContainer)
        backgroundServiceButton = activity.findViewById(R.id.backgroundServiceButton)
        backgroundServiceStatus = activity.findViewById(R.id.backgroundServiceStatus)
        backgroundServiceIcon = activity.findViewById(R.id.backgroundServiceIcon)
        
        setupClickListeners()
        updateStatusIndicator()
        updateBackgroundServiceStatus()
    }
    
    private fun setupClickListeners() {
        captureButton.setOnClickListener {
            // Open scanner activity instead of camera
            openScannerActivity()
        }
        
        micButton.setOnClickListener {
            callback?.onMicButtonClicked()
        }
        
        homeButton.setOnClickListener {
            callback?.onHomeButtonClicked()
        }

        historyButton.setOnClickListener {
            callback?.onHistoryButtonClicked()
        }

        notificationButton.setOnClickListener {
            callback?.onNotificationButtonClicked()
        }
        
        profileButton.setOnClickListener {
            callback?.onProfileButtonClicked()
        }
        
        backgroundServiceButton.setOnClickListener {
            callback?.onBackgroundServiceToggled()
        }

        // Keep old button listeners for backward compatibility
        startButton.setOnClickListener {
            callback?.onStartButtonClicked()
        }

        stopButton.setOnClickListener {
            callback?.onStopButtonClicked()
        }
    }
    
    private fun openScannerActivity() {
        val intent = Intent(activity, ScannerActivity::class.java)
        activity.startActivityForResult(intent, SCANNER_REQUEST_CODE)
    }
    
    companion object {
        const val SCANNER_REQUEST_CODE = 1001
    }
    
    fun toggleChatLog() {
        if (chatLogContainer.visibility == View.VISIBLE) {
            chatLogContainer.visibility = View.GONE
            activity.findViewById<FrameLayout>(R.id.avatarContainer).visibility = View.VISIBLE
            activity.findViewById<LinearLayout>(R.id.statusContainer).visibility = View.VISIBLE
        } else {
            chatLogContainer.visibility = View.VISIBLE
            activity.findViewById<FrameLayout>(R.id.avatarContainer).visibility = View.GONE
            activity.findViewById<LinearLayout>(R.id.statusContainer).visibility = View.GONE
        }
    }
    
    fun updateMicIcon(isRecording: Boolean) {
        activity.runOnUiThread {
            if (isRecording) {
                micIcon.setImageResource(R.drawable.baseline_mic_off_24)
            } else {
                micIcon.setImageResource(R.drawable.baseline_mic_24)
            }
        }
    }
    
    fun displayMessage(message: String) {
        activity.runOnUiThread {
            val currentText = chatLog.text.toString()
            val updatedMessage = "$currentText \n$message"
            chatLog.text = updatedMessage
            Log.d("UIManager", "Displayed message: $message")
        }
    }
    
    fun displayCapturedImage(base64Image: String) {
        activity.runOnUiThread {
            try {
                val imageBytes = Base64.decode(base64Image, Base64.NO_WRAP)
                val bitmap = BitmapFactory.decodeByteArray(imageBytes, 0, imageBytes.size)
                imageView.setImageBitmap(bitmap)
                Log.d("UIManager", "Displayed captured image on ImageView")
            } catch (e: Exception) {
                Log.e("UIManager", "Error displaying captured image", e)
            }
        }
    }
    
    fun setConnectionStatus(connected: Boolean) {
        isConnected = connected
        updateStatusIndicator()
    }
    
    fun setSpeakingStatus(speaking: Boolean) {
        isSpeaking = speaking
        updateStatusIndicator()
    }
    
    fun setAIPlayingStatus(playing: Boolean) {
        isAIPlaying = playing
        updateStatusIndicator()
        updateMicButtonState()
    }
    
    fun setAIRespondingStatus(responding: Boolean) {
        isAIResponding = responding
        updateStatusIndicator()
    }
    
    private fun updateMicButtonState() {
        activity.runOnUiThread {
            if (isAIPlaying) {
                // Vô hiệu hóa nút mic khi AI đang phát âm thanh
                micButton.alpha = 0.5f
                micButton.isClickable = false
            } else {
                // Kích hoạt lại nút mic khi AI ngừng phát âm thanh
                micButton.alpha = 1.0f
                micButton.isClickable = true
            }
        }
    }
    
    private fun updateStatusIndicator() {
        activity.runOnUiThread {
            when {
                !isConnected -> {
                    statusIndicator.setImageResource(R.drawable.baseline_error_24)
                    statusIndicator.setColorFilter(android.graphics.Color.RED)
                }
                isAIResponding -> {
                    // Show AI responding status with equalizer icon in purple color
                    statusIndicator.setImageResource(R.drawable.baseline_equalizer_24)
                    statusIndicator.setColorFilter(android.graphics.Color.parseColor("#9C27B0")) // Purple/Violet
                }
                isAIPlaying -> {
                    statusIndicator.setImageResource(R.drawable.baseline_equalizer_24)
                    statusIndicator.setColorFilter(android.graphics.Color.BLUE) // Màu xanh dương khi AI đang phát âm thanh
                }
                !isSpeaking -> {
                    statusIndicator.setImageResource(R.drawable.baseline_equalizer_24)
                    statusIndicator.setColorFilter(android.graphics.Color.GRAY)
                }
                else -> {
                    statusIndicator.setImageResource(R.drawable.baseline_equalizer_24)
                    statusIndicator.setColorFilter(android.graphics.Color.GREEN)
                }
            }
        }
    }
    
    fun updateBackgroundServiceStatus() {
        activity.runOnUiThread {
            val statusText = if (isBackgroundServiceRunning) {
                "Background Listening: ON"
            } else {
                "Background Listening: OFF"
            }
            backgroundServiceStatus.text = statusText
            
            val iconColor = if (isBackgroundServiceRunning) {
                android.graphics.Color.GREEN
            } else {
                android.graphics.Color.GRAY
            }
            backgroundServiceIcon.setColorFilter(iconColor)
        }
    }
    
    fun setBackgroundServiceRunning(running: Boolean) {
        isBackgroundServiceRunning = running
        updateBackgroundServiceStatus()
    }
    
    fun getImageView(): ImageView = imageView
    
    fun showToast(message: String) {
        activity.runOnUiThread {
            Toast.makeText(activity, message, Toast.LENGTH_SHORT).show()
        }
    }
    
    fun updateConnectionStatus(connected: Boolean) {
        isConnected = connected
        // Use the same logic as updateStatusIndicator for consistency
        updateStatusIndicator()
        Log.d("UIManager", "Connection status updated: $connected")
    }
    
    fun setChatEnabled(enabled: Boolean) {
        activity.runOnUiThread {
            // Enable/disable chat controls
            micButton.isEnabled = enabled
            captureButton.isEnabled = enabled
            startButton.isEnabled = enabled
            stopButton.isEnabled = enabled
            
            // Visual feedback
            val alpha = if (enabled) 1.0f else 0.5f
            micButton.alpha = alpha
            captureButton.alpha = alpha
            startButton.alpha = alpha
            stopButton.alpha = alpha
            
            Log.d("UIManager", "Chat controls enabled: $enabled")
            
            // Removed toast notification as requested by user
            // if (!enabled) {
            //     showToast("Chat không khả dụng ở màn hình này")
            // }
        }
    }
}
