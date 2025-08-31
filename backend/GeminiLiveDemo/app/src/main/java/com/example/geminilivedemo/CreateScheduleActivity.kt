package com.example.geminilivedemo

import android.app.DatePickerDialog
import android.app.TimePickerDialog
import android.os.Bundle
import android.content.Intent
import android.provider.MediaStore
import androidx.activity.result.contract.ActivityResultContracts
import android.net.Uri
import java.io.InputStream
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import android.util.Log
import android.view.View
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText
import com.example.geminilivedemo.data.ApiClient
import com.example.geminilivedemo.data.ApiResult
import com.example.geminilivedemo.data.ScheduleManager
import com.example.geminilivedemo.data.Schedule
import com.example.geminilivedemo.data.CreateScheduleRequest
import com.example.geminilivedemo.data.UserPreferences
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.text.SimpleDateFormat
import java.util.*

class CreateScheduleActivity : AppCompatActivity() {
    
    private lateinit var userPreferences: UserPreferences
    private lateinit var titleText: TextView
    private lateinit var scheduleNameInput: TextInputEditText
    private lateinit var selectDateButton: MaterialButton
    private lateinit var selectTimeButton: MaterialButton
    private lateinit var notesInput: TextInputEditText
    private lateinit var saveScheduleButton: MaterialButton
    private lateinit var createFromPrescriptionButton: MaterialButton
    
    // Category buttons
    private lateinit var medicineButton: MaterialButton
    private lateinit var appointmentButton: MaterialButton
    private lateinit var exerciseButton: MaterialButton
    private lateinit var mealButton: MaterialButton
    private lateinit var otherButton: MaterialButton
    
    private var selectedDate: Calendar = Calendar.getInstance()
    private var selectedTime: Calendar = Calendar.getInstance()
    private var selectedCategory: String = "medicine"
    
    companion object {
        private const val TAG = "CreateScheduleActivity"
        const val EXTRA_ELDERLY_ID = "elderly_id"
        const val EXTRA_ELDERLY_NAME = "elderly_name"
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.dialog_create_schedule)
        
