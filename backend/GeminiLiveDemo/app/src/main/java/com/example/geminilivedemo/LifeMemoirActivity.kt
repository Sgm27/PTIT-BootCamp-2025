package com.example.geminilivedemo

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.geminilivedemo.data.ApiClient
import com.example.geminilivedemo.data.UserPreferences
import com.example.geminilivedemo.adapters.MemoirAdapter
import kotlinx.coroutines.*

class LifeMemoirActivity : AppCompatActivity() {
    
    private lateinit var userPreferences: UserPreferences
    private lateinit var apiClient: ApiClient
    private lateinit var recyclerView: RecyclerView
    private lateinit var adapter: MemoirAdapter
    private lateinit var emptyView: TextView
    private lateinit var statsView: TextView
    
    private val memoirs = mutableListOf<Map<String, Any>>()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_life_memoir)
        
        // Initialize components
        userPreferences = UserPreferences(this)
        apiClient = ApiClient.instance
        
        // Setup UI
        setupUI()
        setupRecyclerView()
        
        // Load memoirs
        loadMemoirs()
        loadMemoirStats()
    }
    
    private fun setupUI() {
        // Setup toolbar
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = "Những câu chuyện đời"
        
        recyclerView = findViewById(R.id.memoirsRecyclerView)
        emptyView = findViewById(R.id.emptyView)
        statsView = findViewById(R.id.statsView)
    }
    
    private fun setupRecyclerView() {
        adapter = MemoirAdapter(memoirs) { memoir ->
            openMemoirDetail(memoir)
        }
        
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
        val userId = userPreferences.getUserId()
        if (userId.isNullOrEmpty()) {
            Log.e("LifeMemoir", "User ID is null or empty")
            Toast.makeText(this, "User not logged in", Toast.LENGTH_SHORT).show()
            return
        }
        
        Log.d("LifeMemoir", "Loading memoirs for user: $userId")
        
        CoroutineScope(Dispatchers.IO).launch {
            try {
                Log.d("LifeMemoir", "Making API call to get user memoirs")
                val response = apiClient.getUserMemoirs(userId)
                
                Log.d("LifeMemoir", "API response received: $response")
                
                withContext(Dispatchers.Main) {
                    if (response != null) {
                        if (response.containsKey("memoirs")) {
                            val memoirList = response["memoirs"] as? List<Map<String, Any>>
                            
                            if (memoirList != null) {
                                Log.d("LifeMemoir", "Found ${memoirList.size} memoirs")
                                memoirs.clear()
                                memoirs.addAll(memoirList)
                                
                                adapter.notifyDataSetChanged()
                                
                                // Show/hide empty view
                                if (memoirs.isEmpty()) {
                                    recyclerView.visibility = View.GONE
                                    emptyView.visibility = View.VISIBLE
                                } else {
                                    recyclerView.visibility = View.VISIBLE
                                    emptyView.visibility = View.GONE
                                }
                            } else {
                                Log.e("LifeMemoir", "Memoirs list is null")
                                Toast.makeText(this@LifeMemoirActivity, 
                                    "Invalid memoir data format", Toast.LENGTH_SHORT).show()
                            }
                        } else {
                            Log.d("LifeMemoir", "No memoirs key in response, showing empty view")
                            // No memoirs found, show empty view
                            recyclerView.visibility = View.GONE
                            emptyView.visibility = View.VISIBLE
                        }
                    } else {
                        Log.e("LifeMemoir", "Response is null")
                        Toast.makeText(this@LifeMemoirActivity, 
                            "Failed to load memoirs", Toast.LENGTH_SHORT).show()
                    }
                }
                
            } catch (e: Exception) {
                Log.e("LifeMemoir", "Error loading memoirs", e)
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@LifeMemoirActivity, 
                        "Error: ${e.message}", Toast.LENGTH_SHORT).show()
                    // Show empty view on error
                    recyclerView.visibility = View.GONE
                    emptyView.visibility = View.VISIBLE
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
        
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val response = apiClient.getUserStats(userId)
                
                Log.d("LifeMemoir", "Stats response received: $response")
                
                withContext(Dispatchers.Main) {
                    if (response != null && response.containsKey("memoir_stats")) {
                        val memoirStats = response["memoir_stats"] as? Map<String, Any>
                        if (memoirStats != null) {
                            val totalMemoirs = memoirStats["total_memoirs"] as? Int ?: 0
                            val categoriesCount = memoirStats["categories_count"] as? Int ?: 0
                            
                            statsView.text = "Tổng: $totalMemoirs câu chuyện • $categoriesCount chủ đề"
                            statsView.visibility = View.VISIBLE
                            Log.d("LifeMemoir", "Stats loaded: $totalMemoirs memoirs, $categoriesCount categories")
                        } else {
                            Log.e("LifeMemoir", "Memoir stats is null")
                        }
                    } else {
                        Log.d("LifeMemoir", "No memoir stats in response")
                        // Hide stats view if no data
                        statsView.visibility = View.GONE
                    }
                }
                
            } catch (e: Exception) {
                Log.e("LifeMemoir", "Error loading memoir stats", e)
                withContext(Dispatchers.Main) {
                    // Hide stats view on error
                    statsView.visibility = View.GONE
                }
            }
        }
    }
    
    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
    
    override fun onResume() {
        super.onResume()
        // Refresh memoirs when returning from detail view
        loadMemoirs()
    }
} 