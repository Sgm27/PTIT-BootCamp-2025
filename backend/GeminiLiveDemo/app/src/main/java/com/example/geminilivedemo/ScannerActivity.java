package com.example.geminilivedemo;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import com.example.geminilivedemo.MedicineInfoActivity;
import com.example.geminilivedemo.GlobalConnectionManager;
import com.example.geminilivedemo.GeminiLiveApplication;
import com.example.geminilivedemo.AudioManager;
import com.example.geminilivedemo.WebSocketManager;
import com.example.geminilivedemo.Response;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Matrix;
import android.media.ExifInterface;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.util.Base64;
import android.util.Log;
import android.view.Surface;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
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
import java.io.IOException;
import java.util.concurrent.ExecutionException;

public class ScannerActivity extends AppCompatActivity {

    private static final int CAMERA_PERMISSION_REQUEST_CODE = 100;
    private static final int GALLERY_PERMISSION_REQUEST_CODE = 101;
    private static final int PICK_IMAGE_REQUEST_CODE = 102;
    private static final String TAG = "ScannerActivity";

    private ImageView backButton;
    private View captureButton;
    private View galleryButton;
    private PreviewView cameraPreviewView;

    private ProcessCameraProvider cameraProvider;
    private ImageCapture imageCapture;
    private Camera camera;
    private int lensFacing = CameraSelector.LENS_FACING_BACK; // Luôn sử dụng camera sau

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_scanner);

        Log.d(TAG, "ScannerActivity onCreate");
        Log.d(TAG, "Note: Audio from AI should continue playing in this activity");

        // Register with GlobalConnectionManager to maintain WebSocket connection
        try {
            GlobalConnectionManager globalConnectionManager = ((GeminiLiveApplication) getApplication())
                    .getGlobalConnectionManager();
            globalConnectionManager.registerActivity(this);
            Log.d(TAG, "Registered with GlobalConnectionManager for audio continuity");

            // Setup AudioManager callback to handle AI audio responses
            setupAudioManagerCallback(globalConnectionManager);

            // Setup WebSocket callback to handle AI responses
            setupWebSocketCallback(globalConnectionManager);

            // Test audio functionality
            Log.d(TAG, "ScannerActivity setup completed - ready to receive AI audio responses");
        } catch (Exception e) {
            Log.e(TAG, "Error registering with GlobalConnectionManager", e);
        }

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
        galleryButton = findViewById(R.id.galleryButton);
        cameraPreviewView = findViewById(R.id.cameraPreviewView);

        Log.d(TAG, "Views initialized - PreviewView: " + (cameraPreviewView != null) +
                ", BackButton: " + (backButton != null) +
                ", CaptureButton: " + (captureButton != null) +
                ", GalleryButton: " + (galleryButton != null));

        if (cameraPreviewView == null) {
            throw new RuntimeException("CameraPreviewView not found in layout");
        }
        if (captureButton == null) {
            throw new RuntimeException("CaptureButton not found in layout");
        }
        if (galleryButton == null) {
            throw new RuntimeException("GalleryButton not found in layout");
        }

        // Set up toolbar
        androidx.appcompat.widget.Toolbar toolbar = findViewById(R.id.toolbar);
        if (toolbar != null) {
            setSupportActionBar(toolbar);
            if (getSupportActionBar() != null) {
                getSupportActionBar().setDisplayShowTitleEnabled(false);
                getSupportActionBar().setDisplayHomeAsUpEnabled(false);
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

        // Gallery button functionality
        galleryButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.d(TAG, "Gallery button clicked");
                openGallery();
            }
        });
    }

    private void openGallery() {
        if (checkGalleryPermission()) {
            Intent intent = new Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
            startActivityForResult(intent, PICK_IMAGE_REQUEST_CODE);
        } else {
            requestGalleryPermission();
        }
    }

    private boolean checkGalleryPermission() {
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
            // Android 13+ (API 33+)
            return ContextCompat.checkSelfPermission(this,
                    Manifest.permission.READ_MEDIA_IMAGES) == PackageManager.PERMISSION_GRANTED;
        } else {
            // Android 12 and below
            return ContextCompat.checkSelfPermission(this,
                    Manifest.permission.READ_EXTERNAL_STORAGE) == PackageManager.PERMISSION_GRANTED;
        }
    }

    private void requestGalleryPermission() {
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
            // Android 13+ (API 33+)
            ActivityCompat.requestPermissions(this,
                    new String[] { Manifest.permission.READ_MEDIA_IMAGES },
                    GALLERY_PERMISSION_REQUEST_CODE);
        } else {
            // Android 12 and below
            ActivityCompat.requestPermissions(this,
                    new String[] { Manifest.permission.READ_EXTERNAL_STORAGE },
                    GALLERY_PERMISSION_REQUEST_CODE);
        }
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
        } else if (requestCode == GALLERY_PERMISSION_REQUEST_CODE) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                openGallery();
            } else {
                Toast.makeText(this, "Gallery permission required", Toast.LENGTH_SHORT).show();
            }
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode == PICK_IMAGE_REQUEST_CODE && resultCode == RESULT_OK && data != null) {
            Uri selectedImageUri = data.getData();
            if (selectedImageUri != null) {
                Log.d(TAG, "Image selected from gallery: " + selectedImageUri);
                processImageFromGallery(selectedImageUri);
            }
        }
    }

    private void processImageFromGallery(Uri imageUri) {
        try {
            // Load image from gallery
            Bitmap bitmap = MediaStore.Images.Media.getBitmap(getContentResolver(), imageUri);
            if (bitmap == null) {
                Log.e(TAG, "Failed to load image from gallery");
                Toast.makeText(this, "Failed to load image", Toast.LENGTH_SHORT).show();
                return;
            }

            Log.d(TAG, "Image loaded from gallery: " + bitmap.getWidth() + "x" + bitmap.getHeight());

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

            // Convert to base64
            ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
            bitmap.compress(Bitmap.CompressFormat.JPEG, 70, byteArrayOutputStream);
            byte[] byteArray = byteArrayOutputStream.toByteArray();
            String base64Image = Base64.encodeToString(byteArray, Base64.NO_WRAP);

            Log.d(TAG, "Gallery image processed successfully, base64 length: " + base64Image.length());

            // Clean up
            bitmap.recycle();
            byteArrayOutputStream.close();

            // Navigate to MedicineInfoActivity
            Intent medicineInfoIntent = new Intent(this, MedicineInfoActivity.class);
            medicineInfoIntent.putExtra(MedicineInfoActivity.EXTRA_IMAGE_BASE64, base64Image);
            medicineInfoIntent.putExtra(MedicineInfoActivity.EXTRA_MEDICINE_NAME,
                    "Thuốc từ thư viện - " + bitmap.getWidth() + "x" + bitmap.getHeight());

            Log.d(TAG, "Navigating to MedicineInfoActivity with gallery image data length: " + base64Image.length());
            startActivity(medicineInfoIntent);
            finish();

        } catch (IOException e) {
            Log.e(TAG, "Error processing gallery image", e);
            Toast.makeText(this, "Error processing image: " + e.getMessage(), Toast.LENGTH_LONG).show();
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

        // Preview use case - Fit within container với aspect ratio phù hợp
        Preview preview = new Preview.Builder()
                .setTargetAspectRatio(AspectRatio.RATIO_16_9)
                .build();

        // Image capture use case với rotation handling
        imageCapture = new ImageCapture.Builder()
                .setTargetAspectRatio(AspectRatio.RATIO_16_9)
                .setTargetRotation(getWindowManager().getDefaultDisplay().getRotation())
                .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
                .build();

        // Camera selector - Luôn sử dụng camera sau
        CameraSelector cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA;

        try {
            // Unbind all use cases before rebinding
            cameraProvider.unbindAll();

            // Bind use cases to camera
            camera = cameraProvider.bindToLifecycle(this, cameraSelector, preview, imageCapture);

            // Connect the preview to the PreviewView
            preview.setSurfaceProvider(cameraPreviewView.getSurfaceProvider());

            Log.d(TAG, "Camera started successfully - using back camera only");

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
                    "Thuốc đã chụp - " + bitmap.getWidth() + "x" + bitmap.getHeight());

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

    private void setupAudioManagerCallback(GlobalConnectionManager globalConnectionManager) {
        try {
            // Get AudioManager from GlobalConnectionManager
            AudioManager audioManager = globalConnectionManager.getAudioManager();
            if (audioManager != null) {
                // Set callback to handle AI audio responses
                audioManager.setCallback(new AudioManager.AudioManagerCallback() {
                    @Override
                    public void onAudioChunkReady(String base64Audio) {
                        // This won't be called in ScannerActivity since we're not recording
                        Log.d(TAG, "Audio chunk ready (not recording in ScannerActivity)");
                    }

                    @Override
                    public void onAudioRecordingStarted() {
                        Log.d(TAG, "Audio recording started (not expected in ScannerActivity)");
                    }

                    @Override
                    public void onAudioRecordingStopped() {
                        Log.d(TAG, "Audio recording stopped (not expected in ScannerActivity)");
                    }

                    @Override
                    public void onAudioPlaybackStarted() {
                        Log.d(TAG, "AI audio playback started in ScannerActivity");
                        // Show visual feedback that AI is speaking
                        runOnUiThread(() -> {
                            // You can add a visual indicator here if needed
                            Log.d(TAG, "AI is now speaking in ScannerActivity");
                        });
                    }

                    @Override
                    public void onAudioPlaybackStopped() {
                        Log.d(TAG, "AI audio playback stopped in ScannerActivity");
                        // Hide visual feedback
                        runOnUiThread(() -> {
                            Log.d(TAG, "AI finished speaking in ScannerActivity");
                        });
                    }
                });

                Log.d(TAG, "AudioManager callback setup completed for ScannerActivity");
            } else {
                Log.w(TAG, "AudioManager is null, cannot setup callback");
            }
        } catch (Exception e) {
            Log.e(TAG, "Error setting up AudioManager callback", e);
        }
    }

    private void setupWebSocketCallback(GlobalConnectionManager globalConnectionManager) {
        try {
            // Get WebSocketManager from GlobalConnectionManager
            WebSocketManager webSocketManager = globalConnectionManager.getWebSocketManager();
            if (webSocketManager != null) {
                // Set callback to handle AI responses
                webSocketManager.setCallback(new WebSocketManager.WebSocketCallback() {
                    @Override
                    public void onConnected() {
                        Log.d(TAG, "WebSocket connected in ScannerActivity");
                    }

                    @Override
                    public void onDisconnected() {
                        Log.d(TAG, "WebSocket disconnected in ScannerActivity");
                    }

                    @Override
                    public void onError(Exception exception) {
                        Log.e(TAG, "WebSocket error in ScannerActivity: " + exception.getMessage());
                    }

                    @Override
                    public void onMessageReceived(Response response) {
                        Log.d(TAG, "AI response received in ScannerActivity");

                        // Handle text response
                        if (response.getText() != null) {
                            Log.d(TAG, "AI text: " + response.getText());
                        }

                        // Handle audio response - this is the key part!
                        if (response.getAudioData() != null) {
                            Log.d(TAG, "AI audio received in ScannerActivity, playing audio");

                            // Get AudioManager and play the audio
                            AudioManager audioManager = globalConnectionManager.getAudioManager();
                            if (audioManager != null) {
                                audioManager.ingestAudioChunkToPlay(response.getAudioData());
                                Log.d(TAG, "Audio sent to AudioManager for playback");
                            } else {
                                Log.e(TAG, "AudioManager is null, cannot play audio");
                            }
                        }

                        // Handle other response types if needed
                        if (response.getVoiceNotificationData() != null) {
                            Log.d(TAG, "Voice notification received in ScannerActivity");
                        }

                        if (response.getToolCallData() != null) {
                            Log.d(TAG, "Tool call received in ScannerActivity");
                        }

                        if (response.getScreenNavigationData() != null) {
                            Log.d(TAG, "Screen navigation received in ScannerActivity");
                        }
                    }
                });

                Log.d(TAG, "WebSocket callback setup completed for ScannerActivity");
            } else {
                Log.w(TAG, "WebSocketManager is null, cannot setup callback");
            }
        } catch (Exception e) {
            Log.e(TAG, "Error setting up WebSocket callback", e);
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (cameraProvider != null) {
            cameraProvider.unbindAll();
        }

        // Unregister from GlobalConnectionManager
        try {
            GlobalConnectionManager globalConnectionManager = ((GeminiLiveApplication) getApplication())
                    .getGlobalConnectionManager();
            globalConnectionManager.unregisterActivity(this);
            Log.d(TAG, "Unregistered from GlobalConnectionManager");
        } catch (Exception e) {
            Log.e(TAG, "Error unregistering from GlobalConnectionManager", e);
        }
    }
}
