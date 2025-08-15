package com.example.geminilivedemo

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.TextView
import android.widget.Toast
import android.widget.LinearLayout
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import androidx.cardview.widget.CardView
import com.example.geminilivedemo.data.ApiClient
import com.example.geminilivedemo.data.UserPreferences
import com.example.geminilivedemo.adapters.MemoirAdapter
import com.example.geminilivedemo.data.DataCacheManager
import kotlinx.coroutines.*

class LifeMemoirActivity : AppCompatActivity() {
    
    private lateinit var userPreferences: UserPreferences

    private lateinit var dataCacheManager: DataCacheManager
    private lateinit var recyclerView: RecyclerView
    private lateinit var adapter: MemoirAdapter
    private lateinit var emptyView: LinearLayout
    private lateinit var statsCard: CardView
    private lateinit var totalMemoirsText: TextView
    private lateinit var totalCategoriesText: TextView
    private lateinit var loadingView: com.google.android.material.progressindicator.CircularProgressIndicator
    private lateinit var loadingContainer: LinearLayout
    
    private val memoirs = mutableListOf<Map<String, Any>>()
    private var loadingJob: Job? = null
    private var isDataFromCache = false
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_life_memoir)
        
        // Initialize components
        userPreferences = UserPreferences(this)
        
        dataCacheManager = DataCacheManager.getInstance(this)
        
        // Setup UI
        setupUI()
        setupRecyclerView()
        
        // Load memoirs first (this is the main functionality)
        loadMemoirs()
        
        // Load stats in background (optional, won't crash if it fails)
        loadMemoirStats()
    }
    
    private fun setupUI() {
        // Setup toolbar
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = "Những câu chuyện đời"
        
        recyclerView = findViewById(R.id.memoirsRecyclerView)
        emptyView = findViewById(R.id.emptyView)
        statsCard = findViewById(R.id.statsCard)
        totalMemoirsText = findViewById(R.id.totalMemoirsText)
        totalCategoriesText = findViewById(R.id.totalCategoriesText)
        loadingView = findViewById(R.id.loadingProgress)
        loadingContainer = findViewById(R.id.loadingContainer)
        
        // Initially show loading state
        showLoading(true)
    }
    
    private fun setupRecyclerView() {
        adapter = MemoirAdapter(
            memoirs = memoirs,
            onItemClick = { memoir ->
                openMemoirDetail(memoir)
            },
            isLoading = false
        )
        
        recyclerView.layoutManager = LinearLayoutManager(this)
        recyclerView.adapter = adapter
    }
    
    private fun openMemoirDetail(memoir: Map<String, Any>) {
        try {
            val memoirId = memoir["id"] as? String
            val memoirTitle = memoir["title"] as? String ?: "Câu chuyện"
            
            if (memoirId != null) {
                val intent = Intent(this, MemoirDetailActivity::class.java)
                intent.putExtra("memoir_id", memoirId)
                intent.putExtra("memoir_title", memoirTitle)
                startActivity(intent)
                Log.d("LifeMemoir", "Opening memoir detail for ID: $memoirId")
            } else {
                Log.e("LifeMemoir", "Memoir ID is null, cannot open detail")
                Toast.makeText(this, "Không thể mở chi tiết câu chuyện", Toast.LENGTH_SHORT).show()
            }
        } catch (e: Exception) {
            Log.e("LifeMemoir", "Error opening memoir detail", e)
            Toast.makeText(this, "Lỗi khi mở chi tiết: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }
    
    private fun loadMemoirs() {
        // Cancel previous loading job
        loadingJob?.cancel()
        
        val userId = userPreferences.getUserId()
        if (userId.isNullOrEmpty()) {
            Log.e("LifeMemoir", "User ID is null or empty")
            Toast.makeText(this, "User not logged in", Toast.LENGTH_SHORT).show()
            return
        }
        
        Log.d("LifeMemoir", "Loading memoirs for user: $userId")
        
        // Kiểm tra cache trước
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val cachedData = dataCacheManager.getCachedMemoirs(userId)
                if (cachedData != null) {
                    Log.d("LifeMemoir", "Found ${cachedData.size} memoirs in cache")
                    
                    withContext(Dispatchers.Main) {
                        // Hiển thị data từ cache ngay lập tức
                        memoirs.clear()
                        memoirs.addAll(cachedData)
                        adapter.notifyDataSetChanged()
                        
                        if (cachedData.isEmpty()) {
                            showEmptyState()
                        } else {
                            showMemoirs()
                        }
                        
                        isDataFromCache = true
                        Log.d("LifeMemoir", "Displayed memoirs from cache")
                    }
                }
            } catch (e: Exception) {
                Log.w("LifeMemoir", "Error loading from cache", e)
            }
        }
        
        // Show loading state
        showLoading(true)
        
        loadingJob = CoroutineScope(Dispatchers.IO).launch {
            try {
                Log.d("LifeMemoir", "Making API call to get user memoirs")
                val response = ApiClient.getUserMemoirs(userId)
                
                Log.d("LifeMemoir", "API response received: $response")
                
                withContext(Dispatchers.Main) {
                    // Hide loading state
                    showLoading(false)
                    
                    if (response != null) {
                        if (response.containsKey("memoirs")) {
                            val memoirList = response["memoirs"] as? List<Map<String, Any>>
                            
                            if (memoirList != null) {
                                Log.d("LifeMemoir", "Found ${memoirList.size} memoirs")
                                
                                // Cache data mới
                                try {
                                    dataCacheManager.cacheMemoirs(userId, memoirList)
                                    Log.d("LifeMemoir", "Cached ${memoirList.size} memoirs")
                                } catch (e: Exception) {
                                    Log.w("LifeMemoir", "Error caching memoirs", e)
                                }
                                
                                memoirs.clear()
                                memoirs.addAll(memoirList)
                                
                                adapter.notifyDataSetChanged()
                                
                                // Show/hide empty view
                                if (memoirs.isEmpty()) {
                                    showEmptyState()
                                } else {
                                    showMemoirs()
                                }
                            } else {
                                Log.e("LifeMemoir", "Memoirs list is null")
                                Toast.makeText(this@LifeMemoirActivity, 
                                    "Invalid memoir data format", Toast.LENGTH_SHORT).show()
                                showEmptyState()
                            }
                        } else {
                            Log.d("LifeMemoir", "No memoirs key in response, showing empty view")
                            // No memoirs found, show empty view
                            showEmptyState()
                        }
                    } else {
                        Log.e("LifeMemoir", "Response is null")
                        Toast.makeText(this@LifeMemoirActivity, 
                            "Failed to load memoirs", Toast.LENGTH_SHORT).show()
                        showEmptyState()
                    }
                }
                
            } catch (e: Exception) {
                Log.e("LifeMemoir", "Error loading memoirs", e)
                withContext(Dispatchers.Main) {
                    showLoading(false)
                    Toast.makeText(this@LifeMemoirActivity, 
                        "Error: ${e.message}", Toast.LENGTH_SHORT).show()
                    // Show empty view on error
                    showEmptyState()
                }
            }

        }
    }
    
    private fun loadMemoirStats() {
        val userId = userPreferences.getUserId()
        if (userId.isNullOrEmpty()) {
            Log.e("LifeMemoir", "Cannot load stats: User ID is null or empty")
            return
        }
        
        Log.d("LifeMemoir", "Loading memoir stats for user: $userId")
        
        // Load stats in background without blocking the main functionality
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val response = ApiClient.getUserStats(userId)
                
                Log.d("LifeMemoir", "Stats response received: $response")
                
                withContext(Dispatchers.Main) {
                    if (response != null && response.containsKey("memoir_stats")) {
                        val memoirStats = response["memoir_stats"] as? Map<String, Any>
                        if (memoirStats != null) {
                            val totalMemoirs = memoirStats["total_memoirs"] as? Int ?: 0
                            val categoriesCount = memoirStats["categories_count"] as? Int ?: 0
                            
                            totalMemoirsText.text = totalMemoirs.toString()
                            totalCategoriesText.text = categoriesCount.toString()
                            statsCard.visibility = View.VISIBLE
                            Log.d("LifeMemoir", "Stats loaded: $totalMemoirs memoirs, $categoriesCount categories")
                        } else {
                            Log.e("LifeMemoir", "Memoir stats is null")
                            // Hide stats view if no data
                            statsCard.visibility = View.GONE
                        }
                    } else {
                        Log.d("LifeMemoir", "No memoir stats in response")
                        // Hide stats view if no data
                        statsCard.visibility = View.GONE
                    }
                }
                
            } catch (e: Exception) {
                Log.e("LifeMemoir", "Error loading memoir stats", e)
                // Don't show error toast for stats - it's optional functionality
                withContext(Dispatchers.Main) {
                    // Hide stats view on error - this won't crash the app
                    statsCard.visibility = View.GONE
                }
            }
        }
    }
    
    private fun showLoading(show: Boolean) {
        if (show) {
            loadingContainer.visibility = View.VISIBLE
            recyclerView.visibility = View.GONE
            emptyView.visibility = View.GONE
            statsCard.visibility = View.GONE
            
            // Add loading animation - CircularProgressIndicator is always indeterminate by default
            // Add shimmer animation to loading container
            try {
                val animator = android.animation.ObjectAnimator.ofFloat(loadingContainer, "alpha", 0.3f, 1.0f)
                animator.duration = 1500
                animator.repeatCount = android.animation.ObjectAnimator.INFINITE
                animator.repeatMode = android.animation.ObjectAnimator.REVERSE
                animator.start()
            } catch (e: Exception) {
                Log.w("LifeMemoir", "Could not start loading animation", e)
            }
            
            Log.d("LifeMemoir", "Loading state: SHOWING with animation")
        } else {
            loadingContainer.visibility = View.GONE
            loadingContainer.alpha = 1.0f // Reset alpha
            Log.d("LifeMemoir", "Loading state: HIDDEN")
        }
    }
    
    private fun showMemoirs() {
        recyclerView.visibility = View.VISIBLE
        emptyView.visibility = View.GONE
        loadingView.visibility = View.GONE
        // Stats card will be shown separately when stats are loaded
    }
    
    private fun showEmptyState() {
        recyclerView.visibility = View.GONE
        emptyView.visibility = View.VISIBLE
        loadingView.visibility = View.GONE
        statsCard.visibility = View.GONE
    }
    
    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
    
    override fun onResume() {
        super.onResume()
        // Refresh memoirs when returning from detail view
        // Chỉ refresh nếu data không phải từ cache hoặc cache đã cũ
        if (!isDataFromCache) {
            loadMemoirs()
        }
    }
    
    /**
     * Force refresh data từ server (bỏ qua cache)
     */
    fun forceRefresh() {
        isDataFromCache = false
        loadMemoirs()
    }
    
    override fun onDestroy() {
        super.onDestroy()
        // Cancel loading job to prevent memory leaks
        loadingJob?.cancel()
    }
} 