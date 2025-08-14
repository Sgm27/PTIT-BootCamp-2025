package com.example.geminilivedemo

import android.content.Intent
import android.os.Bundle
import android.widget.EditText
import android.widget.ImageView
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import com.example.geminilivedemo.data.ProfileRepository
import com.example.geminilivedemo.data.UserPreferences

class EditProfileActivity : AppCompatActivity() {

    private lateinit var profileRepository: ProfileRepository
    private lateinit var userPreferences: UserPreferences
    private lateinit var backButton: ImageView
    private lateinit var editFullName: EditText
    private lateinit var editNickName: EditText
    private lateinit var editEmail: EditText
    private lateinit var editPhoneNumber: EditText
    private lateinit var editAddress: EditText
    private lateinit var saveButton: Button
    
    private var currentUserId: String? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_edit_profile)

        initViews()
        setupServices()
        loadCurrentUserDataFromServer()
        setupClickListeners()
    }

    private fun initViews() {
        backButton = findViewById(R.id.backButton)
        editFullName = findViewById(R.id.editFullName)
        editNickName = findViewById(R.id.editNickName)
        editEmail = findViewById(R.id.editEmail)
        editPhoneNumber = findViewById(R.id.editPhoneNumber)
        editAddress = findViewById(R.id.editAddress)
        saveButton = findViewById(R.id.saveButton)
    }
    
    private fun setupServices() {
        profileRepository = ProfileRepository(this)
        userPreferences = UserPreferences(this)
    }

    private fun loadCurrentUserDataFromServer() {
        // Get current user from UserPreferences
        val currentUser = userPreferences.getCurrentUser()
        if (currentUser == null) {
            showError("Không tìm thấy thông tin người dùng. Vui lòng đăng nhập lại.")
            redirectToLogin()
            return
        }
        
        currentUserId = currentUser.userId
        showLoadingState()
        
        // Load data from server
        lifecycleScope.launch {
            try {
                val result = profileRepository.loadProfileFromServer(currentUser.userId)
                if (result.isSuccess) {
                    val userProfile = result.getOrNull()
                    if (userProfile != null) {
                        populateFields(userProfile)
                    } else {
                        showError("Không thể tải thông tin người dùng từ server")
                    }
                } else {
                    val error = result.exceptionOrNull()
                    showError("Lỗi kết nối server: ${error?.message ?: "Không xác định"}")
                }
            } catch (e: Exception) {
                showError("Lỗi không mong muốn: ${e.message}")
            }
        }
    }
    
    private fun populateFields(userProfile: com.example.geminilivedemo.data.UserResponse) {
        editFullName.setText(userProfile.fullName)
        editNickName.setText(userProfile.fullName) // Use full name as nickname for now
        editEmail.setText(userProfile.email ?: "")
        editPhoneNumber.setText(userProfile.phone ?: "")
        editAddress.setText(userProfile.address ?: "")
    }
    
    private fun showLoadingState() {
        editFullName.setText("Đang tải...")
        editNickName.setText("Đang tải...")
        editEmail.setText("Đang tải...")
        editPhoneNumber.setText("Đang tải...")
        editAddress.setText("Đang tải...")
        saveButton.isEnabled = false
    }
    
    private fun showError(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show()
        editFullName.setText("")
        editNickName.setText("")
        editEmail.setText("")
        editPhoneNumber.setText("")
        editAddress.setText("")
        saveButton.isEnabled = false
    }
    
    private fun redirectToLogin() {
        val intent = Intent(this, LoginActivity::class.java)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        startActivity(intent)
        finish()
    }

    private fun setupClickListeners() {
        // Back button
        backButton.setOnClickListener {
            finish()
        }

        // Save button
        saveButton.setOnClickListener {
            saveUserProfile()
        }
    }

    private fun saveUserProfile() {
        val fullName = editFullName.text.toString().trim()
        val nickName = editNickName.text.toString().trim()
        val email = editEmail.text.toString().trim()
        val phoneNumber = editPhoneNumber.text.toString().trim()
        val address = editAddress.text.toString().trim()

        // Clear previous errors
        editFullName.error = null
        editNickName.error = null
        editEmail.error = null
        editPhoneNumber.error = null
        editAddress.error = null

        // Validate input
        if (fullName.isEmpty()) {
            editFullName.error = "Vui lòng nhập họ và tên"
            editFullName.requestFocus()
            return
        }

        if (nickName.isEmpty()) {
            editNickName.error = "Vui lòng nhập tên người dùng"
            editNickName.requestFocus()
            return
        }

        if (email.isEmpty() || !android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
            editEmail.error = "Vui lòng nhập email hợp lệ"
            editEmail.requestFocus()
            return
        }

        if (phoneNumber.isEmpty()) {
            editPhoneNumber.error = "Vui lòng nhập số điện thoại"
            editPhoneNumber.requestFocus()
            return
        }

        if (address.isEmpty()) {
            editAddress.error = "Vui lòng nhập địa chỉ"
            editAddress.requestFocus()
            return
        }

        // Save profile to server only
        saveProfileToServer(fullName, email, phoneNumber, address)
    }
    
    private fun saveProfileToServer(
        fullName: String,
        email: String,
        phone: String,
        address: String
    ) {
        if (currentUserId == null) {
            showError("Không tìm thấy ID người dùng. Vui lòng đăng nhập lại.")
            return
        }
        
        // Disable save button to prevent multiple clicks
        saveButton.isEnabled = false
        saveButton.text = "Đang lưu..."
        
        lifecycleScope.launch {
            try {
                val result = profileRepository.updateProfileOnServer(
                    userId = currentUserId!!,
                    fullName = fullName,
                    email = email,
                    phone = phone,
                    address = address
                )
                
                if (result.isSuccess) {
                    Toast.makeText(this@EditProfileActivity, "Đã cập nhật thông tin thành công", Toast.LENGTH_SHORT).show()
                    finish()
                } else {
                    val error = result.exceptionOrNull()
                    Toast.makeText(this@EditProfileActivity, "Lỗi cập nhật: ${error?.message ?: "Không xác định"}", Toast.LENGTH_LONG).show()
                }
            } catch (e: Exception) {
                Toast.makeText(this@EditProfileActivity, "Lỗi không mong muốn: ${e.message}", Toast.LENGTH_LONG).show()
            } finally {
                // Re-enable save button
                saveButton.isEnabled = true
                saveButton.text = "Lưu"
            }
        }
    }
}
