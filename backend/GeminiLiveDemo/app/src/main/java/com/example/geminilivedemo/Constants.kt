package com.example.geminilivedemo

import android.media.AudioFormat
import android.media.AudioRecord

object Constants {
    const val URL = "ws://bootcamp.sonktx.online"
    const val CAMERA_REQUEST_CODE = 100
    const val AUDIO_REQUEST_CODE = 200
    const val AUDIO_SAMPLE_RATE = 24000
    const val AUDIO_CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO
    const val AUDIO_ENCODING = AudioFormat.ENCODING_PCM_16BIT
    val AUDIO_BUFFER_SIZE = AudioRecord.getMinBufferSize(AUDIO_SAMPLE_RATE, AUDIO_CHANNEL_CONFIG, AUDIO_ENCODING)
    
    const val MAX_IMAGE_DIMENSION = 1024
    const val JPEG_QUALITY = 70
    const val IMAGE_SEND_INTERVAL: Long = 5000 // 5 seconds
    
    // Audio playback volume (0.0 to 1.0)
    const val AUDIO_PLAYBACK_VOLUME = 0.8f // Tăng âm lượng lên 80%
}
