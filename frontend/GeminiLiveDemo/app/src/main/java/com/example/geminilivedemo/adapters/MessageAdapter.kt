package com.example.geminilivedemo.adapters

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.geminilivedemo.R
import java.text.SimpleDateFormat
import java.util.*

class MessageAdapter(
    private val messages: List<Map<String, Any>>
) : RecyclerView.Adapter<RecyclerView.ViewHolder>() {

    companion object {
        private const val VIEW_TYPE_USER = 1
        private const val VIEW_TYPE_ASSISTANT = 2
        private const val VIEW_TYPE_SYSTEM = 3
    }

    private val dateFormat = SimpleDateFormat("HH:mm", Locale.getDefault())

    override fun getItemViewType(position: Int): Int {
        val message = messages[position]
        return when (message["role"] as? String) {
            "user" -> VIEW_TYPE_USER
            "assistant" -> VIEW_TYPE_ASSISTANT
            "system" -> VIEW_TYPE_SYSTEM
            else -> VIEW_TYPE_SYSTEM
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        return when (viewType) {
            VIEW_TYPE_USER -> {
                val view = LayoutInflater.from(parent.context)
                    .inflate(R.layout.item_message_user, parent, false)
                UserMessageViewHolder(view)
            }
            VIEW_TYPE_ASSISTANT -> {
                val view = LayoutInflater.from(parent.context)
                    .inflate(R.layout.item_message_assistant, parent, false)
                AssistantMessageViewHolder(view)
            }
            else -> {
                val view = LayoutInflater.from(parent.context)
                    .inflate(R.layout.item_message_system, parent, false)
                SystemMessageViewHolder(view)
            }
        }
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        val message = messages[position]
        
        when (holder) {
            is UserMessageViewHolder -> holder.bind(message)
            is AssistantMessageViewHolder -> holder.bind(message)
            is SystemMessageViewHolder -> holder.bind(message)
        }
    }

    override fun getItemCount(): Int = messages.size

    // User message ViewHolder
    inner class UserMessageViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val messageText: TextView = itemView.findViewById(R.id.messageText)
        private val timestampText: TextView = itemView.findViewById(R.id.timestampText)
        private val audioIndicator: View? = itemView.findViewById(R.id.audioIndicator)

        fun bind(message: Map<String, Any>) {
            val content = message["content"] as? String ?: ""
            messageText.text = content

            // Format timestamp
            val timestamp = message["timestamp"] as? String
            if (timestamp != null) {
                try {
                    val isoFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
                    val date = isoFormat.parse(timestamp)
                    timestampText.text = if (date != null) dateFormat.format(date) else ""
                } catch (e: Exception) {
                    timestampText.text = ""
                }
            }

            // Show audio indicator if message has audio
            val hasAudio = message["has_audio"] as? Boolean ?: false
            audioIndicator?.visibility = if (hasAudio) View.VISIBLE else View.GONE
        }
    }

    // Assistant message ViewHolder
    inner class AssistantMessageViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val messageText: TextView = itemView.findViewById(R.id.messageText)
        private val timestampText: TextView = itemView.findViewById(R.id.timestampText)

        fun bind(message: Map<String, Any>) {
            val content = message["content"] as? String ?: ""
            messageText.text = content

            // Format timestamp
            val timestamp = message["timestamp"] as? String
            if (timestamp != null) {
                try {
                    val isoFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
                    val date = isoFormat.parse(timestamp)
                    timestampText.text = if (date != null) dateFormat.format(date) else ""
                } catch (e: Exception) {
                    timestampText.text = ""
                }
            }
        }
    }

    // System message ViewHolder
    inner class SystemMessageViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val messageText: TextView = itemView.findViewById(R.id.messageText)

        fun bind(message: Map<String, Any>) {
            val content = message["content"] as? String ?: ""
            messageText.text = content
        }
    }
} 