package com.example.geminilivedemo

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import kotlinx.coroutines.*
import com.example.geminilivedemo.data.UserPreferences
import android.widget.Toast
import com.example.geminilivedemo.ScannerActivity

class MainActivity : AppCompatActivity(), GlobalConnectionManager.ConnectionStateCallback {
    
    private lateinit var userPreferences: UserPreferences
    private lateinit var globalConnectionManager: GlobalConnectionManager

    // Managers - sẽ được lấy từ GlobalConnectionManager
    private lateinit var audioManager: AudioManager
    private lateinit var webSocketManager: WebSocketManager
    private lateinit var cameraManager: CameraManager
    private lateinit var permissionHelper: PermissionHelper
    private lateinit var uiManager: UIManager
    private lateinit var serviceManager: ServiceManager
    private lateinit var voiceNotificationManager: VoiceNotificationManager
    private lateinit var voiceNotificationWebSocketManager: VoiceNotificationWebSocketManager
    

    
    // State variables
    private var currentFrameB64: String? = null
    private var lastImageSendTime: Long = 0
    private var isBackgroundServiceRunning = false
    private var isChatEnabled = true
    private var isSwitchingToOtherActivity = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize user preferences
        userPreferences = UserPreferences(this)
        
        // Check if user is logged in
        if (!userPreferences.isLoggedIn()) {
            // Redirect to login if not logged in
            val intent = Intent(this, LoginActivity::class.java)
            startActivity(intent)
            finish()
            return
        }
        
        setContentView(R.layout.activity_main)

        // Lấy GlobalConnectionManager từ Application
        globalConnectionManager = (application as GeminiLiveApplication).getGlobalConnectionManager()
        globalConnectionManager.registerCallback(this)
        
        initializeManagers()
        setupCallbacks()
        
        // Đăng ký activity sau khi đã khởi tạo tất cả managers
        globalConnectionManager.registerActivity(this)
        
        uiManager.initializeViews()
        
        // Start background listening service
        serviceManager.startListeningService()
        isBackgroundServiceRunning = true
        globalConnectionManager.setBackgroundServiceRunning(isBackgroundServiceRunning)
        uiManager.setBackgroundServiceRunning(isBackgroundServiceRunning)
        
        // Pause service listening since app is in foreground
        serviceManager.pauseListeningService()
        
        // GlobalConnectionManager sẽ tự động quản lý WebSocket connection
        Log.d("MainActivity", "MainActivity initialized - GlobalConnectionManager will handle connection")
        
