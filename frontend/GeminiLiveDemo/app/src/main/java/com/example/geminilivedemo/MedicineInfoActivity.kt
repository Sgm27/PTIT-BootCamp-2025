package com.example.geminilivedemo

import android.content.Intent
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.os.Bundle
import android.util.Base64
import android.util.Log
import android.view.View
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.widget.Toolbar
import com.google.android.material.button.MaterialButton
import com.google.android.material.card.MaterialCardView
import kotlinx.coroutines.*
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException
import java.util.concurrent.TimeUnit
import com.example.geminilivedemo.data.ApiConfig
import kotlin.math.roundToInt

class MedicineInfoActivity : AppCompatActivity() {
    
    companion object {
        private const val TAG = "MedicineInfoActivity"
        const val EXTRA_IMAGE_BASE64 = "extra_image_base64"
        const val EXTRA_MEDICINE_NAME = "extra_medicine_name"
    }
    
    // UI Components
    private lateinit var toolbar: Toolbar
    private lateinit var backButton: ImageView
    private lateinit var medicineImageView: ImageView
    private lateinit var medicineNameTextView: TextView
    private lateinit var medicineInfoTextView: TextView
    
    // Layout states
    private lateinit var loadingLayout: View
    private lateinit var contentLayout: View
    private lateinit var errorLayout: View
    private lateinit var errorTextView: TextView
    private lateinit var retryButton: MaterialButton
    
    // Action buttons
    private lateinit var saveButton: MaterialButton
    private lateinit var shareButton: MaterialButton
    
    // Voice chat components
    private lateinit var voiceChatButton: FrameLayout
    private lateinit var micIcon: ImageView
    
    // Managers for voice chat
    private lateinit var audioManager: AudioManager
    private lateinit var webSocketManager: WebSocketManager
    private lateinit var globalConnectionManager: GlobalConnectionManager
    
    // Data
    private var imageBase64: String? = null
    private var medicineName: String? = null
    private var medicineInfo: String? = null
    
    // HTTP client
    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(60, TimeUnit.SECONDS)
        .build()
    
