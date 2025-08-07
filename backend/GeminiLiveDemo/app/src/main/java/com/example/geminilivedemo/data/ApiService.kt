package com.example.geminilivedemo.data

import retrofit2.Response
import retrofit2.http.*

interface ApiService {
    
    @POST("api/auth/register")
    suspend fun registerUser(@Body request: RegisterRequest): Response<LoginResponse>
    
    @POST("api/auth/login")
    suspend fun loginUser(@Body request: LoginRequest): Response<LoginResponse>
    
    @GET("api/auth/profile/{user_id}")
    suspend fun getUserProfile(@Path("user_id") userId: String): Response<UserResponse>
    
    @POST("api/auth/create-relationship")
    suspend fun createFamilyRelationship(
        @Body request: CreateRelationshipRequest,
        @Query("family_user_id") familyUserId: String
    ): Response<ApiResponse>
    
    @GET("api/auth/family-members/{elderly_user_id}")
    suspend fun getFamilyMembers(@Path("elderly_user_id") elderlyUserId: String): Response<FamilyMembersResponse>
    
    @GET("api/auth/elderly-patients/{family_user_id}")
    suspend fun getElderlyPatients(@Path("family_user_id") familyUserId: String): Response<ElderlyPatientsResponse>
} 