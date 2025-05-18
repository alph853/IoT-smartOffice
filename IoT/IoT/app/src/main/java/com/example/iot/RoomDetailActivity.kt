package com.example.iot

import android.os.Bundle
import android.util.Log
import android.view.MotionEvent
import android.view.View
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.widget.SwitchCompat

class RoomDetailActivity : AppCompatActivity() {
    
    companion object {
        private const val TAG = "RoomDetailActivity"
    }
    
    private lateinit var roomTitle: TextView
    private lateinit var lightSwitch: SwitchCompat
    private lateinit var temperatureValue: TextView
    private lateinit var humidityValue: TextView
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_room_detail)
        
        // Get the room name from the intent
        val roomName = intent.getStringExtra("ROOM_NAME") ?: getString(R.string.app_name)
        
        setupHeaderClickRegions(roomName)
        setupViews()
        setupListeners(roomName)
        setupNavigationClickRegions()
    }
    
    private fun setupHeaderClickRegions(roomName: String) {
        // Set up header click regions
        val headerView = findViewById<View>(R.id.header)
        
        // Set up profile button
        val profileButton = headerView?.findViewById<View>(R.id.profile_icon)
        profileButton?.setOnClickListener {
            Toast.makeText(this, "Profile clicked", Toast.LENGTH_SHORT).show()
        }
    }
    
    private fun setupViews() {
        roomTitle = findViewById(R.id.room_detail_title)
        lightSwitch = findViewById(R.id.light_switch)
        temperatureValue = findViewById(R.id.temperature_value)
        humidityValue = findViewById(R.id.humidity_value)
        
        // Set default values
        temperatureValue.text = "24°C"
        humidityValue.text = "65%"
    }
    
    private fun setupListeners(roomName: String) {
        roomTitle.text = roomName
        
        lightSwitch.setOnCheckedChangeListener { _, isChecked ->
            val status = if (isChecked) "on" else "off"
            Toast.makeText(this, "$roomName lights turned $status", Toast.LENGTH_SHORT).show()
            // Send command to IoT device
        }
    }
    
    private fun setupNavigationClickRegions() {
        // Set up navigation bar click regions
        val navBarView = findViewById<View>(R.id.nav_bar)
        
        val navHome = navBarView?.findViewById<View>(R.id.home_button)
        navHome?.setOnClickListener {
            finish() // Go back to home screen
        }
        
        val navSettings = navBarView?.findViewById<View>(R.id.settings_button)
        navSettings?.setOnClickListener {
            Toast.makeText(this, "Settings screen will be implemented", Toast.LENGTH_SHORT).show()
        }
        
        val navNotifications = navBarView?.findViewById<View>(R.id.notifications_button)
        navNotifications?.setOnClickListener {
            Toast.makeText(this, "Notifications screen will be implemented", Toast.LENGTH_SHORT).show()
        }
    }
} 