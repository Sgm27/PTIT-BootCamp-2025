package com.example.geminilivedemo

import android.content.Intent
import android.content.SharedPreferences
import android.os.Bundle
import android.widget.ImageView
import android.widget.Switch
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.app.AppCompatDelegate

class ProfileActivity : AppCompatActivity() {

    private lateinit var sharedPreferences: SharedPreferences
    private lateinit var profileAvatar: ImageView
    private lateinit var userName: TextView
    private lateinit var userEmail: TextView
    private lateinit var userPhone: TextView
    private lateinit var switchNotifications: Switch
    private lateinit var currentTheme: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_profile)

        initViews()
        setupSharedPreferences()
        loadUserData()
        setupClickListeners()
    }

    private fun initViews() {
        profileAvatar = findViewById(R.id.profileAvatar)
        userName = findViewById(R.id.userName)
        userEmail = findViewById(R.id.userEmail)
        userPhone = findViewById(R.id.userPhone)
        switchNotifications = findViewById(R.id.switchNotifications)
        currentTheme = findViewById(R.id.currentTheme)
    }

    private fun setupSharedPreferences() {
        sharedPreferences = getSharedPreferences("UserProfile", MODE_PRIVATE)
    }

    private fun loadUserData() {
        // Load user data from SharedPreferences
        val savedName = sharedPreferences.getString("user_name", "Puerto Rico")
        val savedEmail = sharedPreferences.getString("user_email", "youremail@domain.com")
        val savedPhone = sharedPreferences.getString("user_phone", "+01 234 567 89")
        val notificationsEnabled = sharedPreferences.getBoolean("notifications_enabled", true)
        val isDarkTheme = sharedPreferences.getBoolean("dark_theme", false)

        userName.text = savedName
        userEmail.text = savedEmail
        userPhone.text = savedPhone
        switchNotifications.isChecked = notificationsEnabled
        currentTheme.text = if (isDarkTheme) "Tối" else "Sáng"
    }

    private fun setupClickListeners() {
        // Edit Avatar
        findViewById<ImageView>(R.id.editAvatarIcon).setOnClickListener {
            showToast("Chức năng chỉnh sửa ảnh đại diện")
        }

        // Edit Profile Information
        findViewById<android.widget.LinearLayout>(R.id.btnEditProfile).setOnClickListener {
            showEditProfileDialog()
        }

        // Notifications Switch
        switchNotifications.setOnCheckedChangeListener { _, isChecked ->
            saveNotificationSetting(isChecked)
            showToast(if (isChecked) "Đã bật thông báo" else "Đã tắt thông báo")
        }

        // Medical History
        findViewById<android.widget.LinearLayout>(R.id.btnMedicalHistory).setOnClickListener {
            showToast("Chức năng lịch sử y tế")
        }

        // Theme
        findViewById<android.widget.LinearLayout>(R.id.btnTheme).setOnClickListener {
            showThemeDialog()
        }

        // Help & Support
        findViewById<android.widget.LinearLayout>(R.id.btnHelpSupport).setOnClickListener {
            showToast("Chức năng trợ giúp & hỗ trợ")
        }

        // Privacy Policy
        findViewById<android.widget.LinearLayout>(R.id.btnPrivacyPolicy).setOnClickListener {
            showToast("Chính sách bảo mật")
        }

        // Logout
        findViewById<android.widget.LinearLayout>(R.id.btnLogout).setOnClickListener {
            showLogoutDialog()
        }
    }

    private fun showEditProfileDialog() {
        val dialogBuilder = androidx.appcompat.app.AlertDialog.Builder(this)
        dialogBuilder.setTitle("Chỉnh sửa thông tin")
        
        val dialogView = layoutInflater.inflate(R.layout.dialog_edit_profile, null)
        dialogBuilder.setView(dialogView)
        
        val editName = dialogView.findViewById<android.widget.EditText>(R.id.editName)
        val editEmail = dialogView.findViewById<android.widget.EditText>(R.id.editEmail)
        val editPhone = dialogView.findViewById<android.widget.EditText>(R.id.editPhone)
        
        // Set current values
        editName.setText(userName.text.toString())
        editEmail.setText(userEmail.text.toString())
        editPhone.setText(userPhone.text.toString())
        
        dialogBuilder.setPositiveButton("Lưu") { _, _ ->
            val newName = editName.text.toString().trim()
            val newEmail = editEmail.text.toString().trim()
            val newPhone = editPhone.text.toString().trim()
            
            if (newName.isNotEmpty() && newEmail.isNotEmpty() && newPhone.isNotEmpty()) {
                saveUserData(newName, newEmail, newPhone)
                loadUserData()
                showToast("Đã cập nhật thông tin thành công")
            } else {
                showToast("Vui lòng điền đầy đủ thông tin")
            }
        }
        
        dialogBuilder.setNegativeButton("Hủy", null)
        dialogBuilder.create().show()
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

    private fun saveUserData(name: String, email: String, phone: String) {
        val editor = sharedPreferences.edit()
        editor.putString("user_name", name)
        editor.putString("user_email", email)
        editor.putString("user_phone", phone)
        editor.apply()
    }

    private fun saveNotificationSetting(enabled: Boolean) {
        val editor = sharedPreferences.edit()
        editor.putBoolean("notifications_enabled", enabled)
        editor.apply()
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
        // Clear user data
        val editor = sharedPreferences.edit()
        editor.clear()
        editor.apply()

        // Return to main activity or login screen
        showToast("Đã đăng xuất thành công")
        
        // You can redirect to MainActivity or Login Activity here
        val intent = Intent(this, MainActivity::class.java)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        startActivity(intent)
        finish()
    }

    private fun showToast(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }
}
