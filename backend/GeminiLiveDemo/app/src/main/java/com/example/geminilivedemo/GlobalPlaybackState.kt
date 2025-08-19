package com.example.geminilivedemo

/**
 * Global flag to coordinate exclusive audio playback across the app (activities/services).
 * When true, another component should wait before starting new playback to prevent overlap.
 */
object GlobalPlaybackState {
    @Volatile
    var isPlaying: Boolean = false
}

