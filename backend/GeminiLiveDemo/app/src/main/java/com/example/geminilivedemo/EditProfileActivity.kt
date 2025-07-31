package com.example.geminilivedemo

import android.content.Intent
import android.content.SharedPreferences
import android.os.Bundle
import android.widget.EditText
import android.widget.ImageView
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class EditProfileActivity : AppCompatActivity() {

    private lateinit var sharedPreferences: SharedPreferences
    private lateinit var backButton: ImageView
    private lateinit var editFullName: EditText
    private lateinit var editNickName: EditText
    private lateinit var editEmail: EditText
    private lateinit var editPhoneNumber: EditText
    private lateinit var editAddress: EditText
    private lateinit var saveButton: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_edit_profile)

        initViews()
        setupSharedPreferences()
        loadCurrentUserData()
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

    private fun setupSharedPreferences() {
        sharedPreferences = getSharedPreferences("UserProfile", MODE_PRIVATE)
    }

    private fun loadCurrentUserData() {
        // Load current user data from SharedPreferences
        val savedName = sharedPreferences.getString("user_name", "Puerto Rico")
        val savedNickName = sharedPreferences.getString("user_nickname", "puerto.rico")
        val savedEmail = sharedPreferences.getString("user_email", "youremail@domain.com")
        val savedPhone = sharedPreferences.getString("user_phone", "+84 456 7890")
        val savedAddress = sharedPreferences.getString("user_address", "Hà Đông, Hà Nội")

        editFullName.setText(savedName)
        editNickName.setText(savedNickName)
        editEmail.setText(savedEmail)
        editPhoneNumber.setText(savedPhone)
        editAddress.setText(savedAddress)
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

        // Save to SharedPreferences
        val editor = sharedPreferences.edit()
        editor.putString("user_name", fullName)
        editor.putString("user_nickname", nickName)
        editor.putString("user_email", email)
        editor.putString("user_phone", phoneNumber)
        editor.putString("user_address", address)
        editor.apply()

        // Show success message
        Toast.makeText(this, "Đã cập nhật thông tin thành công", Toast.LENGTH_SHORT).show()
        
        // Return to profile activity
        finish()
    }
}
