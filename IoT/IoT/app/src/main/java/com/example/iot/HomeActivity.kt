package com.example.iot

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import com.google.android.material.bottomnavigation.BottomNavigationView

class HomeActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Make the app draw edge-to-edge
        WindowCompat.setDecorFitsSystemWindows(window, false)

        // Hide the status bar
        val windowInsetsController = WindowCompat.getInsetsController(window, window.decorView)
        windowInsetsController.hide(WindowInsetsCompat.Type.statusBars())
        windowInsetsController.systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE

        setContentView(R.layout.activity_home)

        setupNavBarClickListeners()
    }

    private fun setupNavBarClickListeners() {
        val bottomNavigation = findViewById<BottomNavigationView>(R.id.bottom_navigation)
        bottomNavigation.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_home -> {
                    // Đã ở Home
                    true
                }
                R.id.nav_control -> {
                    val intent = Intent(this, ControlActivity::class.java)
                    startActivity(intent)
                    true
                }
                R.id.nav_camera -> {
                    true
                }
                R.id.nav_notifications -> {
                    true
                }
                R.id.nav_settings -> {
                    true
                }
                else -> false
            }
        }
    }
} 