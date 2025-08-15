package com.example.geminilivedemo.data

/**
 * Sealed class for API operation results
 */
sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val exception: Throwable) : ApiResult<Nothing>()
    
    val isSuccess: Boolean
        get() = this is Success
    
    val isError: Boolean
        get() = this is Error
    
    fun getOrNull(): T? = when (this) {
        is Success -> data
        is Error -> null
    }
    
    fun exceptionOrNull(): Throwable? = when (this) {
        is Success -> null
        is Error -> exception
    }
    
    companion object {
        fun <T> success(data: T): ApiResult<T> = Success(data)
        fun failure(exception: Throwable): ApiResult<Nothing> = Error(exception)
    }
} 