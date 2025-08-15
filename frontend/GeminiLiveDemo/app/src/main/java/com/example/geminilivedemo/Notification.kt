package com.example.geminilivedemo

data class Notification(
    val id: String,
    val title: String,
    val message: String,
    val type: NotificationType,
    val timestamp: Long,
    val isRead: Boolean = false
)

enum class NotificationType {
    INFO,
    WARNING,
    ERROR,
    SUCCESS
}

fun NotificationType.getColor(): Int {
    return when (this) {
        NotificationType.INFO -> 0xFF4A90E2.toInt()      // Blue
        NotificationType.WARNING -> 0xFFFF8C00.toInt()   // Orange
        NotificationType.ERROR -> 0xFFFF4444.toInt()     // Red
        NotificationType.SUCCESS -> 0xFF32CD32.toInt()   // Green
    }
}
