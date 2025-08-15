package com.example.geminilivedemo;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import com.example.geminilivedemo.MedicineInfoActivity;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Matrix;
import android.media.ExifInterface;
import android.os.Bundle;
import android.util.Base64;
import android.util.Log;
import android.view.Surface;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.camera.core.Camera;
import androidx.camera.core.CameraSelector;
import androidx.camera.core.ImageCapture;
import androidx.camera.core.ImageCaptureException;
import androidx.camera.core.Preview;
import androidx.camera.core.AspectRatio;
import androidx.camera.lifecycle.ProcessCameraProvider;
import androidx.camera.view.PreviewView;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.google.common.util.concurrent.ListenableFuture;

import java.io.ByteArrayOutputStream;
import java.util.concurrent.ExecutionException;

public class ScannerActivity extends AppCompatActivity {

    private static final int CAMERA_PERMISSION_REQUEST_CODE = 100;
    private static final String TAG = "ScannerActivity";

    private ImageView backButton;
    private Button captureButton;
    private PreviewView cameraPreviewView;

    private ProcessCameraProvider cameraProvider;
    private ImageCapture imageCapture;
    private Camera camera;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_scanner); // Back to original layout

        Log.d(TAG, "ScannerActivity onCreate");

        try {
            initializeViews();
            setupClickListeners();

            if (checkCameraPermission()) {
                Log.d(TAG, "Camera permission granted, starting camera");
                startCamera();
            } else {
                Log.d(TAG, "Camera permission not granted, requesting");
                requestCameraPermission();
            }
        } catch (Exception e) {
            Log.e(TAG, "Error in onCreate", e);
            Toast.makeText(this, "Error initializing camera: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void initializeViews() {
        backButton = findViewById(R.id.backButton);
        captureButton = findViewById(R.id.captureButton);
        cameraPreviewView = findViewById(R.id.cameraPreviewView);

        Log.d(TAG, "Views initialized - PreviewView: " + (cameraPreviewView != null) +
                ", BackButton: " + (backButton != null) +
                ", CaptureButton: " + (captureButton != null));

        if (cameraPreviewView == null) {
            throw new RuntimeException("CameraPreviewView not found in layout");
        }
        if (captureButton == null) {
            throw new RuntimeException("CaptureButton not found in layout");
        }
        if (backButton == null) {
            throw new RuntimeException("BackButton not found in layout");
        }

        // Set up toolbar
        androidx.appcompat.widget.Toolbar toolbar = findViewById(R.id.toolbar);
        if (toolbar != null) {
            setSupportActionBar(toolbar);
            if (getSupportActionBar() != null) {
                getSupportActionBar().setDisplayShowTitleEnabled(false);
            }
        }
    }

    private void setupClickListeners() {
        // Back button functionality
        backButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.d(TAG, "Back button clicked");
                finish(); // Close this activity and return to previous
            }
        });

        // Capture button functionality
        captureButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.d(TAG, "Capture button clicked");
                try {
                    captureImage();
                } catch (Exception e) {
                    Log.e(TAG, "Error in capture button click", e);
                    Toast.makeText(ScannerActivity.this, "Error: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                }
            }
        });
    }

    private boolean checkCameraPermission() {
        return ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED;
    }

    private void requestCameraPermission() {
        ActivityCompat.requestPermissions(this,
                new String[] { Manifest.permission.CAMERA },
                CAMERA_PERMISSION_REQUEST_CODE);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions,
            @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);

        if (requestCode == CAMERA_PERMISSION_REQUEST_CODE) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                startCamera();
            } else {
                Toast.makeText(this, "Camera permission required", Toast.LENGTH_SHORT).show();
                finish();
            }
        }
    }

    private void startCamera() {
        ListenableFuture<ProcessCameraProvider> cameraProviderFuture = ProcessCameraProvider.getInstance(this);

        cameraProviderFuture.addListener(() -> {
            try {
                cameraProvider = cameraProviderFuture.get();
                bindCameraUseCases();
            } catch (ExecutionException | InterruptedException e) {
                Log.e(TAG, "Error starting camera", e);
                Toast.makeText(this, "Error starting camera: " + e.getMessage(), Toast.LENGTH_LONG).show();
            }
        }, ContextCompat.getMainExecutor(this));
    }

    private void bindCameraUseCases() {
        if (cameraProvider == null) {
            Log.e(TAG, "Camera provider is null");
            return;
        }

        // Preview use case - Full screen
        Preview preview = new Preview.Builder()
                .setTargetAspectRatio(AspectRatio.RATIO_16_9)
                .build();

        // Image capture use case with rotation handling - Full screen
        imageCapture = new ImageCapture.Builder()
                .setTargetAspectRatio(AspectRatio.RATIO_16_9)
                .setTargetRotation(getWindowManager().getDefaultDisplay().getRotation())
                .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
                .build();

        // Camera selector (back camera)
        CameraSelector cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA;

        try {
            // Unbind all use cases before rebinding
            cameraProvider.unbindAll();

            // Bind use cases to camera
            camera = cameraProvider.bindToLifecycle(this, cameraSelector, preview, imageCapture);

            // Connect the preview to the PreviewView
            preview.setSurfaceProvider(cameraPreviewView.getSurfaceProvider());

            Log.d(TAG, "Camera started successfully");

        } catch (Exception e) {
            Log.e(TAG, "Use case binding failed", e);
            Toast.makeText(this, "Camera binding failed: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void captureImage() {
        Log.d(TAG, "captureImage() called");

        if (imageCapture == null) {
            Log.e(TAG, "ImageCapture is null");
            Toast.makeText(this, "Camera not ready", Toast.LENGTH_SHORT).show();
            return;
        }

        try {
            // Create a temporary file in internal storage
            java.io.File photoFile = new java.io.File(getCacheDir(),
                    "temp_image_" + System.currentTimeMillis() + ".jpg");
            Log.d(TAG, "Creating photo file: " + photoFile.getAbsolutePath());

            // Create output file options
            ImageCapture.OutputFileOptions outputFileOptions = new ImageCapture.OutputFileOptions.Builder(photoFile)
                    .build();

            Log.d(TAG, "Starting image capture...");
            // Capture image
            imageCapture.takePicture(outputFileOptions, ContextCompat.getMainExecutor(this),
                    new ImageCapture.OnImageSavedCallback() {
                        @Override
                        public void onImageSaved(@NonNull ImageCapture.OutputFileResults output) {
                            // Image saved successfully
                            Log.d(TAG, "Image saved successfully: " + photoFile.getAbsolutePath());
                            runOnUiThread(() -> {
                                Toast.makeText(ScannerActivity.this, "Image captured!", Toast.LENGTH_SHORT).show();
                                processImage(photoFile.getAbsolutePath());
                            });
                        }

                        @Override
                        public void onError(@NonNull ImageCaptureException exception) {
                            Log.e(TAG, "Image capture failed", exception);
                            runOnUiThread(() -> {
                                Toast.makeText(ScannerActivity.this, "Image capture failed: " + exception.getMessage(),
                                        Toast.LENGTH_LONG).show();
                            });
                        }
                    });
        } catch (Exception e) {
            Log.e(TAG, "Error in captureImage", e);
            Toast.makeText(this, "Error: " + e.getMessage(), Toast.LENGTH_SHORT).show();
        }
    }

    private void processImage(String imagePath) {
        Log.d(TAG, "processImage() called with path: " + imagePath);

        try {
            // Check if file exists
            java.io.File imageFile = new java.io.File(imagePath);
            if (!imageFile.exists()) {
                Log.e(TAG, "Image file does not exist: " + imagePath);
                Toast.makeText(this, "Image file not found", Toast.LENGTH_SHORT).show();
                return;
            }

            Log.d(TAG, "Image file exists, size: " + imageFile.length() + " bytes");

            // Load image and convert to base64
            Bitmap bitmap = BitmapFactory.decodeFile(imagePath);
            if (bitmap == null) {
                Log.e(TAG, "Failed to decode image: " + imagePath);
                Toast.makeText(this, "Failed to process image", Toast.LENGTH_SHORT).show();
                return;
            }

            Log.d(TAG, "Bitmap decoded successfully: " + bitmap.getWidth() + "x" + bitmap.getHeight());

            // Fix image orientation using EXIF data
            bitmap = fixImageOrientation(bitmap, imagePath);
            Log.d(TAG, "Image orientation fixed: " + bitmap.getWidth() + "x" + bitmap.getHeight());

            // Resize bitmap if too large to prevent memory issues
            int maxWidth = 800;
            int maxHeight = 800;
            if (bitmap.getWidth() > maxWidth || bitmap.getHeight() > maxHeight) {
                float scale = Math.min((float) maxWidth / bitmap.getWidth(), (float) maxHeight / bitmap.getHeight());
                int newWidth = Math.round(bitmap.getWidth() * scale);
                int newHeight = Math.round(bitmap.getHeight() * scale);
                bitmap = Bitmap.createScaledBitmap(bitmap, newWidth, newHeight, true);
                Log.d(TAG, "Bitmap resized to: " + newWidth + "x" + newHeight);
            }

            ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
            bitmap.compress(Bitmap.CompressFormat.JPEG, 70, byteArrayOutputStream);
            byte[] byteArray = byteArrayOutputStream.toByteArray();
            String base64Image = Base64.encodeToString(byteArray, Base64.NO_WRAP);

            Log.d(TAG, "Image processed successfully, base64 length: " + base64Image.length());

            // Clean up
            bitmap.recycle();
            byteArrayOutputStream.close();

            // Delete temporary file
            if (imageFile.delete()) {
                Log.d(TAG, "Temporary file deleted");
            } else {
                Log.w(TAG, "Failed to delete temporary file");
            }

            // Navigate to MedicineInfoActivity
            Intent medicineInfoIntent = new Intent(this, MedicineInfoActivity.class);
            medicineInfoIntent.putExtra(MedicineInfoActivity.EXTRA_IMAGE_BASE64, base64Image);
            medicineInfoIntent.putExtra(MedicineInfoActivity.EXTRA_MEDICINE_NAME,
                    "Medicine image captured - " + bitmap.getWidth() + "x" + bitmap.getHeight());

            Log.d(TAG, "Navigating to MedicineInfoActivity with image data length: " + base64Image.length());
            Log.d(TAG, "Image dimensions: " + bitmap.getWidth() + "x" + bitmap.getHeight());
            startActivity(medicineInfoIntent);
            finish();

        } catch (Exception e) {
            Log.e(TAG, "Error processing image", e);
            Toast.makeText(this, "Error processing image: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private Bitmap fixImageOrientation(Bitmap bitmap, String imagePath) {
        try {
            ExifInterface exif = new ExifInterface(imagePath);
            int orientation = exif.getAttributeInt(ExifInterface.TAG_ORIENTATION, ExifInterface.ORIENTATION_NORMAL);

            Matrix matrix = new Matrix();
            switch (orientation) {
                case ExifInterface.ORIENTATION_ROTATE_90:
                    matrix.postRotate(90);
                    break;
                case ExifInterface.ORIENTATION_ROTATE_180:
                    matrix.postRotate(180);
                    break;
                case ExifInterface.ORIENTATION_ROTATE_270:
                    matrix.postRotate(270);
                    break;
                case ExifInterface.ORIENTATION_FLIP_HORIZONTAL:
                    matrix.postScale(-1.0f, 1.0f);
                    break;
                case ExifInterface.ORIENTATION_FLIP_VERTICAL:
                    matrix.postScale(1.0f, -1.0f);
                    break;
                default:
                    return bitmap; // No rotation needed
            }

            Log.d(TAG, "Rotating image by orientation: " + orientation);
            Bitmap rotatedBitmap = Bitmap.createBitmap(bitmap, 0, 0, bitmap.getWidth(), bitmap.getHeight(), matrix,
                    true);

            // Recycle original bitmap if it's different from rotated one
            if (rotatedBitmap != bitmap) {
                bitmap.recycle();
            }

            return rotatedBitmap;

        } catch (Exception e) {
            Log.e(TAG, "Error fixing image orientation", e);
            return bitmap; // Return original bitmap if rotation fails
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (cameraProvider != null) {
            cameraProvider.unbindAll();
        }
    }
}