        userPreferences = UserPreferences(this)
        initializeViews()
        setupClickListeners()
        setupCategorySelection()
        updateDateTimeDisplay()
    }
    
    private fun initializeViews() {
        titleText = findViewById(R.id.createScheduleTitle)
        scheduleNameInput = findViewById(R.id.scheduleNameInput)
        selectDateButton = findViewById(R.id.selectDateButton)
        selectTimeButton = findViewById(R.id.selectTimeButton)
        notesInput = findViewById(R.id.notesInput)
        saveScheduleButton = findViewById(R.id.saveScheduleButton)
        createFromPrescriptionButton = findViewById(R.id.createFromPrescriptionButton)
        
        // Category buttons
        medicineButton = findViewById(R.id.medicineButton)
        appointmentButton = findViewById(R.id.appointmentButton)
        exerciseButton = findViewById(R.id.exerciseButton)
        mealButton = findViewById(R.id.mealButton)
        otherButton = findViewById(R.id.otherButton)
        
        // Set title
        titleText.text = "Tạo lịch trình mới"
    }
    
    private fun setupClickListeners() {
        selectDateButton.setOnClickListener {
            showDatePicker()
        }
        
        selectTimeButton.setOnClickListener {
            showTimePicker()
        }
        
        saveScheduleButton.setOnClickListener {
            saveSchedule()
        }

        createFromPrescriptionButton.setOnClickListener {
            openImagePicker()
        }
    }

    private val pickImageLauncher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
        if (result.resultCode == RESULT_OK) {
            try {
                val data: Intent? = result.data
                val imageUri: Uri? = data?.data
                if (imageUri != null) {
                    processPrescriptionImage(imageUri)
                } else {
                    Toast.makeText(this, "Không tìm thấy ảnh đã chọn", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error handling picked image: ${e.message}", e)
                Toast.makeText(this, "Lỗi xử lý ảnh: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun openImagePicker() {
        try {
            val intent = Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI)
            intent.type = "image/*"
            pickImageLauncher.launch(intent)
        } catch (e: Exception) {
            Log.e(TAG, "Error opening image picker: ${e.message}", e)
            Toast.makeText(this, "Không thể mở thư viện ảnh", Toast.LENGTH_SHORT).show()
        }
    }

    private fun processPrescriptionImage(imageUri: Uri) {
        CoroutineScope(Dispatchers.Main).launch {
            try {
                val base64Image = withContext(Dispatchers.IO) {
                    val inputStream: InputStream? = contentResolver.openInputStream(imageUri)
                    val bytes = inputStream?.readBytes()
                    inputStream?.close()
                    if (bytes != null) android.util.Base64.encodeToString(bytes, android.util.Base64.NO_WRAP) else null
                }

                if (base64Image.isNullOrEmpty()) {
                    Toast.makeText(this@CreateScheduleActivity, "Không thể đọc ảnh", Toast.LENGTH_SHORT).show()
                    return@launch
                }

                // Call backend to analyze prescription (using existing medicine analysis endpoint)
                val extraction = withContext(Dispatchers.IO) {
                    analyzePrescriptionViaBackend(base64Image)
                }

                if (extraction != null && extraction.optBoolean("success", false)) {
                    val result = extraction.optString("result", "")
                    // Expect result to be JSON as per your guidance
                    try {
                        val json = org.json.JSONObject(result)
                        applyExtractedSchedule(json)
                    } catch (_: Exception) {
                        // Try array of schedules
                        try {
                            val arr = org.json.JSONArray(result)
                            if (arr.length() > 0) {
                                val json = arr.getJSONObject(0)
                                applyExtractedSchedule(json)
                            } else {
                                Toast.makeText(this@CreateScheduleActivity, "Không có dữ liệu hợp lệ trong đơn thuốc", Toast.LENGTH_SHORT).show()
                            }
                        } catch (e: Exception) {
                            Log.e(TAG, "Extraction result is not valid JSON: ${e.message}")
                            Toast.makeText(this@CreateScheduleActivity, "Định dạng đơn thuốc không hợp lệ", Toast.LENGTH_SHORT).show()
                        }
                    }
                } else {
                    val err = extraction?.optString("error") ?: "Không thể trích xuất thông tin"
                    Toast.makeText(this@CreateScheduleActivity, err, Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error processing prescription image: ${e.message}", e)
                Toast.makeText(this@CreateScheduleActivity, "Lỗi: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun analyzePrescriptionViaBackend(base64Image: String): org.json.JSONObject? {
        // Reuse medicine analysis endpoint which uses OpenAI Vision on backend
        // Returns JSON: { success: bool, result: string/json, error?: string }
        return try {
            val client = okhttp3.OkHttpClient()
            val mediaType = "application/json; charset=utf-8".toMediaType()
            val body = org.json.JSONObject().apply { put("input", base64Image) }.toString().toRequestBody(mediaType)
            val request = okhttp3.Request.Builder()
                .url("${com.example.geminilivedemo.data.ApiConfig.BASE_URL}${com.example.geminilivedemo.data.ApiConfig.Endpoints.ANALYZE_MEDICINE}")
                .post(body)
                .addHeader("Content-Type", "application/json")
                .build()
            client.newCall(request).execute().use { resp ->
                val txt = resp.body?.string()
                if (resp.isSuccessful && txt != null) org.json.JSONObject(txt) else null
            }
        } catch (e: Exception) {
            Log.e(TAG, "analyzePrescriptionViaBackend failed: ${e.message}", e)
            null
        }
    }

    private fun applyExtractedSchedule(json: org.json.JSONObject) {
        // Expected fields from backend-required format
        // title, message, scheduled_at (unix), notification_type, category
        val title = json.optString("title").ifEmpty { json.optString("medicine_name", "Uống thuốc") }
        val message = json.optString("message").ifEmpty { json.optString("instruction", "Uống thuốc theo chỉ định") }
        val scheduledAtUnix = json.optLong("scheduled_at", 0L)
        val category = json.optString("category", "medicine")
        val notificationType = json.optString("notification_type", if (category == "medicine") "medicine_reminder" else getNotificationType(category))

        // Fill UI fields
        scheduleNameInput.setText(title)
        notesInput.setText(message)

        if (scheduledAtUnix > 0) {
            val cal = Calendar.getInstance().apply { timeInMillis = scheduledAtUnix * 1000 }
            selectedDate = (cal.clone() as Calendar)
            selectedTime = (cal.clone() as Calendar)
            updateDateTimeDisplay()
        }

        // Also directly create schedule after extraction
        val elderlyId = intent.getStringExtra(EXTRA_ELDERLY_ID) ?: ""
        if (elderlyId.isNotEmpty()) {
            val scheduledCal = Calendar.getInstance().apply {
                if (scheduledAtUnix > 0) timeInMillis = scheduledAtUnix * 1000
            }
            createScheduleViaAPI(elderlyId, title, message, scheduledCal, category)
        }
    }
    
    private fun setupCategorySelection() {
        // Set initial selection
        updateCategorySelection()
        
        medicineButton.setOnClickListener { selectCategory("medicine") }
        appointmentButton.setOnClickListener { selectCategory("appointment") }
        exerciseButton.setOnClickListener { selectCategory("exercise") }
        mealButton.setOnClickListener { selectCategory("meal") }
        otherButton.setOnClickListener { selectCategory("other") }
    }
    
    private fun selectCategory(category: String) {
        selectedCategory = category
        updateCategorySelection()
    }
    
    private fun updateCategorySelection() {
        // Reset all buttons
        val buttons = listOf(medicineButton, appointmentButton, exerciseButton, mealButton, otherButton)
        buttons.forEach { button ->
            button.setBackgroundResource(R.drawable.category_button_background)
            button.setTextColor(resources.getColor(R.color.text_primary, null))
        }
        
        // Highlight selected button
        val selectedButton = when (selectedCategory) {
            "medicine" -> medicineButton
            "appointment" -> appointmentButton
            "exercise" -> exerciseButton
            "meal" -> mealButton
            "other" -> otherButton
            else -> medicineButton
        }
        
        selectedButton.setBackgroundResource(R.drawable.category_button_selected_background)
        selectedButton.setTextColor(resources.getColor(R.color.primary_500, null))
    }
    
    private fun showDatePicker() {
        val datePickerDialog = DatePickerDialog(
            this,
            { _, year, month, dayOfMonth ->
                selectedDate.set(year, month, dayOfMonth)
                updateDateTimeDisplay()
            },
            selectedDate.get(Calendar.YEAR),
            selectedDate.get(Calendar.MONTH),
            selectedDate.get(Calendar.DAY_OF_MONTH)
        )
        datePickerDialog.show()
    }
    
    private fun showTimePicker() {
        val timePickerDialog = TimePickerDialog(
            this,
            { _, hourOfDay, minute ->
                selectedTime.set(Calendar.HOUR_OF_DAY, hourOfDay)
                selectedTime.set(Calendar.MINUTE, minute)
                updateDateTimeDisplay()
            },
            selectedTime.get(Calendar.HOUR_OF_DAY),
            selectedTime.get(Calendar.MINUTE),
            true
        )
        timePickerDialog.show()
    }
    
    private fun updateDateTimeDisplay() {
        val dateFormat = SimpleDateFormat("dd/MM/yyyy", Locale("vi"))
        val timeFormat = SimpleDateFormat("HH:mm", Locale("vi"))
        
        selectDateButton.text = dateFormat.format(selectedDate.time)
        selectTimeButton.text = timeFormat.format(selectedTime.time)
    }
    
    private fun saveSchedule() {
        val scheduleName = scheduleNameInput.text.toString().trim()
        val notes = notesInput.text.toString().trim()
        
        if (scheduleName.isEmpty()) {
            Toast.makeText(this, "Vui lòng nhập tên lịch trình", Toast.LENGTH_SHORT).show()
            return
        }
        
        // Combine date and time
        val scheduledDateTime = Calendar.getInstance()
        scheduledDateTime.set(
            selectedDate.get(Calendar.YEAR),
            selectedDate.get(Calendar.MONTH),
            selectedDate.get(Calendar.DAY_OF_MONTH),
            selectedTime.get(Calendar.HOUR_OF_DAY),
            selectedTime.get(Calendar.MINUTE),
            0
        )
        
        // Check if scheduled time is in the past
        if (scheduledDateTime.before(Calendar.getInstance())) {
            Toast.makeText(this, "Thời gian lịch trình không thể ở quá khứ", Toast.LENGTH_SHORT).show()
            return
        }
        
        val elderlyId = intent.getStringExtra(EXTRA_ELDERLY_ID)
        if (elderlyId == null) {
            Toast.makeText(this, "Không tìm thấy thông tin người già", Toast.LENGTH_SHORT).show()
            return
        }
        
        // Create schedule via API
        createScheduleViaAPI(elderlyId, scheduleName, notes, scheduledDateTime, selectedCategory)
    }
    
    private fun createScheduleViaAPI(
        elderlyId: String,
        title: String,
        notes: String,
        scheduledDateTime: Calendar,
        category: String
    ) {
        CoroutineScope(Dispatchers.Main).launch {
            try {
                // Get the current logged-in user ID from UserPreferences
                val targetUserId = userPreferences.getUserId()
                if (targetUserId.isNullOrEmpty()) {
                    Log.e(TAG, "No user logged in")
                    Toast.makeText(this@CreateScheduleActivity, "Bạn cần đăng nhập để tạo lịch", Toast.LENGTH_SHORT).show()
                    return@launch
                }
                
                val currentUserName = intent.getStringExtra("current_user_name") ?: userPreferences.getFullName() ?: "Family Member"
                
                Log.d(TAG, "Creating schedule with:")
                Log.d(TAG, "  - Target User ID: $targetUserId")
                Log.d(TAG, "  - Current User Name: $currentUserName")
                Log.d(TAG, "  - Elderly ID: $elderlyId")
                Log.d(TAG, "  - Title: $title")
                Log.d(TAG, "  - Category: $category")
                Log.d(TAG, "  - Scheduled Time: ${scheduledDateTime.time}")
                
                // Create schedule using API (database) - always use target user ID
                val scheduleData = JSONObject().apply {
                    put("elderly_id", targetUserId) // Always use target user ID
                    put("title", title)
                    put("message", notes)
                    put("scheduled_at", scheduledDateTime.timeInMillis / 1000) // Unix timestamp
                    put("notification_type", getNotificationType(category))
                    put("category", category)
                    put("priority", "normal")
                    put("created_by", targetUserId) // Always use target user ID
                }
                
                Log.d(TAG, "Schedule data created:")
                Log.d(TAG, "  - Target User ID: $targetUserId")
                Log.d(TAG, "  - Title: $title")
                Log.d(TAG, "  - Created By: $targetUserId")
                Log.d(TAG, "  - Scheduled At: ${scheduledDateTime.timeInMillis / 1000}")
                Log.d(TAG, "  - JSON Data: $scheduleData")
                
                val result = withContext(Dispatchers.IO) {
                    Log.d(TAG, "Calling ApiClient.createSchedule...")
                    val apiResult = ApiClient.createSchedule(scheduleData, this@CreateScheduleActivity)
                    Log.d(TAG, "ApiClient.createSchedule returned: $apiResult")
                    apiResult
                }
                
                when (result) {
                    is ApiResult.Success<*> -> {
                        Log.d(TAG, "Schedule created successfully via API!")
                        Toast.makeText(this@CreateScheduleActivity, "Đã tạo lịch trình thành công!", Toast.LENGTH_LONG).show()
                        setResult(RESULT_OK)
                        finish()
                    }
                    is ApiResult.Error -> {
                        Log.e(TAG, "Failed to create schedule via API: ${result.exception.message}")
                        
                        // Check if it's a server connection error
                        val errorMessage = result.exception.message ?: "Unknown error"
                        if (errorMessage.contains("502") || errorMessage.contains("Bad Gateway") || 
                            errorMessage.contains("<!DOCTYPE html>") || errorMessage.contains("cloudflare")) {
                            Toast.makeText(this@CreateScheduleActivity, "Máy chủ hiện tại không khả dụng. Vui lòng thử lại sau.", Toast.LENGTH_LONG).show()
                        } else if (errorMessage.contains("401") || errorMessage.contains("Unauthorized")) {
                            Toast.makeText(this@CreateScheduleActivity, "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.", Toast.LENGTH_LONG).show()
                        } else if (errorMessage.contains("Network is unreachable") || errorMessage.contains("No route to host")) {
                            Toast.makeText(this@CreateScheduleActivity, "Không thể kết nối đến máy chủ. Vui lòng kiểm tra kết nối mạng.", Toast.LENGTH_LONG).show()
                        } else {
                            Toast.makeText(this@CreateScheduleActivity, "Không thể tạo lịch trình: $errorMessage", Toast.LENGTH_LONG).show()
                        }
                    }
                }
                
            } catch (e: Exception) {
                Log.e(TAG, "Error creating schedule: ${e.message}", e)
                
                // Check if it's a server connection error
                val errorMessage = e.message ?: "Unknown error"
                if (errorMessage.contains("502") || errorMessage.contains("Bad Gateway") || 
                    errorMessage.contains("<!DOCTYPE html>") || errorMessage.contains("cloudflare")) {
                    Toast.makeText(this@CreateScheduleActivity, "Máy chủ hiện tại không khả dụng. Vui lòng thử lại sau.", Toast.LENGTH_LONG).show()
                } else if (errorMessage.contains("Network is unreachable") || errorMessage.contains("No route to host")) {
                    Toast.makeText(this@CreateScheduleActivity, "Không thể kết nối đến máy chủ. Vui lòng kiểm tra kết nối mạng.", Toast.LENGTH_LONG).show()
                } else {
                    Toast.makeText(this@CreateScheduleActivity, "Lỗi: $errorMessage", Toast.LENGTH_LONG).show()
                }
            }
        }
    }
    
    private fun getNotificationType(category: String): String {
        return when (category) {
            "medicine" -> "medicine_reminder"
            "appointment" -> "appointment_reminder"
            "exercise" -> "health_check"
            "meal" -> "custom"
            "other" -> "custom"
            else -> "custom"
        }
    }
} 