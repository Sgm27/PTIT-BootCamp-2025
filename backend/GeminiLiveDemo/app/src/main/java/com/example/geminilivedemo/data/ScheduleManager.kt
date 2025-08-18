package com.example.geminilivedemo.data

import android.content.Context
import android.util.Log
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import java.io.File
import java.io.FileReader
import java.io.FileWriter
import java.util.*

class ScheduleManager(private val context: Context) {
    
    companion object {
        private const val TAG = "ScheduleManager"
        private const val SCHEDULES_FILE = "schedules.json"
        private const val ELDERLY_SCHEDULES_FILE = "elderly_schedules.json"
    }
    
    private val gson = Gson()
    private val schedulesFile = File(context.filesDir, SCHEDULES_FILE)
    private val elderlySchedulesFile = File(context.filesDir, ELDERLY_SCHEDULES_FILE)
    
    // Save schedule for family member (viewing all schedules)
    fun saveSchedule(schedule: Schedule, familyUserId: String): Boolean {
        return try {
            Log.d(TAG, "saveSchedule called with:")
            Log.d(TAG, "  - Schedule ID: ${schedule.id}")
            Log.d(TAG, "  - Elderly ID: ${schedule.elderlyId}")
            Log.d(TAG, "  - Title: ${schedule.title}")
            Log.d(TAG, "  - Family User ID: $familyUserId")
            
            val schedules = loadAllSchedules().toMutableList()
            Log.d(TAG, "Loaded ${schedules.size} existing schedules")
            
            // Generate unique ID if not exists
            val scheduleWithId = if (schedule.id.isNullOrEmpty()) {
                schedule.copy(id = UUID.randomUUID().toString())
            } else {
                schedule
            }
            
            // Add family user ID to schedule for tracking
            val scheduleWithFamilyInfo = scheduleWithId.copy(createdBy = familyUserId)
            Log.d(TAG, "Schedule with family info:")
            Log.d(TAG, "  - ID: ${scheduleWithFamilyInfo.id}")
            Log.d(TAG, "  - Elderly ID: ${scheduleWithFamilyInfo.elderlyId}")
            Log.d(TAG, "  - Created By: ${scheduleWithFamilyInfo.createdBy}")
            
            schedules.add(scheduleWithFamilyInfo)
            saveAllSchedules(schedules)
            Log.d(TAG, "Saved to main schedules file")
            
            // Also save to elderly-specific file for notifications
            saveElderlySchedule(scheduleWithFamilyInfo)
            Log.d(TAG, "Saved to elderly schedules file")
            
            Log.d(TAG, "Schedule saved successfully: ${scheduleWithFamilyInfo.id} by family user: $familyUserId")
            true
        } catch (e: Exception) {
            Log.e(TAG, "Error saving schedule: ${e.message}", e)
            false
        }
    }
    
    // Load all schedules for family members to view
    fun loadAllSchedules(): List<Schedule> {
        return try {
            if (!schedulesFile.exists()) {
                return emptyList()
            }
            
            val type = object : TypeToken<List<Schedule>>() {}.type
            val schedules: List<Schedule> = gson.fromJson(FileReader(schedulesFile), type) ?: emptyList()
            Log.d(TAG, "Loaded ${schedules.size} schedules")
            schedules
        } catch (e: Exception) {
            Log.e(TAG, "Error loading schedules: ${e.message}", e)
            emptyList()
        }
    }
    
