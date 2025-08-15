package com.example.geminilivedemo

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
import com.example.geminilivedemo.data.UserPreferences
import com.example.geminilivedemo.adapters.MessageAdapter
import com.example.geminilivedemo.data.DataCacheManager
import kotlinx.coroutines.*

class ConversationDetailActivity : AppCompatActivity() {
    
    private lateinit var userPreferences: UserPreferences

    private lateinit var dataCacheManager: DataCacheManager
    private lateinit var recyclerView: RecyclerView
    private lateinit var adapter: MessageAdapter
    private lateinit var emptyView: TextView
    private lateinit var loadingView: ProgressBar
    
    private val messages = mutableListOf<Map<String, Any>>()
    private var conversationId: String? = null
    private var conversationTitle: String? = null
    private var loadingJob: Job? = null
    private var isDataFromCache = false
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_conversation_detail)
        
        try {
            // Get extras from intent
            conversationId = intent.getStringExtra("conversation_id")
            conversationTitle = intent.getStringExtra("conversation_title")
            
            if (conversationId.isNullOrEmpty()) {
                Toast.makeText(this, "ID cuộc trò chuyện không hợp lệ", Toast.LENGTH_SHORT).show()
                finish()
                return
            }
            
            // Initialize components
            userPreferences = UserPreferences(this)

            dataCacheManager = DataCacheManager.getInstance(this)
            
            // Setup UI
            setupUI()
            setupRecyclerView()
            
            // Load conversation messages
            loadConversationMessages()
        } catch (e: Exception) {
            Log.e("ConversationDetail", "Error in onCreate", e)
            Toast.makeText(this, "Lỗi khởi tạo: ${e.message}", Toast.LENGTH_SHORT).show()
            finish()
        }
    }
    
    private fun setupUI() {
        // Setup toolbar
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = conversationTitle ?: "Chi tiết trò chuyện"
        
        recyclerView = findViewById(R.id.messagesRecyclerView)
        emptyView = findViewById(R.id.emptyView)
        
        // Add loading view if exists in layout
        loadingView = findViewById<ProgressBar>(R.id.loadingProgress) ?: run {
            // Create loading view programmatically if not in layout
            ProgressBar(this).apply {
                visibility = View.GONE
            }
        }
    }
    
    private fun setupRecyclerView() {
        adapter = MessageAdapter(messages)
        
        recyclerView.layoutManager = LinearLayoutManager(this)
        recyclerView.adapter = adapter
    }
    
    private fun loadConversationMessages() {
        // Cancel previous loading job
        loadingJob?.cancel()
        
        val userId = userPreferences.getUserId()
        if (userId.isNullOrEmpty() || conversationId.isNullOrEmpty()) {
            showError("Thông tin người dùng hoặc cuộc trò chuyện không hợp lệ")
            return
        }
        
        // Kiểm tra cache trước
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val cachedData = dataCacheManager.getCachedConversationMessages(conversationId!!)
                if (cachedData != null) {
                    Log.d("ConversationDetail", "Found ${cachedData.size} messages in cache")
                    
                    withContext(Dispatchers.Main) {
                        // Hiển thị data từ cache ngay lập tức
                        messages.clear()
                        messages.addAll(cachedData)
                        adapter.notifyDataSetChanged()
                        
                        if (cachedData.isEmpty()) {
                            showEmptyState("Cuộc trò chuyện này chưa có tin nhắn nào")
                        } else {
                            showMessages()
                            // Scroll to bottom (latest message)
                            recyclerView.scrollToPosition(messages.size - 1)
                        }
                        
                        isDataFromCache = true
                        Log.d("ConversationDetail", "Displayed messages from cache")
                    }
                }
            } catch (e: Exception) {
                Log.w("ConversationDetail", "Error loading from cache", e)
            }
        }
        
        // Show loading state
        showLoading(true)
        
        loadingJob = CoroutineScope(Dispatchers.IO).launch {
            try {
                Log.d("ConversationDetail", "Loading conversation detail for userId: $userId, conversationId: $conversationId")
                val response = ApiClient.getConversationDetail(userId, conversationId!!)
                
                withContext(Dispatchers.Main) {
                    showLoading(false)
                    
                    if (response != null && response.containsKey("messages")) {
                        @Suppress("UNCHECKED_CAST")
                        val messageList = response["messages"] as? List<Map<String, Any>> ?: emptyList()
                        
                        // Cache data mới
                        try {
                            dataCacheManager.cacheConversationMessages(conversationId!!, messageList)
                            Log.d("ConversationDetail", "Cached ${messageList.size} messages")
                        } catch (e: Exception) {
                            Log.w("ConversationDetail", "Error caching messages", e)
                        }
                        
                        messages.clear()
                        messages.addAll(messageList)
                        
                        adapter.notifyDataSetChanged()
                        
                        // Show/hide empty view
                        if (messages.isEmpty()) {
                            showEmptyState("Cuộc trò chuyện này chưa có tin nhắn nào")
                        } else {
                            showMessages()
                            // Scroll to bottom (latest message)
                            recyclerView.scrollToPosition(messages.size - 1)
                        }
                        
                        // Update conversation details if available
                        if (response.containsKey("conversation")) {
                            @Suppress("UNCHECKED_CAST")
                            val conversation = response["conversation"] as? Map<String, Any>
                            val summary = conversation?.get("summary") as? String
                            @Suppress("UNCHECKED_CAST")
                            val topics = conversation?.get("topics") as? List<String>
                            
                            updateConversationInfo(summary, topics)
                        }
                        
                        isDataFromCache = false
                        
                    } else {
                        Log.e("ConversationDetail", "Invalid API response: $response")
                        showError("Không thể tải chi tiết cuộc trò chuyện")
                    }
                }
                
            } catch (e: CancellationException) {
                Log.d("ConversationDetail", "Loading cancelled")
            } catch (e: Exception) {
                Log.e("ConversationDetail", "Error loading conversation", e)
                withContext(Dispatchers.Main) {
                    showLoading(false)
                    val errorMessage = when {
                        e.message?.contains("timeout") == true -> "Kết nối bị timeout. Vui lòng thử lại."
                        e.message?.contains("network") == true -> "Lỗi kết nối mạng. Kiểm tra internet và thử lại."
                        e.message?.contains("404") == true -> "Không tìm thấy cuộc trò chuyện."
                        e.message?.contains("500") == true -> "Lỗi server. Vui lòng thử lại sau."
                        else -> "Lỗi: ${e.message}"
                    }
                    showError(errorMessage)
                }
            }
        }
    }
    
    private fun showLoading(show: Boolean) {
        if (show) {
            loadingView.visibility = View.VISIBLE
            recyclerView.visibility = View.GONE
            emptyView.visibility = View.GONE
        } else {
            loadingView.visibility = View.GONE
        }
    }
    
    private fun showMessages() {
        recyclerView.visibility = View.VISIBLE
        emptyView.visibility = View.GONE
        loadingView.visibility = View.GONE
    }
    
    private fun showEmptyState(message: String) {
        recyclerView.visibility = View.GONE
        emptyView.visibility = View.VISIBLE
        emptyView.text = message
        loadingView.visibility = View.GONE
    }
    
    private fun showError(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show()
        showEmptyState("Có lỗi xảy ra. Vui lòng thử lại.")
    }
    
    private fun updateConversationInfo(summary: String?, topics: List<String>?) {
        // You can show conversation summary and topics in a header view if needed
        // For now, just log them
        Log.d("ConversationDetail", "Summary: $summary, Topics: $topics")
    }
    
    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
    
    override fun onDestroy() {
        super.onDestroy()
        // Cancel loading job to prevent memory leaks
        loadingJob?.cancel()
    }
} 