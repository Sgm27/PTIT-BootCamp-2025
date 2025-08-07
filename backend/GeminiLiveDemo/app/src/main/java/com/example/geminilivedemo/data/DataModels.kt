package com.example.geminilivedemo.data

import com.google.gson.annotations.SerializedName

// Enums
enum class UserType {
    @SerializedName("elderly")
    ELDERLY,
    @SerializedName("family")
    FAMILY
}

enum class RelationshipType {
    @SerializedName("child")
    CHILD,
    @SerializedName("grandchild")
    GRANDCHILD,
    @SerializedName("spouse")
    SPOUSE,
    @SerializedName("sibling")
    SIBLING,
    @SerializedName("relative")
    RELATIVE,
    @SerializedName("caregiver")
    CAREGIVER
}

// Request Models
data class RegisterRequest(
    @SerializedName("user_type")
    val userType: UserType,
    @SerializedName("full_name")
    val fullName: String,
    @SerializedName("email")
    val email: String?,
    @SerializedName("phone")
    val phone: String?,
    @SerializedName("password")
    val password: String,
    @SerializedName("date_of_birth")
    val dateOfBirth: String?, // Format: YYYY-MM-DD
    @SerializedName("gender")
    val gender: String?,
    @SerializedName("address")
    val address: String?
)

data class LoginRequest(
    @SerializedName("identifier")
    val identifier: String, // email or phone
    @SerializedName("password")
    val password: String
)

data class CreateRelationshipRequest(
    @SerializedName("elderly_user_identifier")
    val elderlyUserIdentifier: String,
    @SerializedName("relationship_type")
    val relationshipType: RelationshipType,
    @SerializedName("permissions")
    val permissions: Map<String, Boolean>? = null
)

// Response Models
data class UserResponse(
    @SerializedName("user_id")
    val userId: String,
    @SerializedName("user_type")
    val userType: String,
    @SerializedName("full_name")
    val fullName: String,
    @SerializedName("email")
    val email: String?,
    @SerializedName("phone")
    val phone: String?,
    @SerializedName("date_of_birth")
    val dateOfBirth: String?,
    @SerializedName("gender")
    val gender: String?,
    @SerializedName("address")
    val address: String?,
    @SerializedName("created_at")
    val createdAt: String,
    @SerializedName("is_active")
    val isActive: Boolean
)

data class LoginResponse(
    @SerializedName("success")
    val success: Boolean,
    @SerializedName("message")
    val message: String,
    @SerializedName("user")
    val user: UserResponse?,
    @SerializedName("session_token")
    val sessionToken: String?
)

data class ApiResponse(
    @SerializedName("success")
    val success: Boolean,
    @SerializedName("message")
    val message: String
)

data class FamilyMember(
    @SerializedName("user_id")
    val userId: String,
    @SerializedName("full_name")
    val fullName: String,
    @SerializedName("email")
    val email: String?,
    @SerializedName("phone")
    val phone: String?,
    @SerializedName("relationship_type")
    val relationshipType: String,
    @SerializedName("permissions")
    val permissions: Map<String, Boolean>,
    @SerializedName("is_primary_caregiver")
    val isPrimaryCaregiver: Boolean,
    @SerializedName("occupation")
    val occupation: String?
)

data class FamilyMembersResponse(
    @SerializedName("family_members")
    val familyMembers: List<FamilyMember>
)

data class ElderlyPatient(
    @SerializedName("user_id")
    val userId: String,
    @SerializedName("full_name")
    val fullName: String,
    @SerializedName("email")
    val email: String?,
    @SerializedName("phone")
    val phone: String?,
    @SerializedName("relationship_type")
    val relationshipType: String,
    @SerializedName("date_of_birth")
    val dateOfBirth: String?,
    @SerializedName("permissions")
    val permissions: Map<String, Boolean>,
    @SerializedName("medical_conditions")
    val medicalConditions: List<String>?,
    @SerializedName("emergency_contact")
    val emergencyContact: String?
)

data class ElderlyPatientsResponse(
    @SerializedName("elderly_patients")
    val elderlyPatients: List<ElderlyPatient>
) 