    // Load schedules for specific elderly user
    fun loadElderlySchedules(elderlyId: String): List<Schedule> {
        return try {
            Log.d(TAG, "loadElderlySchedules called for elderly: $elderlyId")
            
            if (!elderlySchedulesFile.exists()) {
                Log.d(TAG, "Elderly schedules file does not exist")
                return emptyList()
            }
            
            val type = object : TypeToken<Map<String, List<Schedule>>>() {}.type
            val allElderlySchedules: Map<String, List<Schedule>> = gson.fromJson(FileReader(elderlySchedulesFile), type) ?: emptyMap()
            
            Log.d(TAG, "All elderly schedules keys: ${allElderlySchedules.keys}")
            
            val schedules = allElderlySchedules[elderlyId] ?: emptyList()
            Log.d(TAG, "Loaded ${schedules.size} schedules for elderly: $elderlyId")
            
            schedules.forEach { schedule ->
                Log.d(TAG, "  - Schedule: ${schedule.title} (ID: ${schedule.id}, CreatedBy: ${schedule.createdBy})")
            }
            
            schedules
        } catch (e: Exception) {
            Log.e(TAG, "Error loading elderly schedules: ${e.message}", e)
            emptyList()
        }
    }
    
    // Get schedules for family member to view (all elderly they care for)
    fun getSchedulesForFamilyMember(familyUserId: String, elderlyIds: List<String>): List<Schedule> {
        Log.d(TAG, "getSchedulesForFamilyMember called with:")
        Log.d(TAG, "  - Family User ID: $familyUserId")
        Log.d(TAG, "  - Elderly IDs: $elderlyIds")
        
        val allSchedules = mutableListOf<Schedule>()
        
        elderlyIds.forEach { elderlyId ->
            Log.d(TAG, "Loading schedules for elderly: $elderlyId")
            val elderlySchedules = loadElderlySchedules(elderlyId)
            Log.d(TAG, "Found ${elderlySchedules.size} total schedules for elderly: $elderlyId")
            
            // Filter schedules created by this family member
            val familySchedules = elderlySchedules.filter { 
                Log.d(TAG, "Checking schedule createdBy: ${it.createdBy} vs familyUserId: $familyUserId")
                it.createdBy == familyUserId 
            }
            Log.d(TAG, "Found ${familySchedules.size} schedules created by family member: $familyUserId")
            
            allSchedules.addAll(familySchedules)
        }
        
        Log.d(TAG, "Total schedules for family member: ${allSchedules.size}")
        
        // Sort by scheduled time
        return allSchedules.sortedBy { it.scheduledAt }
    }
    
