package com.example.iot

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.MotionEvent
import android.view.View
import android.widget.ImageView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    
    companion object {
        private const val TAG = "MainActivity"
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_home)
        
        setupClickableRegions()
    }
    
    private fun setupClickableRegions() {
        // Set up header click regions
        val headerView = findViewById<View>(R.id.header)
        val profileButton = headerView?.findViewById<View>(R.id.profile_icon)
        profileButton?.setOnClickListener {
            Toast.makeText(this, "Profile clicked", Toast.LENGTH_SHORT).show()
        }
        
        // Set up navigation bar click regions
        val navBarView = findViewById<View>(R.id.nav_bar)
        
        val navHome = navBarView?.findViewById<View>(R.id.home_button)
        navHome?.setOnClickListener {
            Toast.makeText(this, "Already on Home screen", Toast.LENGTH_SHORT).show()
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
    
    private fun navigateToRoomDetail(roomName: String) {
        val intent = Intent(this, RoomDetailActivity::class.java)
        intent.putExtra("ROOM_NAME", roomName)
        startActivity(intent)
    }
}