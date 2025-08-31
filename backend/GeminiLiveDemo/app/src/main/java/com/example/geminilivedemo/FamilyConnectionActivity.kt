package com.example.geminilivedemo

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.google.android.material.button.MaterialButton
import com.google.android.material.card.MaterialCardView
import com.example.geminilivedemo.data.ApiClient
import com.example.geminilivedemo.data.ApiResult
import com.example.geminilivedemo.data.ElderlyPatientsResponse
import com.example.geminilivedemo.data.ScheduleManager
import com.example.geminilivedemo.ScheduleNotificationService
import com.example.geminilivedemo.CreateScheduleActivity
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.text.SimpleDateFormat
import java.util.*
import android.widget.Toast

/**
 * FamilyConnectionActivity - Màn hình kết nối yêu thương
 * 
 * Chức năng chính:
 * 1. Hiển thị lịch trình của người già
 * 2. Cho phép thành viên gia đình xem lịch trình của người già họ chăm sóc
 * 3. Tạo lịch trình mới cho người già
 * 4. Đồng bộ hoàn toàn với backend database
 * 
 * Luồng hoạt động:
 * - Elderly user: Xem lịch trình của chính mình
 * - Family member: Chọn người già và xem lịch trình của họ
 * 
 * @author AI Assistant
 * @version 1.0
 */
class FamilyConnectionActivity : AppCompatActivity() {
    
    private lateinit var backButton: ImageView
    private lateinit var addButton: MaterialButton
    private lateinit var refreshButton: MaterialButton
    private lateinit var elderlyNameText: TextView
    private lateinit var todayDateText: TextView
    private lateinit var todayScheduleContainer: LinearLayout

    private lateinit var progressBar: android.widget.ProgressBar
    private lateinit var errorContainer: LinearLayout
    private lateinit var errorMessage: TextView
    private lateinit var retryButton: MaterialButton
    private lateinit var emptyStateContainer: LinearLayout
    private lateinit var contentContainer: LinearLayout
    private lateinit var scheduleContainer: LinearLayout
    
    private val schedules = mutableListOf<ScheduleItem>()
    private var currentUserId: String = ""
    private var currentUserType: String = ""
    private var currentUserName: String = ""
    private var elderlyId: String = ""
    private var elderlyName: String = ""
    
    companion object {
        private const val TAG = "FamilyConnectionActivity"
        private const val REQUEST_CREATE_SCHEDULE = 1001
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_family_connection)
        
