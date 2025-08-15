package com.example.geminilivedemo

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.geminilivedemo.data.*
import kotlinx.coroutines.launch

class LoginActivity : AppCompatActivity() {

    private lateinit var userPreferences: UserPreferences
    private lateinit var identifierEditText: EditText
    private lateinit var passwordEditText: EditText
    private lateinit var loginButton: com.google.android.material.button.MaterialButton
    private lateinit var registerLink: TextView
    private lateinit var errorTextView: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        userPreferences = UserPreferences(this)

        // Kiểm tra nếu user đã đăng nhập
        if (userPreferences.isLoggedIn()) {
            navigateToMainActivity()
            return
        }

        initializeViews()
        setupClickListeners()
    }

    private fun initializeViews() {
        identifierEditText = findViewById(R.id.identifierEditText)
        passwordEditText = findViewById(R.id.passwordEditText)
        loginButton = findViewById(R.id.loginButton)
        registerLink = findViewById(R.id.registerLink)
        errorTextView = findViewById(R.id.errorTextView)
    }

    private fun setupClickListeners() {
        loginButton.setOnClickListener {
            attemptLogin()
        }

        registerLink.setOnClickListener {
            val intent = Intent(this, RegisterActivity::class.java)
            startActivity(intent)
        }
    }

    private fun attemptLogin() {
        val identifier = identifierEditText.text.toString().trim()
        val password = passwordEditText.text.toString().trim()

        // Validate inputs
        if (identifier.isEmpty()) {
            identifierEditText.error = "Vui lòng nhập email hoặc số điện thoại"
            return
        }

        if (password.isEmpty()) {
            passwordEditText.error = "Vui lòng nhập mật khẩu"
            return
        }

        if (password.length < 6) {
            passwordEditText.error = "Mật khẩu phải có ít nhất 6 ký tự"
            return
        }

        // Clear previous errors
        errorTextView.visibility = View.GONE
        identifierEditText.error = null
        passwordEditText.error = null

        // Show loading
        setLoadingState(true)

        // Make API call
        val loginRequest = LoginRequest(identifier, password)

        lifecycleScope.launch {
            try {
                Log.d("LoginActivity", "Making login request to: ${loginRequest.identifier}")
                Log.d("LoginActivity", "API Base URL check - making request...")
                
                val response = ApiClient.apiService.loginUser(loginRequest)
                
                Log.d("LoginActivity", "Response received - Code: ${response.code()}, Success: ${response.isSuccessful}")

                if (response.isSuccessful) {
                    val loginResponse = response.body()
                    if (loginResponse?.success == true && loginResponse.user != null) {
                        // Save user data
                        userPreferences.saveUserData(loginResponse)
                        
                        // Show success message
                        Toast.makeText(this@LoginActivity, "Đăng nhập thành công!", Toast.LENGTH_SHORT).show()
                        
                        // Navigate to main activity
                        navigateToMainActivity()
                    } else {
                        showError(loginResponse?.message ?: "Đăng nhập thất bại")
                    }
                } else {
                    when (response.code()) {
                        401 -> showError("Email/SĐT hoặc mật khẩu không chính xác")
                        503 -> showError("Dịch vụ không khả dụng. Vui lòng thử lại sau.")
                        else -> showError("Lỗi kết nối: ${response.code()}")
                    }
                }
            } catch (e: Exception) {
                Log.e("LoginActivity", "Login error: ${e.message}", e)
                
                // More specific error messages
                val errorMessage = when {
                    e.message?.contains("Unable to resolve host") == true -> 
                        "Không thể kết nối đến server. Kiểm tra WiFi/4G và server có đang chạy không."
                    e.message?.contains("Connection refused") == true -> 
                        "Server từ chối kết nối. Kiểm tra server có đang chạy trên port 8000 không."
                    e.message?.contains("timeout") == true -> 
                        "Timeout kết nối. Server phản hồi chậm hoặc mạng yếu."
                    else -> 
                        "Lỗi kết nối: ${e.message}"
                }
                
                showError(errorMessage)
            } finally {
                setLoadingState(false)
            }
        }
    }

    private fun setLoadingState(isLoading: Boolean) {
        loginButton.isEnabled = !isLoading
        registerLink.isEnabled = !isLoading
        identifierEditText.isEnabled = !isLoading
        passwordEditText.isEnabled = !isLoading
        
        loginButton.text = if (isLoading) "Đang đăng nhập..." else "Đăng nhập"
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



    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        // Prevent going back to splash/previous activities
        moveTaskToBack(true)
        super.onBackPressed()
    }
} 