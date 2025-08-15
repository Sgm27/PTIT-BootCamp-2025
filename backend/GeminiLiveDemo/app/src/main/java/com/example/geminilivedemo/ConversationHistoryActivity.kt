package com.example.geminilivedemo

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.TextView
import android.widget.Toast
import android.widget.ProgressBar
import android.widget.LinearLayout
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.geminilivedemo.data.ApiClient
import com.example.geminilivedemo.data.ApiConfig
import com.example.geminilivedemo.data.UserPreferences
import com.example.geminilivedemo.data.UserResponse
import com.example.geminilivedemo.data.LoginResponse
import com.example.geminilivedemo.adapters.ConversationHistoryAdapter
import com.example.geminilivedemo.data.DataCacheManager
import kotlinx.coroutines.*
import android.content.Context
import java.net.URL
import java.net.HttpURLConnection
import java.io.BufferedReader
import java.io.InputStreamReader
import androidx.lifecycle.lifecycleScope

class ConversationHistoryActivity : AppCompatActivity(), GlobalConnectionManager.ConnectionStateCallback {
    
    private lateinit var userPreferences: UserPreferences

    private lateinit var globalConnectionManager: GlobalConnectionManager
    private lateinit var dataCacheManager: DataCacheManager
    private lateinit var recyclerView: RecyclerView
    private lateinit var adapter: ConversationHistoryAdapter
    private lateinit var emptyView: TextView
    private lateinit var emptyViewContainer: android.widget.LinearLayout
    private lateinit var loadingView: ProgressBar
    private lateinit var loadingContainer: android.widget.LinearLayout
    
    private val conversations = mutableListOf<Map<String, Any>>()
    private var loadingJob: Job? = null
    private var isDataFromCache = false
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        Log.d("ConversationHistory", "=== ConversationHistoryActivity onCreate START ===")
        Log.d("ConversationHistory", "API Config: ${ApiConfig.getEnvironmentInfo()}")
        Log.d("ConversationHistory", "Constants API: ${Constants.getApiInfo()}")
        
