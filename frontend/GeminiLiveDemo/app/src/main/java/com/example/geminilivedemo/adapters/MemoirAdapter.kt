package com.example.geminilivedemo.adapters

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import android.view.animation.AnimationUtils
import androidx.recyclerview.widget.RecyclerView
import com.example.geminilivedemo.R
import java.text.SimpleDateFormat
import java.util.*

class MemoirAdapter(
    private val memoirs: List<Map<String, Any>>,
    private val onItemClick: (Map<String, Any>) -> Unit,
    private val isLoading: Boolean = false
) : RecyclerView.Adapter<RecyclerView.ViewHolder>() {

    companion object {
        private const val VIEW_TYPE_MEMOIR = 0
        private const val VIEW_TYPE_LOADING = 1
    }

    private val dateFormat = SimpleDateFormat("dd/MM/yyyy", Locale.getDefault())

    override fun getItemViewType(position: Int): Int {
        return if (isLoading && position >= memoirs.size) VIEW_TYPE_LOADING else VIEW_TYPE_MEMOIR
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        return when (viewType) {
            VIEW_TYPE_MEMOIR -> {
                val view = LayoutInflater.from(parent.context)
                    .inflate(R.layout.item_memoir, parent, false)
                MemoirViewHolder(view)
            }
            VIEW_TYPE_LOADING -> {
                val view = LayoutInflater.from(parent.context)
                    .inflate(R.layout.item_memoir_loading, parent, false)
                LoadingViewHolder(view)
            }
            else -> throw IllegalArgumentException("Invalid view type")
        }
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        when (holder) {
            is MemoirViewHolder -> {
                if (position < memoirs.size) {
                    val memoir = memoirs[position]
                    holder.bind(memoir)
                }
            }
            is LoadingViewHolder -> {
                // Apply shimmer animation to loading view
                holder.applyShimmerAnimation()
            }
        }
    }

    override fun getItemCount(): Int {
        return if (isLoading) memoirs.size + 3 else memoirs.size // Show 3 loading items
    }

    inner class MemoirViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        
        private val titleTextView: TextView = itemView.findViewById(R.id.memoirTitle)
        private val contentTextView: TextView = itemView.findViewById(R.id.memoirContent)
        private val dateTextView: TextView = itemView.findViewById(R.id.memoirDate)
        private val categoriesTextView: TextView = itemView.findViewById(R.id.memoirCategories)
        private val timePeriodTextView: TextView = itemView.findViewById(R.id.memoirTimePeriod)
        private val importanceIndicator: View = itemView.findViewById(R.id.importanceIndicator)

        fun bind(memoir: Map<String, Any>) {
            // Set title
            val title = memoir["title"] as? String ?: "Câu chuyện"
            titleTextView.text = title

            // Set content preview (first 120 characters)
            val content = memoir["content"] as? String ?: ""
            val contentPreview = if (content.length > 120) {
                content.substring(0, 120) + "..."
            } else {
                content
            }
            contentTextView.text = contentPreview

            // Set date with better error handling
            val dateOfMemory = memoir["date_of_memory"] as? String
            val extractedAt = memoir["extracted_at"] as? String
            
            val displayDate = when {
                !dateOfMemory.isNullOrEmpty() -> {
                    try {
                        val isoFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
                        val date = isoFormat.parse(dateOfMemory)
                        if (date != null) dateFormat.format(date) else dateOfMemory
                    } catch (e: Exception) {
                        dateOfMemory
                    }
                }
                !extractedAt.isNullOrEmpty() -> {
                    try {
                        val isoFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
                        val date = isoFormat.parse(extractedAt)
                        if (date != null) dateFormat.format(date) else extractedAt
                    } catch (e: Exception) {
                        extractedAt
                    }
                }
                else -> "Không rõ ngày"
            }
            dateTextView.text = displayDate

            // Set categories with better formatting
            val categories = memoir["categories"] as? List<String>
            if (!categories.isNullOrEmpty()) {
                val formattedCategories = categories.take(3).joinToString(" • ") // Limit to 3 categories
                categoriesTextView.text = formattedCategories
                categoriesTextView.visibility = View.VISIBLE
            } else {
                categoriesTextView.visibility = View.GONE
            }

            // Set time period
            val timePeriod = memoir["time_period"] as? String
            if (!timePeriod.isNullOrEmpty()) {
                timePeriodTextView.text = timePeriod
                timePeriodTextView.visibility = View.VISIBLE
            } else {
                timePeriodTextView.visibility = View.GONE
            }

            // Set importance indicator with better logic
            val importance = memoir["importance_score"] as? Double ?: 0.0
            when {
                importance >= 0.8 -> {
                    importanceIndicator.setBackgroundResource(R.drawable.notification_dot) // High importance - red
                    importanceIndicator.visibility = View.VISIBLE
                }
                importance >= 0.5 -> {
                    importanceIndicator.setBackgroundResource(R.drawable.notification_dot_shape) // Medium importance - yellow  
                    importanceIndicator.visibility = View.VISIBLE
                }
                else -> importanceIndicator.visibility = View.GONE // Low importance - hidden
            }

            // Set click listener
            itemView.setOnClickListener {
                onItemClick(memoir)
            }
        }
    }

    inner class LoadingViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        
        fun applyShimmerAnimation() {
            try {
                val shimmerAnimation = AnimationUtils.loadAnimation(itemView.context, R.anim.shimmer_animation)
                itemView.startAnimation(shimmerAnimation)
            } catch (e: Exception) {
                // Animation might not be available, ignore
            }
        }
    }
} 