    // Update schedule
    fun updateSchedule(scheduleId: String, updatedSchedule: Schedule): Boolean {
        return try {
            val schedules = loadAllSchedules().toMutableList()
            val index = schedules.indexOfFirst { it.id == scheduleId }
            
            if (index != -1) {
                schedules[index] = updatedSchedule.copy(id = scheduleId)
                saveAllSchedules(schedules)
                
                // Update in elderly file too
                updateElderlySchedule(updatedSchedule)
                
                Log.d(TAG, "Schedule updated successfully: $scheduleId")
                true
            } else {
                Log.w(TAG, "Schedule not found for update: $scheduleId")
                false
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error updating schedule: ${e.message}", e)
            false
        }
    }
    
    // Delete schedule
    fun deleteSchedule(scheduleId: String): Boolean {
        return try {
            val schedules = loadAllSchedules().toMutableList()
            val scheduleToDelete = schedules.find { it.id == scheduleId }
            
            if (scheduleToDelete != null) {
                schedules.removeAll { it.id == scheduleId }
                saveAllSchedules(schedules)
                
                // Remove from elderly file too
                removeElderlySchedule(scheduleId, scheduleToDelete.elderlyId)
                
                Log.d(TAG, "Schedule deleted successfully: $scheduleId")
                true
            } else {
                Log.w(TAG, "Schedule not found for deletion: $scheduleId")
                false
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error deleting schedule: ${e.message}", e)
            false
        }
    }
    
    // Mark schedule as complete
    fun markScheduleComplete(scheduleId: String): Boolean {
        return try {
            val schedules = loadAllSchedules().toMutableList()
            val index = schedules.indexOfFirst { it.id == scheduleId }
            
            if (index != -1) {
                val updatedSchedule = schedules[index].copy(isCompleted = true)
                schedules[index] = updatedSchedule
                saveAllSchedules(schedules)
                
                // Update in elderly file too
                updateElderlySchedule(updatedSchedule)
                
                Log.d(TAG, "Schedule marked as complete: $scheduleId")
                true
            } else {
                Log.w(TAG, "Schedule not found for completion: $scheduleId")
                false
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error marking schedule complete: ${e.message}", e)
            false
        }
    }
    
    // Get upcoming schedules for notifications
    fun getUpcomingSchedules(elderlyId: String, limit: Int = 10): List<Schedule> {
        val schedules = loadElderlySchedules(elderlyId)
        val now = System.currentTimeMillis() / 1000
        
        return schedules
            .filter { !it.isCompleted && it.scheduledAt > now }
            .sortedBy { it.scheduledAt }
            .take(limit)
    }
    
    // Private helper methods
    private fun saveAllSchedules(schedules: List<Schedule>) {
        FileWriter(schedulesFile).use { writer ->
            gson.toJson(schedules, writer)
        }
    }
    
    private fun saveElderlySchedule(schedule: Schedule) {
        try {
            Log.d(TAG, "saveElderlySchedule called for schedule: ${schedule.title}")
            Log.d(TAG, "  - Elderly ID: ${schedule.elderlyId}")
            Log.d(TAG, "  - Created By: ${schedule.createdBy}")
            
            val type = object : TypeToken<Map<String, List<Schedule>>>() {}.type
            val allElderlySchedules: MutableMap<String, MutableList<Schedule>> = 
                if (elderlySchedulesFile.exists()) {
                    gson.fromJson(FileReader(elderlySchedulesFile), type) ?: mutableMapOf()
                } else {
                    mutableMapOf()
                }
            
            Log.d(TAG, "Existing elderly schedules keys: ${allElderlySchedules.keys}")
            
            val elderlySchedules = allElderlySchedules.getOrPut(schedule.elderlyId) { mutableListOf() }
            elderlySchedules.add(schedule)
            
            Log.d(TAG, "Added schedule to elderly ${schedule.elderlyId}, total schedules: ${elderlySchedules.size}")
            
            FileWriter(elderlySchedulesFile).use { writer ->
                gson.toJson(allElderlySchedules, writer)
            }
            
            Log.d(TAG, "Saved elderly schedules file successfully")
        } catch (e: Exception) {
            Log.e(TAG, "Error saving elderly schedule: ${e.message}", e)
        }
    }
    
    private fun updateElderlySchedule(updatedSchedule: Schedule) {
        try {
            val type = object : TypeToken<Map<String, List<Schedule>>>() {}.type
            val allElderlySchedules: MutableMap<String, MutableList<Schedule>> = 
                if (elderlySchedulesFile.exists()) {
                    gson.fromJson(FileReader(elderlySchedulesFile), type) ?: mutableMapOf()
                } else {
                    mutableMapOf()
                }
            
            val elderlySchedules = allElderlySchedules[updatedSchedule.elderlyId]
            if (elderlySchedules != null) {
                val index = elderlySchedules.indexOfFirst { it.id == updatedSchedule.id }
                if (index != -1) {
                    elderlySchedules[index] = updatedSchedule
                    
                    FileWriter(elderlySchedulesFile).use { writer ->
                        gson.toJson(allElderlySchedules, writer)
                    }
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error updating elderly schedule: ${e.message}", e)
        }
    }
    
    private fun removeElderlySchedule(scheduleId: String, elderlyId: String) {
        try {
            val type = object : TypeToken<Map<String, List<Schedule>>>() {}.type
            val allElderlySchedules: MutableMap<String, MutableList<Schedule>> = 
                if (elderlySchedulesFile.exists()) {
                    gson.fromJson(FileReader(elderlySchedulesFile), type) ?: mutableMapOf()
                } else {
                    mutableMapOf()
                }
            
            val elderlySchedules = allElderlySchedules[elderlyId]
            if (elderlySchedules != null) {
                elderlySchedules.removeAll { it.id == scheduleId }
                
                FileWriter(elderlySchedulesFile).use { writer ->
                    gson.toJson(allElderlySchedules, writer)
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error removing elderly schedule: ${e.message}", e)
        }
    }
} 