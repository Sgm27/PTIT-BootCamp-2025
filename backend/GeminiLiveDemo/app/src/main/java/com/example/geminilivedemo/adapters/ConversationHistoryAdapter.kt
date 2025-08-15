package com.example.geminilivedemo.adapters

import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.geminilivedemo.R
import java.text.SimpleDateFormat
import java.util.*

class ConversationHistoryAdapter(
    private var conversations: MutableList<Map<String, Any>>,
    private val onItemClick: (Map<String, Any>) -> Unit
) : RecyclerView.Adapter<ConversationHistoryAdapter.ConversationViewHolder>() {

    private val dateFormat = SimpleDateFormat("dd/MM/yyyy HH:mm", Locale.getDefault())
    
    fun updateData(newConversations: List<Map<String, Any>>) {
        Log.d("ConversationAdapter", "updateData() called with ${newConversations.size} items")
        conversations.clear()
        conversations.addAll(newConversations)
        notifyDataSetChanged()
        Log.d("ConversationAdapter", "Data updated, new size: ${conversations.size}")
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ConversationViewHolder {
        try {
            Log.d("ConversationAdapter", "Creating view holder")
            val view = LayoutInflater.from(parent.context)
                .inflate(R.layout.item_conversation_history, parent, false)
            return ConversationViewHolder(view)
        } catch (e: Exception) {
            Log.e("ConversationAdapter", "Error creating view holder", e)
            throw e
        }
    }

    override fun onBindViewHolder(holder: ConversationViewHolder, position: Int) {
        try {
            if (position < 0 || position >= conversations.size) {
                Log.e("ConversationAdapter", "Invalid position: $position, size: ${conversations.size}")
                return
            }
            
            val conversation = conversations[position]
            Log.d("ConversationAdapter", "Binding conversation at position $position: ${conversation["title"]}")
            holder.bind(conversation)
        } catch (e: Exception) {
            Log.e("ConversationAdapter", "Error binding view holder at position $position", e)
            // Don't crash, just log the error
        }
    }

    override fun getItemCount(): Int {
        val count = conversations.size
        Log.d("ConversationAdapter", "getItemCount() called, returning: $count")
        return count
    }

    inner class ConversationViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        
        private val titleTextView: TextView
        private val dateTextView: TextView
        private val summaryTextView: TextView
        private val messageCountTextView: TextView
        private val statusIndicator: View

        init {
            try {
                titleTextView = itemView.findViewById(R.id.conversationTitle)
                    ?: throw RuntimeException("conversationTitle not found")
                dateTextView = itemView.findViewById(R.id.conversationDate)
                    ?: throw RuntimeException("conversationDate not found")
                summaryTextView = itemView.findViewById(R.id.conversationSummary)
                    ?: throw RuntimeException("conversationSummary not found")
                messageCountTextView = itemView.findViewById(R.id.messageCount)
                    ?: throw RuntimeException("messageCount not found")
                statusIndicator = itemView.findViewById(R.id.statusIndicator)
                    ?: throw RuntimeException("statusIndicator not found")
                
                Log.d("ConversationAdapter", "ViewHolder initialized successfully")
            } catch (e: Exception) {
                Log.e("ConversationAdapter", "Error initializing ViewHolder", e)
                throw e
            }
        }

        fun bind(conversation: Map<String, Any>) {
            try {
                Log.d("ConversationAdapter", "Binding conversation: ${conversation["title"]}")
                
                // Set title with null safety
                val title = conversation["title"] as? String ?: "Cuộc trò chuyện"
                titleTextView.text = title

                // Set date with improved error handling and formatting
                val startedAt = conversation["started_at"] as? String
                if (startedAt != null) {
                    try {
                        // Handle different ISO date formats
                        val isoFormats = listOf(
                            SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSSSS", Locale.getDefault()),
                            SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault()),
                            SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())
                        )
                        
                        var parsedDate: Date? = null
                        for (format in isoFormats) {
                            try {
                                parsedDate = format.parse(startedAt)
                                break
                            } catch (e: Exception) {
                                // Try next format
                            }
                        }
                        
                        if (parsedDate != null) {
                            // Format relative time for better UX
                            val now = Date()
                            val diffInMillis = now.time - parsedDate.time
                            val diffInHours = diffInMillis / (1000 * 60 * 60)
                            val diffInDays = diffInHours / 24
                            
                            dateTextView.text = when {
                                diffInHours < 1 -> "Vừa xong"
                                diffInHours < 24 -> "${diffInHours.toInt()} giờ trước"
                                diffInDays < 7 -> "${diffInDays.toInt()} ngày trước"
                                else -> dateFormat.format(parsedDate)
                            }
                        } else {
                            dateTextView.text = startedAt.take(16) // Show first 16 chars if can't parse
                        }
                    } catch (e: Exception) {
                        Log.w("ConversationAdapter", "Error parsing date: $startedAt", e)
                        dateTextView.text = startedAt.take(16)
                    }
                } else {
                    dateTextView.text = "Không xác định"
                }

                // Set summary with improved formatting
                val summary = conversation["summary"] as? String
                if (!summary.isNullOrEmpty() && summary.trim().isNotEmpty()) {
                    // Limit summary length and add ellipsis if needed
                    val maxLength = 80
                    val displaySummary = if (summary.length > maxLength) {
                        summary.take(maxLength).trim() + "..."
                    } else {
                        summary.trim()
                    }
                    summaryTextView.text = displaySummary
                    summaryTextView.visibility = View.VISIBLE
                } else {
                    // Show a default message if no summary
                    summaryTextView.text = "Nhấn để xem chi tiết cuộc trò chuyện"
                    summaryTextView.visibility = View.VISIBLE
                    summaryTextView.alpha = 0.7f // Make it slightly transparent
                }

                // Set message count with improved formatting
                val messageCount = when (val count = conversation["total_messages"]) {
                    is Int -> count
                    is Double -> count.toInt()
                    is String -> count.toIntOrNull() ?: 0
                    else -> 0
                }
                
                // Format message count with better Vietnamese
                messageCountTextView.text = when (messageCount) {
                    0 -> "Chưa có tin nhắn"
                    1 -> "1 tin nhắn"
                    else -> "$messageCount tin nhắn"
                }

                // Set status indicator with improved visual feedback
                val isActive = conversation["is_active"] as? Boolean ?: false
                try {
                    // Use colors with better contrast and meaning
                    val color = if (isActive) {
                        0xFF2196F3.toInt() // Blue for active conversations
                    } else {
                        0xFFBDBDBD.toInt() // Light gray for inactive
                    }
                    statusIndicator.setBackgroundColor(color)
                    
                    // Add content description for accessibility
                    statusIndicator.contentDescription = if (isActive) {
                        "Cuộc trò chuyện đang hoạt động"
                    } else {
                        "Cuộc trò chuyện đã kết thúc"
                    }
                } catch (e: Exception) {
                    Log.w("ConversationAdapter", "Error setting status indicator background", e)
                    // Continue without crashing
                }

                // Set click listener with error handling
                itemView.setOnClickListener {
                    try {
                        Log.d("ConversationAdapter", "Item clicked: ${conversation["title"]}")
                        onItemClick(conversation)
                    } catch (e: Exception) {
                        Log.e("ConversationAdapter", "Error in click listener", e)
                    }
                }

                // Add topics if available (optional)
                val topics = conversation["topics"] as? List<String>
                if (!topics.isNullOrEmpty()) {
                    val topicsText = topics.joinToString(", ")
                    Log.d("ConversationAdapter", "Topics: $topicsText")
                }
                
                Log.d("ConversationAdapter", "Conversation bound successfully")
            } catch (e: Exception) {
                Log.e("ConversationAdapter", "Error binding conversation", e)
                // Set fallback values to prevent crash
                titleTextView.text = "Lỗi tải dữ liệu"
                dateTextView.text = "Không xác định"
                summaryTextView.visibility = View.GONE
                messageCountTextView.text = "0 tin nhắn"
            }
        }
    }
} 