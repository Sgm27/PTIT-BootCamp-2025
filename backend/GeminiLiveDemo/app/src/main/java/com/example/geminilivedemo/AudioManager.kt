package com.example.geminilivedemo

import android.media.AudioFormat
import android.media.AudioRecord
import android.media.AudioTrack
import android.media.MediaRecorder
import android.util.Base64
import android.util.Log
import kotlinx.coroutines.*
import java.nio.ByteBuffer
import java.nio.ByteOrder

class AudioManager {
    
    interface AudioManagerCallback {
        fun onAudioChunkReady(base64Audio: String)
        fun onAudioRecordingStarted()
        fun onAudioRecordingStopped()
    }
    
    private var callback: AudioManagerCallback? = null
    private var isRecording = false
    private var audioRecord: AudioRecord? = null
    private var pcmData = mutableListOf<Short>()
    private var recordInterval: Job? = null
    
    private val audioQueue = mutableListOf<ByteArray>()
    private var isPlaying = false
    private var audioTrack: AudioTrack? = null
    
    fun setCallback(callback: AudioManagerCallback) {
        this.callback = callback
    }
    
    fun startAudioInput() {
        if (isRecording) return
        isRecording = true
        
        callback?.onAudioRecordingStarted()
        
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
                val buffer = ShortArray(Constants.AUDIO_BUFFER_SIZE)
                val readSize = audioRecord?.read(buffer, 0, buffer.size)
                if (readSize != null && readSize > 0) {
                    pcmData.addAll(buffer.take(readSize).toList())
                    if (pcmData.size >= readSize) {
                        recordChunk()
                    }
                }
            }
        }
    }
    
    private fun recordChunk() {
        if (pcmData.isEmpty()) return
        
        GlobalScope.launch(Dispatchers.IO) {
            val buffer = ByteBuffer.allocate(pcmData.size * 2).order(ByteOrder.LITTLE_ENDIAN)
            pcmData.forEach { value ->
                buffer.putShort(value)
            }
            val byteArray = buffer.array()
            val base64 = Base64.encodeToString(byteArray, Base64.DEFAULT or Base64.NO_WRAP)
            Log.d("AudioManager", "Send Audio Chunk")
            callback?.onAudioChunkReady(base64)
            pcmData.clear()
        }
    }
    
    fun stopAudioInput() {
        isRecording = false
        callback?.onAudioRecordingStopped()
        
        recordInterval?.cancel()
        audioRecord?.stop()
        audioRecord?.release()
        audioRecord = null
        Log.d("AudioManager", "Stop Recording")
    }
    
    fun ingestAudioChunkToPlay(base64AudioChunk: String?) {
        if (base64AudioChunk == null) return

        GlobalScope.launch(Dispatchers.IO) {
            try {
                val arrayBuffer = base64ToArrayBuffer(base64AudioChunk)
                synchronized(audioQueue) {
                    audioQueue.add(arrayBuffer)
                }
                if (!isPlaying) {
                    playNextAudioChunk()
                }
                Log.d("AudioManager", "Audio chunk added to the queue")
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

                isPlaying = true
                playAudio(chunk)
            }
            isPlaying = false

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
                Constants.AUDIO_SAMPLE_RATE,
                AudioFormat.CHANNEL_OUT_MONO,
                AudioFormat.ENCODING_PCM_16BIT,
                Constants.AUDIO_BUFFER_SIZE,
                AudioTrack.MODE_STREAM
            )
        }

        audioTrack?.write(byteArray, 0, byteArray.size)
        audioTrack?.play()
        GlobalScope.launch(Dispatchers.IO) {
            while (audioTrack?.playState == AudioTrack.PLAYSTATE_PLAYING) {
                delay(10)
            }
            audioTrack?.stop()
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
    
    fun cleanup() {
        stopAudioInput()
        audioTrack?.release()
        audioTrack = null
    }
}