        // Show connecting status initially
        uiManager.updateConnectionStatusConnecting()
    }
    
    private fun initializeManagers() {
        // Lấy managers từ GlobalConnectionManager
        audioManager = globalConnectionManager.getAudioManager()!!
        webSocketManager = globalConnectionManager.getWebSocketManager()!!
        serviceManager = globalConnectionManager.getServiceManager()!!
        voiceNotificationManager = globalConnectionManager.getVoiceNotificationManager()!!
        
        // Enable audio continuity to ensure AI audio plays completely across activities
        audioManager.setAudioContinuityEnabled(true)
        
        // Khởi tạo các managers local
        cameraManager = CameraManager(this)
        permissionHelper = PermissionHelper(this)
        uiManager = UIManager(this)
        voiceNotificationWebSocketManager = VoiceNotificationWebSocketManager(webSocketManager)
    }
    
    
    private fun setupCallbacks() {
        Log.d("MainActivity", "Setting up callbacks...")
        
        // Setup AudioManager callbacks
        audioManager.setCallback(object : AudioManager.AudioManagerCallback {
            override fun onAudioChunkReady(base64Audio: String) {
                Log.d("MainActivity", "Audio chunk ready, length: ${base64Audio.length}")
                sendVoiceMessage(base64Audio)
            }
            
            override fun onAudioRecordingStarted() {
                Log.d("MainActivity", "Audio recording started callback triggered")
                if (::uiManager.isInitialized) {
                    uiManager.updateMicIcon(true)
                    uiManager.setSpeakingStatus(true)
                    uiManager.setAIListening()
                }
            }
            
            override fun onAudioRecordingStopped() {
                Log.d("MainActivity", "Audio recording stopped callback triggered")
                if (::uiManager.isInitialized) {
                    uiManager.updateMicIcon(false)
                    uiManager.setSpeakingStatus(false)
                    uiManager.setAIThinking()
                }
                webSocketManager.sendEndOfStreamMessage()
            }
            
            override fun onAudioPlaybackStarted() {
                // Audio playback started -> AI is speaking
                Log.d("MainActivity", "Audio playback started")
                if (::uiManager.isInitialized) {
                    try {
                        uiManager.setAIPlayingStatus(true)
                        uiManager.setAISpeaking()
                        // Hiển thị tín hiệu màu tím khi AI đang phát âm thanh
                        uiManager.setAIRespondingStatus(true)
                    } catch (e: Exception) {
                        Log.e("MainActivity", "Error in onAudioPlaybackStarted", e)
                        // Force video switch as fallback
                        uiManager.forceVideoSwitch(true)
                    }
                }
            }
            
            override fun onAudioPlaybackStopped() {
                // Audio playback stopped -> AI finished speaking
                Log.d("MainActivity", "Audio playback stopped")
                if (::uiManager.isInitialized) {
                    try {
                        uiManager.setAIPlayingStatus(false)
                        uiManager.setAIIdle()
                        // Tắt hiển thị tín hiệu màu tím
                        uiManager.setAIRespondingStatus(false)
                    } catch (e: Exception) {
                        Log.e("MainActivity", "Error in onAudioPlaybackStopped", e)
                        // Force video switch as fallback
                        uiManager.forceVideoSwitch(false)
                    }
                }
            }
        })
        
        Log.d("MainActivity", "AudioManager callbacks setup completed")
        
        // Setup WebSocketManager callbacks
        webSocketManager.setCallback(object : WebSocketManager.WebSocketCallback {
            override fun onConnected() {
                Log.d("MainActivity", "WebSocket connected callback triggered")
                if (::uiManager.isInitialized) {
                    uiManager.setConnectionStatus(true)
                    uiManager.updateConnectionStatusDisplay(true)
                }
            }
            
            override fun onDisconnected() {
                Log.d("MainActivity", "WebSocket disconnected callback triggered")
                if (::uiManager.isInitialized) {
                    uiManager.setConnectionStatus(false)
                    uiManager.updateConnectionStatusDisplay(false)
                    uiManager.showToast("Connection closed")
                }
            }
            
            override fun onError(exception: Exception?) {
                Log.e("MainActivity", "WebSocket Error: ${exception?.message}")
                // Update UI only if the WebSocket is no longer open
                if (!webSocketManager.isWebSocketConnected() && ::uiManager.isInitialized) {
                    uiManager.setConnectionStatus(false)
                    uiManager.updateConnectionStatusDisplay(false)
                }
            }
            
            override fun onMessageReceived(response: Response) {
                // Set AI responding status when receiving any response from AI
                if (::uiManager.isInitialized) {
                    uiManager.setAIRespondingStatus(true)
                }
                
                response.text?.let { text ->
                    if (::uiManager.isInitialized) {
                        uiManager.displayMessage("GEMINI: $text")
                    }
                }
                
                response.audioData?.let { audioData ->
                    audioManager.ingestAudioChunkToPlay(audioData)
                }
                
                // Clear AI responding status after a short delay nếu AI không còn phát âm thanh
                android.os.Handler(android.os.Looper.getMainLooper()).postDelayed({
                    if (!audioManager.isCurrentlyPlaying() && ::uiManager.isInitialized) {
                        uiManager.setAIRespondingStatus(false)
                    }
                }, 1500) // 1.5 seconds safety delay
                
                // Handle voice notification responses through VoiceNotificationWebSocketManager
                response.voiceNotificationData?.let { voiceData ->
                    Log.d("MainActivity", "Received voice notification, delegating to VoiceNotificationWebSocketManager")
                    voiceNotificationWebSocketManager.handleVoiceNotificationResponse(response)
                }
                
                // Handle tool calls from Gemini
                response.toolCallData?.let { toolCall ->
                    Log.d("MainActivity", "Received tool call: ${toolCall.functionName}")
                    handleToolCall(toolCall)
                }
                
                // Handle screen navigation requests
                response.screenNavigationData?.let { navigation ->
                    Log.d("MainActivity", "Received screen navigation request: ${navigation.action}")
                    handleScreenNavigation(navigation)
                }
            }
        })
        
        Log.d("MainActivity", "WebSocketManager callbacks setup completed")
        
        // Setup CameraManager callbacks
        cameraManager.setCallback(object : CameraManager.CameraCallback {
            override fun onImageCaptured(base64Image: String) {
                currentFrameB64 = base64Image
                // Optional: Send image immediately on capture
                // sendVoiceMessage(null, base64Image)
            }
            
            override fun onCameraError(error: String) {
                Log.e("MainActivity", "Camera Error: $error")
            }
        })
        
        // Setup PermissionHelper callbacks
        permissionHelper.setCallback(object : PermissionHelper.PermissionCallback {
            override fun onCameraPermissionGranted() {
                Log.d("MainActivity", "Camera permission granted")
                cameraManager.openCamera()
            }
            
            override fun onAudioPermissionGranted() {
                Log.d("MainActivity", "Audio permission granted, starting audio input")
                audioManager.startAudioInput()
            }
            
            override fun onPermissionDenied(permission: String) {
                Log.w("MainActivity", "$permission permission denied")
            }
        })
        
        Log.d("MainActivity", "PermissionHelper callbacks setup completed")
        
        // Setup VoiceNotificationManager callbacks
        voiceNotificationManager.setCallback(object : VoiceNotificationManager.VoiceNotificationCallback {
            override fun onVoiceNotificationGenerated(voiceData: VoiceNotificationData) {
                Log.d("MainActivity", "Voice notification generated via HTTP API")
                voiceData.audioBase64?.let { audioBase64 ->
                    if (GlobalPlaybackState.isPlaying) {
                        Log.d("MainActivity", "Another audio is playing, skip HTTP enqueue to avoid overlap")
                        return
                    }
                    audioManager.ingestAudioChunkToPlay(audioBase64)
                }
                uiManager.displayMessage("SYSTEM: Voice notification - ${voiceData.notificationText}")
            }
            
            override fun onVoiceNotificationError(error: String) {
                Log.e("MainActivity", "Voice notification error via HTTP API: $error")
                uiManager.displayMessage("ERROR: Voice notification failed - $error")
                // Resume recording in case of error
                audioManager.resumeRecordingAfterVoiceNotification()
            }
            
            override fun onVoiceNotificationStarted() {
                Log.d("MainActivity", "Voice notification started - pausing recording")
                audioManager.pauseRecordingForVoiceNotification()
            }
            
            override fun onVoiceNotificationFinished() {
                Log.d("MainActivity", "Voice notification finished - resuming recording")
                audioManager.resumeRecordingAfterVoiceNotification()
            }
        })
        
        // Setup VoiceNotificationWebSocketManager callbacks
        voiceNotificationWebSocketManager.setCallback(object : VoiceNotificationWebSocketManager.VoiceNotificationWebSocketCallback {
            override fun onVoiceNotificationReceived(voiceData: VoiceNotificationData) {
                Log.d("MainActivity", "Voice notification received via WebSocket: ${voiceData.notificationText}")
                
                // Pause recording to prevent feedback
                Log.d("MainActivity", "Pausing recording for voice notification")
                audioManager.pauseRecordingForVoiceNotification()
                
                voiceData.audioBase64?.let { audioBase64 ->
                    if (GlobalPlaybackState.isPlaying) {
                        Log.d("MainActivity", "Another audio is playing, skip enqueue to avoid overlap")
                        return
                    }
                    Log.d("MainActivity", "Playing voice notification audio")
                    audioManager.ingestAudioChunkToPlay(audioBase64)
                    
                    // Calculate estimated playback duration based on audio data length
                    val estimatedDurationMs = (audioBase64.length / 1000L + 2) * 1000L
                    val duration = estimatedDurationMs.coerceAtLeast(3000L).coerceAtMost(10000L)
                    
                    Log.d("MainActivity", "Estimated voice notification duration: ${duration}ms")
                    
                    // Resume recording after estimated playback time
                    GlobalScope.launch {
                        delay(duration)
                        Log.d("MainActivity", "Resuming recording after voice notification")
                        audioManager.resumeRecordingAfterVoiceNotification()
                    }
                }
                
                // Show notification text on UI
                uiManager.displayMessage("🔊 VOICE NOTIFICATION: ${voiceData.notificationText}")
                
                // Show toast for broadcast notifications
                if (voiceData.service?.contains("broadcast") == true) {
                    uiManager.showToast("Voice notification received!")
                }
            }
            
            override fun onVoiceNotificationError(error: String) {
                Log.e("MainActivity", "Voice notification error via WebSocket: $error")
                uiManager.displayMessage("ERROR: Voice notification failed - $error")
                // Resume recording in case of error
                Log.d("MainActivity", "Resuming recording due to voice notification error")
                audioManager.resumeRecordingAfterVoiceNotification()
            }
        })
        
        // Setup UIManager callbacks
        uiManager.setCallback(object : UIManager.UICallback {
            override fun onCaptureButtonClicked() {
                Log.d("MainActivity", "Capture button clicked - opening Scanner Activity")
                isSwitchingToOtherActivity = true
                val intent = Intent(this@MainActivity, ScannerActivity::class.java)
                startActivityForResult(intent, UIManager.SCANNER_REQUEST_CODE)
            }
            
            override fun onMicButtonClicked() {
                Log.d("MainActivity", "Mic button clicked callback triggered!")
                if (audioManager.isCurrentlyRecording()) {
                    Log.d("MainActivity", "Stopping audio recording")
                    audioManager.stopAudioInput()
                } else {
                    Log.d("MainActivity", "Starting audio recording")
                    permissionHelper.checkRecordAudioPermission()
                }
            }
            
            override fun onHomeButtonClicked() {
                uiManager.toggleChatLog()
            }
            
            override fun onStartButtonClicked() {
                permissionHelper.checkRecordAudioPermission()
            }
            
            override fun onStopButtonClicked() {
                audioManager.stopAudioInput()
            }
            
            override fun onScannerButtonClicked() {
                Log.d("MainActivity", "Scanner button clicked - opening Scanner Activity")
                isSwitchingToOtherActivity = true
                val intent = Intent(this@MainActivity, ScannerActivity::class.java)
                startActivityForResult(intent, UIManager.SCANNER_REQUEST_CODE)
            }
            
            override fun onNotificationButtonClicked() {
                openNotificationActivity()
            }
            
            override fun onProfileButtonClicked() {
                openProfileActivity()
            }
            

            
            override fun onHistoryButtonClicked() {
                openConversationHistoryActivity()
            }
            
            override fun onBackgroundServiceToggled() {
                if (isBackgroundServiceRunning) {
                    // Stopping background service
                    serviceManager.stopService()
                    isBackgroundServiceRunning = false
                } else {
                    // Starting background service
                    serviceManager.startListeningService()
                    serviceManager.pauseListeningService() // Pause immediately since app is in foreground
                    isBackgroundServiceRunning = true
                }
                uiManager.setBackgroundServiceRunning(isBackgroundServiceRunning)
            }
        })
    }
    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        permissionHelper.handlePermissionResult(requestCode, permissions, grantResults)
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        
        Log.d("MainActivity", "onActivityResult called - requestCode: $requestCode, resultCode: $resultCode")
        
        when (requestCode) {
            UIManager.SCANNER_REQUEST_CODE -> {
                Log.d("MainActivity", "Scanner activity result received")
                if (resultCode == RESULT_OK) {
                    val scanResult = data?.getStringExtra("scan_result")
                    val capturedImageBase64 = data?.getStringExtra("captured_image_base64")
                    
                    Log.d("MainActivity", "Scan result: $scanResult")
                    Log.d("MainActivity", "Image base64 length: ${capturedImageBase64?.length ?: 0}")
                    
                    scanResult?.let { result ->
                        uiManager.displayMessage("USER: $result")
                    }
                    
                    // Store the captured image for sending to Gemini
                    capturedImageBase64?.let { imageB64 ->
                        currentFrameB64 = imageB64
                        Log.d("MainActivity", "Captured image stored, length: ${imageB64.length}")
                        
                        // Note: We no longer display captured images on the main screen
                        // as it's now a video avatar. The image will be sent to AI directly.
                        
                        // Check WebSocket connection before sending
                        if (webSocketManager.isConnected()) {
                            Log.d("MainActivity", "WebSocket connected, sending image to Gemini")
                            sendVoiceMessage(null, imageB64)
                        } else {
                            Log.e("MainActivity", "WebSocket not connected, cannot send image")
                            uiManager.displayMessage("ERROR: Not connected to Gemini server")
                        }
                    }
                } else {
                    Log.d("MainActivity", "Scanner activity cancelled or failed")
                }
            }
            else -> {
                currentFrameB64 = cameraManager.handleCameraResult(requestCode, resultCode, data, null)
            }
        }
    }
    
    private fun openNotificationActivity() {
        val intent = Intent(this, NotificationActivity::class.java)
        startActivity(intent)
    }
    
    private fun openProfileActivity() {
        val intent = Intent(this, ProfileActivity::class.java)
        startActivity(intent)
    }
    


    private fun openConversationHistoryActivity() {
        try {
            Log.d("MainActivity", "=== Opening ConversationHistoryActivity ===")
            Log.d("MainActivity", "Current user ID: ${UserPreferences(this).getUserId()}")
            Log.d("MainActivity", "Is logged in: ${UserPreferences(this).isLoggedIn()}")
            Log.d("MainActivity", "API Base URL: ${com.example.geminilivedemo.data.ApiConfig.BASE_URL}")
            
            val intent = Intent(this, ConversationHistoryActivity::class.java)
            Log.d("MainActivity", "Intent created, starting activity...")
            startActivity(intent)
            Log.d("MainActivity", "Activity started successfully")
        } catch (e: Exception) {
            Log.e("MainActivity", "=== ERROR opening ConversationHistoryActivity ===", e)
            Log.e("MainActivity", "Error message: ${e.message}")
            Log.e("MainActivity", "Error cause: ${e.cause}")
            uiManager.showToast("Lỗi mở lịch sử trò chuyện: ${e.message}")
        }
    }
    
    private fun sendVoiceMessage(b64PCM: String?, imageB64: String? = null) {
        val imageToSend = imageB64 ?: currentFrameB64
        Log.d("MainActivity", "sendVoiceMessage called - Audio: ${b64PCM != null}, Image: ${imageToSend != null}")
        
        if (imageToSend != null) {
            Log.d("MainActivity", "Sending image to WebSocketManager, size: ${imageToSend.length}")
        }
        
        webSocketManager.sendVoiceMessage(b64PCM, imageToSend)
        
        // Clear the image after sending to prevent sending it multiple times
        if (imageToSend == currentFrameB64) {
            currentFrameB64 = null
            Log.d("MainActivity", "Cleared currentFrameB64 after sending")
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        Log.d("MainActivity", "MainActivity onDestroy called")
        
        // Cleanup UIManager to prevent video-related crashes
        if (::uiManager.isInitialized) {
            uiManager.cleanup()
        }
        
        // Unregister from GlobalConnectionManager
        try {
            globalConnectionManager.unregisterCallback(this)
            globalConnectionManager.unregisterActivity(this)
        } catch (e: Exception) {
            Log.e("MainActivity", "Error unregistering from GlobalConnectionManager", e)
        }
        
        // Clear callbacks to prevent memory leaks (only for classes that have clearCallback method)
        if (::audioManager.isInitialized) {
            audioManager.clearCallback()
        }
        if (::webSocketManager.isInitialized) {
            webSocketManager.clearCallback()
        }
        // Note: cameraManager, permissionHelper, voiceNotificationManager, and voiceNotificationWebSocketManager 
        // don't have clearCallback methods, so we skip them
    }
    
    override fun onPause() {
        super.onPause()
        Log.d("MainActivity", "MainActivity paused - checking if app is going to background")
        
        // Check if app is going to background (no other activities in foreground)
        val isAppGoingToBackground = isFinishing || (!isChangingConfigurations && !isSwitchingToOtherActivity)
        
        if (isAppGoingToBackground) {
            Log.d("MainActivity", "App going to background - pausing service and disconnecting WebSocket")
            // Disable chat UI khi pause
            isChatEnabled = false
            updateChatUI()
            
            // Only disconnect WebSocket if no audio is playing
            if (audioManager.hasAudioToPlay()) {
                Log.d("MainActivity", "Audio is playing or queued, keeping WebSocket alive for audio completion")
            } else {
                Log.d("MainActivity", "No audio to play, disconnecting WebSocket to save resources")
                serviceManager.disconnectWebSocket()
            }
        } else {
            Log.d("MainActivity", "App staying in foreground (switching to another activity) - keeping service active")
            // Don't pause service when switching to another activity (like ScannerActivity)
            // This allows AI to continue playing audio in other activities
        }
        
        // Reset the flag
        isSwitchingToOtherActivity = false
    }
    
    override fun onResume() {
        super.onResume()
        Log.d("MainActivity", "MainActivity resumed - enabling chat")
        
        // Enable chat UI khi resume
        isChatEnabled = true
        updateChatUI()
        
        // Recover video state if needed
        if (::uiManager.isInitialized) {
            try {
                // Reset video state to ensure consistency
                uiManager.resetVideoState()
                
                // Set correct video based on current audio state
                if (audioManager.isCurrentlyPlaying()) {
                    uiManager.forceVideoSwitch(true)
                } else {
                    uiManager.forceVideoSwitch(false)
                }
            } catch (e: Exception) {
                Log.e("MainActivity", "Error recovering video state in onResume", e)
            }
        }
        
        // Only pause background service if it was running and we're coming back from background
        // Don't pause when returning from other activities (like ScannerActivity)
        if (isBackgroundServiceRunning && !isChangingConfigurations) {
            Log.d("MainActivity", "Resuming from background - pausing background service")
            serviceManager.pauseListeningService()
        } else {
            Log.d("MainActivity", "Resuming from another activity - keeping service active for audio continuity")
        }
        
        // Update UI to reflect current service status
        if (::uiManager.isInitialized) {
            uiManager.setBackgroundServiceRunning(isBackgroundServiceRunning)
        }
        
        // Đăng ký lại activity với GlobalConnectionManager trước
        globalConnectionManager.registerActivity(this)
        
        // Sau đó mới setup callbacks để đảm bảo chúng không bị clear
        setupCallbacks()
        
        // GlobalConnectionManager sẽ tự động đảm bảo connection
    }
    
    // Callback methods từ GlobalConnectionManager.ConnectionStateCallback
    override fun onConnectionStateChanged(isConnected: Boolean) {
        Log.d("MainActivity", "Connection state changed: $isConnected")
        runOnUiThread {
            // Kiểm tra xem uiManager đã được khởi tạo chưa
            if (::uiManager.isInitialized) {
                // Cập nhật UI dựa trên trạng thái connection
                uiManager.updateConnectionStatus(isConnected)
                uiManager.updateConnectionStatusDisplay(isConnected)
            }
        }
    }
    
    override fun onChatAvailabilityChanged(isChatAvailable: Boolean) {
        Log.d("MainActivity", "Chat availability changed: $isChatAvailable")
        runOnUiThread {
            isChatEnabled = isChatAvailable
            // Chỉ update UI nếu uiManager đã được khởi tạo
            if (::uiManager.isInitialized) {
                updateChatUI()
            }
        }
    }
    
    private fun updateChatUI() {
        // Kiểm tra xem uiManager đã được khởi tạo chưa
        if (!::uiManager.isInitialized) {
            Log.d("MainActivity", "uiManager not initialized yet, skipping updateChatUI")
            return
        }
        
        // Cập nhật UI để enable/disable chat controls
        uiManager.setChatEnabled(isChatEnabled)
        
        if (!isChatEnabled) {
            Log.d("MainActivity", "Chat disabled - stopping any ongoing recording")
            // Dừng recording nếu đang recording
            if (audioManager.isRecording()) {
                audioManager.stopAudioInput()
            }
        }
    }
    
    /**
     * Handle tool calls from Gemini AI
     */
    private fun handleToolCall(toolCall: ToolCallData) {
        Log.d("MainActivity", "Handling tool call: ${toolCall.functionName}")
        
        // Display tool call message to user
        if (::uiManager.isInitialized) {
            uiManager.displayMessage("SYSTEM: AI đang thực hiện: ${toolCall.functionName}")
        }
        
        // Log tool call for debugging
        Log.i("MainActivity", "Tool call received - Function: ${toolCall.functionName}, ID: ${toolCall.functionId}")
    }
    
    /**
     * Handle screen navigation requests from Gemini AI
     */
    private fun handleScreenNavigation(navigation: ScreenNavigationData) {
        Log.d("MainActivity", "Handling screen navigation: ${navigation.action}")
        
        // Display navigation message to user
        if (::uiManager.isInitialized) {
            uiManager.displayMessage("SYSTEM: ${navigation.message}")
        }
        
        // Execute navigation based on action
        when (navigation.action) {
            "switch_to_main_screen" -> {
                Log.i("MainActivity", "Switching to main screen")
                // Navigate to main screen (current activity)
                runOnUiThread {
                    // Show success message
                    Toast.makeText(this, "Đã chuyển về màn hình chính", Toast.LENGTH_SHORT).show()
                }
            }
            "switch_to_medicine_scan_screen" -> {
                Log.d("MainActivity", "Switching to medicine scan screen - keeping audio active")
                isSwitchingToOtherActivity = true
                startActivity(Intent(this, ScannerActivity::class.java))
            }
            else -> {
                Log.w("MainActivity", "Unknown navigation action: ${navigation.action}")
                runOnUiThread {
                    Toast.makeText(this, "Hành động không được hỗ trợ: ${navigation.action}", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
    

}