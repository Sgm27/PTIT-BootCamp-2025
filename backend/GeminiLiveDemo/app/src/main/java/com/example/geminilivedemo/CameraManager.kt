package com.example.geminilivedemo

import android.app.Activity
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import android.os.Environment
import android.provider.MediaStore
import android.util.Base64
import android.widget.ImageView
import android.widget.Toast
import androidx.core.content.FileProvider
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.*
import kotlin.math.roundToInt

class CameraManager(private val activity: Activity) {
    
    interface CameraCallback {
        fun onImageCaptured(base64Image: String)
        fun onCameraError(error: String)
    }
    
    private var callback: CameraCallback? = null
    private var currentPhotoPath: String? = null
    
    fun setCallback(callback: CameraCallback) {
        this.callback = callback
    }
    
    fun openCamera() {
        val takePictureIntent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
        val photoFile: File? = try {
            createImageFile()
        } catch (ex: IOException) {
            Toast.makeText(activity, "Error creating file", Toast.LENGTH_SHORT).show()
            callback?.onCameraError("Error creating file: ${ex.message}")
            null
        }

        photoFile?.also {
            val photoURI: Uri = FileProvider.getUriForFile(
                activity,
                "${activity.packageName}.fileprovider",
                it
            )
            takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT, photoURI)
            activity.startActivityForResult(takePictureIntent, Constants.CAMERA_REQUEST_CODE)
        }
    }
    
    private fun createImageFile(): File {
        val timeStamp: String = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date())
        val storageDir: File = activity.getExternalFilesDir(Environment.DIRECTORY_PICTURES)!!
        return File.createTempFile(
            "JPEG_${timeStamp}_",
            ".jpg",
            storageDir
        ).apply {
            currentPhotoPath = absolutePath
        }
    }
    
    fun handleCameraResult(requestCode: Int, resultCode: Int, data: Intent?, imageView: ImageView?): String? {
        if (requestCode == Constants.CAMERA_REQUEST_CODE && resultCode == Activity.RESULT_OK) {
            val file = File(currentPhotoPath ?: return null)

            // Step 1: Decode with reduced dimensions
            val options = BitmapFactory.Options().apply {
                inJustDecodeBounds = true
            }
            BitmapFactory.decodeFile(file.absolutePath, options)

            val (originalWidth, originalHeight) = options.outWidth to options.outHeight
            val scaleFactor = calculateScaleFactor(originalWidth, originalHeight, Constants.MAX_IMAGE_DIMENSION)

            options.inJustDecodeBounds = false
            options.inSampleSize = scaleFactor

            val scaledBitmap = BitmapFactory.decodeFile(file.absolutePath, options)

            // Step 2: Compress with reduced quality
            val byteArrayOutputStream = ByteArrayOutputStream()
            scaledBitmap.compress(Bitmap.CompressFormat.JPEG, Constants.JPEG_QUALITY, byteArrayOutputStream)

            // Step 3: Create Base64 string
            val currentFrameB64 = Base64.encodeToString(byteArrayOutputStream.toByteArray(), Base64.DEFAULT or Base64.NO_WRAP)

            // Show preview (using further scaled version if needed) - only if imageView is provided
            if (imageView != null) {
                val previewBitmap = scaleBitmapForPreview(scaledBitmap)
                imageView.setImageBitmap(previewBitmap)
            }

            // Clean up resources
            scaledBitmap.recycle()
            byteArrayOutputStream.close()

            callback?.onImageCaptured(currentFrameB64)
            return currentFrameB64
        }
        return null
    }
    
    private fun calculateScaleFactor(width: Int, height: Int, maxDimension: Int): Int {
        val scaleFactor = when {
            width > height -> width.toFloat() / maxDimension
            else -> height.toFloat() / maxDimension
        }
        return when {
            scaleFactor <= 1 -> 1
            scaleFactor <= 2 -> 2
            scaleFactor <= 4 -> 4
            else -> 8
        }.coerceAtLeast(1)
    }
    
    private fun scaleBitmapForPreview(bitmap: Bitmap): Bitmap {
        val maxWidth = activity.resources.displayMetrics.widthPixels
        val scaleFactor = maxWidth.toFloat() / bitmap.width
        return Bitmap.createScaledBitmap(
            bitmap,
            maxWidth,
            (bitmap.height * scaleFactor).roundToInt(),
            true
        )
    }
}
