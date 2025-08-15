package com.example.geminilivedemo

import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.ArrayAdapter
import android.widget.AutoCompleteTextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.widget.Toolbar
import com.example.geminilivedemo.data.ApiClient
import com.example.geminilivedemo.data.ApiResult
import com.google.android.material.button.MaterialButton
import com.google.android.material.card.MaterialCardView
import com.google.android.material.textfield.TextInputEditText
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import org.json.JSONArray
import android.widget.TextView
import com.google.android.material.chip.Chip
import java.util.*

class FamilyNotificationActivity : AppCompatActivity() {
    
    private lateinit var toolbar: Toolbar
    private lateinit var elderlySpinner: AutoCompleteTextView
    private lateinit var notificationTypeSpinner: AutoCompleteTextView
    private lateinit var notificationTextEdit: TextInputEditText
    private lateinit var prioritySpinner: AutoCompleteTextView
    private lateinit var sendNotificationButton: MaterialButton
    private lateinit var loadingProgress: View
    private lateinit var successCard: MaterialCardView
    private lateinit var errorCard: MaterialCardView
    private lateinit var selectedElderlyInfo: TextView
    private lateinit var notificationPreviewCard: MaterialCardView
    private lateinit var previewTitle: TextView
    private lateinit var previewMessage: TextView
    private lateinit var previewType: Chip
    private lateinit var previewPriority: Chip
    
    private var elderlyList = mutableListOf<ElderlyUser>()
    private var selectedElderlyId: String? = null
    private var selectedElderlyName: String? = null
    
    companion object {
        private const val TAG = "FamilyNotificationActivity"
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_family_notification)
        
