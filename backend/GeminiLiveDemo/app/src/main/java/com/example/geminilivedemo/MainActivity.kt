package com.example.geminilivedemo

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import kotlinx.coroutines.*

class MainActivity : AppCompatActivity() {

    // Managers
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

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        initializeManagers()
        setupCallbacks()
        
        uiManager.initializeViews()
        
        // Start background listening service
        serviceManager.startListeningService()
        isBackgroundServiceRunning = true
        uiManager.setBackgroundServiceRunning(isBackgroundServiceRunning)
        
        // Pause service listening since app is in foreground
        serviceManager.pauseListeningService()
        
        // Delay WebSocket connection to allow UI to fully initialize
        android.os.Handler(android.os.Looper.getMainLooper()).postDelayed({
            Log.d("MainActivity", "Initiating WebSocket connection after UI setup")
            webSocketManager.connect()
        }, 1000) // 1 second delay
    }
    
    private fun initializeManagers() {
        audioManager = AudioManager(this)
        webSocketManager = WebSocketManager()
        cameraManager = CameraManager(this)
        permissionHelper = PermissionHelper(this)
        uiManager = UIManager(this)
        serviceManager = ServiceManager(this)
        voiceNotificationManager = VoiceNotificationManager(this)
        voiceNotificationWebSocketManager = VoiceNotificationWebSocketManager(webSocketManager)
    }
    
    private fun setupCallbacks() {
        // Setup AudioManager callbacks
        audioManager.setCallback(object : AudioManager.AudioManagerCallback {
            override fun onAudioChunkReady(base64Audio: String) {
                Log.d("MainActivity", "Audio chunk ready, length: ${base64Audio.length}")
                sendVoiceMessage(base64Audio)
            }
            
            override fun onAudioRecordingStarted() {
                uiManager.updateMicIcon(true)
                uiManager.setSpeakingStatus(true)
            }
            
            override fun onAudioRecordingStopped() {
                uiManager.updateMicIcon(false)
                uiManager.setSpeakingStatus(false)
                webSocketManager.sendEndOfStreamMessage()
            }
            
            override fun onAudioPlaybackStarted() {
                // Audio playback started -> AI is speaking
                Log.d("MainActivity", "Audio playback started")
                uiManager.setAIPlayingStatus(true)
                // Hiển thị tín hiệu màu tím khi AI đang phát âm thanh
                uiManager.setAIRespondingStatus(true)
            }
            
            override fun onAudioPlaybackStopped() {
                // Audio playback stopped -> AI finished speaking
                Log.d("MainActivity", "Audio playback stopped")
                uiManager.setAIPlayingStatus(false)
                // Tắt hiển thị tín hiệu màu tím
                uiManager.setAIRespondingStatus(false)
            }
        })
        
        // Setup WebSocketManager callbacks
        webSocketManager.setCallback(object : WebSocketManager.WebSocketCallback {
            override fun onConnected() {
                uiManager.setConnectionStatus(true)
            }
            
            override fun onDisconnected() {
                uiManager.setConnectionStatus(false)
                uiManager.showToast("Connection closed")
            }
            
            override fun onError(exception: Exception?) {
                Log.e("MainActivity", "WebSocket Error: ${exception?.message}")
                // Update UI only if the WebSocket is no longer open
                if (!webSocketManager.isWebSocketConnected()) {
                    uiManager.setConnectionStatus(false)
                }
            }
            
            override fun onMessageReceived(response: Response) {
                // Set AI responding status when receiving any response from AI
                uiManager.setAIRespondingStatus(true)
                
                response.text?.let { text ->
                    uiManager.displayMessage("GEMINI: $text")
                }
                
                response.audioData?.let { audioData ->
                    audioManager.ingestAudioChunkToPlay(audioData)
                }
                
                // Clear AI responding status after a short delay nếu AI không còn phát âm thanh
                android.os.Handler(android.os.Looper.getMainLooper()).postDelayed({
                    if (!audioManager.isCurrentlyPlaying()) {
                        uiManager.setAIRespondingStatus(false)
                    }
                }, 1500) // 1.5 seconds safety delay
                
                // Handle voice notification responses through VoiceNotificationWebSocketManager
                response.voiceNotificationData?.let { voiceData ->
                    Log.d("MainActivity", "Received voice notification, delegating to VoiceNotificationWebSocketManager")
                    voiceNotificationWebSocketManager.handleVoiceNotificationResponse(response)
                }
            }
        })
        
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
                cameraManager.openCamera()
            }
            
            override fun onAudioPermissionGranted() {
                audioManager.startAudioInput()
            }
            
            override fun onPermissionDenied(permission: String) {
                Log.w("MainActivity", "$permission permission denied")
            }
        })
        
        // Setup VoiceNotificationManager callbacks
        voiceNotificationManager.setCallback(object : VoiceNotificationManager.VoiceNotificationCallback {
            override fun onVoiceNotificationGenerated(voiceData: VoiceNotificationData) {
                Log.d("MainActivity", "Voice notification generated via HTTP API")
                voiceData.audioBase64?.let { audioBase64 ->
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
                permissionHelper.checkCameraPermission()
            }
            
            override fun onMicButtonClicked() {
                if (audioManager.isCurrentlyRecording()) {
                    audioManager.stopAudioInput()
                } else {
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
                // This is handled directly in UIManager now
            }
            
            override fun onNotificationButtonClicked() {
                openNotificationActivity()
            }
            
            override fun onProfileButtonClicked() {
                openProfileActivity()
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
                        
                        // Display the captured image on the main screen
                        uiManager.displayCapturedImage(imageB64)
                        
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
                currentFrameB64 = cameraManager.handleCameraResult(requestCode, resultCode, data, uiManager.getImageView())
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
        audioManager.cleanup()
        webSocketManager.disconnect()
        voiceNotificationManager.cleanup()
        // Resume background service when app is completely closed
        if (isBackgroundServiceRunning) {
            serviceManager.resumeListeningService()
        }
    }
    
    override fun onPause() {
        super.onPause()
        // App is going to background - pause our connection and resume service
        Log.d("MainActivity", "App going to background - resuming service listening")
        if (isBackgroundServiceRunning) {
            serviceManager.resumeListeningService()
            // Give service a moment to reconnect before we disconnect
            Handler(Looper.getMainLooper()).postDelayed({
                webSocketManager.disconnect()
                Log.d("MainActivity", "App WebSocket disconnected after service reconnection")
            }, 1000) // 1 second delay
        } else {
            // No background service, disconnect immediately
            webSocketManager.disconnect()
        }
    }
    
    override fun onResume() {
        super.onResume()
        // App is coming to foreground - pause service and resume our connection
        Log.d("MainActivity", "App coming to foreground - pausing service listening")
        if (isBackgroundServiceRunning) {
            serviceManager.pauseListeningService()
            // Give service a moment to pause and disconnect before we reconnect
            android.os.Handler(android.os.Looper.getMainLooper()).postDelayed({
                if (!webSocketManager.isConnected()) {
                    Log.d("MainActivity", "Reconnecting WebSocket after service pause")
                    webSocketManager.connect()
                } else {
                    Log.d("MainActivity", "WebSocket already connected")
                }
            }, 800) // Slightly longer delay for stability
        } else {
            // No background service, connect if not already connected
            if (!webSocketManager.isConnected()) {
                Log.d("MainActivity", "Connecting WebSocket (no background service)")
                webSocketManager.connect()
            }
        }
        // Update UI to reflect current service status when returning to app
        uiManager.setBackgroundServiceRunning(isBackgroundServiceRunning)
    }
}