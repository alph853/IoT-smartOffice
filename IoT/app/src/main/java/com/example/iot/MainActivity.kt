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
import android.widget.ImageButton
import android.widget.PopupMenu
import android.widget.GridLayout
import android.util.TypedValue
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.RecyclerView

class MainActivity : AppCompatActivity() {

    private lateinit var navItems: List<View>
    private var selectedNavIndex = 0
    private lateinit var homeScreen: ConstraintLayout
    private lateinit var fragmentContainer: FrameLayout
    private lateinit var roomAdapter: RoomAdapter
    private val roomList = mutableListOf<Room>()
    private lateinit var tvActiveCount: TextView

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
        tvActiveCount = findViewById(R.id.tv_active_count)
        
        setupNavigation()
        
        // Ensure Home UI is visible at startup
        homeScreen.visibility = View.VISIBLE
        
        // Override selectedNavIndex since Home tab should be selected by default
        selectedNavIndex = 0
        updateNavItemState(0, true)

        // Setup menu button event
        val btnMenu = findViewById<ImageButton>(R.id.btn_menu)
        btnMenu.setOnClickListener { v ->
            val popup = PopupMenu(this, v)
            popup.menu.add(0, 0, 0, "Add")
            popup.menu.add(0, 1, 1, "Remove")
            popup.menu.add(0, 2, 2, "Modify")
            popup.setOnMenuItemClickListener { item ->
                when (item.itemId) {
                    0 -> {
                        onMenuAdd()
                        true
                    }
                    1 -> {
                        onMenuRemove()
                        true
                    }
                    2 -> {
                        onMenuModify()
                        true
                    }
                    else -> false
                }
            }
            popup.show()
        }

        // Setup RecyclerView for room cards
        val rvRooms = findViewById<RecyclerView>(R.id.rvRooms)
        roomAdapter = RoomAdapter(roomList) { updateActiveCount() }
        rvRooms.layoutManager = GridLayoutManager(this, 2)
        rvRooms.adapter = roomAdapter

        // Add click listener to root layout to hide remove button
        findViewById<View>(R.id.main).setOnClickListener {
            if (roomAdapter.isRemoveMode()) {
                roomAdapter.setRemoveMode(false)
            }
        }

        // Update active count initially
        updateActiveCount()
    }

    private fun updateActiveCount() {
        tvActiveCount.text = "${roomList.size} active(s)"
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

        }
    }

    private fun onMenuAdd() {
        // Add a new room card and update the adapter
        roomList.add(Room())
        roomAdapter.notifyItemInserted(roomList.size - 1)
        updateActiveCount()
    }

    private fun onMenuRemove() {
        // Toggle remove mode in the adapter
        roomAdapter.setRemoveMode(!roomAdapter.isRemoveMode())
    }

    private fun onMenuModify() {
        // TODO: Implement Modify action
    }
}