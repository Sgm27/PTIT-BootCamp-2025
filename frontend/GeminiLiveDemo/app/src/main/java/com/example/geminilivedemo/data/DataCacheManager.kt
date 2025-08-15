package com.example.geminilivedemo.data

import android.content.Context
import android.content.SharedPreferences
import android.util.Log
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import java.util.concurrent.ConcurrentHashMap
// Sử dụng synchronized thay vì Mutex để tránh dependency issues

/**
 * DataCacheManager - Quản lý cache data cho các activity chính
 * Sử dụng cả memory cache và disk cache để tối ưu performance
 */
class DataCacheManager private constructor(context: Context) {
    
    companion object {
        private const val PREFS_NAME = "DataCachePrefs"
        private const val CACHE_EXPIRY_TIME = 5 * 60 * 1000L // 5 phút
        private const val MAX_MEMORY_CACHE_SIZE = 100 // Số lượng item tối đa trong memory cache
        
        @Volatile
        private var INSTANCE: DataCacheManager? = null
        
        fun getInstance(context: Context): DataCacheManager {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: DataCacheManager(context.applicationContext).also { INSTANCE = it }
            }
        }
    }
    
    private val sharedPreferences: SharedPreferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private val gson = Gson()
    
    // Memory cache với ConcurrentHashMap để thread-safe
    private val memoryCache = ConcurrentHashMap<String, CacheItem<*>>()
    // Sử dụng synchronized thay vì Mutex
    
    /**
     * Cache item với timestamp và expiry
     */
    data class CacheItem<T>(
        val data: T,
        val timestamp: Long,
        val expiryTime: Long = CACHE_EXPIRY_TIME
    ) {
        fun isExpired(): Boolean = System.currentTimeMillis() - timestamp > expiryTime
        fun getAge(): Long = System.currentTimeMillis() - timestamp
    }
    
    /**
     * Cache conversations cho user
     */
    fun cacheConversations(userId: String, conversations: List<Map<String, Any>>) {
        synchronized(this) {
            try {
                val cacheKey = "conversations_$userId"
                val cacheItem = CacheItem(conversations, System.currentTimeMillis())
                
                // Cache vào memory
                memoryCache[cacheKey] = cacheItem
                
                // Cache vào disk
                val jsonData = gson.toJson(conversations)
                sharedPreferences.edit()
                    .putString(cacheKey, jsonData)
                    .putLong("${cacheKey}_timestamp", cacheItem.timestamp)
                    .apply()
                
                Log.d("DataCache", "Cached ${conversations.size} conversations for user $userId")
                
                // Cleanup memory cache nếu quá lớn
                cleanupMemoryCache()
                
            } catch (e: Exception) {
                Log.e("DataCache", "Error caching conversations", e)
            }
        }
    }
    
    /**
     * Lấy conversations từ cache
     */
    fun getCachedConversations(userId: String): List<Map<String, Any>>? {
        return synchronized(this) {
            try {
                val cacheKey = "conversations_$userId"
                
                // Kiểm tra memory cache trước
                val memoryItem = memoryCache[cacheKey] as? CacheItem<List<Map<String, Any>>>
                if (memoryItem != null && !memoryItem.isExpired()) {
                    Log.d("DataCache", "Found conversations in memory cache for user $userId")
                    return@synchronized memoryItem.data
                }
                
                // Kiểm tra disk cache
                val jsonData = sharedPreferences.getString(cacheKey, null)
                val timestamp = sharedPreferences.getLong("${cacheKey}_timestamp", 0L)
                
                if (jsonData != null && timestamp > 0) {
                    val diskItem = CacheItem<List<Map<String, Any>>>(
                        data = gson.fromJson(jsonData, object : TypeToken<List<Map<String, Any>>>() {}.type),
                        timestamp = timestamp
                    )
                    
                    if (!diskItem.isExpired()) {
                        // Restore vào memory cache
                        memoryCache[cacheKey] = diskItem
                        Log.d("DataCache", "Restored conversations from disk cache for user $userId")
                        return@synchronized diskItem.data
                    } else {
                        // Xóa cache hết hạn
                        clearCacheForUser(userId, "conversations")
                    }
                }
                
                null
                
            } catch (e: Exception) {
                Log.e("DataCache", "Error getting cached conversations", e)
                null
            }
        }
    }
    
    /**
     * Cache memoirs cho user
     */
    fun cacheMemoirs(userId: String, memoirs: List<Map<String, Any>>) {
        synchronized(this) {
            try {
                val cacheKey = "memoirs_$userId"
                val cacheItem = CacheItem(memoirs, System.currentTimeMillis())
                
                // Cache vào memory
                memoryCache[cacheKey] = cacheItem
                
                // Cache vào disk
                val jsonData = gson.toJson(memoirs)
                sharedPreferences.edit()
                    .putString(cacheKey, jsonData)
                    .putLong("${cacheKey}_timestamp", cacheItem.timestamp)
                    .apply()
                
                Log.d("DataCache", "Cached ${memoirs.size} memoirs for user $userId")
                
                // Cleanup memory cache nếu quá lớn
                cleanupMemoryCache()
                
            } catch (e: Exception) {
                Log.e("DataCache", "Error caching memoirs", e)
            }
        }
    }
    
    /**
     * Lấy memoirs từ cache
     */
    fun getCachedMemoirs(userId: String): List<Map<String, Any>>? {
        return synchronized(this) {
            try {
                val cacheKey = "memoirs_$userId"
                
                // Kiểm tra memory cache trước
                val memoryItem = memoryCache[cacheKey] as? CacheItem<List<Map<String, Any>>>
                if (memoryItem != null && !memoryItem.isExpired()) {
                    Log.d("DataCache", "Found memoirs in memory cache for user $userId")
                    return@synchronized memoryItem.data
                }
                
                // Kiểm tra disk cache
                val jsonData = sharedPreferences.getString(cacheKey, null)
                val timestamp = sharedPreferences.getLong("${cacheKey}_timestamp", 0L)
                
                if (jsonData != null && timestamp > 0) {
                    val diskItem = CacheItem<List<Map<String, Any>>>(
                        data = gson.fromJson(jsonData, object : TypeToken<List<Map<String, Any>>>() {}.type),
                        timestamp = timestamp
                    )
                    
                    if (!diskItem.isExpired()) {
                        // Restore vào memory cache
                        memoryCache[cacheKey] = diskItem
                        Log.d("DataCache", "Restored memoirs from disk cache for user $userId")
                        return@synchronized diskItem.data
                    } else {
                        // Xóa cache hết hạn
                        clearCacheForUser(userId, "memoirs")
                    }
                }
                
                null
                
            } catch (e: Exception) {
                Log.e("DataCache", "Error getting cached memoirs", e)
                null
            }
        }
    }
    
    /**
     * Cache messages cho conversation
     */
    fun cacheConversationMessages(conversationId: String, messages: List<Map<String, Any>>) {
        synchronized(this) {
            try {
                val cacheKey = "messages_$conversationId"
                val cacheItem = CacheItem(messages, System.currentTimeMillis())
                
                // Cache vào memory
                memoryCache[cacheKey] = cacheItem
                
                // Cache vào disk
                val jsonData = gson.toJson(messages)
                sharedPreferences.edit()
                    .putString(cacheKey, jsonData)
                    .putLong("${cacheKey}_timestamp", cacheItem.timestamp)
                    .apply()
                
                Log.d("DataCache", "Cached ${messages.size} messages for conversation $conversationId")
                
                // Cleanup memory cache nếu quá lớn
                cleanupMemoryCache()
                
            } catch (e: Exception) {
                Log.e("DataCache", "Error caching messages", e)
            }
        }
    }
    
    /**
     * Lấy messages từ cache
     */
    fun getCachedConversationMessages(conversationId: String): List<Map<String, Any>>? {
        return synchronized(this) {
            try {
                val cacheKey = "messages_$conversationId"
                
                // Kiểm tra memory cache trước
                val memoryItem = memoryCache[cacheKey] as? CacheItem<List<Map<String, Any>>>
                if (memoryItem != null && !memoryItem.isExpired()) {
                    Log.d("DataCache", "Found messages in memory cache for conversation $conversationId")
                    return@synchronized memoryItem.data
                }
                
                // Kiểm tra disk cache
                val jsonData = sharedPreferences.getString(cacheKey, null)
                val timestamp = sharedPreferences.getLong("${cacheKey}_timestamp", 0L)
                
                if (jsonData != null && timestamp > 0) {
                    val diskItem = CacheItem<List<Map<String, Any>>>(
                        data = gson.fromJson(jsonData, object : TypeToken<List<Map<String, Any>>>() {}.type),
                        timestamp = timestamp
                    )
                    
                    if (!diskItem.isExpired()) {
                        // Restore vào memory cache
                        memoryCache[cacheKey] = diskItem
                        Log.d("DataCache", "Restored messages from disk cache for conversation $conversationId")
                        return@synchronized diskItem.data
                    } else {
                        // Xóa cache hết hạn
                        clearCacheForUser(conversationId, "messages")
                    }
                }
                
                null
                
            } catch (e: Exception) {
                Log.e("DataCache", "Error getting cached messages", e)
                null
            }
        }
    }
    
    /**
     * Xóa cache cho user cụ thể
     */
    fun clearCacheForUser(userId: String, dataType: String? = null) {
        synchronized(this) {
            try {
                if (dataType == null) {
                    // Xóa tất cả cache của user
                    val keysToRemove = memoryCache.keys.filter { it.startsWith("${dataType}_$userId") }
                    keysToRemove.forEach { memoryCache.remove(it) }
                    
                    // Xóa disk cache
                    val editor = sharedPreferences.edit()
                    sharedPreferences.all.keys.filter { it.startsWith("${dataType}_$userId") }.forEach { key ->
                        editor.remove(key)
                        editor.remove("${key}_timestamp")
                    }
                    editor.apply()
                    
                    Log.d("DataCache", "Cleared all cache for user $userId")
                } else {
                    // Xóa cache cụ thể
                    val cacheKey = "${dataType}_$userId"
                    memoryCache.remove(cacheKey)
                    
                    sharedPreferences.edit()
                        .remove(cacheKey)
                        .remove("${cacheKey}_timestamp")
                        .apply()
                    
                    Log.d("DataCache", "Cleared $dataType cache for user $userId")
                }
            } catch (e: Exception) {
                Log.e("DataCache", "Error clearing cache for user $userId", e)
            }
        }
    }
    
    /**
     * Xóa tất cả cache
     */
    fun clearAllCache() {
        synchronized(this) {
            try {
                memoryCache.clear()
                sharedPreferences.edit().clear().apply()
                Log.d("DataCache", "Cleared all cache")
            } catch (e: Exception) {
                Log.e("DataCache", "Error clearing all cache", e)
            }
        }
    }
    
    /**
     * Cleanup memory cache nếu quá lớn
     */
    private fun cleanupMemoryCache() {
        if (memoryCache.size > MAX_MEMORY_CACHE_SIZE) {
            // Xóa các item cũ nhất
            val sortedItems = memoryCache.entries.sortedBy { it.value.timestamp }
            val itemsToRemove = sortedItems.take(memoryCache.size - MAX_MEMORY_CACHE_SIZE)
            
            itemsToRemove.forEach { (key, _) ->
                memoryCache.remove(key)
            }
            
            Log.d("DataCache", "Cleaned up ${itemsToRemove.size} old cache items")
        }
    }
    
    /**
     * Lấy thông tin cache status
     */
    fun getCacheStatus(): Map<String, Any> {
        return mapOf(
            "memory_cache_size" to memoryCache.size,
            "max_memory_cache_size" to MAX_MEMORY_CACHE_SIZE,
            "cache_expiry_time" to CACHE_EXPIRY_TIME,
            "memory_cache_keys" to memoryCache.keys.toList()
        )
    }
} 