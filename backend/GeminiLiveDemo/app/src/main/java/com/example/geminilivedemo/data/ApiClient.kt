package com.example.geminilivedemo.data

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import java.util.concurrent.TimeUnit
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import javax.net.ssl.*
import java.security.cert.X509Certificate

class ApiClient {
    
    companion object {
        // Base URL từ ApiConfig - Automatically selects based on environment
        private val BASE_URL = ApiConfig.BASE_URL
        
        private val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }
        
        // Add network interceptor for debugging
        private val networkInterceptor = okhttp3.Interceptor { chain ->
            val originalRequest = chain.request()
            val request = originalRequest.newBuilder()
                .addHeader("Accept", "application/json; charset=utf-8")
                .addHeader("Content-Type", "application/json; charset=utf-8")
                .build()
                
            Log.d("ApiClient", "=== NETWORK REQUEST ===")
            Log.d("ApiClient", "URL: ${request.url}")
            Log.d("ApiClient", "Method: ${request.method}")
            Log.d("ApiClient", "Headers: ${request.headers}")
            
            try {
                val response = chain.proceed(request)
                Log.d("ApiClient", "=== NETWORK RESPONSE ===")
                Log.d("ApiClient", "Code: ${response.code}")
                Log.d("ApiClient", "Message: ${response.message}")
                Log.d("ApiClient", "Headers: ${response.headers}")
                
                // Log response body for debugging
                val responseBody = response.body
                if (responseBody != null) {
                    val contentType = responseBody.contentType()
                    val charset = contentType?.charset(Charsets.UTF_8) ?: Charsets.UTF_8
                    Log.d("ApiClient", "Response charset: $charset")
                    Log.d("ApiClient", "Response content type: $contentType")
                }
                
                response
            } catch (e: Exception) {
                Log.e("ApiClient", "=== NETWORK ERROR ===", e)
                Log.e("ApiClient", "Error type: ${e.javaClass.simpleName}")
                Log.e("ApiClient", "Error message: ${e.message}")
                throw e
            }
        }
        
        // Create a trust manager that accepts all certificates (for development only)
        private val trustAllCerts = arrayOf<TrustManager>(object : X509TrustManager {
            override fun checkClientTrusted(chain: Array<out X509Certificate>?, authType: String?) {}
            override fun checkServerTrusted(chain: Array<out X509Certificate>?, authType: String?) {}
            override fun getAcceptedIssuers(): Array<X509Certificate> = arrayOf()
        })
        
        private val okHttpClient = OkHttpClient.Builder()
            .addInterceptor(loggingInterceptor)
            .addInterceptor(networkInterceptor) // Add the network interceptor
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .apply {
                // For development/testing - bypass SSL verification
                try {
                    val sslContext = SSLContext.getInstance("SSL")
                    sslContext.init(null, trustAllCerts, java.security.SecureRandom())
                    sslSocketFactory(sslContext.socketFactory, trustAllCerts[0] as X509TrustManager)
                    hostnameVerifier { _, _ -> true }
                    Log.d("ApiClient", "SSL verification bypassed for development")
                } catch (e: Exception) {
                    Log.e("ApiClient", "Error setting up SSL bypass", e)
                }
            }
            .build()
        
