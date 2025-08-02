package com.example.geminilivedemo

import android.content.Context
import android.content.pm.PackageManager
import android.Manifest
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.AudioTrack
import android.media.MediaRecorder
import android.util.Base64
import android.util.Log
import androidx.core.app.ActivityCompat
import kotlinx.coroutines.*
import java.nio.ByteBuffer
import java.nio.ByteOrder

class AudioManager(private val context: Context) {
    
    interface AudioManagerCallback {
        fun onAudioChunkReady(base64Audio: String)
        fun onAudioRecordingStarted()
        fun onAudioRecordingStopped()
        fun onAudioPlaybackStarted()
        fun onAudioPlaybackStopped()
    }
    
    private var callback: AudioManagerCallback? = null
    private var isRecording = false
    private var isPlayingAudio = false  // Renamed for clarity
    private var audioRecord: AudioRecord? = null
    private var pcmData = mutableListOf<Short>()
    private var recordInterval: Job? = null
    
    private val audioQueue = mutableListOf<ByteArray>()
    private var audioTrack: AudioTrack? = null
    
    // Voice Activity Detection parameters - More permissive settings
    private var silenceThreshold = 200  // Lower threshold for easier voice detection
    private var silenceCount = 0
    private var maxSilenceFrames = 20   // Longer before stopping (about 1 second)
    
    // Timing controls - Shorter cooldown
    private var lastPlaybackEndTime = 0L
    private val playbackCooldownMs = 500L  // Reduced to 0.5 second cooldown
    
    fun setCallback(callback: AudioManagerCallback) {
        this.callback = callback
    }
    
