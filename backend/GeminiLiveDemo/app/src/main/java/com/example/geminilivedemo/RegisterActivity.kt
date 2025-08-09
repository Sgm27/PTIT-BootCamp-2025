package com.example.geminilivedemo

import android.app.DatePickerDialog
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.geminilivedemo.data.*
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

class RegisterActivity : AppCompatActivity() {

    private lateinit var userPreferences: UserPreferences
    
    // UI Components
    private lateinit var userTypeRadioGroup: RadioGroup
    private lateinit var elderlyRadioButton: RadioButton
    private lateinit var familyRadioButton: RadioButton
    private lateinit var fullNameEditText: EditText
    private lateinit var emailEditText: EditText
    private lateinit var phoneEditText: EditText
    private lateinit var passwordEditText: EditText
    private lateinit var confirmPasswordEditText: EditText
    private lateinit var dateOfBirthEditText: EditText
    private lateinit var genderSpinner: Spinner
    private lateinit var addressEditText: EditText
    private lateinit var registerButton: Button
    private lateinit var backButton: Button
    private lateinit var progressBar: ProgressBar
    private lateinit var errorTextView: TextView
    
    private var selectedDate: Date? = null
    private val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
    private val displayDateFormat = SimpleDateFormat("dd/MM/yyyy", Locale.getDefault())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_register)

        userPreferences = UserPreferences(this)
        
        initializeViews()
        setupClickListeners()
        setupSpinner()
    }

    private fun initializeViews() {
        userTypeRadioGroup = findViewById(R.id.userTypeRadioGroup)
        elderlyRadioButton = findViewById(R.id.elderlyRadioButton)
        familyRadioButton = findViewById(R.id.familyRadioButton)
        fullNameEditText = findViewById(R.id.fullNameEditText)
        emailEditText = findViewById(R.id.emailEditText)
        phoneEditText = findViewById(R.id.phoneEditText)
        passwordEditText = findViewById(R.id.passwordEditText)
        confirmPasswordEditText = findViewById(R.id.confirmPasswordEditText)
        dateOfBirthEditText = findViewById(R.id.dateOfBirthEditText)
        genderSpinner = findViewById(R.id.genderSpinner)
        addressEditText = findViewById(R.id.addressEditText)
        registerButton = findViewById(R.id.registerButton)
        backButton = findViewById(R.id.backButton)
        progressBar = findViewById(R.id.progressBar)
        errorTextView = findViewById(R.id.errorTextView)
        
        // Set default user type
        elderlyRadioButton.isChecked = true
    }

    private fun setupClickListeners() {
        registerButton.setOnClickListener {
            attemptRegister()
        }

        backButton.setOnClickListener {
            finish()
        }

        dateOfBirthEditText.setOnClickListener {
            showDatePicker()
        }
    }

    private fun setupSpinner() {
        val genderOptions = arrayOf("Chọn giới tính", "Nam", "Nữ", "Khác")
        val adapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, genderOptions)
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        genderSpinner.adapter = adapter
    }

    private fun showDatePicker() {
        val calendar = Calendar.getInstance()
        val year = calendar.get(Calendar.YEAR)
        val month = calendar.get(Calendar.MONTH)
        val day = calendar.get(Calendar.DAY_OF_MONTH)

        val datePicker = DatePickerDialog(this, { _, selectedYear, selectedMonth, selectedDay ->
            calendar.set(selectedYear, selectedMonth, selectedDay)
            selectedDate = calendar.time
            dateOfBirthEditText.setText(displayDateFormat.format(selectedDate!!))
        }, year, month, day)

        // Set maximum date to today
        datePicker.datePicker.maxDate = System.currentTimeMillis()
        
        // Set minimum date to 120 years ago
        calendar.add(Calendar.YEAR, -120)
        datePicker.datePicker.minDate = calendar.timeInMillis
        
        datePicker.show()
    }

    private fun attemptRegister() {
        // Get form data
        val userType = if (elderlyRadioButton.isChecked) UserType.ELDERLY else UserType.FAMILY_MEMBER
        val fullName = fullNameEditText.text.toString().trim()
        val email = emailEditText.text.toString().trim().ifEmpty { null }
        val phone = phoneEditText.text.toString().trim().ifEmpty { null }
        val password = passwordEditText.text.toString()
        val confirmPassword = confirmPasswordEditText.text.toString()
        val dateOfBirth = selectedDate?.let { dateFormat.format(it) }
        val gender = if (genderSpinner.selectedItemPosition > 0) {
            genderSpinner.selectedItem.toString()
        } else null
        val address = addressEditText.text.toString().trim().ifEmpty { null }

        // Validate inputs
        if (!validateInputs(fullName, email, phone, password, confirmPassword)) {
            return
        }

        // Clear previous errors
        errorTextView.visibility = View.GONE

        // Show loading
        setLoadingState(true)

        // Make API call
        val registerRequest = RegisterRequest(
            userType = userType,
            fullName = fullName,
            email = email,
            phone = phone,
            password = password,
            dateOfBirth = dateOfBirth,
            gender = gender,
            address = address
        )

        lifecycleScope.launch {
            try {
                val response = ApiClient.apiService.registerUser(registerRequest)

                if (response.isSuccessful) {
                    val registerResponse = response.body()
                    if (registerResponse?.success == true && registerResponse.user != null) {
                        // Save user data
                        userPreferences.saveUserData(registerResponse)
                        
                        // Show success message
                        Toast.makeText(this@RegisterActivity, "Đăng ký thành công!", Toast.LENGTH_SHORT).show()
                        
                        // Navigate to main activity
                        navigateToMainActivity()
                    } else {
                        showError(registerResponse?.message ?: "Đăng ký thất bại")
                    }
                } else {
                    when (response.code()) {
                        400 -> showError("Thông tin không hợp lệ hoặc email/SĐT đã tồn tại")
                        503 -> showError("Dịch vụ không khả dụng. Vui lòng thử lại sau.")
                        else -> showError("Lỗi kết nối: ${response.code()}")
                    }
                }
            } catch (e: Exception) {
                Log.e("RegisterActivity", "Register error", e)
                showError("Lỗi kết nối mạng. Vui lòng kiểm tra kết nối internet.")
            } finally {
                setLoadingState(false)
            }
        }
    }

    private fun validateInputs(
        fullName: String,
        email: String?,
        phone: String?,
        password: String,
        confirmPassword: String
    ): Boolean {
        var isValid = true

        // Full name validation
        if (fullName.isEmpty()) {
            fullNameEditText.error = "Vui lòng nhập họ tên"
            isValid = false
        } else if (fullName.length < 2) {
            fullNameEditText.error = "Họ tên phải có ít nhất 2 ký tự"
            isValid = false
        }

        // Email or phone validation (at least one is required)
        if (email.isNullOrEmpty() && phone.isNullOrEmpty()) {
            emailEditText.error = "Vui lòng nhập email hoặc số điện thoại"
            phoneEditText.error = "Vui lòng nhập email hoặc số điện thoại"
            isValid = false
        } else {
            // Email validation
            if (!email.isNullOrEmpty() && !android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
                emailEditText.error = "Email không hợp lệ"
                isValid = false
            }

            // Phone validation
            if (!phone.isNullOrEmpty() && (phone.length < 10 || !phone.all { it.isDigit() })) {
                phoneEditText.error = "Số điện thoại không hợp lệ"
                isValid = false
            }
        }

        // Password validation
        if (password.isEmpty()) {
            passwordEditText.error = "Vui lòng nhập mật khẩu"
            isValid = false
        } else if (password.length < 6) {
            passwordEditText.error = "Mật khẩu phải có ít nhất 6 ký tự"
            isValid = false
        }

        // Confirm password validation
        if (confirmPassword.isEmpty()) {
            confirmPasswordEditText.error = "Vui lòng xác nhận mật khẩu"
            isValid = false
        } else if (password != confirmPassword) {
            confirmPasswordEditText.error = "Mật khẩu xác nhận không khớp"
            isValid = false
        }

        return isValid
    }

    private fun setLoadingState(isLoading: Boolean) {
        progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
        registerButton.isEnabled = !isLoading
        backButton.isEnabled = !isLoading
        
        // Disable all form inputs
        userTypeRadioGroup.isEnabled = !isLoading
        elderlyRadioButton.isEnabled = !isLoading
        familyRadioButton.isEnabled = !isLoading
        fullNameEditText.isEnabled = !isLoading
        emailEditText.isEnabled = !isLoading
        phoneEditText.isEnabled = !isLoading
        passwordEditText.isEnabled = !isLoading
        confirmPasswordEditText.isEnabled = !isLoading
        dateOfBirthEditText.isEnabled = !isLoading
        genderSpinner.isEnabled = !isLoading
        addressEditText.isEnabled = !isLoading
        
        registerButton.text = if (isLoading) "Đang đăng ký..." else "Đăng ký"
    }

    private fun showError(message: String) {
        errorTextView.text = message
        errorTextView.visibility = View.VISIBLE
    }

    private fun navigateToMainActivity() {
        val intent = Intent(this, MainActivity::class.java)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        startActivity(intent)
        finish()
    }
} 