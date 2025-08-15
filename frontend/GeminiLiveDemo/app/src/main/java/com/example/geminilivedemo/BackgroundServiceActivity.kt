package com.example.geminilivedemo

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.Switch
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class BackgroundServiceActivity : AppCompatActivity() {
    
    private lateinit var serviceManager: ServiceManager
    private lateinit var serviceStatusText: TextView
    private lateinit var serviceToggleSwitch: Switch
    private lateinit var stopServiceButton: Button
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_background_service)
        
        serviceManager = ServiceManager(this)
        
        initializeViews()
        setupListeners()
        updateServiceStatus()
    }
    
    private fun initializeViews() {
        serviceStatusText = findViewById(R.id.serviceStatusText)
        serviceToggleSwitch = findViewById(R.id.serviceToggleSwitch)
        stopServiceButton = findViewById(R.id.stopServiceButton)
    }
    
    private fun setupListeners() {
        serviceToggleSwitch.setOnCheckedChangeListener { _, isChecked ->
            if (isChecked) {
                serviceManager.startListeningService()
            } else {
                serviceManager.stopListeningService()
            }
            updateServiceStatus()
        }
        
        stopServiceButton.setOnClickListener {
            serviceManager.stopService()
            serviceToggleSwitch.isChecked = false
            updateServiceStatus()
        }
    }
    
    private fun updateServiceStatus() {
        // In a real implementation, you would check the actual service status
        val isRunning = serviceToggleSwitch.isChecked
        val statusText = if (isRunning) {
            "Background Service: RUNNING\nAI is listening for voice commands"
        } else {
            "Background Service: STOPPED\nAI is not listening"
        }
        serviceStatusText.text = statusText
    }
    
    override fun onResume() {
        super.onResume()
        updateServiceStatus()
    }
}