    // Coroutine scope
    private val activityScope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_medicine_info)
        
        Log.d(TAG, "MedicineInfoActivity onCreate")
        
        // Get data from intent
        imageBase64 = intent.getStringExtra(EXTRA_IMAGE_BASE64)
        medicineName = intent.getStringExtra(EXTRA_MEDICINE_NAME)
        
        Log.d(TAG, "Received imageBase64: ${imageBase64?.take(100)}...")
        Log.d(TAG, "Received medicineName: $medicineName")
        
        if (imageBase64.isNullOrEmpty()) {
            Log.e(TAG, "No image data provided")
            Toast.makeText(this, "Không có dữ liệu hình ảnh", Toast.LENGTH_SHORT).show()
            finish()
            return
        }
        
        initializeViews()
        setupClickListeners()
        initializeVoiceChat()
        
        // Delay display image to ensure layout is ready
        medicineImageView.post {
            displayImage()
        }
        
        analyzeMedicine()
    }
    
    private fun initializeViews() {
        // Initialize toolbar
        toolbar = findViewById(R.id.toolbar)
        setSupportActionBar(toolbar)
        supportActionBar?.setDisplayShowTitleEnabled(false)
        
        // Initialize UI components
        backButton = findViewById(R.id.backButton)
        medicineImageView = findViewById(R.id.medicineImageView)
        medicineNameTextView = findViewById(R.id.medicineNameTextView)
        medicineInfoTextView = findViewById(R.id.medicineInfoTextView)
        
        // Initialize layout states
        loadingLayout = findViewById(R.id.loadingLayout)
        contentLayout = findViewById(R.id.contentLayout)
        errorLayout = findViewById(R.id.errorLayout)
        errorTextView = findViewById(R.id.errorTextView)
        retryButton = findViewById(R.id.retryButton)
        
        // Initialize action buttons
        saveButton = findViewById(R.id.saveButton)
        shareButton = findViewById(R.id.shareButton)
        
        // Initialize voice chat components
        voiceChatButton = findViewById<FrameLayout>(R.id.voiceChatButton)
        micIcon = findViewById<ImageView>(R.id.micIcon)
        
        // Set initial state
        showLoadingState()
        
        // Set placeholder image initially
        medicineImageView.setImageResource(R.drawable.medicine_placeholder)
        Log.d(TAG, "ImageView initialized with placeholder")
    }
    
    private fun setupClickListeners() {
        backButton.setOnClickListener {
            finish()
        }
        
        retryButton.setOnClickListener {
            analyzeMedicine()
        }
        
        saveButton.setOnClickListener {
            saveMedicine()
        }
        
        shareButton.setOnClickListener {
            shareMedicine()
        }
        
        voiceChatButton.setOnClickListener(View.OnClickListener {
            // Toggle recording - allow voice chat even when analyzing medicine
            if (audioManager.isCurrentlyRecording()) {
                Log.d(TAG, "Stopping audio recording")
                audioManager.stopAudioInput()
            } else {
                // Check if WebSocket is connected before starting recording
                if (webSocketManager.isWebSocketConnected()) {
                    Log.d(TAG, "Starting audio recording")
                    // Allow voice chat even when medicine analysis is in progress
                    audioManager.startAudioInput()
                } else {
                    Log.w(TAG, "WebSocket not connected, cannot start recording")
                    Toast.makeText(this, "Không thể kết nối với Gemini. Vui lòng thử lại.", Toast.LENGTH_SHORT).show()
                }
            }
        })
    }
    
    private fun displayImage() {
        try {
            Log.d(TAG, "Displaying image, base64 length: ${imageBase64?.length}")
            
            // Decode base64 image
            val imageBytes = Base64.decode(imageBase64, Base64.DEFAULT)
            Log.d(TAG, "Decoded image bytes: ${imageBytes.size} bytes")
            
            // Use optimized bitmap decoding like CameraManager
            val options = BitmapFactory.Options().apply {
                inJustDecodeBounds = true
            }
            BitmapFactory.decodeByteArray(imageBytes, 0, imageBytes.size, options)
            
            val (originalWidth, originalHeight) = options.outWidth to options.outHeight
            val scaleFactor = calculateScaleFactor(originalWidth, originalHeight, Constants.MAX_IMAGE_DIMENSION)
            
            options.inJustDecodeBounds = false
            options.inSampleSize = scaleFactor
            
            val scaledBitmap = BitmapFactory.decodeByteArray(imageBytes, 0, imageBytes.size, options)
            
            if (scaledBitmap != null) {
                Log.d(TAG, "Bitmap created successfully: ${scaledBitmap.width}x${scaledBitmap.height}")
                
                // Scale bitmap for preview like CameraManager
                val previewBitmap = scaleBitmapForPreview(scaledBitmap)
                medicineImageView.setImageBitmap(previewBitmap)
                Log.d(TAG, "Image displayed successfully")
                
                // Clean up resources like CameraManager
                scaledBitmap.recycle()
                
                // Force layout update
                medicineImageView.requestLayout()
                medicineImageView.invalidate()
            } else {
                Log.e(TAG, "Failed to decode image")
                medicineImageView.setImageResource(R.drawable.medicine_placeholder)
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error displaying image", e)
            medicineImageView.setImageResource(R.drawable.medicine_placeholder)
        }
    }
    
    private fun calculateScaleFactor(width: Int, height: Int, maxDimension: Int): Int {
        val scaleFactor = when {
            width > height -> width.toFloat() / maxDimension
            else -> height.toFloat() / maxDimension
        }
        return when {
            scaleFactor <= 1 -> 1
            scaleFactor <= 2 -> 2
            scaleFactor <= 4 -> 4
            else -> 8
        }.coerceAtLeast(1)
    }
    
    private fun scaleBitmapForPreview(bitmap: Bitmap): Bitmap {
        val maxWidth = resources.displayMetrics.widthPixels
        val scaleFactor = maxWidth.toFloat() / bitmap.width
        return Bitmap.createScaledBitmap(
            bitmap,
            maxWidth,
            (bitmap.height * scaleFactor).roundToInt(),
            true
        )
    }
    
    private fun analyzeMedicine() {
        showLoadingState()
        
        activityScope.launch {
            try {
                val result = withContext(Dispatchers.IO) {
                    callMedicineAnalysisAPI()
                }
                
                if (result.success) {
                    medicineInfo = result.info
                    showContentState()
                } else {
                    showErrorState(result.error ?: "Không thể phân tích thuốc")
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error analyzing medicine", e)
                showErrorState("Lỗi kết nối: ${e.message}")
            }
        }
    }
    
    private suspend fun callMedicineAnalysisAPI(): MedicineAnalysisResult {
        return withContext(Dispatchers.IO) {
            try {
                // Create request body
                val requestBody = JSONObject().apply {
                    put("input", imageBase64)
                }.toString()
                
                val mediaType = "application/json; charset=utf-8".toMediaType()
                val body = requestBody.toRequestBody(mediaType)
                
                // Create request using production API URL
                val apiUrl = "${ApiConfig.BASE_URL}${ApiConfig.Endpoints.ANALYZE_MEDICINE}"
                Log.d(TAG, "Calling API: $apiUrl")
                
                val request = Request.Builder()
                    .url(apiUrl)
                    .post(body)
                    .addHeader("Content-Type", "application/json")
                    .build()
                
                Log.d(TAG, "Calling medicine analysis API...")
                
                // Execute request
                client.newCall(request).execute().use { response ->
                    val responseBody = response.body?.string()
                    Log.d(TAG, "API Response: $responseBody")
                    
                    if (response.isSuccessful && responseBody != null) {
                        val jsonResponse = JSONObject(responseBody)
                        
                        if (jsonResponse.getBoolean("success")) {
                            val result = jsonResponse.getString("result")
                            
                            // Extract medicine name and info from OpenAI Vision response
                            val medicineName = extractMedicineName(result)
                            val medicineInfo = formatMedicineInfo(result)
                            
                            MedicineAnalysisResult(
                                success = true,
                                name = medicineName,
                                info = medicineInfo
                            )
                        } else {
                            val error = jsonResponse.optString("result", "Unknown error")
                            MedicineAnalysisResult(success = false, error = error)
                        }
                    } else {
                        val error = "HTTP ${response.code}: ${response.message}"
                        MedicineAnalysisResult(success = false, error = error)
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "API call failed", e)
                MedicineAnalysisResult(success = false, error = e.message ?: "Unknown error")
            }
        }
    }
    
    private fun extractMedicineName(result: String): String {
        // Try to extract medicine name from the result
        // This is a simple extraction - you might want to improve this based on your API response format
        return result.split("\n").firstOrNull()?.trim() ?: "Thuốc không xác định"
    }
    
    private fun formatMedicineInfo(result: String): String {
        // Format the medicine information for display
        return result.trim()
    }
    
    private fun initializeVoiceChat() {
        try {
            Log.d(TAG, "Initializing voice chat...")
            
            // Get GlobalConnectionManager from Application
            globalConnectionManager = (application as GeminiLiveApplication).getGlobalConnectionManager()
            
            // Get managers from GlobalConnectionManager
            audioManager = globalConnectionManager.getAudioManager()!!
            webSocketManager = globalConnectionManager.getWebSocketManager()!!
            
            Log.d(TAG, "Managers obtained successfully")
            
            // Ensure WebSocket is connected before setting up callbacks
            if (!webSocketManager.isWebSocketConnected()) {
                Log.d(TAG, "WebSocket not connected, attempting to connect...")
                webSocketManager.connect()
                
                // Wait a bit for connection to establish
                activityScope.launch {
                    delay(2000) // Wait 2 seconds for connection
                    if (webSocketManager.isWebSocketConnected()) {
                        Log.d(TAG, "WebSocket connected successfully")
                        setupWebSocketCallbacks()
                    } else {
                        Log.e(TAG, "Failed to connect WebSocket")
                        runOnUiThread {
                            Toast.makeText(this@MedicineInfoActivity, "Không thể kết nối với Gemini", Toast.LENGTH_SHORT).show()
                        }
                    }
                }
            } else {
                Log.d(TAG, "WebSocket already connected")
                setupWebSocketCallbacks()
            }
            
            // Setup AudioManager callbacks with better audio quality handling like MainActivity
            audioManager.setCallback(object : AudioManager.AudioManagerCallback {
                override fun onAudioChunkReady(base64Audio: String) {
                    Log.d(TAG, "Audio chunk ready, length: ${base64Audio.length}")
                    // Check WebSocket connection before sending
                    if (webSocketManager.isWebSocketConnected()) {
                        sendVoiceMessage(base64Audio)
                    } else {
                        Log.w(TAG, "WebSocket not connected, cannot send audio")
                        runOnUiThread {
                            Toast.makeText(this@MedicineInfoActivity, "Mất kết nối với Gemini", Toast.LENGTH_SHORT).show()
                        }
                    }
                }
                
                override fun onAudioRecordingStarted() {
                    Log.d(TAG, "Audio recording started")
                    updateVoiceChatUI(true)
                }
                
                override fun onAudioRecordingStopped() {
                    Log.d(TAG, "Audio recording stopped")
                    updateVoiceChatUI(false)
                    if (webSocketManager.isWebSocketConnected()) {
                        webSocketManager.sendEndOfStreamMessage()
                    }
                }
                
                override fun onAudioPlaybackStarted() {
                    Log.d(TAG, "Audio playback started - AI is speaking")
                }
                
                override fun onAudioPlaybackStopped() {
                    Log.d(TAG, "Audio playback stopped - AI finished speaking")
                }
            })
            
            Log.d(TAG, "Voice chat initialized successfully")
            
        } catch (e: Exception) {
            Log.e(TAG, "Error initializing voice chat", e)
            runOnUiThread {
                Toast.makeText(this, "Lỗi khởi tạo voice chat: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    private fun setupWebSocketCallbacks() {
        // Setup WebSocketManager callbacks with better response handling
        webSocketManager.setCallback(object : WebSocketManager.WebSocketCallback {
            override fun onConnected() {
                Log.d(TAG, "WebSocket connected")
            }
            
            override fun onDisconnected() {
                Log.d(TAG, "WebSocket disconnected")
            }
            
            override fun onError(exception: Exception?) {
                Log.e(TAG, "WebSocket Error: ${exception?.message}")
                
                // Provide more specific error messages like CameraManager
                val errorMessage = when {
                    exception?.message?.contains("timeout", ignoreCase = true) == true -> "Kết nối bị timeout"
                    exception?.message?.contains("network", ignoreCase = true) == true -> "Lỗi mạng"
                    exception?.message?.contains("connection", ignoreCase = true) == true -> "Không thể kết nối"
                    else -> "Lỗi kết nối: ${exception?.message ?: "Không xác định"}"
                }
                
                runOnUiThread {
                    Toast.makeText(this@MedicineInfoActivity, errorMessage, Toast.LENGTH_SHORT).show()
                }
            }
            
            override fun onMessageReceived(response: Response) {
                // Handle text response if any
                response.text?.let { text ->
                    Log.d(TAG, "Received text response: $text")
                    // Show text response in toast for user feedback on main thread
                    runOnUiThread {
                        Toast.makeText(this@MedicineInfoActivity, "AI: $text", Toast.LENGTH_LONG).show()
                    }
                }
                
                // Handle audio response with better quality like CameraManager handles image data
                response.audioData?.let { audioData ->
                    Log.d(TAG, "Received audio response, length: ${audioData.length}")
                    
                    // Validate audio data before playing
                    if (audioData.isNotBlank()) {
                        try {
                            val audioBytes = Base64.decode(audioData, Base64.DEFAULT)
                            Log.d(TAG, "Playing audio chunk: ${audioBytes.size} bytes")
                            audioManager.ingestAudioChunkToPlay(audioData)
                        } catch (e: Exception) {
                            Log.e(TAG, "Error decoding audio data", e)
                            runOnUiThread {
                                Toast.makeText(this@MedicineInfoActivity, "Lỗi phát âm thanh", Toast.LENGTH_SHORT).show()
                            }
                        }
                    } else {
                        Log.w(TAG, "Empty audio data received")
                    }
                }
            }
        })
    }
    
    private fun updateVoiceChatUI(isRecording: Boolean) {
        if (isRecording) {
            micIcon.setImageResource(R.drawable.baseline_stop_24)
        } else {
            micIcon.setImageResource(R.drawable.baseline_mic_off_24)
        }
    }
    
    private fun sendVoiceMessage(base64Audio: String) {
        Log.d(TAG, "Sending voice message with medicine image context")
        
        // Check if WebSocket is connected
        if (!webSocketManager.isWebSocketConnected()) {
            Log.w(TAG, "WebSocket not connected, attempting to reconnect...")
            
            // Try to reconnect
            webSocketManager.connect()
            
            // Wait a bit and try again
            activityScope.launch {
                delay(3000) // Wait 3 seconds for reconnection
                if (webSocketManager.isWebSocketConnected()) {
                    Log.d(TAG, "WebSocket reconnected, sending message now")
                    sendVoiceMessageInternal(base64Audio)
                } else {
                    Log.e(TAG, "Failed to reconnect WebSocket")
                    runOnUiThread {
                        Toast.makeText(this@MedicineInfoActivity, "Không thể kết nối với Gemini. Vui lòng thử lại.", Toast.LENGTH_SHORT).show()
                    }
                }
            }
            return
        }
        
        // WebSocket is connected, send message immediately
        sendVoiceMessageInternal(base64Audio)
    }
    
    private fun sendVoiceMessageInternal(base64Audio: String) {
        // Validate audio data like CameraManager validates image data
        if (base64Audio.isBlank()) {
            Log.w(TAG, "Empty audio data received")
            return
        }
        
        // Send voice message with the medicine image as context
        // This will allow Gemini to see the medicine image while processing the voice input
        try {
            // Log audio data size for debugging
            val audioBytes = Base64.decode(base64Audio, Base64.DEFAULT)
            Log.d(TAG, "Sending audio chunk: ${audioBytes.size} bytes")
            
            webSocketManager.sendVoiceMessage(base64Audio, imageBase64)
            Log.d(TAG, "Voice message sent successfully with medicine context")
        } catch (e: Exception) {
            Log.e(TAG, "Error sending voice message", e)
            runOnUiThread {
                Toast.makeText(this, "Lỗi gửi tin nhắn: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    private fun showLoadingState() {
        loadingLayout.visibility = View.VISIBLE
        contentLayout.visibility = View.GONE
        errorLayout.visibility = View.GONE
        
        medicineNameTextView.text = getString(R.string.loading_medicine_name)
    }
    
    private fun showContentState() {
        loadingLayout.visibility = View.GONE
        contentLayout.visibility = View.VISIBLE
        errorLayout.visibility = View.GONE
        
        // Update medicine info
        medicineInfo?.let { info ->
            // Extract medicine name from the first line
            val lines = info.split("\n")
            val extractedName = lines.firstOrNull()?.trim() ?: "Thuốc không xác định"
            medicineNameTextView.text = extractedName
            
            // Display full medicine info
            medicineInfoTextView.text = info
        }
    }
    
    private fun showErrorState(error: String) {
        loadingLayout.visibility = View.GONE
        contentLayout.visibility = View.GONE
        errorLayout.visibility = View.VISIBLE
        
        errorTextView.text = error
    }
    
    private fun saveMedicine() {
        // TODO: Implement save medicine functionality
        Log.d(TAG, "Save medicine feature not yet implemented")
    }
    
    private fun shareMedicine() {
        try {
            val shareText = buildString {
                append("Thông tin thuốc:\n\n")
                medicineName?.let { append("Tên thuốc: $it\n\n") }
                medicineInfo?.let { append("Thông tin: $it") }
            }
            
            val intent = Intent(Intent.ACTION_SEND).apply {
                type = "text/plain"
                putExtra(Intent.EXTRA_TEXT, shareText)
                putExtra(Intent.EXTRA_SUBJECT, "Thông tin thuốc")
            }
            
            startActivity(Intent.createChooser(intent, "Chia sẻ thông tin thuốc"))
        } catch (e: Exception) {
            Log.e(TAG, "Error sharing medicine info", e)
            Toast.makeText(this, "Không thể chia sẻ thông tin", Toast.LENGTH_SHORT).show()
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        activityScope.cancel()
        
        // Stop recording if active
        if (::audioManager.isInitialized && audioManager.isCurrentlyRecording()) {
            audioManager.stopAudioInput()
        }
        
        // Note: Callbacks will be automatically cleaned up when managers are destroyed
        // No need to set callbacks to null as the interfaces don't allow null values
    }
    
    override fun onBackPressed() {
        // Stop recording if active
        if (::audioManager.isInitialized && audioManager.isCurrentlyRecording()) {
            audioManager.stopAudioInput()
        }
        super.onBackPressed()
    }
    
    override fun onPause() {
        super.onPause()
        // Pause recording when app goes to background
        if (::audioManager.isInitialized && audioManager.isCurrentlyRecording()) {
            audioManager.stopAudioInput()
        }
    }
    
    override fun onResume() {
        super.onResume()
        // Re-initialize voice chat when returning to foreground
        if (::globalConnectionManager.isInitialized) {
            initializeVoiceChat()
        }
    }
    
    data class MedicineAnalysisResult(
        val success: Boolean,
        val name: String? = null,
        val info: String? = null,
        val error: String? = null
    )
} 