    fun startAudioInput() {
        if (isRecording) return
        
        Log.d("AudioManager", "Starting audio input")
        
        isRecording = true
        silenceCount = 0
        
        callback?.onAudioRecordingStarted()

        if (ActivityCompat.checkSelfPermission(
                context,
                Manifest.permission.RECORD_AUDIO
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            // TODO: Consider calling
            //    ActivityCompat#requestPermissions
            // here to request the missing permissions, and then overriding
            //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
            //                                          int[] grantResults)
            // to handle the case where the user grants the permission. See the documentation
            // for ActivityCompat#requestPermissions for more details.
            return
        }
        audioRecord = AudioRecord(
            MediaRecorder.AudioSource.VOICE_COMMUNICATION,
            Constants.AUDIO_SAMPLE_RATE,
            Constants.AUDIO_CHANNEL_CONFIG,
            Constants.AUDIO_ENCODING,
            Constants.AUDIO_BUFFER_SIZE
        )

        if (audioRecord?.state != AudioRecord.STATE_INITIALIZED) {
            Log.e("AudioManager", "AudioRecord initialization failed")
            return
        }

        audioRecord?.startRecording()
        Log.d("AudioManager", "Start Recording")
        
        recordInterval = GlobalScope.launch(Dispatchers.IO) {
            while (isRecording) {
                // Simple pause if AI is playing
                if (isPlayingAudio) {
                    delay(100)
                    continue
                }
                
                val buffer = ShortArray(Constants.AUDIO_CHUNK_SIZE)
                val readSize = audioRecord?.read(buffer, 0, buffer.size)
                
                if (readSize != null && readSize > 0) {
                    // Always add audio data - remove complex VAD for now
                    pcmData.addAll(buffer.take(readSize).toList())
                    
                    // Send chunk when we have enough data
                    if (pcmData.size >= Constants.AUDIO_CHUNK_SIZE) {
                        recordChunk()
                        Log.d("AudioManager", "Sending audio chunk, size: ${pcmData.size}")
                    }
                }
                
                delay(Constants.AUDIO_PROCESSING_DELAY)
            }
        }
    }
    
    private fun recordChunk() {
        if (pcmData.isEmpty()) {
            Log.w("AudioManager", "recordChunk called but pcmData is empty")
            return
        }
        
        Log.d("AudioManager", "Recording chunk with ${pcmData.size} samples")
        
        GlobalScope.launch(Dispatchers.IO) {
            val buffer = ByteBuffer.allocate(pcmData.size * 2).order(ByteOrder.LITTLE_ENDIAN)
            pcmData.forEach { value ->
                buffer.putShort(value)
            }
            val byteArray = buffer.array()
            val base64 = Base64.encodeToString(byteArray, Base64.DEFAULT or Base64.NO_WRAP)
            Log.d("AudioManager", "Sending audio chunk, base64 length: ${base64.length}")
            callback?.onAudioChunkReady(base64)
            pcmData.clear()
        }
    }
    
    private fun calculateAudioLevel(buffer: ShortArray, size: Int): Int {
        var sum = 0L
        for (i in 0 until size) {
            sum += (buffer[i] * buffer[i]).toLong()
        }
        return if (size > 0) (sum / size).toInt() else 0
    }
    
    fun stopAudioInput() {
        if (!isRecording) return
        
        isRecording = false
        
        // Send any remaining audio data
        if (pcmData.isNotEmpty()) {
            recordChunk()
        }
        
        callback?.onAudioRecordingStopped()
        
        recordInterval?.cancel()
        audioRecord?.stop()
        audioRecord?.release()
        audioRecord = null
        Log.d("AudioManager", "Stop Recording")
    }
    
    fun ingestAudioChunkToPlay(base64AudioChunk: String?) {
        if (base64AudioChunk == null) {
            Log.w("AudioManager", "Received null audio chunk")
            return
        }

        Log.d("AudioManager", "Received audio chunk to play, base64 length: ${base64AudioChunk.length}")

        GlobalScope.launch(Dispatchers.IO) {
            try {
                val arrayBuffer = base64ToArrayBuffer(base64AudioChunk)
                Log.d("AudioManager", "Decoded audio buffer, size: ${arrayBuffer.size} bytes")
                
                synchronized(audioQueue) {
                    audioQueue.add(arrayBuffer)
                    Log.d("AudioManager", "Added to queue, queue size: ${audioQueue.size}")
                }
                if (!isPlayingAudio) {
                    playNextAudioChunk()
                }
            } catch (e: Exception) {
                Log.e("AudioManager", "Error processing chunk", e)
            }
        }
    }
    
    private fun playNextAudioChunk() {
        GlobalScope.launch(Dispatchers.IO) {
            while (true) {
                val chunk = synchronized(audioQueue) {
                    if (audioQueue.isNotEmpty()) audioQueue.removeAt(0) else null
                } ?: break

                if (!isPlayingAudio) {
                    isPlayingAudio = true
                    callback?.onAudioPlaybackStarted()
                }
                playAudio(chunk)
            }
            
            // Audio playback finished
            isPlayingAudio = false
            lastPlaybackEndTime = System.currentTimeMillis()
            callback?.onAudioPlaybackStopped()
            
            Log.d("AudioManager", "AI finished speaking, cooldown started")
            
            // Automatically try to restart recording after cooldown if needed
            GlobalScope.launch(Dispatchers.Main) {
                delay(playbackCooldownMs)
                Log.d("AudioManager", "Cooldown finished, ready for next input")
            }

            synchronized(audioQueue) {
                if (audioQueue.isNotEmpty()) {
                    playNextAudioChunk()
                }
            }
        }
    }
    
    private fun playAudio(byteArray: ByteArray) {
        if (audioTrack == null) {
            audioTrack = AudioTrack(
                android.media.AudioManager.STREAM_MUSIC,
                Constants.AUDIO_PLAYBACK_SAMPLE_RATE,
                AudioFormat.CHANNEL_OUT_MONO,
                AudioFormat.ENCODING_PCM_16BIT,
                Constants.AUDIO_BUFFER_SIZE,
                AudioTrack.MODE_STREAM
            )
            Log.d("AudioManager", "AudioTrack created with sample rate: ${Constants.AUDIO_PLAYBACK_SAMPLE_RATE} Hz")
            // Thiết lập âm lượng cao hơn cho chatbot
            audioTrack?.setStereoVolume(Constants.AUDIO_PLAYBACK_VOLUME, Constants.AUDIO_PLAYBACK_VOLUME)
        }

        Log.d("AudioManager", "Playing audio chunk, size: ${byteArray.size} bytes")
        audioTrack?.write(byteArray, 0, byteArray.size)
        audioTrack?.play()
        Log.d("AudioManager", "AudioTrack state: ${audioTrack?.state}, playState: ${audioTrack?.playState}")
        
        GlobalScope.launch(Dispatchers.IO) {
            while (audioTrack?.playState == AudioTrack.PLAYSTATE_PLAYING) {
                delay(10)
            }
            audioTrack?.stop()
            Log.d("AudioManager", "Audio playback finished")
        }
    }
    
    private fun base64ToArrayBuffer(base64: String): ByteArray {
        return Base64.decode(base64, Base64.DEFAULT)
    }
    
    private fun convertPCM16LEToFloat32(pcmData: ByteArray): FloatArray {
        val shortArray = pcmData.asShortArray()
        val floatArray = FloatArray(shortArray.size)

        for (i in shortArray.indices) {
            floatArray[i] = shortArray[i] / 32768f
        }
        return floatArray
    }

    private fun ByteArray.asShortArray(): ShortArray {
        val shortArray = ShortArray(this.size / 2)
        val byteBuffer = ByteBuffer.wrap(this).order(ByteOrder.LITTLE_ENDIAN)
        for (i in shortArray.indices) {
            shortArray[i] = byteBuffer.short
        }
        return shortArray
    }
    
    fun isCurrentlyRecording(): Boolean = isRecording
    
    // Phương thức để kiểm tra AI có đang phát âm thanh không
    fun isCurrentlyPlaying(): Boolean = isPlayingAudio
    
    // Phương thức để điều chỉnh âm lượng phát
    fun setPlaybackVolume(volume: Float) {
        val clampedVolume = volume.coerceIn(0.0f, 1.0f)
        audioTrack?.setStereoVolume(clampedVolume, clampedVolume)
        Log.d("AudioManager", "Playback volume set to: $clampedVolume")
    }
    
    fun cleanup() {
        stopAudioInput()
        audioTrack?.release()
        audioTrack = null
    }
}
