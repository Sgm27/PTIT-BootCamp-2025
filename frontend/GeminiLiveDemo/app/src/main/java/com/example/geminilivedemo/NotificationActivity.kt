package com.example.geminilivedemo

import android.os.Bundle
import android.widget.ImageView
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView

class NotificationActivity : AppCompatActivity() {

    private lateinit var notificationsRecyclerView: RecyclerView
    private lateinit var notificationAdapter: NotificationAdapter
    private lateinit var webSocketManager: WebSocketManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_notification)

        setupBackButton()
        setupRecyclerView()
        setupWebSocket()
        loadNotifications()
    }

    private fun setupBackButton() {
        val backButton = findViewById<ImageView>(R.id.backButton)
        backButton.setOnClickListener {
            finish() // Close this activity and return to the previous one
        }
    }

    private fun setupRecyclerView() {
        notificationsRecyclerView = findViewById(R.id.notificationsRecyclerView)
        notificationAdapter = NotificationAdapter(emptyList())
        
        notificationsRecyclerView.apply {
            layoutManager = LinearLayoutManager(this@NotificationActivity)
            adapter = notificationAdapter
        }
    }
    
    private fun setupWebSocket() {
        webSocketManager = WebSocketManager()
        webSocketManager.setCallback(object : WebSocketManager.WebSocketCallback {
            override fun onConnected() {
                // Request notifications when connected
                webSocketManager.requestNotifications()
            }
            
            override fun onDisconnected() {
                // Handle disconnection
            }
            
            override fun onError(exception: Exception?) {
                // Handle error
            }
            
            override fun onMessageReceived(response: Response) {
                // Handle notification responses
                response.notifications?.let { notifications ->
                    runOnUiThread {
                        notificationAdapter.updateNotifications(notifications)
                    }
                }
            }
        })
        
        // Connect to websocket
        webSocketManager.connect()
    }

    private fun loadNotifications() {
        // Request notifications from backend
        if (webSocketManager.isConnected()) {
            webSocketManager.requestNotifications()
        }
        // If not connected, notifications will be requested when connection is established
    }
    
    override fun onDestroy() {
        super.onDestroy()
        webSocketManager.disconnect()
    }
}