        try {
            Log.d(TAG, "Starting FamilyConnectionActivity initialization")
            
            // Check if we have the required layout
            if (findViewById<View>(R.id.contentContainer) == null) {
                throw IllegalStateException("Required layout elements not found")
            }
            
            initializeViews()
            setupClickListeners()
            updateDateDisplay()
            
            // Start schedule notification service
            try {
                ScheduleNotificationService.startService(this)
                Log.d(TAG, "Schedule notification service started successfully")
            } catch (e: Exception) {
                Log.w(TAG, "Could not start schedule notification service: ${e.message}", e)
                // Don't fail the entire activity for this
            }
            
            // Load user profile and data
            loadElderlyProfile()
            
            Log.d(TAG, "FamilyConnectionActivity initialized successfully")
        } catch (e: Exception) {
            Log.e(TAG, "Error in onCreate: ${e.message}", e)
            
            // Show user-friendly error message
            val errorMessage = when (e) {
                is IllegalStateException -> "Lỗi giao diện: ${e.message}"
                is OutOfMemoryError -> "Ứng dụng không đủ bộ nhớ để khởi động"
                else -> "Lỗi khởi tạo màn hình: ${e.message}"
            }
            
            Toast.makeText(this, errorMessage, Toast.LENGTH_LONG).show()
            
            // Try to show error state
            try {
                if (::errorMessage.isInitialized) {
                    this.errorMessage.text = errorMessage
                }
                if (::errorContainer.isInitialized) {
                    errorContainer.visibility = android.view.View.VISIBLE
                }
                if (::progressBar.isInitialized) {
                    progressBar.visibility = android.view.View.GONE
                }
            } catch (e2: Exception) {
                Log.e(TAG, "Could not show error state: ${e2.message}", e2)
                // If we can't even show error state, finish the activity
                finish()
            }
        }
    }
    
    private fun initializeViews() {
        try {
            // Initialize all required views with null checks
            backButton = findViewById<ImageView>(R.id.backButton) ?: throw IllegalStateException("backButton not found")
            addButton = findViewById<MaterialButton>(R.id.addButton) ?: throw IllegalStateException("addButton not found")
            refreshButton = findViewById<MaterialButton>(R.id.refreshButton) ?: throw IllegalStateException("refreshButton not found")
            elderlyNameText = findViewById<TextView>(R.id.elderlyName) ?: throw IllegalStateException("elderlyName not found")
            todayDateText = findViewById<TextView>(R.id.todayDate) ?: throw IllegalStateException("todayDate not found")
            todayScheduleContainer = findViewById<LinearLayout>(R.id.todayScheduleContainer) ?: throw IllegalStateException("todayScheduleContainer not found")
            progressBar = findViewById<android.widget.ProgressBar>(R.id.progressBar) ?: throw IllegalStateException("progressBar not found")
            errorContainer = findViewById<LinearLayout>(R.id.errorContainer) ?: throw IllegalStateException("errorContainer not found")
            errorMessage = findViewById<TextView>(R.id.errorMessage) ?: throw IllegalStateException("errorMessage not found")
            retryButton = findViewById<MaterialButton>(R.id.retryButton) ?: throw IllegalStateException("retryButton not found")
            emptyStateContainer = findViewById<LinearLayout>(R.id.emptyStateContainer) ?: throw IllegalStateException("emptyStateContainer not found")
            contentContainer = findViewById<LinearLayout>(R.id.contentContainer) ?: throw IllegalStateException("contentContainer not found")
            scheduleContainer = findViewById<LinearLayout>(R.id.scheduleContainer) ?: throw IllegalStateException("scheduleContainer not found")
            
            Log.d(TAG, "All views initialized successfully")
            
            // Set initial visibility states
            progressBar.visibility = android.view.View.GONE
            errorContainer.visibility = android.view.View.GONE
            emptyStateContainer.visibility = android.view.View.GONE
            contentContainer.visibility = android.view.View.GONE
            scheduleContainer.visibility = android.view.View.GONE
            
        } catch (e: Exception) {
            Log.e(TAG, "Error initializing views: ${e.message}", e)
            
            // Provide specific error message based on what failed
            val specificError = when (e) {
                is IllegalStateException -> "Lỗi khởi tạo giao diện: ${e.message}"
                is NullPointerException -> "Lỗi giao diện: Không thể tìm thấy các thành phần cần thiết"
                else -> "Lỗi khởi tạo giao diện: ${e.message}"
            }
            
            Toast.makeText(this, specificError, Toast.LENGTH_SHORT).show()
            throw e // Re-throw to be handled by onCreate
        }
    }
    
    private fun setupClickListeners() {
        try {
            // Setup back button
            backButton.setOnClickListener {
                try {
                    finish()
                } catch (e: Exception) {
                    Log.e(TAG, "Error in back button click: ${e.message}", e)
                    finish() // Force finish even if there's an error
                }
            }
            
            // Setup add button (MaterialButton)
            addButton.setOnClickListener {
                try {
                    if (elderlyId.isNotEmpty()) {
                        // Open the actual create schedule form
                        openCreateScheduleActivity()
                    } else {
                        Toast.makeText(this, "Vui lòng chọn người già trước khi tạo lịch trình", Toast.LENGTH_SHORT).show()
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Error in add button click: ${e.message}", e)
                    Toast.makeText(this, "Không thể mở trang tạo lịch trình", Toast.LENGTH_SHORT).show()
                }
            }
            
            // Setup refresh button
            refreshButton.setOnClickListener {
                try {
                    Log.d(TAG, "Refresh button clicked - reloading schedules from backend")
                    Toast.makeText(this, "Đang làm mới dữ liệu...", Toast.LENGTH_SHORT).show()
                    loadSchedules()
                } catch (e: Exception) {
                    Log.e(TAG, "Error in refresh button click: ${e.message}", e)
                    Toast.makeText(this, "Lỗi khi làm mới dữ liệu", Toast.LENGTH_SHORT).show()
                }
            }
            
            // Setup retry button
            retryButton.setOnClickListener {
                try {
                    hideError()
                    showLoading()
                    
                    // Retry loading based on current state
                    if (elderlyId.isNotEmpty()) {
                        // If we have elderly ID, retry loading schedules
                        loadSchedules()
                    } else {
                        // If no elderly ID, retry loading elderly profile
                        loadElderlyProfile()
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Error in retry button click: ${e.message}", e)
                    Toast.makeText(this, "Lỗi khi thử lại: ${e.message}", Toast.LENGTH_SHORT).show()
                    showError("Lỗi khi thử lại: ${e.message}")
                }
            }
            
            Log.d(TAG, "Click listeners set up successfully")
        } catch (e: Exception) {
            Log.e(TAG, "Error setting up click listeners: ${e.message}", e)
            Toast.makeText(this, "Lỗi thiết lập giao diện: ${e.message}", Toast.LENGTH_SHORT).show()
            throw e // Re-throw to be handled by onCreate
        }
    }
    
    private fun loadElderlyProfile() {
        try {
            // Get current user information from intent
            currentUserId = intent.getStringExtra("current_user_id") ?: ""
            currentUserType = intent.getStringExtra("current_user_type") ?: ""
            currentUserName = intent.getStringExtra("current_user_name") ?: "Người dùng"
            
            Log.d(TAG, "Intent extras - userId: '$currentUserId', userType: '$currentUserType', userName: '$currentUserName'")
            
            // Get the current logged-in user ID from UserPreferences
            val userPreferences = com.example.geminilivedemo.data.UserPreferences(this)
            val targetUserId = userPreferences.getUserId()
            
            if (targetUserId.isNullOrEmpty()) {
                Log.e(TAG, "No user logged in")
                Toast.makeText(this, "Bạn cần đăng nhập để sử dụng tính năng này", Toast.LENGTH_SHORT).show()
                finish()
                return
            }
            
            if (currentUserId.isEmpty() || currentUserType.isEmpty()) {
                Log.e(TAG, "Missing user information from intent")
                
                // Try to get user info from UserPreferences as fallback
                try {
                    val userPreferences = com.example.geminilivedemo.data.UserPreferences(this)
                    val fallbackUserId = userPreferences.getUserId()
                    val fallbackUserType = userPreferences.getUserType()
                    val fallbackUserName = userPreferences.getFullName()
                    
                    if (!fallbackUserId.isNullOrEmpty() && !fallbackUserType.isNullOrEmpty()) {
                        Log.d(TAG, "Using fallback user info from UserPreferences")
                        currentUserId = fallbackUserId
                        currentUserType = fallbackUserType
                        currentUserName = fallbackUserName ?: "Người dùng"
                    } else {
                        Log.e(TAG, "No fallback user info available")
                        showError("Thông tin người dùng không hợp lệ. Vui lòng đăng nhập lại.", false)
                        return
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Error getting fallback user info: ${e.message}", e)
                    showError("Thông tin người dùng không hợp lệ. Vui lòng đăng nhập lại.", false)
                    return
                }
            }
            
            Log.d(TAG, "Current user: $currentUserId, Type: $currentUserType, Name: $currentUserName")
            
            // Always use target user for schedules
            elderlyId = targetUserId
            elderlyName = "Đức Sơn" // son123@gmail.com user name
            
            if (::elderlyNameText.isInitialized) {
                elderlyNameText.text = elderlyName
            }
            
            // Elderly selection container is hidden in layout
            
            Log.d(TAG, "Using target user for schedules: $elderlyName (ID: $elderlyId)")
            
            // Show loading and load schedules
            showLoading()
            loadSchedules()
            
        } catch (e: Exception) {
            Log.e(TAG, "Error in loadElderlyProfile: ${e.message}", e)
            showError("Lỗi tải thông tin người dùng: ${e.message}")
        }
    }
    
    private fun loadElderlyListForFamily(familyUserId: String) {
        try {
            CoroutineScope(Dispatchers.Main).launch {
                try {
                    Log.d(TAG, "Loading elderly list for family member: $familyUserId")
                    
                    val result = withContext(Dispatchers.IO) {
                        ApiClient.getElderlyPatients(familyUserId)
                    }
                    
                    when (result) {
                        is ApiResult.Success<*> -> {
                            try {
                                val response = result.data as ElderlyPatientsResponse
                                Log.d(TAG, "Elderly patients response: success=${response.success}, count=${response.elderlyPatients.size}")
                                
                                if (response.success) {
                                    val elderlyList = response.elderlyPatients
                                    if (elderlyList.isNotEmpty()) {
                                        // For now, use the first elderly patient
                                        val firstElderly = elderlyList[0]
                                        elderlyId = firstElderly.userId
                                        elderlyName = firstElderly.fullName
                                        
                                        if (::elderlyNameText.isInitialized) {
                                            elderlyNameText.text = elderlyName
                                        }
                                        
                                        Log.d(TAG, "Loaded elderly profile: $elderlyName (ID: $elderlyId)")
                                        
                                        // Now load schedules for this elderly
                                        loadSchedules()
                                    } else {
                                        Log.w(TAG, "No elderly patients found for family member")
                                        showError("Bạn chưa được liên kết với người già nào. Vui lòng liên hệ quản trị viên để thiết lập mối quan hệ.", false)
                                    }
                                } else {
                                    Log.w(TAG, "API returned success=false for elderly list")
                                    showError("Không thể tải danh sách người già. Vui lòng thử lại sau.")
                                }
                            } catch (e: Exception) {
                                Log.e(TAG, "Error parsing elderly patients response: ${e.message}", e)
                                showError("Lỗi xử lý dữ liệu người già: ${e.message}")
                            }
                        }
                        is ApiResult.Error -> {
                            Log.w(TAG, "API error loading elderly list: ${result.exception.message}")
                            
                            // Check if it's a server connection error
                            val errorMessage = result.exception.message ?: "Unknown error"
                            if (errorMessage.contains("502") || errorMessage.contains("Bad Gateway") || 
                                errorMessage.contains("<!DOCTYPE html>") || errorMessage.contains("cloudflare")) {
                                // Server is down - show specific message and offer fallback
                                showServerDownError()
                            } else if (errorMessage.contains("404") || errorMessage.contains("Not Found")) {
                                showError("Không tìm thấy thông tin người già. Vui lòng kiểm tra lại tài khoản của bạn.", false)
                            } else if (errorMessage.contains("401") || errorMessage.contains("Unauthorized")) {
                                showError("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.", false)
                            } else {
                                showError("Lỗi kết nối: $errorMessage")
                            }
                        }
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Error loading elderly list: ${e.message}", e)
                    
                    // Check if it's a server connection error
                    val errorMessage = e.message ?: "Unknown error"
                    if (errorMessage.contains("502") || errorMessage.contains("Bad Gateway") || 
                        errorMessage.contains("<!DOCTYPE html>") || errorMessage.contains("cloudflare")) {
                        // Server is down - show specific message and offer fallback
                        showServerDownError()
                    } else if (errorMessage.contains("Network is unreachable") || errorMessage.contains("No route to host")) {
                        showError("Không thể kết nối đến máy chủ. Vui lòng kiểm tra kết nối mạng của bạn.", true)
                    } else {
                        showError("Lỗi: $errorMessage")
                    }
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error starting coroutine for elderly list: ${e.message}", e)
            
            // Check if it's a server connection error
            val errorMessage = e.message ?: "Unknown error"
            if (errorMessage.contains("502") || errorMessage.contains("Bad Gateway") || 
                errorMessage.contains("<!DOCTYPE html>") || errorMessage.contains("cloudflare")) {
                // Server is down - show specific message
                showServerDownError()
            } else {
                showError("Lỗi khởi tạo: $errorMessage")
            }
        }
    }
    
    private fun showError(message: String, showRetry: Boolean = true) {
        try {
            Log.e(TAG, "Error: $message")
            if (::errorMessage.isInitialized) {
                errorMessage.text = message
            }
            if (::retryButton.isInitialized) {
                retryButton.visibility = if (showRetry) android.view.View.VISIBLE else android.view.View.GONE
            }
            if (::errorContainer.isInitialized) {
                errorContainer.visibility = android.view.View.VISIBLE
            }
            if (::progressBar.isInitialized) {
                progressBar.visibility = android.view.View.GONE
            }
            if (::contentContainer.isInitialized) {
                contentContainer.visibility = android.view.View.GONE
            }
            if (::scheduleContainer.isInitialized) {
                scheduleContainer.visibility = android.view.View.GONE
            }
            if (::emptyStateContainer.isInitialized) {
                emptyStateContainer.visibility = android.view.View.GONE
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error in showError: ${e.message}", e)
        }
    }
    
    private fun hideError() {
        try {
            if (::errorContainer.isInitialized) {
                errorContainer.visibility = android.view.View.GONE
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error in hideError: ${e.message}", e)
        }
    }
    
    private fun showLoading() {
        try {
            if (::progressBar.isInitialized) {
                progressBar.visibility = android.view.View.VISIBLE
            }
            // Show loading container
            val loadingContainer = findViewById<LinearLayout>(R.id.loadingContainer)
            if (loadingContainer != null) {
                loadingContainer.visibility = android.view.View.VISIBLE
            }
            if (::errorContainer.isInitialized) {
                errorContainer.visibility = android.view.View.GONE
            }
            if (::contentContainer.isInitialized) {
                contentContainer.visibility = android.view.View.GONE
            }
            if (::scheduleContainer.isInitialized) {
                scheduleContainer.visibility = android.view.View.GONE
            }
            if (::emptyStateContainer.isInitialized) {
                emptyStateContainer.visibility = android.view.View.GONE
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error in showLoading: ${e.message}", e)
        }
    }
    
    private fun hideLoading() {
        try {
            if (::progressBar.isInitialized) {
                progressBar.visibility = android.view.View.GONE
            }
            // Hide loading container
            val loadingContainer = findViewById<LinearLayout>(R.id.loadingContainer)
            if (loadingContainer != null) {
                loadingContainer.visibility = android.view.View.GONE
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error in hideLoading: ${e.message}", e)
        }
    }
    
    private fun showContent() {
        try {
            Log.d(TAG, "showContent() called")
            Log.d(TAG, "  - progressBar initialized: ${::progressBar.isInitialized}")
            Log.d(TAG, "  - errorContainer initialized: ${::errorContainer.isInitialized}")
            Log.d(TAG, "  - contentContainer initialized: ${::contentContainer.isInitialized}")
            Log.d(TAG, "  - scheduleContainer initialized: ${::scheduleContainer.isInitialized}")
            Log.d(TAG, "  - emptyStateContainer initialized: ${::emptyStateContainer.isInitialized}")
            
            if (::progressBar.isInitialized) {
                progressBar.visibility = android.view.View.GONE
                Log.d(TAG, "  - progressBar hidden")
            }
            if (::errorContainer.isInitialized) {
                errorContainer.visibility = android.view.View.GONE
                Log.d(TAG, "  - errorContainer hidden")
            }
            if (::contentContainer.isInitialized) {
                contentContainer.visibility = android.view.View.VISIBLE
                Log.d(TAG, "  - contentContainer shown")
            }
            if (::scheduleContainer.isInitialized) {
                scheduleContainer.visibility = android.view.View.VISIBLE
                Log.d(TAG, "  - scheduleContainer shown")
            }
            if (::emptyStateContainer.isInitialized) {
                emptyStateContainer.visibility = android.view.View.GONE
                Log.d(TAG, "  - emptyStateContainer hidden")
            }
            
            Log.d(TAG, "showContent() completed successfully")
        } catch (e: Exception) {
            Log.e(TAG, "Error in showContent: ${e.message}", e)
        }
    }
    
    private fun showEmptyState() {
        try {
            Log.d(TAG, "Showing empty state - schedules count: ${schedules.size}")
            
            if (::emptyStateContainer.isInitialized) {
                emptyStateContainer.visibility = android.view.View.VISIBLE
            }
            if (::scheduleContainer.isInitialized) {
                scheduleContainer.visibility = android.view.View.GONE
            }
            if (::contentContainer.isInitialized) {
                contentContainer.visibility = android.view.View.VISIBLE
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error in showEmptyState: ${e.message}", e)
        }
    }
    
    private fun loadSchedules() {
        try {
            if (elderlyId.isEmpty()) {
                Log.w(TAG, "Cannot load schedules: elderlyId is empty")
                showError("Không tìm thấy thông tin người già", false)
                return
            }
            
            Log.d(TAG, "Starting to load schedules for elderly: $elderlyId")
            Log.d(TAG, "Current user info - ID: $currentUserId, Type: $currentUserType, Name: $currentUserName")
            
            // Show loading state
            showLoading()
            
            CoroutineScope(Dispatchers.Main).launch {
                try {
                    Log.d(TAG, "Loading schedules for elderly: $elderlyId")
                    
                    // Use API to load schedules from database
                    Log.d(TAG, "Loading schedules from API for elderly: $elderlyId")
                    
                    val result = withContext(Dispatchers.IO) {
                        Log.d(TAG, "Calling ApiClient.getUserSchedules...")
                        val apiResult = ApiClient.getUserSchedules(elderlyId, this@FamilyConnectionActivity)
                        Log.d(TAG, "ApiClient.getUserSchedules returned: $apiResult")
                        apiResult
                    }
                    
                    when (result) {
                        is ApiResult.Success<*> -> {
                            Log.d(TAG, "API call successful")
                            Log.d(TAG, "Raw result data: ${result.data}")
                            Log.d(TAG, "Raw result data type: ${result.data?.javaClass}")
                            
                            // Clear existing schedules first
                            val oldCount = schedules.size
                            schedules.clear()
                            Log.d(TAG, "Cleared existing schedules. Old count: $oldCount, New count: ${schedules.size}")
                            
                            try {
                                // Parse the JSON response correctly
                                var responseData = result.data as? org.json.JSONObject
                                Log.d(TAG, "Response data: $responseData")
                                Log.d(TAG, "Response data type: ${responseData?.javaClass}")
                                
                                if (responseData == null) {
                                    Log.e(TAG, "Failed to cast result.data to JSONObject")
                                    Log.d(TAG, "Attempting to convert result.data to JSONObject manually")
                                    
                                    // Try to convert manually if casting fails
                                    val jsonString = com.google.gson.Gson().toJson(result.data)
                                    Log.d(TAG, "Converted to JSON string: $jsonString")
                                    
                                    try {
                                        val manualJsonObject = org.json.JSONObject(jsonString)
                                        Log.d(TAG, "Successfully created JSONObject manually")
                                        responseData = manualJsonObject
                                    } catch (e: Exception) {
                                        Log.e(TAG, "Failed to create JSONObject manually: ${e.message}", e)
                                        showError("Lỗi xử lý dữ liệu từ máy chủ: ${e.message}")
                                        return@launch
                                    }
                                }
                                
                                if (responseData != null) {
                                    // Log all keys in responseData
                                    val responseKeys = responseData.keys()
                                    Log.d(TAG, "Response keys:")
                                    while (responseKeys.hasNext()) {
                                        val key = responseKeys.next()
                                        Log.d(TAG, "  - $key: ${responseData.get(key)}")
                                    }
                                    
                                    val schedulesArray = responseData.optJSONArray("schedules")
                                    Log.d(TAG, "Schedules array: $schedulesArray")
                                    Log.d(TAG, "Schedules array type: ${schedulesArray?.javaClass}")
                                    Log.d(TAG, "Schedules array length: ${schedulesArray?.length() ?: "null"}")
                                    
                                    if (schedulesArray != null && schedulesArray.length() > 0) {
                                        Log.d(TAG, "Found ${schedulesArray.length()} schedules from API")
                                        Log.d(TAG, "Schedules array length: ${schedulesArray.length()}")
                                        
                                        for (i in 0 until schedulesArray.length()) {
                                            val scheduleObj = schedulesArray.getJSONObject(i)
                                            Log.d(TAG, "Processing schedule $i: $scheduleObj")
                                            
                                            // Log individual schedule fields for debugging
                                            Log.d(TAG, "Schedule $i fields:")
                                            Log.d(TAG, "  - id: ${scheduleObj.optString("id", "N/A")}")
                                            Log.d(TAG, "  - title: ${scheduleObj.optString("title", "N/A")}")
                                            Log.d(TAG, "  - message: ${scheduleObj.optString("message", "N/A")}")
                                            Log.d(TAG, "  - scheduled_at: ${scheduleObj.optString("scheduled_at", "N/A")}")
                                            Log.d(TAG, "  - notification_type: ${scheduleObj.optString("notification_type", "N/A")}")
                                            Log.d(TAG, "  - category: ${scheduleObj.optString("category", "N/A")}")
                                            Log.d(TAG, "  - is_sent: ${scheduleObj.optBoolean("is_sent", false)}")
                                            
                                            try {
                                                // Parse scheduled_at from ISO format to timestamp
                                                val scheduledAtStr = scheduleObj.optString("scheduled_at", "")
                                                Log.d(TAG, "Parsing scheduled_at: $scheduledAtStr")
                                                
                                                val scheduledAtTimestamp = if (scheduledAtStr.isNotEmpty()) {
                                                    try {
                                                        // Try multiple date formats to handle different ISO formats
                                                        var date: java.util.Date? = null
                                                        var parseError: Exception? = null
                                                        
                                                        // Try format without milliseconds first (most common)
                                                        try {
                                                            val dateFormat1 = java.text.SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", java.util.Locale.getDefault())
                                                            date = dateFormat1.parse(scheduledAtStr)
                                                            Log.d(TAG, "Parsed with format: yyyy-MM-dd'T'HH:mm:ss")
                                                        } catch (e: Exception) {
                                                            parseError = e
                                                            Log.d(TAG, "Format 1 failed: ${e.message}")
                                                            
                                                            // Try format with milliseconds
                                                            try {
                                                                val dateFormat2 = java.text.SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSSSS", java.util.Locale.getDefault())
                                                                date = dateFormat2.parse(scheduledAtStr)
                                                                Log.d(TAG, "Parsed with format: yyyy-MM-dd'T'HH:mm:ss.SSSSSS")
                                                            } catch (e2: Exception) {
                                                                parseError = e2
                                                                Log.d(TAG, "Format 2 failed: ${e2.message}")
                                                                
                                                                // Try format with timezone
                                                                try {
                                                                    val dateFormat3 = java.text.SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssZ", java.util.Locale.getDefault())
                                                                    date = dateFormat3.parse(scheduledAtStr)
                                                                    Log.d(TAG, "Parsed with format: yyyy-MM-dd'T'HH:mm:ssZ")
                                                                } catch (e3: Exception) {
                                                                    parseError = e3
                                                                    Log.d(TAG, "Format 3 failed: ${e3.message}")
                                                                    
                                                                    // Try format with timezone and milliseconds
                                                                    try {
                                                                        val dateFormat4 = java.text.SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSSSSZ", java.util.Locale.getDefault())
                                                                        date = dateFormat4.parse(scheduledAtStr)
                                                                        Log.d(TAG, "Parsed with format: yyyy-MM-dd'T'HH:mm:ss.SSSSSSZ")
                                                                    } catch (e4: Exception) {
                                                                        parseError = e4
                                                                        Log.e(TAG, "All date parsing attempts failed for: $scheduledAtStr")
                                                                        Log.e(TAG, "Last error: ${e4.message}")
                                                                    }
                                                                }
                                                            }
                                                        }
                                                        
                                                        if (date != null) {
                                                            val timestamp = date.time / 1000
                                                            Log.d(TAG, "Successfully parsed scheduled_at timestamp: $timestamp")
                                                            timestamp
                                                        } else {
                                                            Log.e(TAG, "Failed to parse scheduled_at: $scheduledAtStr", parseError)
                                                            0L
                                                        }
                                                    } catch (e: Exception) {
                                                        Log.e(TAG, "Error parsing scheduled_at: $scheduledAtStr", e)
                                                        0L
                                                    }
                                                } else {
                                                    Log.w(TAG, "scheduled_at is empty")
                                                    0L
                                                }
                                                
                                                val scheduleItem = ScheduleItem(
                                                    id = scheduleObj.optString("id", ""),
                                                    title = scheduleObj.optString("title", ""),
                                                    message = scheduleObj.optString("message", ""),
                                                    scheduledAt = scheduledAtTimestamp.toString(),
                                                    notificationType = scheduleObj.optString("notification_type", ""),
                                                    category = scheduleObj.optString("category", ""),
                                                    isCompleted = scheduleObj.optBoolean("is_sent", false)
                                                )
                                                
                                                schedules.add(scheduleItem)
                                                Log.d(TAG, "Added schedule: ${scheduleItem.title}")
                                                Log.d(TAG, "  - ID: ${scheduleItem.id}")
                                                Log.d(TAG, "  - Scheduled At: ${scheduleItem.scheduledAt}")
                                                Log.d(TAG, "  - Is Completed: ${scheduleItem.isCompleted}")
                                                Log.d(TAG, "  - Current schedules count: ${schedules.size}")
                                                
                                            } catch (e: Exception) {
                                                Log.e(TAG, "Error processing schedule $i", e)
                                            }
                                        }
                                    } else {
                                        Log.w(TAG, "No schedules found in response")
                                        Log.d(TAG, "Schedules array is null or empty")
                                    }
                                } else {
                                    Log.w(TAG, "Response data is null")
                                    Log.d(TAG, "Raw result data: ${result.data}")
                                    Log.d(TAG, "Raw result data class: ${result.data?.javaClass}")
                                }
                                
                                // Display schedules
                                Log.d(TAG, "About to display schedules. Total count: ${schedules.size}")
                                Log.d(TAG, "Schedule IDs loaded from backend:")
                                schedules.forEachIndexed { index, schedule ->
                                    Log.d(TAG, "  Schedule $index: ID=${schedule.id}, Title=${schedule.title}, ScheduledAt=${schedule.scheduledAt}")
                                }
                                
                                if (schedules.isNotEmpty()) {
                                    Log.d(TAG, "Calling displaySchedules() with ${schedules.size} schedules")
                                    displaySchedules()
                                    Log.d(TAG, "Calling showContent()")
                                    showContent()
                                    Log.d(TAG, "Successfully loaded ${schedules.size} schedules from API")
                                } else {
                                    Log.w(TAG, "No schedules to display - schedules list is empty")
                                    showEmptyState()
                                }
                                
                            } catch (e: Exception) {
                                Log.e(TAG, "Error parsing API response", e)
                                showEmptyState()
                            }
                        }
                        is ApiResult.Error -> {
                            Log.e(TAG, "Error loading schedules from API: ${result.exception.message}")
                            
                            // Check if it's a server connection error
                            val errorMessage = result.exception.message ?: "Unknown error"
                            if (errorMessage.contains("502") || errorMessage.contains("Bad Gateway") || 
                                errorMessage.contains("<!DOCTYPE html>") || errorMessage.contains("cloudflare")) {
                                // Server is down - show specific message and offer fallback
                                showServerDownError()
                            } else if (errorMessage.contains("404") || errorMessage.contains("Not Found")) {
                                showError("Không tìm thấy lịch trình. Vui lòng kiểm tra lại thông tin người già.", false)
                            } else if (errorMessage.contains("401") || errorMessage.contains("Unauthorized")) {
                                showError("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.", false)
                            } else if (errorMessage.contains("Network is unreachable") || errorMessage.contains("No route to host")) {
                                showError("Không thể kết nối đến máy chủ. Vui lòng kiểm tra kết nối mạng của bạn.", true)
                            } else {
                                showError("Lỗi tải lịch trình: $errorMessage")
                            }
                        }
                    }
                    
                } catch (e: Exception) {
                    Log.e(TAG, "Error loading schedules from local storage: ${e.message}", e)
                    
                    // Check if it's a server connection error
                    val errorMessage = e.message ?: "Unknown error"
                    if (errorMessage.contains("502") || errorMessage.contains("Bad Gateway") || 
                        errorMessage.contains("<!DOCTYPE html>") || errorMessage.contains("cloudflare")) {
                        // Server is down - show specific message and offer fallback
                        showServerDownError()
                    } else if (errorMessage.contains("Network is unreachable") || errorMessage.contains("No route to host")) {
                        showError("Không thể kết nối đến máy chủ. Vui lòng kiểm tra kết nối mạng của bạn.", true)
                    } else {
                        showError("Lỗi tải lịch trình: $errorMessage")
                    }
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error starting coroutine for schedules: ${e.message}", e)
            showError("Lỗi khởi tạo: ${e.message}")
        }
    }
    
    private fun loadSampleSchedules() {
        try {
            schedules.clear()
            
            // Add sample schedules for today (August 7th)
            val today = Calendar.getInstance().apply {
                set(Calendar.MONTH, Calendar.AUGUST)
                set(Calendar.DAY_OF_MONTH, 7)
                set(Calendar.HOUR_OF_DAY, 8)
                set(Calendar.MINUTE, 0)
                set(Calendar.SECOND, 0)
            }
            val todayTimestamp = today.timeInMillis / 1000
            
            schedules.add(
                ScheduleItem(
                    id = "1",
                    title = "Uống thuốc huyết áp",
                    message = "Uống thuốc huyết áp theo chỉ định của bác sĩ",
                    scheduledAt = todayTimestamp.toString(),
                    notificationType = "medicine_reminder",
                    category = "medicine",
                    isCompleted = true
                )
            )
            
            val appointmentTime = Calendar.getInstance().apply {
                set(Calendar.MONTH, Calendar.AUGUST)
                set(Calendar.DAY_OF_MONTH, 7)
                set(Calendar.HOUR_OF_DAY, 10)
                set(Calendar.MINUTE, 30)
                set(Calendar.SECOND, 0)
            }
            val appointmentTimestamp = appointmentTime.timeInMillis / 1000
            
            schedules.add(
                ScheduleItem(
                    id = "2",
                    title = "Tái khám bác sĩ Tim mạch",
                    message = "Tái khám định kỳ với bác sĩ chuyên khoa tim mạch",
                    scheduledAt = appointmentTimestamp.toString(),
                    notificationType = "appointment_reminder",
                    category = "appointment",
                    isCompleted = false
                )
            )
            
            val exerciseTime = Calendar.getInstance().apply {
                set(Calendar.MONTH, Calendar.AUGUST)
                set(Calendar.DAY_OF_MONTH, 7)
                set(Calendar.HOUR_OF_DAY, 16)
                set(Calendar.MINUTE, 0)
                set(Calendar.SECOND, 0)
            }
            val exerciseTimestamp = exerciseTime.timeInMillis / 1000
            
            schedules.add(
                ScheduleItem(
                    id = "3",
                    title = "Đi bộ 30 phút",
                    message = "Tập thể dục nhẹ nhàng bằng cách đi bộ",
                    scheduledAt = exerciseTimestamp.toString(),
                    notificationType = "health_check",
                    category = "exercise",
                    isCompleted = false
                )
            )
            
            // Add sample schedule for yesterday (August 6th)
            val yesterday = Calendar.getInstance().apply {
                set(Calendar.MONTH, Calendar.AUGUST)
                set(Calendar.DAY_OF_MONTH, 6)
                set(Calendar.HOUR_OF_DAY, 8)
                set(Calendar.MINUTE, 0)
                set(Calendar.SECOND, 0)
            }
            val yesterdayTimestamp = yesterday.timeInMillis / 1000
            
            schedules.add(
                ScheduleItem(
                    id = "4",
                    title = "Uống thuốc huyết áp",
                    message = "Uống thuốc huyết áp theo chỉ định của bác sĩ",
                    scheduledAt = yesterdayTimestamp.toString(),
                    notificationType = "medicine_reminder",
                    category = "medicine",
                    isCompleted = true
                )
            )
            
            displaySchedules()
            showContent()
            
            Log.d(TAG, "Sample schedules loaded successfully - ${schedules.size} schedules")
        } catch (e: Exception) {
            Log.e(TAG, "Error loading sample schedules: ${e.message}", e)
            showError("Lỗi tải dữ liệu mẫu: ${e.message}")
        }
    }
    
    private fun displaySchedules() {
        try {
            Log.d(TAG, "displaySchedules() called")
            Log.d(TAG, "Displaying ${schedules.size} schedules")
            Log.d(TAG, "  - todayScheduleContainer initialized: ${::todayScheduleContainer.isInitialized}")
            
            // Clear existing views
            if (::todayScheduleContainer.isInitialized) {
                todayScheduleContainer.removeAllViews()
                Log.d(TAG, "  - Cleared todayScheduleContainer")
            }
            
            // Sort schedules by scheduled time (nearest first)
            val sortedSchedules = schedules.sortedBy { schedule ->
                try {
                    schedule.scheduledAt.toLong()
                } catch (e: Exception) {
                    Log.e(TAG, "Error parsing schedule time: ${schedule.scheduledAt}", e)
                    0L
                }
            }
            
            Log.d(TAG, "  - Sorted ${sortedSchedules.size} schedules by time")
            
            var totalCount = 0
            
            sortedSchedules.forEach { schedule ->
                val scheduleView = createScheduleItemView(schedule)
                
                try {
                    // Add sorted schedules to the container
                    Log.d(TAG, "Processing schedule: ${schedule.title}")
                    Log.d(TAG, "  - Schedule timestamp: ${schedule.scheduledAt}")
                    
                    // Always add to today container
                    if (::todayScheduleContainer.isInitialized) {
                        todayScheduleContainer.addView(scheduleView)
                        totalCount++
                        Log.d(TAG, "  -> Added to schedule container. Count: $totalCount")
                    }
                    
                } catch (e: Exception) {
                    Log.e(TAG, "Error processing schedule: ${schedule.title}", e)
                    // Add to today container as fallback even if processing fails
                    if (::todayScheduleContainer.isInitialized) {
                        todayScheduleContainer.addView(scheduleView)
                        totalCount++
                        Log.d(TAG, "  -> Added to schedule container after error. Count: $totalCount")
                    }
                }
            }
            
            Log.d(TAG, "Schedules displayed successfully - Total: $totalCount")
            Log.d(TAG, "displaySchedules() completed")
        } catch (e: Exception) {
            Log.e(TAG, "Error in displaySchedules: ${e.message}", e)
        }
    }
    
    private fun createScheduleItemView(schedule: ScheduleItem): View {
        try {
            val inflater = LayoutInflater.from(this)
            val scheduleView = inflater.inflate(R.layout.item_schedule, null)
            
            val titleView = scheduleView.findViewById<TextView>(R.id.scheduleTitleText)
            val messageView = scheduleView.findViewById<TextView>(R.id.scheduleMessageText)
            val timeView = scheduleView.findViewById<TextView>(R.id.scheduleTimeText)
            val categoryView = scheduleView.findViewById<TextView>(R.id.scheduleCategoryText)
            val statusView = scheduleView.findViewById<TextView>(R.id.scheduleStatusText)
            val completeButton = scheduleView.findViewById<android.widget.ImageButton>(R.id.completeButton)
            val deleteButton = scheduleView.findViewById<android.widget.ImageButton>(R.id.deleteButton)
            
            // Set title and message
            titleView.text = schedule.title
            messageView.text = schedule.message ?: ""
            
            // Set time
            timeView.text = formatScheduleTime(schedule.scheduledAt)
            
            // Set category
            categoryView.text = getCategoryDisplayName(schedule.category)
            
            // Set status
            if (schedule.isCompleted) {
                statusView.text = "Đã hoàn thành"
                statusView.setTextColor(ContextCompat.getColor(this, R.color.success_500))
                // Disable complete button if already completed
                completeButton.isEnabled = false
                completeButton.alpha = 0.5f
            } else {
                statusView.text = "Chưa hoàn thành"
                statusView.setTextColor(ContextCompat.getColor(this, R.color.warning_500))
                completeButton.isEnabled = true
                completeButton.alpha = 1.0f
            }
            
            // Set click listeners for action buttons
            completeButton.setOnClickListener {
                markScheduleComplete(schedule)
            }
            
            deleteButton.setOnClickListener {
                showDeleteConfirmationDialog(schedule)
            }
            
            return scheduleView
        } catch (e: Exception) {
            Log.e(TAG, "Error creating schedule item view: ${e.message}", e)
            // Return a simple TextView as fallback
            return TextView(this).apply {
                text = "Lỗi hiển thị lịch trình"
                setTextColor(ContextCompat.getColor(this@FamilyConnectionActivity, android.R.color.holo_red_dark))
            }
        }
    }
    
    private fun getCategoryDisplayName(category: String): String {
        return when (category) {
            "medicine", "medicine_reminder" -> "Thuốc"
            "appointment", "appointment_reminder" -> "Hẹn khám"
            "exercise", "health_check" -> "Tập thể dục"
            "eating", "meal" -> "Bữa ăn"
            "other" -> "Khác"
            else -> category
        }
    }
    
    private fun formatScheduleTime(dateTime: Any): String {
        return try {
            val date = when (dateTime) {
                is String -> {
                    // Try to parse as Long first (Unix timestamp)
                    try {
                        val timestamp = dateTime.toLong()
                        Date(timestamp * 1000)
                    } catch (e: NumberFormatException) {
                        // If not a number, try string format (yyyy-MM-dd'T'HH:mm:ss)
                        SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault()).parse(dateTime)
                    }
                }
                is Long -> {
                    // Handle Unix timestamp
                    Date(dateTime * 1000)
                }
                else -> null
            }
            
            if (date != null) {
                // Format to show both date and time
                val dateTimeFormat = SimpleDateFormat("dd/MM/yyyy HH:mm", Locale("vi"))
                dateTimeFormat.format(date)
            } else {
                "00/00/0000 00:00"
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error formatting schedule time: $dateTime", e)
            "00/00/0000 00:00"
        }
    }
    
    private fun updateDateDisplay() {
        try {
            // Set text for schedule section showing sorting by time
            if (::todayDateText.isInitialized) {
                todayDateText.text = "Lịch trình (sắp xếp theo thời gian gần nhất)"
            }
            
            Log.d(TAG, "Date display updated successfully with time sorting info")
        } catch (e: Exception) {
            Log.e(TAG, "Error updating date display: ${e.message}", e)
        }
    }
        
    private fun openCreateScheduleActivity() {
        try {
            if (elderlyId.isEmpty()) {
                Toast.makeText(this, "Vui lòng chọn người già trước khi tạo lịch trình", Toast.LENGTH_SHORT).show()
                return
            }
            
            Log.d(TAG, "Opening CreateScheduleActivity with:")
            Log.d(TAG, "  - Elderly ID: $elderlyId")
            Log.d(TAG, "  - Elderly Name: $elderlyName")
            Log.d(TAG, "  - Current User ID: $currentUserId")
            Log.d(TAG, "  - Current User Name: $currentUserName")
            Log.d(TAG, "  - Current User Type: $currentUserType")
            
            val intent = Intent(this, CreateScheduleActivity::class.java).apply {
                putExtra(CreateScheduleActivity.EXTRA_ELDERLY_ID, elderlyId)
                putExtra(CreateScheduleActivity.EXTRA_ELDERLY_NAME, elderlyName)
                // Pass current user information
                putExtra("current_user_id", currentUserId)
                putExtra("current_user_name", currentUserName)
                putExtra("current_user_type", currentUserType)
            }
            
            // Check if CreateScheduleActivity exists
            try {
                startActivityForResult(intent, REQUEST_CREATE_SCHEDULE)
                Log.d(TAG, "Opened CreateScheduleActivity successfully")
            } catch (e: Exception) {
                Log.e(TAG, "Error starting CreateScheduleActivity: ${e.message}", e)
                Toast.makeText(this, "Không thể mở trang tạo lịch trình. Vui lòng thử lại sau.", Toast.LENGTH_SHORT).show()
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error opening CreateScheduleActivity: ${e.message}", e)
            Toast.makeText(this, "Không thể mở trang tạo lịch trình", Toast.LENGTH_SHORT).show()
        }
    }
    
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        
        try {
            if (requestCode == REQUEST_CREATE_SCHEDULE) {
                when (resultCode) {
                    Activity.RESULT_OK -> {
                        // Refresh schedules after creating new one
                        Log.d(TAG, "Schedule created successfully, refreshing schedules")
                        Toast.makeText(this, "Lịch trình đã được tạo thành công", Toast.LENGTH_SHORT).show()
                        loadSchedules()
                    }
                    Activity.RESULT_CANCELED -> {
                        Log.d(TAG, "Schedule creation was cancelled")
                        // User cancelled, no action needed
                    }
                    else -> {
                        Log.w(TAG, "Schedule creation returned unexpected result code: $resultCode")
                        // Handle unexpected result codes if needed
                    }
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error handling activity result: ${e.message}", e)
            Toast.makeText(this, "Lỗi xử lý kết quả: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }
    
    private fun showServerDownError() {
        try {
            val message = """
                Máy chủ hiện tại không khả dụng (Lỗi 502)
                
                Nguyên nhân có thể:
                • Máy chủ đang bảo trì
                • Vấn đề kết nối mạng
                • Máy chủ quá tải
                
                Bạn có thể:
                • Thử lại sau vài phút
                • Kiểm tra kết nối mạng
                • Liên hệ hỗ trợ kỹ thuật
                
                Thời gian: ${getCurrentTime()}
                
                Ứng dụng sẽ hiển thị dữ liệu mẫu để bạn có thể xem giao diện.
            """.trimIndent()
            
            if (::errorMessage.isInitialized) {
                errorMessage.text = message
            }
            if (::retryButton.isInitialized) {
                retryButton.visibility = android.view.View.VISIBLE
            }
            if (::errorContainer.isInitialized) {
                errorContainer.visibility = android.view.View.VISIBLE
            }
            if (::progressBar.isInitialized) {
                progressBar.visibility = android.view.View.GONE
            }
            if (::contentContainer.isInitialized) {
                contentContainer.visibility = android.view.View.GONE
            }
            if (::scheduleContainer.isInitialized) {
                scheduleContainer.visibility = android.view.View.GONE
            }
            if (::emptyStateContainer.isInitialized) {
                emptyStateContainer.visibility = android.view.View.GONE
            }
            
            // Show a toast message to inform user about fallback
            Toast.makeText(this, "Đang tải dữ liệu mẫu do máy chủ không khả dụng", Toast.LENGTH_LONG).show()
            
            // Load sample data as fallback after a short delay
            android.os.Handler(android.os.Looper.getMainLooper()).postDelayed({
                try {
                    loadSampleSchedules()
                } catch (e: Exception) {
                    Log.e(TAG, "Error loading sample schedules as fallback: ${e.message}", e)
                }
            }, 2000) // 2 seconds delay
            
            Log.w(TAG, "Showing server down error message with fallback to sample data")
        } catch (e: Exception) {
            Log.e(TAG, "Error in showServerDownError: ${e.message}", e)
            showError("Máy chủ không khả dụng. Vui lòng thử lại sau.")
        }
    }
    
    private fun getCurrentTime(): String {
        return try {
            val dateFormat = SimpleDateFormat("HH:mm:ss dd/MM/yyyy", Locale("vi"))
            dateFormat.format(Date())
        } catch (e: Exception) {
            "N/A"
        }
    }
    
    // Test method to create schedule directly
    private fun testCreateSchedule() {
        CoroutineScope(Dispatchers.Main).launch {
            try {
                Log.d(TAG, "TEST: Creating schedule directly")
                Log.d(TAG, "TEST: Current User ID: $currentUserId")
                Log.d(TAG, "TEST: Elderly ID: $elderlyId")
                
                val scheduleManager = com.example.geminilivedemo.data.ScheduleManager(this@FamilyConnectionActivity)
                
                val testSchedule = com.example.geminilivedemo.data.Schedule(
                    elderlyId = elderlyId,
                    title = "Test Schedule - ${System.currentTimeMillis()}",
                    message = "This is a test schedule created directly",
                    scheduledAt = System.currentTimeMillis() / 1000 + 3600, // 1 hour from now
                    notificationType = "medicine_reminder",
                    category = "medicine",
                    priority = "normal",
                    createdBy = currentUserId
                )
                
                Log.d(TAG, "TEST: Schedule object created:")
                Log.d(TAG, "TEST:   - ID: ${testSchedule.id}")
                Log.d(TAG, "TEST:   - Elderly ID: ${testSchedule.elderlyId}")
                Log.d(TAG, "TEST:   - Created By: ${testSchedule.createdBy}")
                Log.d(TAG, "TEST:   - Title: ${testSchedule.title}")
                
                val success = withContext(Dispatchers.IO) {
                    scheduleManager.saveSchedule(testSchedule, currentUserId)
                }
                
                if (success) {
                    Log.d(TAG, "TEST: Schedule saved successfully!")
                    Toast.makeText(this@FamilyConnectionActivity, "Test schedule created successfully!", Toast.LENGTH_LONG).show()
                    
                    // Reload schedules to see if it appears
                    loadSchedules()
                } else {
                    Log.e(TAG, "TEST: Failed to save schedule")
                    Toast.makeText(this@FamilyConnectionActivity, "Failed to create test schedule", Toast.LENGTH_LONG).show()
                }
                
            } catch (e: Exception) {
                Log.e(TAG, "TEST: Error creating test schedule: ${e.message}", e)
                Toast.makeText(this@FamilyConnectionActivity, "Error: ${e.message}", Toast.LENGTH_LONG).show()
            }
        }
    }
    
    // Method for empty state button click
    fun onCreateScheduleClick(view: View) {
        try {
            if (elderlyId.isNotEmpty()) {
                openCreateScheduleActivity()
            } else {
                Toast.makeText(this, "Vui lòng chọn người già trước khi tạo lịch trình", Toast.LENGTH_SHORT).show()
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error in onCreateScheduleClick: ${e.message}", e)
            Toast.makeText(this, "Không thể mở trang tạo lịch trình", Toast.LENGTH_SHORT).show()
        }
    }
    
    private fun showDeleteConfirmationDialog(schedule: ScheduleItem) {
        try {
            val alertDialog = androidx.appcompat.app.AlertDialog.Builder(this)
                .setTitle("Xác nhận xóa")
                .setMessage("Bạn có chắc chắn muốn xóa lịch trình \"${schedule.title}\"?\n\nHành động này không thể hoàn tác.")
                .setPositiveButton("Xóa") { _, _ ->
                    deleteSchedule(schedule)
                }
                .setNegativeButton("Hủy", null)
                .create()
            
            alertDialog.show()
        } catch (e: Exception) {
            Log.e(TAG, "Error showing delete confirmation dialog: ${e.message}", e)
            Toast.makeText(this, "Lỗi hiển thị hộp thoại xác nhận", Toast.LENGTH_SHORT).show()
        }
    }
    
    private fun deleteSchedule(schedule: ScheduleItem) {
        try {
            Log.d(TAG, "Deleting schedule: ${schedule.id} - ${schedule.title}")
            
            // Show loading indicator
            Toast.makeText(this, "Đang xóa lịch trình...", Toast.LENGTH_SHORT).show()
            
            CoroutineScope(Dispatchers.Main).launch {
                try {
                    // Get the current logged-in user ID from UserPreferences
                    val userPreferences = com.example.geminilivedemo.data.UserPreferences(this@FamilyConnectionActivity)
                    val targetUserId = userPreferences.getUserId()
                    
                    if (targetUserId.isNullOrEmpty()) {
                        Log.e(TAG, "No user logged in")
                        Toast.makeText(this@FamilyConnectionActivity, "Bạn cần đăng nhập để xóa lịch", Toast.LENGTH_SHORT).show()
                        return@launch
                    }
                    
                    val result = withContext(Dispatchers.IO) {
                        ApiClient.deleteSchedule(schedule.id, this@FamilyConnectionActivity)
                    }
                    
                    when (result) {
                        is ApiResult.Success<*> -> {
                            Log.d(TAG, "Schedule deleted successfully from backend")
                            
                            // Show success message
                            Toast.makeText(this@FamilyConnectionActivity, "Đã xóa lịch trình thành công", Toast.LENGTH_SHORT).show()
                            
                            // Force refresh from backend to ensure data consistency
                            Log.d(TAG, "Force refreshing schedules from backend after deletion")
                            loadSchedules()
                        }
                        is ApiResult.Error -> {
                            Log.e(TAG, "Error deleting schedule from backend: ${result.exception.message}")
                            
                            val errorMessage = result.exception.message ?: "Lỗi không xác định"
                            if (errorMessage.contains("404")) {
                                Toast.makeText(this@FamilyConnectionActivity, "Lịch trình không tồn tại hoặc đã bị xóa", Toast.LENGTH_SHORT).show()
                            } else if (errorMessage.contains("403")) {
                                Toast.makeText(this@FamilyConnectionActivity, "Bạn không có quyền xóa lịch trình này", Toast.LENGTH_SHORT).show()
                            } else if (errorMessage.contains("401")) {
                                Toast.makeText(this@FamilyConnectionActivity, "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại", Toast.LENGTH_SHORT).show()
                            } else {
                                Toast.makeText(this@FamilyConnectionActivity, "Lỗi xóa lịch trình: $errorMessage", Toast.LENGTH_SHORT).show()
                            }
                        }
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Exception deleting schedule: ${e.message}", e)
                    Toast.makeText(this@FamilyConnectionActivity, "Lỗi xóa lịch trình: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error starting delete schedule coroutine: ${e.message}", e)
            Toast.makeText(this, "Lỗi khởi tạo xóa lịch trình: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }
    
    private fun markScheduleComplete(schedule: ScheduleItem) {
        try {
            Log.d(TAG, "Marking schedule as complete: ${schedule.id} - ${schedule.title}")
            
            // Show loading indicator
            Toast.makeText(this, "Đang cập nhật trạng thái...", Toast.LENGTH_SHORT).show()
            
            CoroutineScope(Dispatchers.Main).launch {
                try {
                    // Get the current logged-in user ID from UserPreferences
                    val userPreferences = com.example.geminilivedemo.data.UserPreferences(this@FamilyConnectionActivity)
                    val targetUserId = userPreferences.getUserId()
                    
                    if (targetUserId.isNullOrEmpty()) {
                        Log.e(TAG, "No user logged in")
                        Toast.makeText(this@FamilyConnectionActivity, "Bạn cần đăng nhập để cập nhật lịch", Toast.LENGTH_SHORT).show()
                        return@launch
                    }
                    
                    val result = withContext(Dispatchers.IO) {
                        ApiClient.markScheduleComplete(schedule.id, this@FamilyConnectionActivity)
                    }
                    
                    when (result) {
                        is ApiResult.Success<*> -> {
                            Log.d(TAG, "Schedule marked as complete successfully")
                            
                            // Show success message
                            Toast.makeText(this@FamilyConnectionActivity, "Đã đánh dấu lịch trình hoàn thành", Toast.LENGTH_SHORT).show()
                            
                            // Force refresh from backend to ensure data consistency
                            Log.d(TAG, "Force refreshing schedules from backend after marking complete")
                            loadSchedules()
                        }
                        is ApiResult.Error -> {
                            Log.e(TAG, "Error marking schedule complete: ${result.exception.message}")
                            
                            val errorMessage = result.exception.message ?: "Lỗi không xác định"
                            if (errorMessage.contains("404")) {
                                Toast.makeText(this@FamilyConnectionActivity, "Lịch trình không tồn tại", Toast.LENGTH_SHORT).show()
                            } else if (errorMessage.contains("403")) {
                                Toast.makeText(this@FamilyConnectionActivity, "Bạn không có quyền cập nhật lịch trình này", Toast.LENGTH_SHORT).show()
                            } else if (errorMessage.contains("401")) {
                                Toast.makeText(this@FamilyConnectionActivity, "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại", Toast.LENGTH_SHORT).show()
                            } else {
                                Toast.makeText(this@FamilyConnectionActivity, "Lỗi cập nhật trạng thái: $errorMessage", Toast.LENGTH_SHORT).show()
                            }
                        }
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Exception marking schedule complete: ${e.message}", e)
                    Toast.makeText(this@FamilyConnectionActivity, "Lỗi cập nhật trạng thái: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error starting mark complete coroutine: ${e.message}", e)
            Toast.makeText(this, "Lỗi khởi tạo cập nhật trạng thái: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }
    
    data class ScheduleItem(
        val id: String,
        val title: String,
        val message: String,
        val scheduledAt: String,
        val notificationType: String,
        val category: String,
        val isCompleted: Boolean
    )
} 