        initializeViews()
        setupToolbar()
        setupSpinners()
        setupPreviewCard()
        loadElderlyList()
        setupSendButton()
        setupTextChangeListeners()
    }
    
    private fun initializeViews() {
        toolbar = findViewById(R.id.toolbar)
        elderlySpinner = findViewById(R.id.elderly_spinner)
        notificationTypeSpinner = findViewById(R.id.notification_type_spinner)
        notificationTextEdit = findViewById(R.id.notification_text_edit)
        prioritySpinner = findViewById(R.id.priority_spinner)
        sendNotificationButton = findViewById(R.id.send_notification_button)
        loadingProgress = findViewById(R.id.loading_progress)
        successCard = findViewById(R.id.success_card)
        errorCard = findViewById(R.id.error_card)
        selectedElderlyInfo = findViewById(R.id.selected_elderly_info)
        notificationPreviewCard = findViewById(R.id.notification_preview_card)
        previewTitle = findViewById(R.id.preview_title)
        previewMessage = findViewById(R.id.preview_message)
        previewType = findViewById(R.id.preview_type)
        previewPriority = findViewById(R.id.preview_priority)
    }
    
    private fun setupToolbar() {
        setSupportActionBar(toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.setDisplayShowHomeEnabled(true)
        
        toolbar.setNavigationOnClickListener {
            onBackPressed()
        }
    }
    
    private fun setupSpinners() {
        // Notification types with Vietnamese labels
        val notificationTypes = arrayOf(
            "medicine" to "Nhắc nhở thuốc",
            "appointment" to "Lịch khám",
            "exercise" to "Tập thể dục",
            "water" to "Uống nước",
            "meal" to "Bữa ăn",
            "health_check" to "Kiểm tra sức khỏe",
            "emergency" to "Khẩn cấp",
            "custom" to "Tùy chỉnh"
        )
        
        val notificationTypeAdapter = ArrayAdapter(
            this, 
            android.R.layout.simple_dropdown_item_1line, 
            notificationTypes.map { "${it.second} (${it.first})" }
        )
        notificationTypeSpinner.setAdapter(notificationTypeAdapter)
        notificationTypeSpinner.setText("Nhắc nhở thuốc (medicine)", false)
        
        // Priority levels with Vietnamese labels
        val priorityLevels = arrayOf(
            "low" to "Thấp",
            "normal" to "Bình thường", 
            "high" to "Cao",
            "urgent" to "Khẩn cấp"
        )
        
        val priorityAdapter = ArrayAdapter(
            this, 
            android.R.layout.simple_dropdown_item_1line, 
            priorityLevels.map { "${it.second} (${it.first})" }
        )
        prioritySpinner.setAdapter(priorityAdapter)
        prioritySpinner.setText("Bình thường (normal)", false)
    }
    
    private fun setupPreviewCard() {
        // Initially hide preview card
        notificationPreviewCard.visibility = View.GONE
    }
    
    private fun setupTextChangeListeners() {
        // Update preview when text changes
        notificationTextEdit.addTextChangedListener(object : android.text.TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: android.text.Editable?) {
                updateNotificationPreview()
            }
        })
        
        // Update preview when spinners change
        notificationTypeSpinner.setOnItemClickListener { _, _, position, _ ->
            updateNotificationPreview()
        }
        
        prioritySpinner.setOnItemClickListener { _, _, position, _ ->
            updateNotificationPreview()
        }
    }
    
    private fun updateNotificationPreview() {
        val text = notificationTextEdit.text.toString().trim()
        val type = extractValueFromSpinner(notificationTypeSpinner.text.toString())
        val priority = extractValueFromSpinner(prioritySpinner.text.toString())
        
        if (text.isNotEmpty() && selectedElderlyName != null) {
            previewTitle.text = "Thông báo cho $selectedElderlyName"
            previewMessage.text = text
            previewType.text = getNotificationTypeLabel(type)
            previewPriority.text = getPriorityLabel(priority)
            
            // Set chip colors based on type and priority
            setChipColors(previewType, type)
            setChipColors(previewPriority, priority)
            
            notificationPreviewCard.visibility = View.VISIBLE
        } else {
            notificationPreviewCard.visibility = View.GONE
        }
    }
    
    private fun extractValueFromSpinner(spinnerText: String): String {
        // Extract value from "Label (value)" format
        return spinnerText.substringAfterLast("(").substringBefore(")")
    }
    
    private fun getNotificationTypeLabel(type: String): String {
        return when (type) {
            "medicine" -> "Thuốc"
            "appointment" -> "Lịch khám"
            "exercise" -> "Tập thể dục"
            "water" -> "Uống nước"
            "meal" -> "Bữa ăn"
            "health_check" -> "Kiểm tra sức khỏe"
            "emergency" -> "Khẩn cấp"
            "custom" -> "Tùy chỉnh"
            else -> type
        }
    }
    
    private fun getPriorityLabel(priority: String): String {
        return when (priority) {
            "low" -> "Thấp"
            "normal" -> "Bình thường"
            "high" -> "Cao"
            "urgent" -> "Khẩn cấp"
            else -> priority
        }
    }
    
    private fun setChipColors(chip: Chip, value: String) {
        val colorRes = when (value) {
            "medicine" -> android.R.color.holo_blue_light
            "appointment" -> android.R.color.holo_green_light
            "exercise" -> android.R.color.holo_orange_light
            "water" -> android.R.color.holo_blue_light
            "meal" -> android.R.color.holo_green_light
            "health_check" -> android.R.color.holo_blue_light
            "emergency" -> android.R.color.holo_red_dark
            "custom" -> android.R.color.holo_blue_light
            "low" -> android.R.color.holo_green_light
            "normal" -> android.R.color.holo_blue_light
            "high" -> android.R.color.holo_orange_light
            "urgent" -> android.R.color.holo_red_light
            else -> android.R.color.holo_blue_light
        }
        
        chip.chipBackgroundColor = android.content.res.ColorStateList.valueOf(
            getColor(colorRes)
        )
    }
    
    private fun loadElderlyList() {
        CoroutineScope(Dispatchers.Main).launch {
            try {
                loadingProgress.visibility = View.VISIBLE
                
                val result = withContext(Dispatchers.IO) {
                    ApiClient.getElderlyList()
                }
                
                when (result) {
                    is ApiResult.Success -> {
                        val response = result.data
                        if (response.getBoolean("success")) {
                            val elderlyArray = response.getJSONArray("elderly_list")
                            elderlyList.clear()
                            
                            for (i in 0 until elderlyArray.length()) {
                                val elderly = elderlyArray.getJSONObject(i)
                                elderlyList.add(
                                    ElderlyUser(
                                        id = elderly.getString("elderly_id"),
                                        name = elderly.getString("full_name"),
                                        email = elderly.getString("email"),
                                        relationship = elderly.getString("relationship_type")
                                    )
                                )
                            }
                            
                            setupElderlySpinner()
                        } else {
                            showError("Không thể tải danh sách người già")
                        }
                    }
                    is ApiResult.Error -> {
                        showError("Lỗi: ${result.exception.message ?: "Không xác định"}")
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error loading elderly list", e)
                showError("Có lỗi xảy ra: ${e.message}")
            } finally {
                loadingProgress.visibility = View.GONE
            }
        }
    }
    
    private fun setupElderlySpinner() {
        val elderlyNames = elderlyList.map { "${it.name} (${it.relationship})" }
        val adapter = ArrayAdapter(this, android.R.layout.simple_dropdown_item_1line, elderlyNames)
        elderlySpinner.setAdapter(adapter)
        
        if (elderlyList.isNotEmpty()) {
            elderlySpinner.setText(elderlyNames[0], false)
            selectedElderlyId = elderlyList[0].id
            selectedElderlyName = elderlyList[0].name
            updateSelectedElderlyInfo()
        }
        
        elderlySpinner.setOnItemClickListener { _, _, position, _ ->
            selectedElderlyId = elderlyList[position].id
            selectedElderlyName = elderlyList[position].name
            updateSelectedElderlyInfo()
            updateNotificationPreview()
        }
    }
    
    private fun updateSelectedElderlyInfo() {
        selectedElderlyName?.let { name ->
            selectedElderlyInfo.text = "Đang tạo thông báo cho: $name"
            selectedElderlyInfo.visibility = View.VISIBLE
        }
    }
    
    private fun setupSendButton() {
        sendNotificationButton.setOnClickListener {
            sendNotification()
        }
    }
    
    private fun sendNotification() {
        val elderlyId = selectedElderlyId
        val notificationText = notificationTextEdit.text.toString().trim()
        val notificationType = extractValueFromSpinner(notificationTypeSpinner.text.toString())
        val priority = extractValueFromSpinner(prioritySpinner.text.toString())
        
        if (elderlyId == null) {
            showError("Vui lòng chọn người già")
            return
        }
        
        if (notificationText.isEmpty()) {
            showError("Vui lòng nhập nội dung thông báo")
            return
        }
        
        CoroutineScope(Dispatchers.Main).launch {
            try {
                loadingProgress.visibility = View.VISIBLE
                sendNotificationButton.isEnabled = false
                hideMessages()
                
                val notificationData = JSONObject().apply {
                    put("elderly_user_id", elderlyId)
                    put("notification_data", JSONObject().apply {
                        put("text", notificationText)
                        put("type", notificationType)
                        put("priority", priority)
                    })
                }
                
                val result = withContext(Dispatchers.IO) {
                    ApiClient.sendFamilyNotification(notificationData)
                }
                
                when (result) {
                    is ApiResult.Success -> {
                        val response = result.data
                        if (response.getBoolean("success")) {
                            showSuccess("Thông báo đã được gửi thành công!")
                            notificationTextEdit.text?.clear()
                            notificationPreviewCard.visibility = View.GONE
                            selectedElderlyInfo.visibility = View.GONE
                        } else {
                            showError("Không thể gửi thông báo")
                        }
                    }
                    is ApiResult.Error -> {
                        showError("Lỗi: ${result.exception.message ?: "Không xác định"}")
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error sending notification", e)
                showError("Có lỗi xảy ra: ${e.message}")
            } finally {
                loadingProgress.visibility = View.GONE
                sendNotificationButton.isEnabled = true
            }
        }
    }
    
    private fun showSuccess(message: String) {
        successCard.visibility = View.VISIBLE
        errorCard.visibility = View.GONE
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }
    
    private fun showError(message: String) {
        errorCard.visibility = View.VISIBLE
        successCard.visibility = View.GONE
        Toast.makeText(this, message, Toast.LENGTH_LONG).show()
    }
    
    private fun hideMessages() {
        successCard.visibility = View.GONE
        errorCard.visibility = View.GONE
    }
    
    data class ElderlyUser(
        val id: String,
        val name: String,
        val email: String,
        val relationship: String
    )
} 