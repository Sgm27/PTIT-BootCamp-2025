package com.example.geminilivedemo

import android.app.DatePickerDialog
import android.app.TimePickerDialog
import android.os.Bundle
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
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.text.SimpleDateFormat
import java.util.*

class CreateScheduleActivity : AppCompatActivity() {
    
    private lateinit var titleText: TextView
    private lateinit var scheduleNameInput: TextInputEditText
    private lateinit var selectDateButton: MaterialButton
    private lateinit var selectTimeButton: MaterialButton
    private lateinit var notesInput: TextInputEditText
    private lateinit var saveScheduleButton: MaterialButton
    
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
        
        // Category buttons
        medicineButton = findViewById(R.id.medicineButton)
        appointmentButton = findViewById(R.id.appointmentButton)
        exerciseButton = findViewById(R.id.exerciseButton)
        mealButton = findViewById(R.id.mealButton)
        otherButton = findViewById(R.id.otherButton)
        
        // Set title
        val elderlyName = intent.getStringExtra(EXTRA_ELDERLY_NAME) ?: "Người già"
        titleText.text = "Tạo lịch trình cho $elderlyName"
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
            button.setBackgroundResource(R.drawable.classification_button_background)
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
        
        selectedButton.setBackgroundResource(R.drawable.primary_button_background)
        selectedButton.setTextColor(resources.getColor(R.color.white, null))
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
                val scheduleData = JSONObject().apply {
                    put("elderly_id", elderlyId)
                    put("title", title)
                    put("message", notes)
                    put("scheduled_at", scheduledDateTime.timeInMillis / 1000) // Convert to Unix timestamp
                    put("notification_type", getNotificationType(category))
                    put("category", category)
                    put("priority", "normal")
                }
                
                val result = withContext(Dispatchers.IO) {
                    ApiClient.createSchedule(scheduleData)
                }
                
                when (result) {
                    is ApiResult.Success<*> -> {
                        val response = result.data as JSONObject
                        if (response.getBoolean("success")) {
                            Toast.makeText(this@CreateScheduleActivity, "Đã tạo lịch trình thành công!", Toast.LENGTH_LONG).show()
                            setResult(RESULT_OK)
                            finish()
                        } else {
                            val errorMessage = response.optString("message", "Không thể tạo lịch trình")
                            Toast.makeText(this@CreateScheduleActivity, errorMessage, Toast.LENGTH_LONG).show()
                        }
                    }
                    is ApiResult.Error -> {
                        Log.e(TAG, "API error: ${result.exception.message}")
                        Toast.makeText(this@CreateScheduleActivity, "Lỗi kết nối: ${result.exception.message}", Toast.LENGTH_LONG).show()
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error creating schedule: ${e.message}", e)
                Toast.makeText(this@CreateScheduleActivity, "Lỗi: ${e.message}", Toast.LENGTH_LONG).show()
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