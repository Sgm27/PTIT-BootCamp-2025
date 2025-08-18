package com.example.geminilivedemo

import android.content.Intent
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.Base64
import android.util.Log
import android.view.View
import android.widget.*
import android.widget.VideoView
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
    private lateinit var avatarVideoView: VideoView
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
    private var isCurrentlyPlayingTalking = false // Track current video state
    
    fun setCallback(callback: UICallback) {
        this.callback = callback
    }
    
    fun initializeViews() {
        // Initialize all UI components
        avatarVideoView = activity.findViewById(R.id.avatarVideoView)
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
        
        // Set default avatar video
        setDefaultAvatarVideo()
        
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
    

    
    fun setConnectionStatus(connected: Boolean) {
        isConnected = connected
    }
    
    fun setSpeakingStatus(speaking: Boolean) {
        isSpeaking = speaking
        // Không chuyển đổi video khi user đang nói - chỉ khi AI phát âm thanh
        // updateAvatarVideo()
    }
    
    fun setAIPlayingStatus(playing: Boolean) {
        isAIPlaying = playing
        updateMicButtonState()
        // Chỉ chuyển đổi video khi trạng thái phát âm thanh thay đổi
        updateAvatarVideo()
    }
    
    fun setAIRespondingStatus(responding: Boolean) {
        isAIResponding = responding
        if (responding) {
            setAISpeaking()
        } else if (!isAIPlaying && !isSpeaking) {
            setAIIdle()
        }
        // Chỉ chuyển đổi video khi AI thực sự phát âm thanh
        if (responding && isAIPlaying) {
            updateAvatarVideo()
        } else if (!responding && !isAIPlaying) {
            updateAvatarVideo()
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
    
    fun getVideoView(): VideoView = avatarVideoView
    
    fun showToast(message: String) {
        activity.runOnUiThread {
            Toast.makeText(activity, message, Toast.LENGTH_SHORT).show()
        }
    }
    
    fun updateConnectionStatus(connected: Boolean) {
        isConnected = connected
        Log.d("UIManager", "Connection status updated: $connected")
    }
    
    private fun setDefaultAvatarVideo() {
        // Kiểm tra xem các UI components đã được khởi tạo chưa
        if (!::avatarVideoView.isInitialized) {
            Log.d("UIManager", "AvatarVideoView not initialized yet, skipping setDefaultAvatarVideo")
            return
        }
        
        activity.runOnUiThread {
            isCurrentlyPlayingTalking = false // Khởi tạo với video waiting
            playWaitingAvatar()
        }
    }
    
    private fun playWaitingAvatar() {
        if (!::avatarVideoView.isInitialized) {
            Log.d("UIManager", "AvatarVideoView not initialized yet, skipping playWaitingAvatar")
            return
        }
        
        try {
            val videoPath = "android.resource://${activity.packageName}/raw/waiting_avatar"
            avatarVideoView.setVideoURI(android.net.Uri.parse(videoPath))
            avatarVideoView.setOnPreparedListener { mediaPlayer ->
                mediaPlayer.isLooping = true
                mediaPlayer.setVolume(0f, 0f) // Tắt âm thanh
            }
            avatarVideoView.setOnCompletionListener { mediaPlayer ->
                // Tự động phát lại khi kết thúc
                mediaPlayer.start()
            }
            avatarVideoView.start()
            Log.d("UIManager", "Started playing waiting avatar video")
        } catch (e: Exception) {
            Log.e("UIManager", "Error playing waiting avatar video", e)
        }
    }
    
    private fun playTalkingAvatar() {
        if (!::avatarVideoView.isInitialized) {
            Log.d("UIManager", "AvatarVideoView not initialized yet, skipping playTalkingAvatar")
            return
        }
        
        try {
            val videoPath = "android.resource://${activity.packageName}/raw/talking_avatar"
            avatarVideoView.setVideoURI(android.net.Uri.parse(videoPath))
            avatarVideoView.setOnPreparedListener { mediaPlayer ->
                mediaPlayer.isLooping = true
                mediaPlayer.setVolume(0f, 0f) // Tắt âm thanh
            }
            avatarVideoView.setOnCompletionListener { mediaPlayer ->
                // Tự động phát lại khi kết thúc
                mediaPlayer.start()
            }
            avatarVideoView.start()
            Log.d("UIManager", "Started playing talking avatar video")
        } catch (e: Exception) {
            Log.e("UIManager", "Error playing talking avatar video", e)
        }
    }
    
    fun switchToTalkingAvatar() {
        if (isAIResponding || isAIPlaying) {
            playTalkingAvatar()
        }
    }
    
    fun switchToWaitingAvatar() {
        if (!isAIResponding && !isAIPlaying && !isSpeaking) {
            playWaitingAvatar()
        }
    }
    
    private fun updateAvatarVideo() {
        // Chỉ chuyển đổi video khi thực sự cần thiết
        val shouldPlayTalking = isAIPlaying // Chỉ khi AI thực sự đang phát âm thanh
        
        // Tránh chuyển đổi video không cần thiết
        if (shouldPlayTalking == isCurrentlyPlayingTalking) {
            return // Video đã đang phát đúng trạng thái
        }
        
        // Thêm delay nhỏ để tránh chuyển đổi quá nhanh
        activity.runOnUiThread {
            if (shouldPlayTalking) {
                // AI đang phát âm thanh - phát video talking
                playTalkingAvatar()
                isCurrentlyPlayingTalking = true
            } else {
                // AI không phát âm thanh - phát video waiting
                playWaitingAvatar()
                isCurrentlyPlayingTalking = false
            }
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
        // Chỉ chuyển đổi video nếu AI không đang phát âm thanh
        if (!isAIPlaying) {
            updateAvatarVideo()
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
        // Không chuyển đổi video khi AI lắng nghe - giữ nguyên video hiện tại
        // updateAvatarVideo()
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
        // Chỉ chuyển đổi video nếu AI thực sự đang phát âm thanh
        if (isAIPlaying) {
            updateAvatarVideo()
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
        // Không chuyển đổi video khi AI suy nghĩ - giữ nguyên video hiện tại
        // updateAvatarVideo()
    }
}