        private val retrofit = Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create(
                com.google.gson.GsonBuilder()
                    .setLenient()
                    .disableHtmlEscaping()
                    .create()
            ))
            .build()
        
        val apiService: ApiService = retrofit.create(ApiService::class.java)
        
        // Singleton instance for backward compatibility
        val instance: ApiClient by lazy { ApiClient() }
        
        init {
            // Log environment information
            Log.i("ApiClient", "=== API Configuration ===")
            Log.i("ApiClient", ApiConfig.getEnvironmentInfo())
            Log.i("ApiClient", "========================")
        }
    }
    
    // ====== CONVERSATION API METHODS ======
    
    suspend fun getUserConversations(userId: String, limit: Int = 50, offset: Int = 0): Map<String, Any>? {
        return withContext(Dispatchers.IO) {
            try {
                Log.d("ApiClient", "=== getUserConversations() START ===")
                Log.d("ApiClient", "User ID: '$userId'")
                Log.d("ApiClient", "Limit: $limit, Offset: $offset")
                Log.d("ApiClient", "Base URL: $BASE_URL")
                Log.d("ApiClient", "Full URL: ${BASE_URL}api/conversations/$userId?limit=$limit&offset=$offset")
                
                val response = Companion.apiService.getUserConversations(userId, limit, offset)
                
                Log.d("ApiClient", "=== HTTP RESPONSE RECEIVED ===")
                Log.d("ApiClient", "Response code: ${response.code()}")
                Log.d("ApiClient", "Response message: ${response.message()}")
                Log.d("ApiClient", "Is successful: ${response.isSuccessful}")
                
                if (response.isSuccessful) {
                    val body = response.body()
                    Log.d("ApiClient", "Response body is null: ${body == null}")
                    if (body != null) {
                        Log.d("ApiClient", "Response body keys: ${body.keys}")
                        Log.d("ApiClient", "Response body: $body")
                    }
                    body
                } else {
                    val errorBody = response.errorBody()?.string()
                    Log.e("ApiClient", "Error getting conversations - Code: ${response.code()}")
                    Log.e("ApiClient", "Error body: $errorBody")
                    Log.e("ApiClient", "Error headers: ${response.headers()}")
                    null
                }
            } catch (e: Exception) {
                Log.e("ApiClient", "=== EXCEPTION IN getUserConversations ===", e)
                Log.e("ApiClient", "Exception type: ${e.javaClass.simpleName}")
                Log.e("ApiClient", "Exception message: ${e.message}")
                Log.e("ApiClient", "Exception cause: ${e.cause}")
                null
            }
        }
    }
    
    suspend fun getConversationDetail(userId: String, conversationId: String): Map<String, Any>? {
        return withContext(Dispatchers.IO) {
            try {
                val response = Companion.apiService.getConversationDetail(userId, conversationId)
                if (response.isSuccessful) {
                    response.body()
                } else {
                    Log.e("ApiClient", "Error getting conversation detail: ${response.errorBody()?.string()}")
                    null
                }
            } catch (e: Exception) {
                Log.e("ApiClient", "Exception getting conversation detail", e)
                null
            }
        }
    }
    
    suspend fun searchConversations(userId: String, query: String, limit: Int = 20): Map<String, Any>? {
        return withContext(Dispatchers.IO) {
            try {
                val response = Companion.apiService.searchConversations(userId, query, limit)
                if (response.isSuccessful) {
                    response.body()
                } else {
                    Log.e("ApiClient", "Error searching conversations: ${response.errorBody()?.string()}")
                    null
                }
            } catch (e: Exception) {
                Log.e("ApiClient", "Exception searching conversations", e)
                null
            }
        }
    }
    
    // ====== MEMOIR API METHODS ======
    
    suspend fun getUserMemoirs(userId: String, limit: Int = 50, offset: Int = 0, orderBy: String = "extracted_at"): Map<String, Any>? {
        return withContext(Dispatchers.IO) {
            try {
                val response = Companion.apiService.getUserMemoirs(userId, limit, offset, orderBy)
                if (response.isSuccessful) {
                    response.body()
                } else {
                    Log.e("ApiClient", "Error getting memoirs: ${response.errorBody()?.string()}")
                    null
                }
            } catch (e: Exception) {
                Log.e("ApiClient", "Exception getting memoirs", e)
                null
            }
        }
    }
    
    suspend fun getMemoirDetail(userId: String, memoirId: String): Map<String, Any>? {
        return withContext(Dispatchers.IO) {
            try {
                val response = Companion.apiService.getMemoirDetail(userId, memoirId)
                if (response.isSuccessful) {
                    response.body()
                } else {
                    Log.e("ApiClient", "Error getting memoir detail: ${response.errorBody()?.string()}")
                    null
                }
            } catch (e: Exception) {
                Log.e("ApiClient", "Exception getting memoir detail", e)
                null
            }
        }
    }
    
    suspend fun searchMemoirs(userId: String, searchRequest: Map<String, Any>): Map<String, Any>? {
        return withContext(Dispatchers.IO) {
            try {
                val response = Companion.apiService.searchMemoirs(userId, searchRequest)
                if (response.isSuccessful) {
                    response.body()
                } else {
                    Log.e("ApiClient", "Error searching memoirs: ${response.errorBody()?.string()}")
                    null
                }
            } catch (e: Exception) {
                Log.e("ApiClient", "Exception searching memoirs", e)
                null
            }
        }
    }
    
    suspend fun getMemoirTimeline(userId: String): Map<String, Any>? {
        return withContext(Dispatchers.IO) {
            try {
                val response = Companion.apiService.getMemoirTimeline(userId)
                if (response.isSuccessful) {
                    response.body()
                } else {
                    Log.e("ApiClient", "Error getting memoir timeline: ${response.errorBody()?.string()}")
                    null
                }
            } catch (e: Exception) {
                Log.e("ApiClient", "Exception getting memoir timeline", e)
                null
            }
        }
    }
    
    suspend fun exportMemoirs(userId: String, formatType: String = "text"): Map<String, Any>? {
        return withContext(Dispatchers.IO) {
            try {
                val exportRequest = mapOf("format_type" to formatType, "user_id" to userId)
                val response = Companion.apiService.exportMemoirs(userId, exportRequest)
                if (response.isSuccessful) {
                    response.body()
                } else {
                    Log.e("ApiClient", "Error exporting memoirs: ${response.errorBody()?.string()}")
                    null
                }
            } catch (e: Exception) {
                Log.e("ApiClient", "Exception exporting memoirs", e)
                null
            }
        }
    }
    
    suspend fun getUserStats(userId: String): Map<String, Any>? {
        return withContext(Dispatchers.IO) {
            try {
                val response = Companion.apiService.getUserStats(userId)
                if (response.isSuccessful) {
                    response.body()
                } else {
                    Log.e("ApiClient", "Error getting user stats: ${response.errorBody()?.string()}")
                    null
                }
            } catch (e: Exception) {
                Log.e("ApiClient", "Exception getting user stats", e)
                null
            }
        }
    }
} 