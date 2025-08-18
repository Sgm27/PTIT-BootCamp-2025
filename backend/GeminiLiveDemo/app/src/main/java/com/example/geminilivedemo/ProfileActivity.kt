package com.example.geminilivedemo

import android.content.Intent
import android.content.SharedPreferences
import android.os.Bundle
import android.util.Log
import android.widget.ImageView
import android.widget.Switch
import android.widget.TextView
import android.widget.Toast
import android.widget.LinearLayout
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.app.AppCompatDelegate
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import com.example.geminilivedemo.data.UserPreferences
import com.example.geminilivedemo.data.DataCacheManager
import com.example.geminilivedemo.FamilyConnectionActivity

class ProfileActivity : AppCompatActivity() {

    private lateinit var sharedPreferences: SharedPreferences
    private lateinit var userPreferences: UserPreferences
    private lateinit var profileAvatar: ImageView
    private lateinit var userName: TextView
    private lateinit var userEmail: TextView
    private lateinit var userPhone: TextView
    private lateinit var currentTheme: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_profile)

        initViews()
        setupSharedPreferences()
        setupServices()
        loadThemeSetting()
        loadUserData()
        setupClickListeners()
    }

    override fun onResume() {
        super.onResume()
        // Reload user data when returning from EditProfileActivity
        loadUserData()
    }

    private fun initViews() {
        try {
            profileAvatar = findViewById(R.id.profileAvatar)
            userName = findViewById(R.id.userName)
            currentTheme = findViewById(R.id.currentTheme)
            
            // Setup back button
            setupBackButton()
        } catch (e: Exception) {
            Log.e("ProfileActivity", "Error initializing views", e)
            // Create dummy TextViews if findViewById fails
            userName = TextView(this)
            currentTheme = TextView(this)
        }
    }
    
    private fun setupBackButton() {
        // Setup back button
        findViewById<ImageView>(R.id.backButton)?.setOnClickListener {
            finish() // Go back to previous activity
        }
    }

    private fun setupSharedPreferences() {
        sharedPreferences = getSharedPreferences("UserProfile", MODE_PRIVATE)
    }
    
    private fun setupServices() {
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

    private fun loadUserData() {
        try {
            // Load data from UserPreferences
            val fullName = userPreferences.getFullName() ?: "Lan Xinh"
            val email = userPreferences.getEmail() ?: "Chưa cập nhật"
            val phone = userPreferences.getPhone() ?: "Chưa cập nhật"
            
            updateUI(fullName, email, phone)
        } catch (e: Exception) {
            Log.e("ProfileActivity", "Error loading user data", e)
            showError(getString(R.string.error_loading_user_data))
        }
    }
    
    private fun updateUI(fullName: String, email: String, phone: String) {
        try {
            userName.text = fullName
            // userEmail and userPhone are no longer in the layout
            
            // Load theme setting
            val isDarkTheme = sharedPreferences.getBoolean("dark_theme", false)
            val isSystemTheme = sharedPreferences.getBoolean("system_theme", false)
            currentTheme.text = when {
                isSystemTheme -> "Theo hệ thống"
                isDarkTheme -> "Tối"
                else -> "Sáng"
            }
        } catch (e: Exception) {
            Log.e("ProfileActivity", "Error updating UI", e)
        }
    }
    
    private fun showError(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show()
        try {
            userName.text = "Lỗi tải dữ liệu"
            userEmail.text = "Vui lòng thử lại"
            userPhone.text = "Kiểm tra kết nối mạng"
        } catch (e: Exception) {
            Log.e("ProfileActivity", "Error showing error state", e)
        }
    }
    
    private fun redirectToLogin() {
        try {
            val intent = Intent(this, LoginActivity::class.java)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            startActivity(intent)
            finish()
        } catch (e: Exception) {
            Log.e("ProfileActivity", "Error redirecting to login", e)
        }
    }

    private fun setupClickListeners() {
        try {
            // Edit profile
            findViewById<android.widget.LinearLayout>(R.id.btnEditProfile)?.setOnClickListener {
                try {
                    val intent = Intent(this, EditProfileActivity::class.java)
                    startActivity(intent)
                } catch (e: Exception) {
                    Log.e("ProfileActivity", "Error opening EditProfileActivity", e)
                    Toast.makeText(this, "Không thể mở trang chỉnh sửa", Toast.LENGTH_SHORT).show()
                }
            }

            // Notifications switch
            findViewById<Switch>(R.id.notificationSwitch)?.setOnCheckedChangeListener { _, isChecked ->
                // Handle notification toggle
                Log.d("ProfileActivity", "Notifications enabled: $isChecked")
            }

            // Loved ones
            findViewById<android.widget.LinearLayout>(R.id.btnLovedOnes)?.setOnClickListener {
                try {
                    openFamilyConnectionActivity()
                } catch (e: Exception) {
                    Log.e("ProfileActivity", "Error opening loved ones", e)
                }
            }

            // Medical history
            findViewById<android.widget.LinearLayout>(R.id.btnMedicalHistory)?.setOnClickListener {
                try {
                    // TODO: Open medical history activity
                    Toast.makeText(this, "Tính năng đang phát triển", Toast.LENGTH_SHORT).show()
                } catch (e: Exception) {
                    Log.e("ProfileActivity", "Error opening medical history", e)
                }
            }

            // Life Memoirs
            findViewById<android.widget.LinearLayout>(R.id.btnLifeMemoir)?.setOnClickListener {
                try {
                    val intent = Intent(this, LifeMemoirActivity::class.java)
                    startActivity(intent)
                } catch (e: Exception) {
                    Log.e("ProfileActivity", "Error opening Life Memoir Activity", e)
                    Toast.makeText(this, "Không thể mở những câu chuyện đời", Toast.LENGTH_SHORT).show()
                }
            }

            // Theme settings
            findViewById<android.widget.LinearLayout>(R.id.btnTheme)?.setOnClickListener {
                showThemeDialog()
            }

            // Help and support
            findViewById<android.widget.LinearLayout>(R.id.btnHelpSupport)?.setOnClickListener {
                try {
                    // TODO: Open help and support activity
                    Toast.makeText(this, "Tính năng đang phát triển", Toast.LENGTH_SHORT).show()
                } catch (e: Exception) {
                    Log.e("ProfileActivity", "Error opening help and support", e)
                }
            }

            // Privacy policy
            findViewById<android.widget.LinearLayout>(R.id.btnPrivacyPolicy)?.setOnClickListener {
                try {
                    // TODO: Open privacy policy activity
                    Toast.makeText(this, "Tính năng đang phát triển", Toast.LENGTH_SHORT).show()
                } catch (e: Exception) {
                    Log.e("ProfileActivity", "Error opening privacy policy", e)
                }
            }

            // Logout
            findViewById<android.widget.LinearLayout>(R.id.btnLogout)?.setOnClickListener {
                showLogoutDialog()
            }
        } catch (e: Exception) {
            Log.e("ProfileActivity", "Error setting up click listeners", e)
        }
    }
    
    private fun showThemeDialog() {
        try {
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
                            try {
                                currentTheme.text = "Sáng"
                            } catch (e: Exception) {
                                Log.e("ProfileActivity", "Error updating theme text", e)
                            }
                        }
                        1 -> {
                            setTheme(true, false)
                            try {
                                currentTheme.text = "Tối"
                            } catch (e: Exception) {
                                Log.e("ProfileActivity", "Error updating theme text", e)
                            }
                        }
                        2 -> {
                            setTheme(false, true)
                            try {
                                currentTheme.text = "Theo hệ thống"
                            } catch (e: Exception) {
                                Log.e("ProfileActivity", "Error updating theme text", e)
                            }
                        }
                    }
                    dialog.dismiss()
                }
                .setNegativeButton("Hủy", null)
                .show()
        } catch (e: Exception) {
            Log.e("ProfileActivity", "Error showing theme dialog", e)
        }
    }
    
    private fun openFamilyConnectionActivity() {
        try {
            // Get current user information
            val currentUserId = userPreferences.getUserId()
            val currentUserType = userPreferences.getUserType()
            
            if (currentUserId.isNullOrEmpty() || currentUserType.isNullOrEmpty()) {
                Toast.makeText(this, "Vui lòng đăng nhập lại", Toast.LENGTH_SHORT).show()
                redirectToLogin()
                return
            }
            
            val intent = Intent(this, FamilyConnectionActivity::class.java).apply {
                putExtra("current_user_id", currentUserId)
                putExtra("current_user_type", currentUserType)
                putExtra("current_user_name", userPreferences.getFullName() ?: "Người dùng")
            }
            startActivity(intent)
        } catch (e: Exception) {
            Log.e("ProfileActivity", "Error opening family connection activity", e)
            Toast.makeText(this, "Không thể mở kết nối yêu thương", Toast.LENGTH_SHORT).show()
        }
    }
    
    private fun showLogoutDialog() {
        try {
            androidx.appcompat.app.AlertDialog.Builder(this)
                .setTitle("Đăng xuất")
                .setMessage("Bạn có chắc chắn muốn đăng xuất không?")
                .setPositiveButton("Đăng xuất") { _, _ ->
                    logout()
                }
                .setNegativeButton("Hủy", null)
                .show()
        } catch (e: Exception) {
            Log.e("ProfileActivity", "Error showing logout dialog", e)
        }
    }
    
    private fun setTheme(isDark: Boolean, isSystem: Boolean) {
        try {
            val editor = sharedPreferences.edit()
            editor.putBoolean("dark_theme", isDark)
            editor.putBoolean("system_theme", isSystem)
            editor.apply()

            when {
                isSystem -> AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM)
                isDark -> AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_YES)
                else -> AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO)
            }
        } catch (e: Exception) {
            Log.e("ProfileActivity", "Error setting theme", e)
        }
    }

    private fun logout() {
        try {
            // Clear user session data
            userPreferences.clearUserData()
            
            // Clear any remaining SharedPreferences data
            sharedPreferences.edit().clear().apply()
            
            // Clear data cache khi logout
            try {
                val dataCacheManager = DataCacheManager.getInstance(this)
                dataCacheManager.clearAllCache()
                Log.d("ProfileActivity", "Cleared all data cache on logout")
            } catch (e: Exception) {
                Log.w("ProfileActivity", "Error clearing data cache", e)
            }
            
            // Redirect to login
            val intent = Intent(this, LoginActivity::class.java)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            startActivity(intent)
            finish()
            
            Toast.makeText(this, "Đã đăng xuất", Toast.LENGTH_SHORT).show()
        } catch (e: Exception) {
            Log.e("ProfileActivity", "Error during logout", e)
        }
    }
}
