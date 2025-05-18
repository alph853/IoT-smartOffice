package com.example.iot

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.cardview.widget.CardView
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat

class MCUDetailActivity : AppCompatActivity() {

    private var isActive = false
    private var mcuId = "Unknown"
    private var mcuOffice = "Office 1"
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Make the app draw edge-to-edge
        WindowCompat.setDecorFitsSystemWindows(window, false)
        
        // Hide the status bar
        val windowInsetsController = WindowCompat.getInsetsController(window, window.decorView)
        windowInsetsController.hide(WindowInsetsCompat.Type.statusBars())
        windowInsetsController.systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        
        setContentView(R.layout.activity_mcu_detail)
        
        // Get MCU information from intent
        mcuId = intent.getStringExtra("MCU_ID") ?: "Unknown"
        mcuOffice = intent.getStringExtra("MCU_OFFICE") ?: "Office 1"
        isActive = intent.getBooleanExtra("MCU_STATUS", false)
        
        // Setup UI with received data
        setupUI(mcuId, mcuOffice, isActive)
        
        // Back button click listener
        findViewById<View>(R.id.back_button)?.setOnClickListener {
            finish()
        }
        
        // Toggle button click listener
        findViewById<View>(R.id.control_button)?.setOnClickListener {
            toggleMCUStatus()
        }
        
        // Setup navigation bar listeners
        setupNavBarListeners()
    }
    
    private fun setupUI(mcuId: String, mcuOffice: String, isActive: Boolean) {
        // Set MCU title
        findViewById<TextView>(R.id.mcu_detail_title)?.text = "MCU $mcuId Details"
        
        // Set MCU location
        findViewById<TextView>(R.id.mcu_location)?.text = mcuOffice
        
        // Set MCU status
        updateStatusUI(isActive)
        
        // Set button text
        val controlButton = findViewById<TextView>(R.id.control_button)
        controlButton?.text = if (isActive) "Deactivate MCU" else "Activate MCU"
        
        // Set button color
        val controlButtonCard = findViewById<CardView>(R.id.control_button_card)
        controlButtonCard?.setCardBackgroundColor(resources.getColor(
            if (isActive) android.R.color.holo_red_light else android.R.color.holo_green_light,
            theme
        ))
    }
    
    private fun toggleMCUStatus() {
        isActive = !isActive
        
        // Update UI to reflect new status
        updateStatusUI(isActive)
        
        // Update button text
        val controlButton = findViewById<TextView>(R.id.control_button)
        controlButton?.text = if (isActive) "Deactivate MCU" else "Activate MCU"
        
        // Update button color
        val controlButtonCard = findViewById<CardView>(R.id.control_button_card)
        controlButtonCard?.setCardBackgroundColor(resources.getColor(
            if (isActive) android.R.color.holo_red_light else android.R.color.holo_green_light,
            theme
        ))
        
        // Show status changed toast
        val status = if (isActive) "activated" else "deactivated"
        Toast.makeText(this, "MCU $mcuId $status", Toast.LENGTH_SHORT).show()
        
        // Send result back to HomeActivity
        val intent = Intent()
        intent.putExtra("MCU_ID", mcuId)
        intent.putExtra("MCU_OFFICE", mcuOffice)
        intent.putExtra("MCU_STATUS", isActive)
        setResult(RESULT_OK, intent)
    }
    
    private fun updateStatusUI(active: Boolean) {
        val statusTextView = findViewById<TextView>(R.id.mcu_detail_status)
        statusTextView?.text = if (active) "Active" else "Inactive"
        statusTextView?.setTextColor(resources.getColor(
            if (active) android.R.color.holo_green_light else android.R.color.darker_gray,
            theme
        ))
    }
    
    private fun setupNavBarListeners() {
        // Home button click listener
        findViewById<View>(R.id.home_button)?.setOnClickListener {
            finish() // Just go back to home activity
        }
        
        // Notifications button click listener
        findViewById<View>(R.id.notifications_button)?.setOnClickListener {
            Toast.makeText(this, "Notifications not implemented yet", Toast.LENGTH_SHORT).show()
        }
        
        // Settings button click listener
        findViewById<View>(R.id.settings_button)?.setOnClickListener {
            Toast.makeText(this, "Settings not implemented yet", Toast.LENGTH_SHORT).show()
        }
    }
} 