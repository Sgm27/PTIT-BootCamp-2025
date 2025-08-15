package com.example.geminilivedemo.data

import android.content.Context
import android.content.SharedPreferences

class UserPreferences(context: Context) {
    
    private val sharedPreferences: SharedPreferences = 
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    
    companion object {
        private const val PREFS_NAME = "healthcare_ai_prefs"
        private const val KEY_USER_ID = "user_id"
        private const val KEY_SESSION_TOKEN = "session_token"
        private const val KEY_USER_TYPE = "user_type"
        private const val KEY_FULL_NAME = "full_name"
        private const val KEY_EMAIL = "email"
        private const val KEY_PHONE = "phone"
        private const val KEY_IS_LOGGED_IN = "is_logged_in"
        private const val KEY_DATE_OF_BIRTH = "date_of_birth"
        private const val KEY_GENDER = "gender"
        private const val KEY_ADDRESS = "address"
    }
    
    fun saveUserData(loginResponse: LoginResponse) {
        val editor = sharedPreferences.edit()
        
        loginResponse.user?.let { user ->
            editor.putString(KEY_USER_ID, user.userId)
            editor.putString(KEY_USER_TYPE, user.userType)
            editor.putString(KEY_FULL_NAME, user.fullName)
            editor.putString(KEY_EMAIL, user.email)
            editor.putString(KEY_PHONE, user.phone)
            editor.putString(KEY_DATE_OF_BIRTH, user.dateOfBirth)
            editor.putString(KEY_GENDER, user.gender)
            editor.putString(KEY_ADDRESS, user.address)
        }
        
        editor.putString(KEY_SESSION_TOKEN, loginResponse.sessionToken)
        editor.putBoolean(KEY_IS_LOGGED_IN, true)
        editor.apply()
    }
    
    fun getUserId(): String? = sharedPreferences.getString(KEY_USER_ID, null)
    
    fun getSessionToken(): String? = sharedPreferences.getString(KEY_SESSION_TOKEN, null)
    
    fun getUserType(): String? = sharedPreferences.getString(KEY_USER_TYPE, null)
    
    fun getFullName(): String? = sharedPreferences.getString(KEY_FULL_NAME, null)
    
    fun getEmail(): String? = sharedPreferences.getString(KEY_EMAIL, null)
    
    fun getPhone(): String? = sharedPreferences.getString(KEY_PHONE, null)
    
    fun getDateOfBirth(): String? = sharedPreferences.getString(KEY_DATE_OF_BIRTH, null)
    
    fun getGender(): String? = sharedPreferences.getString(KEY_GENDER, null)
    
    fun getAddress(): String? = sharedPreferences.getString(KEY_ADDRESS, null)
    
    fun isLoggedIn(): Boolean = sharedPreferences.getBoolean(KEY_IS_LOGGED_IN, false)
    
    fun isElderlyUser(): Boolean = getUserType() == "elderly"
    
    fun isFamilyMember(): Boolean = getUserType() == "family"
    
    fun clearUserData() {
        val editor = sharedPreferences.edit()
        editor.clear()
        editor.apply()
    }
    
    fun getCurrentUser(): UserResponse? {
        return if (isLoggedIn()) {
            UserResponse(
                userId = getUserId() ?: return null,
                userType = getUserType() ?: return null,
                fullName = getFullName() ?: return null,
                email = getEmail(),
                phone = getPhone(),
                dateOfBirth = getDateOfBirth(),
                gender = getGender(),
                address = getAddress(),
                createdAt = "", // Not stored locally
                isActive = true
            )
        } else {
            null
        }
    }
} 