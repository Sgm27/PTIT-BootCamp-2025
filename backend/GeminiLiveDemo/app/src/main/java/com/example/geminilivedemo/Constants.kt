package com.example.geminilivedemo

import android.media.AudioFormat
import android.media.AudioRecord

object Constants {
    const val URL = "ws://backend-bootcamp.sonktx.online/gemini-live"
    const val CAMERA_REQUEST_CODE = 100
    const val AUDIO_REQUEST_CODE = 200
    
    // Audio settings optimized for smooth performance and backend compatibility
    const val AUDIO_SAMPLE_RATE = 16000  // Recording sample rate - must be 16000 for backend
    const val AUDIO_PLAYBACK_SAMPLE_RATE = 24000  // Playback sample rate - backend sends 24000
    const val AUDIO_CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO
    const val AUDIO_ENCODING = AudioFormat.ENCODING_PCM_16BIT
    
    // Optimized buffer size for smooth audio streaming
    private val MIN_BUFFER_SIZE = AudioRecord.getMinBufferSize(AUDIO_SAMPLE_RATE, AUDIO_CHANNEL_CONFIG, AUDIO_ENCODING)
    val AUDIO_BUFFER_SIZE = kotlin.math.max(MIN_BUFFER_SIZE, 1024)  // At least 1024 bytes
    
    // Smaller chunk size for real-time processing and better turn-taking
    const val AUDIO_CHUNK_SIZE = 512  // Increase back for stability
    
    const val MAX_IMAGE_DIMENSION = 1024
    const val JPEG_QUALITY = 70
    const val IMAGE_SEND_INTERVAL: Long = 5000 // 5 seconds
    
    // Reduced audio check interval for more responsive audio switching
    const val AUDIO_PLAYING_CHECK_INTERVAL: Long = 50  // Reduced from 100ms to 50ms
    
    // Audio playback volume (0.0 to 1.0)
    const val AUDIO_PLAYBACK_VOLUME = 0.85f // Slightly increased for better hearing
    
    // Audio processing delays - optimized for turn-taking
    const val AUDIO_PROCESSING_DELAY: Long = 20  // Slightly longer for better stability
    const val AUDIO_QUEUE_MAX_SIZE = 30  // Smaller queue to reduce latency
}