        try {
            Log.d("ConversationHistory", "Setting content view...")
            setContentView(R.layout.activity_conversation_history)
            Log.d("ConversationHistory", "Content view set successfully")
            
            // Lấy GlobalConnectionManager và đăng ký callback
            globalConnectionManager = (application as GeminiLiveApplication).getGlobalConnectionManager()
            globalConnectionManager.registerCallback(this)
            
            // Initialize components
            Log.d("ConversationHistory", "Initializing UserPreferences...")
            userPreferences = UserPreferences(this)
            Log.d("ConversationHistory", "UserPreferences initialized")
            
            Log.d("ConversationHistory", "Initializing ApiClient...")

            Log.d("ConversationHistory", "ApiClient initialized successfully")
            Log.d("ConversationHistory", "ApiService instance: ${ApiClient.apiService}")
            
            Log.d("ConversationHistory", "Initializing DataCacheManager...")
            dataCacheManager = DataCacheManager.getInstance(this)
            Log.d("ConversationHistory", "DataCacheManager initialized successfully")
            
            // Setup UI
            Log.d("ConversationHistory", "Setting up UI...")
            setupUI()
            Log.d("ConversationHistory", "UI setup completed")
            
            Log.d("ConversationHistory", "Setting up RecyclerView...")
            setupRecyclerView()
            Log.d("ConversationHistory", "RecyclerView setup completed")
            
            // Check user data
            val userId = userPreferences.getUserId()
            val isLoggedIn = userPreferences.isLoggedIn()
            Log.d("ConversationHistory", "User ID: '$userId'")
            Log.d("ConversationHistory", "Is logged in: $isLoggedIn")
            
            // Check if user is logged in
            if (userId.isNullOrEmpty() || !isLoggedIn) {
                Log.e("ConversationHistory", "User not logged in or no user ID found")
                showError("Vui lòng đăng nhập để xem lịch sử trò chuyện")
                finish()
                return
            }
            
            // Load conversations
            Log.d("ConversationHistory", "Loading conversations for user: $userId")
            loadConversations()
            
            Log.d("ConversationHistory", "=== ConversationHistoryActivity onCreate COMPLETED ===")
        
        // Log cache status
        try {
            val cacheStatus = dataCacheManager.getCacheStatus()
            Log.d("ConversationHistory", "Cache status: $cacheStatus")
        } catch (e: Exception) {
            Log.w("ConversationHistory", "Could not get cache status", e)
        }
        } catch (e: Exception) {
            Log.e("ConversationHistory", "=== CRITICAL ERROR in onCreate ===", e)
            Log.e("ConversationHistory", "Error message: ${e.message}")
            Log.e("ConversationHistory", "Error cause: ${e.cause}")
            Log.e("ConversationHistory", "Stack trace: ${e.stackTrace.joinToString("\n")}")
            
            // Try to show a simple fallback UI instead of crashing
            try {
                // Just show error message instead of creating fallback layout
                showError("Lỗi khởi tạo ứng dụng: ${e.message}")
            } catch (fallbackError: Exception) {
                Log.e("ConversationHistory", "Even error display failed", fallbackError)
                // Last resort - finish activity
                try {
                    finish()
                } catch (finishError: Exception) {
                    Log.e("ConversationHistory", "Error finishing activity", finishError)
                }
            }
        }
    }
    
    private fun setupUI() {
        try {
            // Skip ActionBar setup to avoid issues
            // supportActionBar?.setDisplayHomeAsUpEnabled(true)
            // supportActionBar?.title = "Lịch sử trò chuyện"
            
            // Find views with null checks using Elvis operator
            recyclerView = findViewById(R.id.conversationsRecyclerView)
                ?: throw RuntimeException("Required view conversationsRecyclerView not found")
            
            // Fix: emptyView is a LinearLayout, not TextView - find the container
            emptyViewContainer = findViewById<android.widget.LinearLayout>(R.id.emptyView)
                ?: throw RuntimeException("Required view emptyView not found")
            
            // Create a TextView reference for the empty message - find the actual text view inside
            emptyView = emptyViewContainer.findViewById<TextView>(android.R.id.text1) 
                ?: emptyViewContainer.getChildAt(1) as? TextView  // Second child should be the main text
                ?: TextView(this).apply {
                    text = "Chưa có cuộc trò chuyện nào"
                    emptyViewContainer.addView(this)
                    Log.w("ConversationHistory", "Created fallback TextView for empty message")
                }
            
            // Add loading view if exists in layout
            loadingView = findViewById<ProgressBar>(R.id.loadingProgress)
                ?: ProgressBar(this).apply {
                    visibility = View.GONE
                    Log.w("ConversationHistory", "loadingProgress not found, created programmatically")
                }
            
            // Add loading container if exists in layout
            loadingContainer = findViewById<android.widget.LinearLayout>(R.id.loadingContainer)
                ?: android.widget.LinearLayout(this).apply {
                    visibility = View.GONE
                    Log.w("ConversationHistory", "loadingContainer not found, created programmatically")
                }
            
            Log.d("ConversationHistory", "UI setup completed successfully")
        } catch (e: Exception) {
            Log.e("ConversationHistory", "Error in setupUI", e)
            throw e
        }
    }
    
    private fun setupRecyclerView() {
        try {
            Log.d("ConversationHistory", "Setting up RecyclerView")
            
            adapter = ConversationHistoryAdapter(conversations) { conversation ->
                openConversationDetail(conversation)
            }
            
            recyclerView.layoutManager = LinearLayoutManager(this)
            recyclerView.adapter = adapter
            
            Log.d("ConversationHistory", "RecyclerView setup completed")
        } catch (e: Exception) {
            Log.e("ConversationHistory", "Error in setupRecyclerView", e)
            throw e
        }
    }
    
    private fun openConversationDetail(conversation: Map<String, Any>) {
        try {
            val conversationId = conversation["id"] as? String
            val conversationTitle = conversation["title"] as? String ?: "Cuộc trò chuyện"
            
            if (conversationId.isNullOrEmpty()) {
                Log.e("ConversationHistory", "Conversation ID is null or empty")
                showError("ID cuộc trò chuyện không hợp lệ")
                return
            }
            
            Log.d("ConversationHistory", "Opening conversation detail: $conversationTitle (ID: $conversationId)")
            
            val intent = Intent(this, ConversationDetailActivity::class.java)
            intent.putExtra("conversation_id", conversationId)
            intent.putExtra("conversation_title", conversationTitle)
            
            // Add extra safety check before starting activity
            if (intent.resolveActivity(packageManager) != null) {
                startActivity(intent)
                Log.d("ConversationHistory", "ConversationDetailActivity started successfully")
            } else {
                Log.e("ConversationHistory", "ConversationDetailActivity not found")
                showError("Không thể mở chi tiết cuộc trò chuyện - Activity không tồn tại")
            }
        } catch (e: Exception) {
            Log.e("ConversationHistory", "Error opening conversation detail", e)
            Log.e("ConversationHistory", "Conversation data: $conversation")
            showError("Lỗi mở chi tiết cuộc trò chuyện: ${e.message}")
        }
    }
    
    private fun loadConversations() {
        // Cancel previous loading job and wait a bit
        loadingJob?.cancel()
        
        Log.d("ConversationHistory", "=== loadConversations() START ===")
        
        val userId = userPreferences.getUserId()
        val isLoggedIn = userPreferences.isLoggedIn()
        Log.d("ConversationHistory", "User ID: '$userId'")
        Log.d("ConversationHistory", "Is logged in: $isLoggedIn")
        
        // Check if user is logged in
        if (userId.isNullOrEmpty() || !isLoggedIn) {
            Log.e("ConversationHistory", "User not logged in or no user ID found")
            showError("Vui lòng đăng nhập để xem lịch sử trò chuyện")
            finish()
            return
        }
        
        Log.d("ConversationHistory", "API Base URL: ${ApiConfig.BASE_URL}")
        Log.d("ConversationHistory", "Using userId: $userId")
        
        // Kiểm tra cache trước
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val cachedData = dataCacheManager.getCachedConversations(userId)
                if (cachedData != null) {
                    Log.d("ConversationHistory", "Found ${cachedData.size} conversations in cache")
                    
                    withContext(Dispatchers.Main) {
                        // Hiển thị data từ cache ngay lập tức
                        conversations.clear()
                        conversations.addAll(cachedData)
                        adapter.updateData(cachedData)
                        
                        if (cachedData.isEmpty()) {
                            showEmptyState("Chưa có cuộc trò chuyện nào")
                        } else {
                            showConversations()
                        }
                        
                        isDataFromCache = true
                        Log.d("ConversationHistory", "Displayed conversations from cache")
                    }
                }
            } catch (e: Exception) {
                Log.w("ConversationHistory", "Error loading from cache", e)
            }
        }
        
        // Show loading state
        showLoading(true)
        
        // Use lifecycleScope instead of CoroutineScope
        loadingJob = lifecycleScope.launch(Dispatchers.IO) {
            try {
                // Small delay to avoid race conditions
                kotlinx.coroutines.delay(100)
                
                Log.d("ConversationHistory", "=== STARTING API CALL ===")
                Log.d("ConversationHistory", "Making API call to get conversations for userId: $userId")
                Log.d("ConversationHistory", "Full API URL: ${ApiConfig.BASE_URL}api/conversations/$userId")
                
                val response = ApiClient.getUserConversations(userId)
                
                Log.d("ConversationHistory", "=== API CALL COMPLETED ===")
                Log.d("ConversationHistory", "Response is null: ${response == null}")
                if (response != null) {
                    Log.d("ConversationHistory", "Response keys: ${response.keys}")
                    Log.d("ConversationHistory", "Response size: ${response.size}")
                }
                
                // Ensure we're still active before updating UI
                if (!isActive) {
                    Log.d("ConversationHistory", "Coroutine cancelled, not updating UI")
                    return@launch
                }
                
                withContext(Dispatchers.Main) {
                    showLoading(false)
                    
                    Log.d("ConversationHistory", "=== ANALYZING RESPONSE ===")
                    if (response == null) {
                        Log.e("ConversationHistory", "Response is null")
                        showError("Không nhận được phản hồi từ server")
                        return@withContext
                    }
                    
                    Log.d("ConversationHistory", "Response type: ${response.javaClass.simpleName}")
                    Log.d("ConversationHistory", "Response keys: ${response.keys.toList()}")
                    
                    // Check if response contains conversations key
                    val hasConversationsKey = response.containsKey("conversations")
                    Log.d("ConversationHistory", "Has 'conversations' key: $hasConversationsKey")
                    
                    if (hasConversationsKey) {
                        val conversationsValue = response["conversations"]
                        Log.d("ConversationHistory", "Conversations value type: ${conversationsValue?.javaClass?.simpleName}")
                        
                        @Suppress("UNCHECKED_CAST")
                        val conversationList = conversationsValue as? List<Map<String, Any>> ?: emptyList()
                        
                        Log.d("ConversationHistory", "Conversation list size: ${conversationList.size}")
                        
                        if (conversationList.isNotEmpty()) {
                            Log.d("ConversationHistory", "First conversation: ${conversationList[0]}")
                        }
                        
                        // Cache data mới
                        try {
                            dataCacheManager.cacheConversations(userId, conversationList)
                            Log.d("ConversationHistory", "Cached ${conversationList.size} conversations")
                        } catch (e: Exception) {
                            Log.w("ConversationHistory", "Error caching conversations", e)
                        }
                        
                        // Update adapter with new data
                        Log.d("ConversationHistory", "=== UPDATING ADAPTER ===")
                        adapter.updateData(conversationList)
                        
                        Log.d("ConversationHistory", "=== UPDATING UI ===")
                        Log.d("ConversationHistory", "Adapter item count after update: ${adapter.itemCount}")
                        
                        // Show/hide empty view
                        if (conversationList.isEmpty()) {
                            Log.d("ConversationHistory", "Showing empty state - conversationList is empty")
                            showEmptyState("Chưa có cuộc trò chuyện nào")
                        } else {
                            Log.d("ConversationHistory", "Showing conversations - found ${conversationList.size} items")
                            showConversations()
                            
                            // Log first few conversations for verification
                            conversationList.take(3).forEachIndexed { index, conv ->
                                val title = conv["title"] as? String ?: "No title"
                                val id = conv["id"] as? String ?: "No ID"
                                Log.d("ConversationHistory", "Conversation $index: ID=$id, Title=$title")
                            }
                        }
                        
                        isDataFromCache = false
                    } else {
                        Log.e("ConversationHistory", "=== INVALID API RESPONSE - NO CONVERSATIONS KEY ===")
                        Log.e("ConversationHistory", "Available keys: ${response.keys.toList()}")
                        showError("Định dạng phản hồi không đúng từ server")
                    }
                }
                
            } catch (e: CancellationException) {
                Log.d("ConversationHistory", "Loading cancelled")
            } catch (e: Exception) {
                Log.e("ConversationHistory", "Error loading conversations", e)
                if (isActive) {
                    withContext(Dispatchers.Main) {
                        showLoading(false)
                        val errorMessage = when {
                            e.message?.contains("timeout") == true -> "Kết nối bị timeout. Vui lòng thử lại."
                            e.message?.contains("network") == true -> "Lỗi kết nối mạng. Kiểm tra internet và thử lại."
                            e.message?.contains("404") == true -> "Không tìm thấy dữ liệu."
                            e.message?.contains("500") == true -> "Lỗi server. Vui lòng thử lại sau."
                            else -> "Lỗi: ${e.message}"
                        }
                        showError(errorMessage)
                    }
                }
            }
        }
    }
    
    private fun showLoading(show: Boolean) {
        if (show) {
            loadingContainer.visibility = View.VISIBLE
            recyclerView.visibility = View.GONE
            emptyViewContainer.visibility = View.GONE
            
            // Add loading animation - ProgressBar is always indeterminate by default
            // Add shimmer animation to loading container
            try {
                val animator = android.animation.ObjectAnimator.ofFloat(loadingContainer, "alpha", 0.3f, 1.0f)
                animator.duration = 1500
                animator.repeatCount = android.animation.ObjectAnimator.INFINITE
                animator.repeatMode = android.animation.ObjectAnimator.REVERSE
                animator.start()
            } catch (e: Exception) {
                Log.w("ConversationHistory", "Could not start loading animation", e)
            }
            
            Log.d("ConversationHistory", "Loading state: SHOWING with animation")
        } else {
            loadingContainer.visibility = View.GONE
            loadingContainer.alpha = 1.0f // Reset alpha
            Log.d("ConversationHistory", "Loading state: HIDDEN")
        }
    }
    
    private fun showConversations() {
        recyclerView.visibility = View.VISIBLE
        emptyViewContainer.visibility = View.GONE
        loadingView.visibility = View.GONE
    }
    
    private fun showEmptyState(message: String) {
        recyclerView.visibility = View.GONE
        emptyViewContainer.visibility = View.VISIBLE
        emptyView.text = message
        loadingView.visibility = View.GONE
    }
    
    private fun showError(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show()
        // Show empty view on error if views are initialized
        try {
            if (::emptyViewContainer.isInitialized) {
                showEmptyState("Có lỗi xảy ra. Vui lòng thử lại.")
            }
        } catch (e: Exception) {
            Log.e("ConversationHistory", "Error showing empty state", e)
        }
    }
    
    override fun onResume() {
        super.onResume()
        // Refresh conversations when returning from detail view
        // Chỉ refresh nếu data không phải từ cache hoặc cache đã cũ
        if (!isDataFromCache) {
            loadConversations()
        }
    }
    
    /**
     * Force refresh data từ server (bỏ qua cache)
     */
    fun forceRefresh() {
        isDataFromCache = false
        loadConversations()
    }
    
    private fun createFallbackLayout(): android.view.View {
        // Create a simple fallback layout programmatically
        val linearLayout = android.widget.LinearLayout(this).apply {
            orientation = android.widget.LinearLayout.VERTICAL
            setPadding(32, 32, 32, 32)
        }
        
        val titleText = TextView(this).apply {
            text = "Lịch sử trò chuyện"
            textSize = 20f
            setTypeface(null, android.graphics.Typeface.BOLD)
            setPadding(0, 0, 0, 32)
        }
        
        val errorText = TextView(this).apply {
            text = "Có lỗi xảy ra khi tải giao diện. Vui lòng thử lại sau."
            textSize = 16f
            setPadding(0, 0, 0, 32)
        }
        
        val backButton = android.widget.Button(this).apply {
            text = "Quay lại"
            setOnClickListener { finish() }
        }
        
        linearLayout.addView(titleText)
        linearLayout.addView(errorText)
        linearLayout.addView(backButton)
        
        return linearLayout
    }

    override fun onDestroy() {
        super.onDestroy()
        // Cancel loading job to prevent memory leaks
        loadingJob?.cancel()
        // Hủy đăng ký callback
        globalConnectionManager.unregisterCallback(this)
    }
    
    // Callback methods từ GlobalConnectionManager.ConnectionStateCallback
    override fun onConnectionStateChanged(isConnected: Boolean) {
        Log.d("ConversationHistoryActivity", "Connection state changed: $isConnected")
        // ConversationHistoryActivity không cần xử lý connection state đặc biệt
    }
    
    override fun onChatAvailabilityChanged(isChatAvailable: Boolean) {
        Log.d("ConversationHistoryActivity", "Chat availability changed: $isChatAvailable")
        // ConversationHistoryActivity không có chat UI nên không cần xử lý
    }
} 