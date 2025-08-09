package com.example.geminilivedemo.adapters

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.geminilivedemo.R
import java.text.SimpleDateFormat
import java.util.*

class MemoirAdapter(
    private val memoirs: List<Map<String, Any>>,
    private val onItemClick: (Map<String, Any>) -> Unit
) : RecyclerView.Adapter<MemoirAdapter.MemoirViewHolder>() {

    private val dateFormat = SimpleDateFormat("dd/MM/yyyy", Locale.getDefault())

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MemoirViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_memoir, parent, false)
        return MemoirViewHolder(view)
    }

    override fun onBindViewHolder(holder: MemoirViewHolder, position: Int) {
        val memoir = memoirs[position]
        holder.bind(memoir)
    }

    override fun getItemCount(): Int = memoirs.size

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

            // Set content preview (first 100 characters)
            val content = memoir["content"] as? String ?: ""
            val contentPreview = if (content.length > 100) {
                content.substring(0, 100) + "..."
            } else {
                content
            }
            contentTextView.text = contentPreview

            // Set date
            val dateOfMemory = memoir["date_of_memory"] as? String
            val extractedAt = memoir["extracted_at"] as? String
            
            if (!dateOfMemory.isNullOrEmpty()) {
                try {
                    val isoFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
                    val date = isoFormat.parse(dateOfMemory)
                    dateTextView.text = if (date != null) dateFormat.format(date) else dateOfMemory
                } catch (e: Exception) {
                    dateTextView.text = dateOfMemory
                }
            } else if (!extractedAt.isNullOrEmpty()) {
                try {
                    val isoFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
                    val date = isoFormat.parse(extractedAt)
                    dateTextView.text = if (date != null) dateFormat.format(date) else extractedAt
                } catch (e: Exception) {
                    dateTextView.text = extractedAt
                }
            } else {
                dateTextView.text = "Không rõ ngày"
            }

            // Set categories
            val categories = memoir["categories"] as? List<String>
            if (!categories.isNullOrEmpty()) {
                categoriesTextView.text = categories.joinToString(" • ")
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

            // Set importance indicator
            val importance = memoir["importance_score"] as? Double ?: 0.0
            when {
                importance >= 0.8 -> importanceIndicator.setBackgroundResource(R.drawable.notification_dot) // High importance - red
                importance >= 0.5 -> importanceIndicator.setBackgroundResource(R.drawable.notification_dot_shape) // Medium importance - yellow  
                else -> importanceIndicator.visibility = View.GONE // Low importance - hidden
            }

            // Set click listener
            itemView.setOnClickListener {
                onItemClick(memoir)
            }
        }
    }
} 