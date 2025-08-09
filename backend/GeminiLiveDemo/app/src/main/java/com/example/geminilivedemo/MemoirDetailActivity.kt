package com.example.geminilivedemo

import android.os.Bundle
import android.util.Log
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.geminilivedemo.data.ApiClient
import com.example.geminilivedemo.data.UserPreferences
import kotlinx.coroutines.*

class MemoirDetailActivity : AppCompatActivity() {
    
    private lateinit var userPreferences: UserPreferences
    private lateinit var apiClient: ApiClient
    
    private lateinit var memoirTitle: TextView
    private lateinit var memoirContent: TextView
    private lateinit var memoirDate: TextView
    private lateinit var memoirCategories: TextView
    private lateinit var memoirPeople: TextView
    private lateinit var memoirTimePeriod: TextView
    private lateinit var memoirEmotionalTone: TextView
    
    private var memoirId: String? = null
    private var memoirTitleText: String? = null
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_memoir_detail)
        
        // Get extras from intent
        memoirId = intent.getStringExtra("memoir_id")
        memoirTitleText = intent.getStringExtra("memoir_title")
        
        if (memoirId.isNullOrEmpty()) {
            Toast.makeText(this, "Invalid memoir", Toast.LENGTH_SHORT).show()
            finish()
            return
        }
        
        // Initialize components
        userPreferences = UserPreferences(this)
        apiClient = ApiClient.instance
        
        // Setup UI
        setupUI()
        
        // Load memoir detail
        loadMemoirDetail()
    }
    
    private fun setupUI() {
        // Setup toolbar
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = memoirTitleText ?: "Chi tiết câu chuyện"
        
        memoirTitle = findViewById(R.id.memoirTitle)
        memoirContent = findViewById(R.id.memoirContent)
        memoirDate = findViewById(R.id.memoirDate)
        memoirCategories = findViewById(R.id.memoirCategories)
        memoirPeople = findViewById(R.id.memoirPeople)
        memoirTimePeriod = findViewById(R.id.memoirTimePeriod)
        memoirEmotionalTone = findViewById(R.id.memoirEmotionalTone)
    }
    
    private fun loadMemoirDetail() {
        val userId = userPreferences.getUserId()
        if (userId.isNullOrEmpty() || memoirId.isNullOrEmpty()) {
            Toast.makeText(this, "Invalid request", Toast.LENGTH_SHORT).show()
            return
        }
        
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val response = apiClient.getMemoirDetail(userId, memoirId!!)
                
                withContext(Dispatchers.Main) {
                    if (response != null && response.containsKey("memoir")) {
                        val memoir = response["memoir"] as Map<String, Any>
                        displayMemoirDetails(memoir)
                    } else {
                        Toast.makeText(this@MemoirDetailActivity, 
                            "Failed to load memoir detail", Toast.LENGTH_SHORT).show()
                    }
                }
                
            } catch (e: Exception) {
                Log.e("MemoirDetail", "Error loading memoir detail", e)
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MemoirDetailActivity, 
                        "Error: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
    
    private fun displayMemoirDetails(memoir: Map<String, Any>) {
        // Set title
        val title = memoir["title"] as? String ?: "Câu chuyện"
        memoirTitle.text = title
        
        // Set content
        val content = memoir["content"] as? String ?: ""
        memoirContent.text = content
        
        // Set date
        val dateOfMemory = memoir["date_of_memory"] as? String
        val extractedAt = memoir["extracted_at"] as? String
        if (!dateOfMemory.isNullOrEmpty()) {
            memoirDate.text = "Ngày ký ức: ${formatDate(dateOfMemory)}"
        } else if (!extractedAt.isNullOrEmpty()) {
            memoirDate.text = "Được ghi lại: ${formatDate(extractedAt)}"
        }
        
        // Set categories
        val categories = memoir["categories"] as? List<String>
        if (!categories.isNullOrEmpty()) {
            memoirCategories.text = "Chủ đề: ${categories.joinToString(", ")}"
        }
        
        // Set people mentioned
        val people = memoir["people_mentioned"] as? List<String>
        if (!people.isNullOrEmpty()) {
            memoirPeople.text = "Người được nhắc đến: ${people.joinToString(", ")}"
        }
        
        // Set time period
        val timePeriod = memoir["time_period"] as? String
        if (!timePeriod.isNullOrEmpty()) {
            memoirTimePeriod.text = "Thời kỳ: $timePeriod"
        }
        
        // Set emotional tone
        val emotionalTone = memoir["emotional_tone"] as? String
        if (!emotionalTone.isNullOrEmpty()) {
            memoirEmotionalTone.text = "Cảm xúc: $emotionalTone"
        }
    }
    
    private fun formatDate(dateString: String): String {
        // Simple date formatting - you can improve this
        return try {
            if (dateString.contains("T")) {
                dateString.split("T")[0]
            } else {
                dateString
            }
        } catch (e: Exception) {
            dateString
        }
    }
    
    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
} 