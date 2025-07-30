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
    private lateinit var micIcon: ImageView
    private lateinit var chatLogContainer: ScrollView
    
    // Status variables
    private var isConnected = false
    private var isSpeaking = false
    
    fun setCallback(callback: UICallback) {
        this.callback = callback
    }
    
    fun initializeViews() {
        imageView = activity.findViewById(R.id.imageView)
        captureButton = activity.findViewById(R.id.captureButton)
        startButton = activity.findViewById(R.id.startButton)
        stopButton = activity.findViewById(R.id.stopButton)
        chatLog = activity.findViewById(R.id.chatLog)
        statusIndicator = activity.findViewById(R.id.statusIndicator)
        micButton = activity.findViewById(R.id.micButton)
        homeButton = activity.findViewById(R.id.homeButton)
        micIcon = activity.findViewById(R.id.micIcon)
        chatLogContainer = activity.findViewById(R.id.chatLogContainer)
        
        setupClickListeners()
        updateStatusIndicator()
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
    
    private fun updateStatusIndicator() {
        activity.runOnUiThread {
            when {
                !isConnected -> {
                    statusIndicator.setImageResource(R.drawable.baseline_error_24)
                    statusIndicator.setColorFilter(android.graphics.Color.RED)
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
    
    fun getImageView(): ImageView = imageView
    
    fun showToast(message: String) {
        activity.runOnUiThread {
            Toast.makeText(activity, message, Toast.LENGTH_SHORT).show()
        }
    }
}
