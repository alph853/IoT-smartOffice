package com.example.iot

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.TextView
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.updatePadding

class MCUDetailActivity : AppCompatActivity() {

    private lateinit var navigationBar: NavigationBar

    companion object {
        private const val EXTRA_MCU_NAME = "extra_mcu_name"
        private const val EXTRA_MCU_STATUS = "extra_mcu_status"

        fun newIntent(context: Context, mcu: MCU): Intent {
            return Intent(context, MCUDetailActivity::class.java).apply {
                putExtra(EXTRA_MCU_NAME, mcu.name)
                putExtra(EXTRA_MCU_STATUS, mcu.status)
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        supportActionBar?.hide()
        setContentView(R.layout.activity_mcu_detail)

        // Apply window insets properly
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.mcu_detail_main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.updatePadding(left = systemBars.left, right = systemBars.right)
            insets
        }

        // Get MCU details from intent
        val mcuName = intent.getStringExtra(EXTRA_MCU_NAME) ?: "MCU"
        val mcuStatus = intent.getStringExtra(EXTRA_MCU_STATUS) ?: "Unknown"

        // Set MCU name in the header
        findViewById<TextView>(R.id.tvDetailMCUName).text = mcuName

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
        
        // Set the Home tab as selected (index 0) since MCU details belong to Home functionality
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