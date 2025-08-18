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

    private lateinit var micButton: FrameLayout
    private lateinit var homeButton: FrameLayout
    private lateinit var historyButton: FrameLayout
    private lateinit var notificationButton: FrameLayout
    private lateinit var profileButton: FrameLayout

    private lateinit var micIcon: ImageView
    private lateinit var chatLogContainer: ScrollView
    
    // New UI components for simplified layout
    private lateinit var topActionButtons: LinearLayout
    private lateinit var avatarContainer: FrameLayout
    
    // Status bar components
    private lateinit var statusBar: LinearLayout
    private lateinit var connectionStatusContainer: LinearLayout
    private lateinit var connectionStatusIcon: ImageView
    private lateinit var connectionStatusText: TextView
    private lateinit var aiStatusContainer: LinearLayout
    private lateinit var aiStatusIcon: ImageView
    private lateinit var aiStatusText: TextView
    
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

        micButton = activity.findViewById(R.id.micButton)
        homeButton = activity.findViewById(R.id.homeButton)
        historyButton = activity.findViewById(R.id.historyButton)
        notificationButton = activity.findViewById(R.id.notificationButton)
        profileButton = activity.findViewById(R.id.profileButton)

        micIcon = activity.findViewById(R.id.micIcon)
        chatLogContainer = activity.findViewById(R.id.chatLogContainer)
        
        // Initialize new UI components
        topActionButtons = activity.findViewById(R.id.topActionButtons)
        avatarContainer = activity.findViewById(R.id.avatarContainer)
        
        // Initialize status bar components
        statusBar = activity.findViewById(R.id.statusBar)
        connectionStatusContainer = activity.findViewById(R.id.connectionStatusContainer)
        connectionStatusIcon = activity.findViewById(R.id.connectionStatusIcon)
        connectionStatusText = activity.findViewById(R.id.connectionStatusText)
        aiStatusContainer = activity.findViewById(R.id.aiStatusContainer)
        aiStatusIcon = activity.findViewById(R.id.aiStatusIcon)
        aiStatusText = activity.findViewById(R.id.aiStatusText)
        
        setupClickListeners()
        
        // Set default avatar
        setDefaultAvatar()
        
        // Initialize status bar
        initializeStatusBar()
        
        // Default AI status
        setAIIdle()
    }
    
    private fun setupClickListeners() {
        captureButton.setOnClickListener {
            // Open scanner activity instead of camera
            openScannerActivity()
        }
        
        micButton.setOnClickListener {
            Log.d("UIManager", "Mic button clicked! Callback is: ${callback != null}")
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
            avatarContainer.visibility = View.VISIBLE
            topActionButtons.visibility = View.VISIBLE
        } else {
            chatLogContainer.visibility = View.VISIBLE
            avatarContainer.visibility = View.GONE
            topActionButtons.visibility = View.GONE
        }
    }
    
    fun updateMicIcon(isRecording: Boolean) {
        // Kiểm tra xem các UI components đã được khởi tạo chưa
        if (!::micIcon.isInitialized) {
            Log.d("UIManager", "Mic icon not initialized yet, skipping updateMicIcon")
            return
        }
        
        activity.runOnUiThread {
            if (isRecording) {
                micIcon.setImageResource(R.drawable.baseline_mic_24)
            } else {
                micIcon.setImageResource(R.drawable.baseline_mic_off_24)
            }
        }
    }
    
    fun displayMessage(message: String) {
        // Kiểm tra xem các UI components đã được khởi tạo chưa
        if (!::chatLog.isInitialized) {
            Log.d("UIManager", "Chat log not initialized yet, skipping displayMessage")
            return
        }
        
        activity.runOnUiThread {
            val currentText = chatLog.text.toString()
            val updatedMessage = "$currentText \n$message"
            chatLog.text = updatedMessage
            Log.d("UIManager", "Displayed message: $message")
        }
    }
    
    fun displayCapturedImage(base64Image: String) {
        // Kiểm tra xem các UI components đã được khởi tạo chưa
        if (!::imageView.isInitialized) {
            Log.d("UIManager", "ImageView not initialized yet, skipping displayCapturedImage")
            return
        }
        
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
    }
    
    fun setSpeakingStatus(speaking: Boolean) {
        isSpeaking = speaking
    }
    
    fun setAIPlayingStatus(playing: Boolean) {
        isAIPlaying = playing
        updateMicButtonState()
    }
    
    fun setAIRespondingStatus(responding: Boolean) {
        isAIResponding = responding
        if (responding) {
            setAISpeaking()
        } else if (!isAIPlaying && !isSpeaking) {
            setAIIdle()
        }
    }
    
    private fun updateMicButtonState() {
        // Kiểm tra xem các UI components đã được khởi tạo chưa
        if (!::micButton.isInitialized) {
            Log.d("UIManager", "Mic button not initialized yet, skipping updateMicButtonState")
            return
        }
        
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
    

    
    fun setBackgroundServiceRunning(running: Boolean) {
        isBackgroundServiceRunning = running
        // Background service status is no longer displayed in UI
    }
    
    fun getImageView(): ImageView = imageView
    
    fun showToast(message: String) {
        activity.runOnUiThread {
            Toast.makeText(activity, message, Toast.LENGTH_SHORT).show()
        }
    }
    
    fun updateConnectionStatus(connected: Boolean) {
        isConnected = connected
        Log.d("UIManager", "Connection status updated: $connected")
    }
    
    private fun setDefaultAvatar() {
        // Kiểm tra xem các UI components đã được khởi tạo chưa
        if (!::imageView.isInitialized) {
            Log.d("UIManager", "ImageView not initialized yet, skipping setDefaultAvatar")
            return
        }
        
        activity.runOnUiThread {
            imageView.setImageResource(R.drawable.doctor_avatar)
        }
    }
    
    fun setChatEnabled(enabled: Boolean) {
        // Kiểm tra xem các UI components đã được khởi tạo chưa
        if (!::micButton.isInitialized || !::captureButton.isInitialized || 
            !::startButton.isInitialized || !::stopButton.isInitialized) {
            Log.d("UIManager", "UI components not initialized yet, skipping setChatEnabled")
            return
        }
        
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
    
    // Status Bar Management Methods
    private fun initializeStatusBar() {
        activity.runOnUiThread {
            // Set initial connection status
            updateConnectionStatusDisplay(false)
        }
    }
    
    fun updateConnectionStatusDisplay(connected: Boolean) {
        // Kiểm tra xem các UI components đã được khởi tạo chưa
        if (!::connectionStatusIcon.isInitialized || !::connectionStatusText.isInitialized) {
            Log.d("UIManager", "Status bar components not initialized yet, skipping updateConnectionStatusDisplay")
            return
        }
        
        activity.runOnUiThread {
            isConnected = connected
            if (connected) {
                connectionStatusIcon.setImageResource(R.drawable.baseline_signal_wifi_4_bar_24)
                connectionStatusIcon.setColorFilter(activity.getColor(R.color.connection_online))
                connectionStatusText.text = "Online"
                connectionStatusText.setTextColor(activity.getColor(R.color.connection_online))
            } else {
                connectionStatusIcon.setImageResource(R.drawable.baseline_signal_wifi_off_24)
                connectionStatusIcon.setColorFilter(activity.getColor(R.color.connection_offline))
                connectionStatusText.text = "Offline"
                connectionStatusText.setTextColor(activity.getColor(R.color.connection_offline))
            }
        }
    }
    
    fun updateConnectionStatusConnecting() {
        // Kiểm tra xem các UI components đã được khởi tạo chưa
        if (!::connectionStatusIcon.isInitialized || !::connectionStatusText.isInitialized) {
            Log.d("UIManager", "Status bar components not initialized yet, skipping updateConnectionStatusConnecting")
            return
        }
        
        activity.runOnUiThread {
            connectionStatusIcon.setImageResource(R.drawable.baseline_signal_wifi_connecting_24)
            connectionStatusIcon.setColorFilter(activity.getColor(R.color.connection_connecting))
            connectionStatusText.text = "Connecting..."
            connectionStatusText.setTextColor(activity.getColor(R.color.connection_connecting))
        }
    }
    
    // AI chat status helpers
    fun setAIIdle() {
        // Kiểm tra xem các UI components đã được khởi tạo chưa
        if (!::aiStatusIcon.isInitialized || !::aiStatusText.isInitialized) {
            Log.d("UIManager", "AI status components not initialized yet, skipping setAIIdle")
            return
        }
        
        activity.runOnUiThread {
            aiStatusIcon.setImageResource(R.drawable.baseline_equalizer_24_static)
            aiStatusIcon.setColorFilter(activity.getColor(R.color.text_secondary))
            aiStatusText.text = "AI: Rảnh"
            aiStatusText.setTextColor(activity.getColor(R.color.text_secondary))
        }
    }

    fun setAIListening() {
        // Kiểm tra xem các UI components đã được khởi tạo chưa
        if (!::aiStatusIcon.isInitialized || !::aiStatusText.isInitialized) {
            Log.d("UIManager", "AI status components not initialized yet, skipping setAIListening")
            return
        }
        
        activity.runOnUiThread {
            aiStatusIcon.setImageResource(R.drawable.baseline_mic_24)
            aiStatusIcon.setColorFilter(activity.getColor(R.color.primary_600))
            aiStatusText.text = "AI: Đang lắng nghe"
            aiStatusText.setTextColor(activity.getColor(R.color.primary_600))
        }
    }

    fun setAISpeaking() {
        // Kiểm tra xem các UI components đã được khởi tạo chưa
        if (!::aiStatusIcon.isInitialized || !::aiStatusText.isInitialized) {
            Log.d("UIManager", "AI status components not initialized yet, skipping setAISpeaking")
            return
        }
        
        activity.runOnUiThread {
            aiStatusIcon.setImageResource(R.drawable.baseline_equalizer_24)
            aiStatusIcon.setColorFilter(activity.getColor(R.color.accent_600))
            aiStatusText.text = "AI: Đang nói"
            aiStatusText.setTextColor(activity.getColor(R.color.accent_600))
        }
    }

    fun setAIThinking() {
        // Kiểm tra xem các UI components đã được khởi tạo chưa
        if (!::aiStatusIcon.isInitialized || !::aiStatusText.isInitialized) {
            Log.d("UIManager", "AI status components not initialized yet, skipping setAIThinking")
            return
        }
        
        activity.runOnUiThread {
            aiStatusIcon.setImageResource(R.drawable.baseline_refresh_24)
            aiStatusIcon.setColorFilter(activity.getColor(R.color.text_secondary))
            aiStatusText.text = "AI: Đang suy nghĩ"
            aiStatusText.setTextColor(activity.getColor(R.color.text_secondary))
        }
    }
}
