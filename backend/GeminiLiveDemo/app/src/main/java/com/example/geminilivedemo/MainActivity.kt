package com.example.geminilivedemo

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.Log
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    companion object {
        var isAppInForeground = false
    }

    // Managers
    private lateinit var audioManager: AudioManager
    private lateinit var webSocketManager: WebSocketManager
    private lateinit var cameraManager: CameraManager
    private lateinit var permissionHelper: PermissionHelper
    private lateinit var uiManager: UIManager
    private lateinit var serviceManager: ServiceManager
    
    // State variables
    private var currentFrameB64: String? = null
    private var lastImageSendTime: Long = 0
    private var isBackgroundServiceRunning = false
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        initializeManagers()
        setupCallbacks()
        
        uiManager.initializeViews()
        webSocketManager.connect()
        
        // Start background listening service
        serviceManager.startListeningService()
        isBackgroundServiceRunning = true
        uiManager.setBackgroundServiceRunning(isBackgroundServiceRunning)
    }
    
    private fun initializeManagers() {
        audioManager = AudioManager()
        webSocketManager = WebSocketManager()
        cameraManager = CameraManager(this)
        permissionHelper = PermissionHelper(this)
        uiManager = UIManager(this)
        serviceManager = ServiceManager(this)
    }
    
    private fun setupCallbacks() {
        // Setup AudioManager callbacks
        audioManager.setCallback(object : AudioManager.AudioManagerCallback {
            override fun onAudioChunkReady(base64Audio: String) {
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
                uiManager.setAIPlayingStatus(true)
            }
            
            override fun onAudioPlaybackStopped() {
                uiManager.setAIPlayingStatus(false)
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
                uiManager.setConnectionStatus(false)
                Log.e("MainActivity", "WebSocket Error: ${exception?.message}")
            }
            
            override fun onMessageReceived(response: Response) {
                response.text?.let { text ->
                    uiManager.displayMessage("GEMINI: $text")
                }
                
                response.audioData?.let { audioData ->
                    audioManager.ingestAudioChunkToPlay(audioData)
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
        
        // Setup UIManager callbacks
        uiManager.setCallback(object : UIManager.UICallback {
            override fun onCaptureButtonClicked() {
                permissionHelper.checkCameraPermission()
            }
            
            override fun onMicButtonClicked() {
                // Kiểm tra xem AI có đang phát âm thanh không
                if (audioManager.isCurrentlyPlaying()) {
                    return
                }
                
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
                serviceManager.toggleListeningService()
                // Toggle the background service status
                isBackgroundServiceRunning = !isBackgroundServiceRunning
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
        // Note: We don't stop the background service here because 
        // we want it to continue running even when the app is closed
    }
    
    override fun onResume() {
        super.onResume()
        isAppInForeground = true
        
        // Đợi một chút để Service có thời gian ngắt kết nối trước khi MainActivity kết nối lại
        handler.postDelayed({
            if (!webSocketManager.isConnected()) {
                webSocketManager.connect()
            }
        }, 500)
        
        // Update UI to reflect current service status when returning to app
        // In a real implementation, you might query the actual service status
    }
    
    override fun onPause() {
        super.onPause()
        isAppInForeground = false
        
        // Ngắt kết nối WebSocket khi app vào background để tránh trùng lặp
        webSocketManager.disconnect()
        
        // The app is going to background, but service continues running
    }
}