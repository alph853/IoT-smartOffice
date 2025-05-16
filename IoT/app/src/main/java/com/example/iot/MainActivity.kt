package com.example.iot

import android.os.Bundle
import android.view.View
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.TextView
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.constraintlayout.widget.ConstraintLayout
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.isVisible
import androidx.core.view.updatePadding
import androidx.fragment.app.Fragment
import com.example.iot.fragments.*

class MainActivity : AppCompatActivity() {

    private lateinit var navItems: List<View>
    private var selectedNavIndex = 0
    private lateinit var homeScreen: ConstraintLayout
    private lateinit var fragmentContainer: FrameLayout

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        supportActionBar?.hide()
        setContentView(R.layout.activity_main)
        
        // Apply window insets properly
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            // Only apply left and right padding to the main container
            v.updatePadding(left = systemBars.left, right = systemBars.right)
            insets
        }
        
        // Get references to home screen and fragment container
        homeScreen = findViewById(R.id.home_screen)
        fragmentContainer = findViewById(R.id.fragment_container)
        
        setupNavigation()
        
        // Ensure Home UI is visible at startup
        homeScreen.visibility = View.VISIBLE
        fragmentContainer.visibility = View.GONE
        
        // Override selectedNavIndex since Home tab should be selected by default
        selectedNavIndex = 0
        updateNavItemState(0, true)
    }
    
    private fun setupNavigation() {
        // Find all navigation items
        navItems = listOf(
            findViewById(R.id.nav_home),
            findViewById(R.id.nav_control),
            findViewById(R.id.nav_camera),
            findViewById(R.id.nav_notification),
            findViewById(R.id.nav_setting)
        )
        
        // Set up icons and text
        setupNavItem(navItems[0], R.drawable.nav_home_selector, R.string.nav_home)
        setupNavItem(navItems[1], R.drawable.nav_control_selector, R.string.nav_control)
        setupNavItem(navItems[2], R.drawable.nav_camera_selector, R.string.nav_camera)
        setupNavItem(navItems[3], R.drawable.nav_notification_selector, R.string.nav_notification)
        setupNavItem(navItems[4], R.drawable.nav_setting_selector, R.string.nav_setting)
        
        // Initially set all items to unselected state
        navItems.forEachIndexed { index, _ ->
            updateNavItemState(index, false)
        }
        
        // Set up click listeners
        navItems.forEachIndexed { index, item ->
            item.setOnClickListener {
                selectNavItem(index)
            }
        }
    }
    
    private fun setupNavItem(navItem: View, iconResId: Int, titleResId: Int) {
        val icon = navItem.findViewById<ImageView>(R.id.icon)
        val title = navItem.findViewById<TextView>(R.id.title)
        
        icon.setImageResource(iconResId)
        title.setText(titleResId)
    }
    
    private fun selectNavItem(index: Int) {
        // Skip if already selected
        if (index == selectedNavIndex) return
        
        // Update UI state
        updateNavItemState(selectedNavIndex, false)
        updateNavItemState(index, true)
        
        // Update selected index
        selectedNavIndex = index
        
        // Show corresponding view/fragment
        showContent(index)
    }
    
    private fun updateNavItemState(index: Int, isSelected: Boolean) {
        val navItem = navItems[index]
        val icon = navItem.findViewById<ImageView>(R.id.icon)
        val title = navItem.findViewById<TextView>(R.id.title)
        
        icon.isSelected = isSelected
        title.isSelected = isSelected
        
        // Apply alpha to reflect selection state
        icon.alpha = if (isSelected) 1.0f else 0.5f
        title.alpha = if (isSelected) 1.0f else 0.5f
    }
    
    private fun showContent(index: Int) {
        if (index == 0) {
            // Show Home screen with header
            homeScreen.visibility = View.VISIBLE
            fragmentContainer.visibility = View.GONE
        } else {
            // Show other fragments
            homeScreen.visibility = View.GONE
            fragmentContainer.visibility = View.VISIBLE
            
            val fragment = when(index) {
                1 -> ControlFragment.newInstance()
                2 -> CameraFragment.newInstance()
                3 -> NotificationFragment.newInstance() 
                4 -> SettingFragment.newInstance()
                else -> ControlFragment.newInstance()
            }
            
            supportFragmentManager.beginTransaction()
                .replace(R.id.fragment_container, fragment)
                .commit()
        }
    }
}