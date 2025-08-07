package com.example.geminilivedemo

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.geminilivedemo.data.*
import kotlinx.coroutines.launch
import okhttp3.OkHttpClient
import okhttp3.Request
import java.util.concurrent.TimeUnit

class LoginActivity : AppCompatActivity() {

    private lateinit var userPreferences: UserPreferences
    private lateinit var identifierEditText: EditText
    private lateinit var passwordEditText: EditText
    private lateinit var loginButton: Button
    private lateinit var registerButton: Button
    private lateinit var progressBar: ProgressBar
    private lateinit var errorTextView: TextView
    private lateinit var forgotPasswordTextView: TextView

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
        registerButton = findViewById(R.id.registerButton)
        progressBar = findViewById(R.id.progressBar)
        errorTextView = findViewById(R.id.errorTextView)
        forgotPasswordTextView = findViewById(R.id.forgotPasswordTextView)
    }

    private fun setupClickListeners() {
        loginButton.setOnClickListener {
            attemptLogin()
        }

        registerButton.setOnClickListener {
            val intent = Intent(this, RegisterActivity::class.java)
            startActivity(intent)
        }

        forgotPasswordTextView.setOnClickListener {
            // Debug: Test server connectivity
            testServerConnectivity()
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
        progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
        loginButton.isEnabled = !isLoading
        registerButton.isEnabled = !isLoading
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

    private fun testServerConnectivity() {
        lifecycleScope.launch {
            try {
                showError("Testing server connectivity...")
                Log.d("LoginActivity", "Testing connectivity to backend server...")
                
                // Try to call a simple endpoint
                val testUrl = "https://backend-bootcamp.sonktx.online/health"
                Log.d("LoginActivity", "Testing URL: $testUrl")
                
                val client = OkHttpClient.Builder()
                    .connectTimeout(10, TimeUnit.SECONDS)
                    .readTimeout(10, TimeUnit.SECONDS)
                    .build()
                
                val request = Request.Builder()
                    .url(testUrl)
                    .build()
                
                val response = client.newCall(request).execute()
                
                if (response.isSuccessful) {
                    val body = response.body?.string()
                    Log.d("LoginActivity", "Server response: $body")
                    showError("✅ Server connected! Response: ${response.code}")
                } else {
                    showError("❌ Server responded with: ${response.code}")
                }
                
            } catch (e: Exception) {
                Log.e("LoginActivity", "Connectivity test failed", e)
                showError("❌ Connection failed: ${e.message}")
            }
        }
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        // Prevent going back to splash/previous activities
        moveTaskToBack(true)
        super.onBackPressed()
    }
} 