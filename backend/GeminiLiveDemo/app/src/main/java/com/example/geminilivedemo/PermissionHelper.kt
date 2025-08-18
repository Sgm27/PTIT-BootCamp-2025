package com.example.geminilivedemo

import android.Manifest
import android.app.Activity
import android.content.pm.PackageManager
import android.widget.Toast
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import android.util.Log

class PermissionHelper(private val activity: Activity) {
    
    interface PermissionCallback {
        fun onCameraPermissionGranted()
        fun onAudioPermissionGranted()
        fun onPermissionDenied(permission: String)
    }
    
    private var callback: PermissionCallback? = null
    
    fun setCallback(callback: PermissionCallback) {
        this.callback = callback
    }
    
    fun checkCameraPermission() {
        if (ContextCompat.checkSelfPermission(
                activity,
                Manifest.permission.CAMERA
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            ActivityCompat.requestPermissions(
                activity,
                arrayOf(Manifest.permission.CAMERA),
                Constants.CAMERA_REQUEST_CODE
            )
        } else {
            callback?.onCameraPermissionGranted()
        }
    }
    
    fun checkRecordAudioPermission() {
        Log.d("PermissionHelper", "checkRecordAudioPermission called")
        val permissions = mutableListOf<String>()
        
        if (ContextCompat.checkSelfPermission(
                activity,
                Manifest.permission.RECORD_AUDIO
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            Log.d("PermissionHelper", "RECORD_AUDIO permission not granted, requesting...")
            permissions.add(Manifest.permission.RECORD_AUDIO)
        } else {
            Log.d("PermissionHelper", "RECORD_AUDIO permission already granted")
        }
        
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(
                    activity,
                    Manifest.permission.POST_NOTIFICATIONS
                ) != PackageManager.PERMISSION_GRANTED
            ) {
                Log.d("PermissionHelper", "POST_NOTIFICATIONS permission not granted, requesting...")
                permissions.add(Manifest.permission.POST_NOTIFICATIONS)
            } else {
                Log.d("PermissionHelper", "POST_NOTIFICATIONS permission already granted")
            }
        }
        
        if (permissions.isNotEmpty()) {
            Log.d("PermissionHelper", "Requesting permissions: $permissions")
            ActivityCompat.requestPermissions(
                activity,
                permissions.toTypedArray(),
                Constants.AUDIO_REQUEST_CODE
            )
        } else {
            Log.d("PermissionHelper", "All permissions granted, calling onAudioPermissionGranted callback")
            callback?.onAudioPermissionGranted()
        }
    }
    
    fun handlePermissionResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        when (requestCode) {
            Constants.CAMERA_REQUEST_CODE -> {
                if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    callback?.onCameraPermissionGranted()
                } else {
                    callback?.onPermissionDenied("Camera")
                    Toast.makeText(activity, "Camera permission denied", Toast.LENGTH_SHORT).show()
                }
            }
            Constants.AUDIO_REQUEST_CODE -> {
                var audioGranted = false
                var notificationGranted = true // Default to true for older Android versions
                
                for (i in permissions.indices) {
                    when (permissions[i]) {
                        Manifest.permission.RECORD_AUDIO -> {
                            audioGranted = grantResults[i] == PackageManager.PERMISSION_GRANTED
                        }
                        Manifest.permission.POST_NOTIFICATIONS -> {
                            notificationGranted = grantResults[i] == PackageManager.PERMISSION_GRANTED
                        }
                    }
                }
                
                if (audioGranted) {
                    callback?.onAudioPermissionGranted()
                    if (!notificationGranted) {
                        Toast.makeText(activity, "Notification permission denied - some features may not work", Toast.LENGTH_LONG).show()
                    }
                } else {
                    callback?.onPermissionDenied("Audio")
                    Toast.makeText(activity, "Audio permission denied", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
    
    fun checkAllBackgroundPermissions() {
        val permissions = mutableListOf<String>()
        
        if (ContextCompat.checkSelfPermission(activity, Manifest.permission.RECORD_AUDIO) 
            != PackageManager.PERMISSION_GRANTED) {
            permissions.add(Manifest.permission.RECORD_AUDIO)
        }
        
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(activity, Manifest.permission.POST_NOTIFICATIONS) 
                != PackageManager.PERMISSION_GRANTED) {
                permissions.add(Manifest.permission.POST_NOTIFICATIONS)
            }
        }
        
        if (permissions.isNotEmpty()) {
            ActivityCompat.requestPermissions(
                activity,
                permissions.toTypedArray(),
                Constants.AUDIO_REQUEST_CODE
            )
        } else {
            callback?.onAudioPermissionGranted()
        }
    }
}
