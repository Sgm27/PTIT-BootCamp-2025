package com.example.geminilivedemo

import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.geminilivedemo.adapters.ScheduleAdapter
import com.example.geminilivedemo.data.Schedule
import com.example.geminilivedemo.data.ScheduleManager
import com.google.android.material.floatingactionbutton.FloatingActionButton
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.text.SimpleDateFormat
import java.util.*

class ScheduleListActivity : AppCompatActivity() {
    
    private lateinit var scheduleRecyclerView: RecyclerView
    private lateinit var emptyStateText: TextView
    private lateinit var addScheduleFab: FloatingActionButton
    private lateinit var scheduleAdapter: ScheduleAdapter
    private lateinit var scheduleManager: ScheduleManager
    
    companion object {
        private const val TAG = "ScheduleListActivity"
        const val EXTRA_ELDERLY_IDS = "elderly_ids"
        const val EXTRA_ELDERLY_NAMES = "elderly_names"
        const val EXTRA_FAMILY_USER_ID = "family_user_id"
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_schedule_list)
        
        initializeViews()
        setupRecyclerView()
        loadSchedules()
    }
    
    private fun initializeViews() {
        scheduleRecyclerView = findViewById(R.id.scheduleRecyclerView)
        emptyStateText = findViewById(R.id.emptyStateText)
        addScheduleFab = findViewById(R.id.addScheduleFab)
        
        scheduleManager = ScheduleManager(this)
        
        addScheduleFab.setOnClickListener {
            // Navigate to create schedule activity
            // For now, we'll just show a message
            showCreateScheduleDialog()
        }
    }
    
    private fun setupRecyclerView() {
        scheduleAdapter = ScheduleAdapter(
            onScheduleClick = { schedule -> onScheduleClick(schedule) },
            onScheduleComplete = { schedule -> onScheduleComplete(schedule) },
            onScheduleDelete = { schedule -> onScheduleDelete(schedule) }
        )
        
        scheduleRecyclerView.apply {
            layoutManager = LinearLayoutManager(this@ScheduleListActivity)
            adapter = scheduleAdapter
        }
    }
    
    private fun loadSchedules() {
        CoroutineScope(Dispatchers.Main).launch {
            try {
                val elderlyIds = intent.getStringArrayListExtra(EXTRA_ELDERLY_IDS) ?: arrayListOf()
                val familyUserId = intent.getStringExtra(EXTRA_FAMILY_USER_ID) ?: ""
                
                if (elderlyIds.isEmpty()) {
                    showEmptyState("Không có người già nào được kết nối")
                    return@launch
                }
                
                if (familyUserId.isEmpty()) {
                    showEmptyState("Không tìm thấy thông tin người dùng")
                    return@launch
                }
                
                val schedules = withContext(Dispatchers.IO) {
                    scheduleManager.getSchedulesForFamilyMember(familyUserId, elderlyIds)
                }
                
                if (schedules.isEmpty()) {
                    showEmptyState("Chưa có lịch trình nào được tạo")
                } else {
                    showSchedules(schedules)
                }
                
            } catch (e: Exception) {
                Log.e(TAG, "Error loading schedules: ${e.message}", e)
                showEmptyState("Lỗi khi tải lịch trình")
            }
        }
    }
    
    private fun showEmptyState(message: String) {
        emptyStateText.text = message
        emptyStateText.visibility = View.VISIBLE
        scheduleRecyclerView.visibility = View.GONE
    }
    
    private fun showSchedules(schedules: List<Schedule>) {
        emptyStateText.visibility = View.GONE
        scheduleRecyclerView.visibility = View.VISIBLE
        scheduleAdapter.submitList(schedules)
    }
    
    private fun onScheduleClick(schedule: Schedule) {
        // Show schedule details dialog
        showScheduleDetailsDialog(schedule)
    }
    
    private fun onScheduleComplete(schedule: Schedule) {
        CoroutineScope(Dispatchers.Main).launch {
            try {
                val success = withContext(Dispatchers.IO) {
                    scheduleManager.markScheduleComplete(schedule.id ?: "")
                }
                
                if (success) {
                    // Refresh the list
                    loadSchedules()
                }
                
            } catch (e: Exception) {
                Log.e(TAG, "Error marking schedule complete: ${e.message}", e)
            }
        }
    }
    
    private fun onScheduleDelete(schedule: Schedule) {
        // Show confirmation dialog
        showDeleteConfirmationDialog(schedule)
    }
    
    private fun showScheduleDetailsDialog(schedule: Schedule) {
        val dateFormat = SimpleDateFormat("dd/MM/yyyy HH:mm", Locale("vi"))
        val scheduledDate = Date(schedule.scheduledAt * 1000)
        
        val message = """
            Tiêu đề: ${schedule.title}
            Nội dung: ${schedule.message}
            Thời gian: ${dateFormat.format(scheduledDate)}
            Danh mục: ${getCategoryDisplayName(schedule.category)}
            Trạng thái: ${if (schedule.isCompleted) "Đã hoàn thành" else "Chưa hoàn thành"}
        """.trimIndent()
        
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("Chi tiết lịch trình")
            .setMessage(message)
            .setPositiveButton("Đóng") { dialog, _ ->
                dialog.dismiss()
            }
            .show()
    }
    
    private fun showDeleteConfirmationDialog(schedule: Schedule) {
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("Xóa lịch trình")
            .setMessage("Bạn có chắc chắn muốn xóa lịch trình '${schedule.title}'?")
            .setPositiveButton("Xóa") { dialog, _ ->
                deleteSchedule(schedule)
                dialog.dismiss()
            }
            .setNegativeButton("Hủy") { dialog, _ ->
                dialog.dismiss()
            }
            .show()
    }
    
    private fun deleteSchedule(schedule: Schedule) {
        CoroutineScope(Dispatchers.Main).launch {
            try {
                val success = withContext(Dispatchers.IO) {
                    scheduleManager.deleteSchedule(schedule.id ?: "")
                }
                
                if (success) {
                    // Refresh the list
                    loadSchedules()
                }
                
            } catch (e: Exception) {
                Log.e(TAG, "Error deleting schedule: ${e.message}", e)
            }
        }
    }
    
    private fun showCreateScheduleDialog() {
        // For now, just show a message
        // In a real app, this would navigate to CreateScheduleActivity
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("Tạo lịch trình mới")
            .setMessage("Chức năng này sẽ được mở từ màn hình chính hoặc từ danh sách người già.")
            .setPositiveButton("Đóng") { dialog, _ ->
                dialog.dismiss()
            }
            .show()
    }
    
    private fun getCategoryDisplayName(category: String): String {
        return when (category) {
            "medicine" -> "Thuốc"
            "appointment" -> "Hẹn khám"
            "exercise" -> "Tập thể dục"
            "meal" -> "Bữa ăn"
            "other" -> "Khác"
            else -> category
        }
    }
} 