package com.example.geminilivedemo.data

import retrofit2.Response
import retrofit2.http.*

interface ApiService {
    
    // ====== AUTHENTICATION ENDPOINTS ======
    
    @POST("api/auth/register")
    suspend fun registerUser(@Body request: RegisterRequest): Response<LoginResponse>
    
    @POST("api/auth/login")
    suspend fun loginUser(@Body request: LoginRequest): Response<LoginResponse>
    
    @GET("api/auth/profile/{user_id}")
    suspend fun getUserProfile(@Path("user_id") userId: String): Response<UserResponse>
    
    @PUT("api/auth/profile/{user_id}")
    suspend fun updateUserProfile(
        @Path("user_id") userId: String,
        @Body request: ProfileUpdateRequest
    ): Response<ProfileUpdateResponse>
    
    @POST("api/auth/create-relationship")
    suspend fun createFamilyRelationship(
        @Body request: CreateRelationshipRequest,
        @Query("family_user_id") familyUserId: String
    ): Response<ApiResponse>
    
    @GET("api/auth/family-members/{elderly_user_id}")
    suspend fun getFamilyMembers(@Path("elderly_user_id") elderlyUserId: String): Response<FamilyMembersResponse>
    
    @GET("api/auth/elderly-patients/{family_user_id}")
    suspend fun getElderlyPatients(@Path("family_user_id") familyUserId: String): Response<ElderlyPatientsResponse>
    
    // ====== CONVERSATION ENDPOINTS ======
    
    @GET("api/conversations/{user_id}")
    suspend fun getUserConversations(
        @Path("user_id") userId: String,
        @Query("limit") limit: Int = 50,
        @Query("offset") offset: Int = 0
    ): Response<Map<String, Any>>
    
    @GET("api/conversations/{user_id}/{conversation_id}")
    suspend fun getConversationDetail(
        @Path("user_id") userId: String,
        @Path("conversation_id") conversationId: String
    ): Response<Map<String, Any>>
    
    @GET("api/conversations/{user_id}/search")
    suspend fun searchConversations(
        @Path("user_id") userId: String,
        @Query("query") query: String,
        @Query("limit") limit: Int = 20
    ): Response<Map<String, Any>>
    
    @POST("api/conversations")
    suspend fun createConversation(
        @Body request: Map<String, Any>
    ): Response<Map<String, Any>>
    
    @POST("api/conversations/messages")
    suspend fun addMessageToConversation(
        @Body request: Map<String, Any>
    ): Response<Map<String, Any>>
    
    // ====== MEMOIR ENDPOINTS ======
    
    @GET("api/memoirs/{user_id}")
    suspend fun getUserMemoirs(
        @Path("user_id") userId: String,
        @Query("limit") limit: Int = 50,
        @Query("offset") offset: Int = 0,
        @Query("order_by") orderBy: String = "extracted_at"
    ): Response<Map<String, Any>>
    
    @GET("api/memoirs/{user_id}/{memoir_id}")
    suspend fun getMemoirDetail(
        @Path("user_id") userId: String,
        @Path("memoir_id") memoirId: String
    ): Response<Map<String, Any>>
    
    @POST("api/memoirs/{user_id}/search")
    suspend fun searchMemoirs(
        @Path("user_id") userId: String,
        @Body searchRequest: Map<String, Any>
    ): Response<Map<String, Any>>
    
    @GET("api/memoirs/{user_id}/timeline")
    suspend fun getMemoirTimeline(
        @Path("user_id") userId: String
    ): Response<Map<String, Any>>
    
    @POST("api/memoirs/{user_id}/export")
    suspend fun exportMemoirs(
        @Path("user_id") userId: String,
        @Body exportRequest: Map<String, Any>
    ): Response<Map<String, Any>>
    
    // ====== USER STATS ENDPOINT ======
    
    @GET("api/users/{user_id}/stats")
    suspend fun getUserStats(
        @Path("user_id") userId: String
    ): Response<Map<String, Any>>
    
    // ====== FAMILY NOTIFICATION ENDPOINTS ======
    
    @GET("api/family/elderly-list")
    suspend fun getElderlyList(): Response<Map<String, Any>>
    
    @POST("api/family/send-notification")
    suspend fun sendFamilyNotification(@Body notificationData: String): Response<Map<String, Any>>
    
    // ====== FAMILY MEMBERS & REMINDERS ENDPOINTS ======
    
    @GET("api/family/members")
    suspend fun getFamilyMembers(): Response<Map<String, Any>>
    
    @GET("api/family/reminders")
    suspend fun getUserReminders(): Response<Map<String, Any>>
    
    // ====== SCHEDULE MANAGEMENT ENDPOINTS ======
    
    @POST("api/schedules")
    suspend fun createSchedule(@Body scheduleData: Map<String, Any>): Response<Map<String, Any>>
    
    @GET("api/schedules")
    suspend fun getUserSchedules(@Query("user_id") userId: String? = null): Response<Map<String, Any>>
    
    @PUT("api/schedules/{schedule_id}")
    suspend fun updateSchedule(
        @Path("schedule_id") scheduleId: String,
        @Body updateData: Map<String, Any>
    ): Response<Map<String, Any>>
    
    @DELETE("api/schedules/{schedule_id}")
    suspend fun deleteSchedule(@Path("schedule_id") scheduleId: String): Response<Map<String, Any>>
    
    @POST("api/schedules/{schedule_id}/complete")
    suspend fun markScheduleComplete(@Path("schedule_id") scheduleId: String): Response<Map<String, Any>>
} 