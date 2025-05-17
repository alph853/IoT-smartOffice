package com.example.iot

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.ImageButton
import android.widget.TextView
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.updatePadding
import androidx.fragment.app.Fragment

class RoomDetailActivity : AppCompatActivity() {

    private lateinit var navigationBar: NavigationBar

    companion object {
        private const val EXTRA_ROOM_NAME = "extra_room_name"
        private const val EXTRA_ROOM_DESC = "extra_room_desc"
        private const val EXTRA_ROOM_DEVICE_COUNT = "extra_room_device_count"

        fun newIntent(context: Context, room: Room): Intent {
            return Intent(context, RoomDetailActivity::class.java).apply {
                putExtra(EXTRA_ROOM_NAME, room.name)
                putExtra(EXTRA_ROOM_DESC, room.description)
                putExtra(EXTRA_ROOM_DEVICE_COUNT, room.deviceCount)
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        supportActionBar?.hide()
        setContentView(R.layout.activity_room_detail)

        // Apply window insets properly
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.detail_main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            // Only apply left and right padding to the main container
            v.updatePadding(left = systemBars.left, right = systemBars.right)
            insets
        }

        // Get room details from intent
        val roomName = intent.getStringExtra(EXTRA_ROOM_NAME) ?: "Room"
        val roomDesc = intent.getStringExtra(EXTRA_ROOM_DESC) ?: "Building"
        val deviceCount = intent.getIntExtra(EXTRA_ROOM_DEVICE_COUNT, 0)

        // Set room name in the header
        findViewById<TextView>(R.id.tvDetailRoomName).text = roomName

        // Setup back button
        findViewById<View>(R.id.backButton).setOnClickListener {
            finish() // Close this activity and return to previous screen
        }
        
        // Setup navigation bar
        setupNavigationBar()
    }
    
    private fun setupNavigationBar() {
        navigationBar = NavigationBar(this)
        navigationBar.setup()
        
        // Set the Home tab as selected (index 0) since room details belong to Home functionality
        navigationBar.setSelectedIndex(0)
        
        // Handle navigation item clicks
        navigationBar.setOnItemSelectedListener { index ->
            if (index == 0) {
                // When Home tab is clicked, always go back to MainActivity's home screen
                val intent = Intent(this, MainActivity::class.java)
                intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
                startActivity(intent)
                finish()
            } else {
                // For other tabs, start the MainActivity and set the appropriate tab
                val intent = Intent(this, MainActivity::class.java)
                intent.putExtra("selected_tab", index)
                startActivity(intent)
                finish()
            }
        }
    }
} 