package com.example.iot

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.TextView
import android.widget.ImageView
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.updatePadding

class NotificationDetailActivity : AppCompatActivity() {

    companion object {
        private const val EXTRA_NOTIFICATION_ID = "extra_notification_id"
        private const val EXTRA_NOTIFICATION_TITLE = "extra_notification_title"
        private const val EXTRA_NOTIFICATION_MESSAGE = "extra_notification_message"
        private const val EXTRA_NOTIFICATION_TYPE = "extra_notification_type"
        private const val EXTRA_NOTIFICATION_TIME = "extra_notification_time"
        private const val EXTRA_NOTIFICATION_ICON = "extra_notification_icon"

        fun newIntent(
            context: Context,
            notification: Notification
        ): Intent {
            return Intent(context, NotificationDetailActivity::class.java).apply {
                putExtra(EXTRA_NOTIFICATION_ID, notification.id)
                putExtra(EXTRA_NOTIFICATION_TITLE, notification.title)
                putExtra(EXTRA_NOTIFICATION_MESSAGE, notification.message)
                putExtra(EXTRA_NOTIFICATION_TYPE, notification.type)
                putExtra(EXTRA_NOTIFICATION_TIME, notification.ts)
                putExtra(EXTRA_NOTIFICATION_ICON, notification.iconRes)
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        supportActionBar?.hide()
        setContentView(R.layout.activity_notification_detail)

        // Apply window insets properly
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.notification_detail_main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.updatePadding(left = systemBars.left, right = systemBars.right)
            insets
        }

        setupUI()
    }

    private fun setupUI() {
        // Get notification data from intent
        val notificationId = intent.getIntExtra(EXTRA_NOTIFICATION_ID, -1)
        val title = intent.getStringExtra(EXTRA_NOTIFICATION_TITLE) ?: "Unknown Title"
        val message = intent.getStringExtra(EXTRA_NOTIFICATION_MESSAGE) ?: "No message"
        val type = intent.getStringExtra(EXTRA_NOTIFICATION_TYPE) ?: "info"
        val time = intent.getStringExtra(EXTRA_NOTIFICATION_TIME) ?: "Unknown time"
        val iconRes = intent.getIntExtra(EXTRA_NOTIFICATION_ICON, R.drawable.ic_notifications)

        // Setup views
        findViewById<TextView>(R.id.detail_title).text = title
        findViewById<TextView>(R.id.detail_message).text = message
        findViewById<TextView>(R.id.detail_type).text = type.uppercase()
        findViewById<TextView>(R.id.detail_time).text = time
        findViewById<ImageView>(R.id.detail_icon).setImageResource(iconRes)

        // Setup back button
        findViewById<View>(R.id.backButton).setOnClickListener {
            finish()
        }

        // Setup navigation bar
        setupNavigationBar()
    }

    private fun setupNavigationBar() {
        val navigationBar = NavigationBar(this)
        navigationBar.setup()
        
        // Set the Notification tab as selected (index 3)
        navigationBar.setSelectedIndex(3)
        
        // Handle navigation item clicks
        navigationBar.setOnItemSelectedListener { index ->
            when (index) {
                3 -> {
                    // Already on notification, just go back to notification list
                    finish()
                }
                else -> {
                    // For other tabs, start the MainActivity and set the appropriate tab
                    val intent = Intent(this, MainActivity::class.java)
                    intent.putExtra("selected_tab", index)
                    startActivity(intent)
                    finish()
                }
            }
        }
    }
} 