package com.example.geminilivedemo

import android.Manifest
import android.app.Activity
import android.content.pm.PackageManager
import android.widget.Toast
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

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
        if (ContextCompat.checkSelfPermission(
                activity,
                Manifest.permission.RECORD_AUDIO
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            ActivityCompat.requestPermissions(
                activity,
                arrayOf(Manifest.permission.RECORD_AUDIO),
                Constants.AUDIO_REQUEST_CODE
            )
        } else {
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
                if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    callback?.onAudioPermissionGranted()
                } else {
                    callback?.onPermissionDenied("Audio")
                    Toast.makeText(activity, "Audio permission denied", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
}
