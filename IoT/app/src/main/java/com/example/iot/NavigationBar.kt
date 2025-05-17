package com.example.iot

import android.view.View
import android.widget.ImageView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class NavigationBar(private val activity: AppCompatActivity) {

    private lateinit var navItems: List<View>
    private var selectedNavIndex = 0
    private var onItemSelectedListener: ((Int) -> Unit)? = null

    fun setup() {
        // Find all navigation items
        navItems = listOf(
            activity.findViewById(R.id.nav_home),
            activity.findViewById(R.id.nav_control),
            activity.findViewById(R.id.nav_camera),
            activity.findViewById(R.id.nav_notification),
            activity.findViewById(R.id.nav_setting)
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
    
    fun selectNavItem(index: Int) {
        // Skip if already selected
        if (index == selectedNavIndex) return
        
        // Update UI state
        updateNavItemState(selectedNavIndex, false)
        updateNavItemState(index, true)
        
        // Update selected index
        selectedNavIndex = index
        
        // Notify listener
        onItemSelectedListener?.invoke(index)
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
    
    fun setOnItemSelectedListener(listener: (Int) -> Unit) {
        onItemSelectedListener = listener
    }
    
    fun setSelectedIndex(index: Int) {
        if (index != selectedNavIndex) {
            updateNavItemState(selectedNavIndex, false)
            updateNavItemState(index, true)
            selectedNavIndex = index
        } else {
            updateNavItemState(index, true)
        }
    }
} 