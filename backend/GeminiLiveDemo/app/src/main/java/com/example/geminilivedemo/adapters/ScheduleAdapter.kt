package com.example.geminilivedemo.adapters

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageButton
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.geminilivedemo.R
import com.example.geminilivedemo.data.Schedule
import java.text.SimpleDateFormat
import java.util.*

class ScheduleAdapter(
    private val onScheduleClick: (Schedule) -> Unit,
    private val onScheduleComplete: (Schedule) -> Unit,
    private val onScheduleDelete: (Schedule) -> Unit
) : ListAdapter<Schedule, ScheduleAdapter.ScheduleViewHolder>(ScheduleDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ScheduleViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_schedule, parent, false)
        return ScheduleViewHolder(view)
    }

    override fun onBindViewHolder(holder: ScheduleViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    inner class ScheduleViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val titleText: TextView = itemView.findViewById(R.id.scheduleTitleText)
        private val messageText: TextView = itemView.findViewById(R.id.scheduleMessageText)
        private val timeText: TextView = itemView.findViewById(R.id.scheduleTimeText)
        private val categoryText: TextView = itemView.findViewById(R.id.scheduleCategoryText)
        private val statusText: TextView = itemView.findViewById(R.id.scheduleStatusText)
        private val completeButton: ImageButton = itemView.findViewById(R.id.completeButton)
        private val deleteButton: ImageButton = itemView.findViewById(R.id.deleteButton)

        fun bind(schedule: Schedule) {
            titleText.text = schedule.title
            messageText.text = schedule.message
            
            // Format time
            val dateFormat = SimpleDateFormat("dd/MM/yyyy HH:mm", Locale("vi"))
            val scheduledDate = Date(schedule.scheduledAt * 1000)
            timeText.text = dateFormat.format(scheduledDate)
            
            // Set category
            categoryText.text = getCategoryDisplayName(schedule.category)
            
            // Set status
            if (schedule.isCompleted) {
                statusText.text = "Đã hoàn thành"
                statusText.setTextColor(itemView.context.getColor(R.color.success_500))
                completeButton.visibility = View.GONE
            } else {
                statusText.text = "Chưa hoàn thành"
                statusText.setTextColor(itemView.context.getColor(R.color.warning_500))
                completeButton.visibility = View.VISIBLE
            }
            
            // Set click listeners
            itemView.setOnClickListener { onScheduleClick(schedule) }
            completeButton.setOnClickListener { onScheduleComplete(schedule) }
            deleteButton.setOnClickListener { onScheduleDelete(schedule) }
            
            // Set button states
            completeButton.isEnabled = !schedule.isCompleted
            deleteButton.isEnabled = true
        }
        
        private fun getCategoryDisplayName(category: String): String {
            return when (category) {
                "medicine" -> "Thuốc"
                "appointment" -> "Hẹn khám"
                "exercise" -> "Tập thể dục"
                "meal" -> "Bữa ăn"
                "other" -> "Khác"
                else -> category
            }
        }
    }
}

class ScheduleDiffCallback : DiffUtil.ItemCallback<Schedule>() {
    override fun areItemsTheSame(oldItem: Schedule, newItem: Schedule): Boolean {
        return oldItem.id == newItem.id
    }

    override fun areContentsTheSame(oldItem: Schedule, newItem: Schedule): Boolean {
        return oldItem == newItem
    }
} 