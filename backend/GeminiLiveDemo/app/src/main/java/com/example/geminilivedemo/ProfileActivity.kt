package com.example.geminilivedemo

import android.content.Intent
import android.content.SharedPreferences
import android.os.Bundle
import android.util.Log
import android.widget.ImageView
import android.widget.Switch
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.app.AppCompatDelegate
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import com.example.geminilivedemo.data.ProfileRepository
import com.example.geminilivedemo.data.UserPreferences

class ProfileActivity : AppCompatActivity(), GlobalConnectionManager.ConnectionStateCallback {

    private lateinit var sharedPreferences: SharedPreferences
    private lateinit var profileRepository: ProfileRepository
    private lateinit var userPreferences: UserPreferences
    private lateinit var profileAvatar: ImageView
    private lateinit var userName: TextView
    private lateinit var userEmail: TextView
    private lateinit var userPhone: TextView
    private lateinit var currentTheme: TextView
    private lateinit var globalConnectionManager: GlobalConnectionManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_profile)

        // Lấy GlobalConnectionManager và đăng ký callback
        globalConnectionManager = (application as GeminiLiveApplication).getGlobalConnectionManager()
        globalConnectionManager.registerCallback(this)

        initViews()
        setupSharedPreferences()
        setupServices()
        loadThemeSetting()
        loadUserDataFromServer()
        setupClickListeners()
    }

    override fun onResume() {
        super.onResume()
        // Reload user data from server when returning from EditProfileActivity
        loadUserDataFromServer()
    }

    private fun initViews() {
        profileAvatar = findViewById(R.id.profileAvatar)
        userName = findViewById(R.id.userName)
        userEmail = findViewById(R.id.userEmail)
        userPhone = findViewById(R.id.userPhone)
        currentTheme = findViewById(R.id.currentTheme)
    }

    private fun setupSharedPreferences() {
        sharedPreferences = getSharedPreferences("UserProfile", MODE_PRIVATE)
    }
    
    private fun setupServices() {
        profileRepository = ProfileRepository(this)
        userPreferences = UserPreferences(this)
    }
    
    private fun loadThemeSetting() {
        val isDarkTheme = sharedPreferences.getBoolean("dark_theme", false)
        val isSystemTheme = sharedPreferences.getBoolean("system_theme", false)
        
        when {
            isSystemTheme -> AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM)
            isDarkTheme -> AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_YES)
            else -> AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO)
        }
    }

    private fun loadUserDataFromServer() {
        // Get current user ID from UserPreferences
        val currentUser = userPreferences.getCurrentUser()
        if (currentUser == null) {
            showError("Không tìm thấy thông tin người dùng. Vui lòng đăng nhập lại.")
            redirectToLogin()
            return
        }

        // Show loading state
        showLoadingState()
        
        // Load data directly from server
        lifecycleScope.launch {
            try {
                val result = profileRepository.loadProfileFromServer(currentUser.userId)
                if (result.isSuccess) {
                    val userProfile = result.getOrNull()
                    if (userProfile != null) {
                        updateUI(userProfile)
                        Toast.makeText(this@ProfileActivity, "Đã tải dữ liệu từ server", Toast.LENGTH_SHORT).show()
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
    
    private fun updateUI(userProfile: com.example.geminilivedemo.data.UserResponse) {
        userName.text = userProfile.fullName
        userEmail.text = userProfile.email ?: "Chưa cập nhật"
        userPhone.text = userProfile.phone ?: "Chưa cập nhật"
        
        // Load theme setting (this can stay in SharedPreferences as it's a UI preference)
        val isDarkTheme = sharedPreferences.getBoolean("dark_theme", false)
        val isSystemTheme = sharedPreferences.getBoolean("system_theme", false)
        currentTheme.text = when {
            isSystemTheme -> "Theo hệ thống"
            isDarkTheme -> "Tối"
            else -> "Sáng"
        }
    }
    
    private fun showLoadingState() {
        userName.text = "Đang tải..."
        userEmail.text = "Đang tải..."
        userPhone.text = "Đang tải..."
    }
    
    private fun showError(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show()
        // Show error state in UI
        userName.text = "Lỗi tải dữ liệu"
        userEmail.text = "Vui lòng thử lại"
        userPhone.text = "Kiểm tra kết nối mạng"
    }
    
    private fun redirectToLogin() {
        val intent = Intent(this, LoginActivity::class.java)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        startActivity(intent)
        finish()
    }

    private fun setupClickListeners() {
        // Edit profile
        findViewById<android.widget.LinearLayout>(R.id.btnEditProfile).setOnClickListener {
            val intent = Intent(this, EditProfileActivity::class.java)
            startActivity(intent)
        }

        // Life memoir
        findViewById<android.widget.LinearLayout>(R.id.btnLifeMemoir).setOnClickListener {
            val intent = Intent(this, LifeMemoirActivity::class.java)
            startActivity(intent)
        }

        // Theme settings
        findViewById<android.widget.LinearLayout>(R.id.btnTheme).setOnClickListener {
            showThemeDialog()
        }

        // Logout
        findViewById<android.widget.LinearLayout>(R.id.btnLogout).setOnClickListener {
            showLogoutDialog()
        }
    }
    
    private fun showThemeDialog() {
        val themes = arrayOf("Sáng", "Tối", "Theo hệ thống")
        val currentThemeIndex = when {
            sharedPreferences.getBoolean("dark_theme", false) -> 1
            sharedPreferences.getBoolean("system_theme", false) -> 2
            else -> 0
        }

        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("Chọn giao diện")
            .setSingleChoiceItems(themes, currentThemeIndex) { dialog, which ->
                when (which) {
                    0 -> {
                        setTheme(false, false)
                        currentTheme.text = "Sáng"
                    }
                    1 -> {
                        setTheme(true, false)
                        currentTheme.text = "Tối"
                    }
                    2 -> {
                        setTheme(false, true)
                        currentTheme.text = "Theo hệ thống"
                    }
                }
                dialog.dismiss()
            }
            .setNegativeButton("Hủy", null)
            .show()
    }
    
    private fun showLogoutDialog() {
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("Đăng xuất")
            .setMessage("Bạn có chắc chắn muốn đăng xuất không?")
            .setPositiveButton("Đăng xuất") { _, _ ->
                logout()
            }
            .setNegativeButton("Hủy", null)
            .show()
    }
    
    private fun setTheme(isDark: Boolean, isSystem: Boolean) {
        val editor = sharedPreferences.edit()
        editor.putBoolean("dark_theme", isDark)
        editor.putBoolean("system_theme", isSystem)
        editor.apply()

        when {
            isSystem -> AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM)
            isDark -> AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_YES)
            else -> AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO)
        }
    }

    private fun logout() {
        // Clear user session data
        userPreferences.clearUserData()
        
        // Clear any remaining SharedPreferences data
        sharedPreferences.edit().clear().apply()
        
        // Redirect to login
        val intent = Intent(this, LoginActivity::class.java)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        startActivity(intent)
        finish()
        
        Toast.makeText(this, "Đã đăng xuất", Toast.LENGTH_SHORT).show()
    }
    
    override fun onDestroy() {
        super.onDestroy()
        // Hủy đăng ký callback
        globalConnectionManager.unregisterCallback(this)
    }
    
    // Callback methods từ GlobalConnectionManager.ConnectionStateCallback
    override fun onConnectionStateChanged(isConnected: Boolean) {
        Log.d("ProfileActivity", "Connection state changed: $isConnected")
        // ProfileActivity không cần xử lý connection state đặc biệt
    }
    
    override fun onChatAvailabilityChanged(isChatAvailable: Boolean) {
        Log.d("ProfileActivity", "Chat availability changed: $isChatAvailable")
        // ProfileActivity không có chat UI nên không cần xử lý
        if (isChatAvailable) {
            // Có thể hiển thị thông báo rằng chat chỉ khả dụng ở màn hình chính
            runOnUiThread {
                Toast.makeText(this, "Chat chỉ khả dụng ở màn hình chính", Toast.LENGTH_SHORT).show()
            }
        }
    }
}
