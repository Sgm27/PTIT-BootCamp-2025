package com.example.geminilivedemo.data

import android.content.Context
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class ProfileRepository(private val context: Context) {
    
    private val apiService = ApiClient.apiService
    
    companion object {
        private const val TAG = "ProfileRepository"
    }
    
    /**
     * Load user profile from server only - no caching
     */
    suspend fun loadProfileFromServer(userId: String): ApiResult<UserResponse> {
        return withContext(Dispatchers.IO) {
            try {
                Log.d(TAG, "Loading profile from server for user: $userId")
                val response = apiService.getUserProfile(userId)
                if (response.isSuccessful && response.body() != null) {
                    val userProfile = response.body()!!
                    Log.d(TAG, "Profile loaded successfully from server")
                    ApiResult.success(userProfile)
                } else {
                    Log.e(TAG, "Failed to load profile from server: ${response.code()}")
                    ApiResult.failure(RuntimeException("Failed to load profile: ${response.code()} - ${response.message()}"))
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error loading profile from server", e)
                ApiResult.failure(e)
            }
        }
    }
    
    /**
     * Update profile on server only - no local caching
     */
    suspend fun updateProfileOnServer(
        userId: String,
        fullName: String,
        email: String,
        phone: String,
        address: String,
        dateOfBirth: String? = null,
        gender: String? = null
    ): ApiResult<ProfileUpdateResponse> {
        return withContext(Dispatchers.IO) {
            try {
                Log.d(TAG, "Updating profile on server for user: $userId")
                val request = ProfileUpdateRequest(
                    fullName = fullName,
                    email = email,
                    phone = phone,
                    address = address,
                    dateOfBirth = dateOfBirth,
                    gender = gender
                )
                
                val response = apiService.updateUserProfile(userId, request)
                if (response.isSuccessful && response.body() != null) {
                    val updateResponse = response.body()!!
                    
                    if (updateResponse.success && updateResponse.user != null) {
                        Log.d(TAG, "Profile updated successfully on server")
                        ApiResult.success(updateResponse)
                    } else {
                        Log.e(TAG, "Server returned error: ${updateResponse.message}")
                        ApiResult.failure(RuntimeException(updateResponse.message))
                    }
                } else {
                    Log.e(TAG, "Failed to update profile on server: ${response.code()}")
                    ApiResult.failure(RuntimeException("Failed to update profile: ${response.code()} - ${response.message()}"))
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error updating profile on server", e)
                ApiResult.failure(e)
            }
        }
    }
    
    /**
     * Check server connectivity
     */
    suspend fun checkServerConnection(): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                // Try to make a simple request to check connectivity
                val response = apiService.getUserProfile("test")
                // Even if user doesn't exist, if we get a proper HTTP response, server is reachable
                response.code() in 200..499
            } catch (e: Exception) {
                Log.e(TAG, "Server connection check failed", e)
                false
            }
        }
    }
} 