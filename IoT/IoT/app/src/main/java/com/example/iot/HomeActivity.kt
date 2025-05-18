package com.example.iot

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import com.google.android.material.tabs.TabLayout

class HomeActivity : AppCompatActivity() {
    
    companion object {
        private const val TAG = "HomeActivity"
        private const val MCU_DETAIL_REQUEST = 100
    }
    
    // MCU active status tracking
    private val mcuActiveStatusOffice1 = mutableMapOf(
        "mcu1" to true,
        "mcu2" to true,
        "mcu3" to false,
        "mcu4" to true,
        "mcu5" to false,
        "mcu6" to false
    )
    
    private val mcuActiveStatusOffice2 = mutableMapOf(
        "mcu1" to true,
        "mcu2" to false,
        "mcu3" to false,
        "mcu4" to true,
        "mcu5" to true,
        "mcu6" to false
    )
    
    private val mcuActiveStatusOffice3 = mutableMapOf(
        "mcu1" to true,
        "mcu2" to true,
        "mcu3" to true,
        "mcu4" to false,
        "mcu5" to false,
        "mcu6" to false
    )
    
    // Activity result launcher
    private val mcuDetailLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            val data = result.data ?: return@registerForActivityResult
            
            val mcuId = data.getStringExtra("MCU_ID") ?: return@registerForActivityResult
            val mcuOffice = data.getStringExtra("MCU_OFFICE") ?: return@registerForActivityResult
            val mcuStatus = data.getBooleanExtra("MCU_STATUS", false)
            
            // Update MCU status based on result
            updateMCUStatusFromResult(mcuId, mcuOffice, mcuStatus)
        }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Make the app draw edge-to-edge
        WindowCompat.setDecorFitsSystemWindows(window, false)
        
        // Hide the status bar
        val windowInsetsController = WindowCompat.getInsetsController(window, window.decorView)
        windowInsetsController.hide(WindowInsetsCompat.Type.statusBars())
        windowInsetsController.systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        
        setContentView(R.layout.activity_home)
        
        setupClickableRegions()
        setupTabLayout()
        updateMCUGroupStatuses()
    }
    
    private fun updateMCUStatusFromResult(mcuId: String, mcuOffice: String, isActive: Boolean) {
        val officeId = when {
            mcuOffice.contains("1") -> 1
            mcuOffice.contains("2") -> 2
            mcuOffice.contains("3") -> 3
            else -> return
        }
        
        val statusMap = when (officeId) {
            1 -> mcuActiveStatusOffice1
            2 -> mcuActiveStatusOffice2
            3 -> mcuActiveStatusOffice3
            else -> return
        }
        
        statusMap[mcuId] = isActive
        
        // Update UI
        when (officeId) {
            1 -> updateOffice1MCUStatuses()
            2 -> updateOffice2MCUStatuses()
            3 -> updateOffice3MCUStatuses()
        }
    }
    
    /**
     * Opens the MCU detail activity for the specified office and MCU ID
     */
    private fun openMCUDetailActivity(officeId: Int, mcuId: Int) {
        val statusMap = when (officeId) {
            1 -> mcuActiveStatusOffice1
            2 -> mcuActiveStatusOffice2
            3 -> mcuActiveStatusOffice3
            else -> return
        }
        
        val mcuKey = "mcu$mcuId"
        val mcuStatus = statusMap[mcuKey] ?: false
        
        val intent = Intent(this, MCUDetailActivity::class.java)
        intent.putExtra("MCU_ID", mcuId.toString())
        intent.putExtra("MCU_OFFICE", "Office $officeId")
        intent.putExtra("MCU_STATUS", mcuStatus)
        
        mcuDetailLauncher.launch(intent)
    }
    
    /**
     * Sets up the tab layout to switch between offices
     */
    private fun setupTabLayout() {
        val tabLayout = findViewById<TabLayout>(R.id.office_tabs)
        tabLayout?.addOnTabSelectedListener(object : TabLayout.OnTabSelectedListener {
            override fun onTabSelected(tab: TabLayout.Tab?) {
                when (tab?.position) {
                    0 -> showOffice1()
                    1 -> showOffice2()
                    2 -> showOffice3()
                    3 -> showOffice4()
                }
            }

            override fun onTabUnselected(tab: TabLayout.Tab?) {
                // Not needed
            }

            override fun onTabReselected(tab: TabLayout.Tab?) {
                // Not needed
            }
        })
    }
    
    /**
     * Updates all MCU group statuses for all offices
     */
    private fun updateMCUGroupStatuses() {
        updateOffice1MCUStatuses()
        updateOffice2MCUStatuses()
        updateOffice3MCUStatuses()
    }
    
    /**
     * Updates the MCU statuses for Office 1
     */
    private fun updateOffice1MCUStatuses() {
        // Count active MCUs in Group 1
        val activeInGroup1 = countActiveMCUs(mcuActiveStatusOffice1, 1, 3)
        findViewById<TextView>(R.id.mcu_group1_status)?.text = "$activeInGroup1 active"
        
        // Count active MCUs in Group 2
        val activeInGroup2 = countActiveMCUs(mcuActiveStatusOffice1, 4, 6)
        findViewById<TextView>(R.id.mcu_group2_status)?.text = "$activeInGroup2 active"
        
        // Update individual MCU statuses
        for (i in 1..6) {
            val mcuStatusTextView = findViewById<TextView>(resources.getIdentifier("mcu${i}_status", "id", packageName))
            val isActive = mcuActiveStatusOffice1["mcu$i"] ?: false
            
            mcuStatusTextView?.text = if (isActive) "Active" else "Inactive"
            mcuStatusTextView?.setTextColor(resources.getColor(
                if (isActive) android.R.color.holo_green_light else android.R.color.darker_gray,
                theme
            ))
        }
    }
    
    /**
     * Updates the MCU statuses for Office 2
     */
    private fun updateOffice2MCUStatuses() {
        // Count active MCUs in Group 1
        val activeInGroup1 = countActiveMCUs(mcuActiveStatusOffice2, 1, 3)
        findViewById<TextView>(R.id.mcu_group1_office2_status)?.text = "$activeInGroup1 active"
        
        // Count active MCUs in Group 2
        val activeInGroup2 = countActiveMCUs(mcuActiveStatusOffice2, 4, 6)
        findViewById<TextView>(R.id.mcu_group2_office2_status)?.text = "$activeInGroup2 active"
        
        // Update individual MCU statuses
        for (i in 1..6) {
            val mcuStatusTextView = findViewById<TextView>(resources.getIdentifier("mcu${i}_office2_status", "id", packageName))
            val isActive = mcuActiveStatusOffice2["mcu$i"] ?: false
            
            mcuStatusTextView?.text = if (isActive) "Active" else "Inactive"
            mcuStatusTextView?.setTextColor(resources.getColor(
                if (isActive) android.R.color.holo_green_light else android.R.color.darker_gray,
                theme
            ))
        }
    }
    
    /**
     * Updates the MCU statuses for Office 3
     */
    private fun updateOffice3MCUStatuses() {
        // Count active MCUs in Group 1
        val activeInGroup1 = countActiveMCUs(mcuActiveStatusOffice3, 1, 3)
        findViewById<TextView>(R.id.mcu_group1_office3_status)?.text = "$activeInGroup1 active"
        
        // Count active MCUs in Group 2
        val activeInGroup2 = countActiveMCUs(mcuActiveStatusOffice3, 4, 6)
        findViewById<TextView>(R.id.mcu_group2_office3_status)?.text = "$activeInGroup2 active"
        
        // Update individual MCU statuses
        for (i in 1..6) {
            val mcuStatusTextView = findViewById<TextView>(resources.getIdentifier("mcu${i}_office3_status", "id", packageName))
            val isActive = mcuActiveStatusOffice3["mcu$i"] ?: false
            
            mcuStatusTextView?.text = if (isActive) "Active" else "Inactive"
            mcuStatusTextView?.setTextColor(resources.getColor(
                if (isActive) android.R.color.holo_green_light else android.R.color.darker_gray,
                theme
            ))
        }
    }
    
    /**
     * Counts the number of active MCUs in a given range
     */
    private fun countActiveMCUs(statusMap: Map<String, Boolean>, startId: Int, endId: Int): Int {
        var count = 0
        for (i in startId..endId) {
            if (statusMap["mcu$i"] == true) {
                count++
            }
        }
        return count
    }
    
    /**
     * Shows the Office 1 content and hides other offices
     */
    private fun showOffice1() {
        findViewById<View>(R.id.office1_content)?.visibility = View.VISIBLE
        findViewById<View>(R.id.office2_content)?.visibility = View.GONE
        findViewById<View>(R.id.office3_content)?.visibility = View.GONE
        findViewById<View>(R.id.office4_content)?.visibility = View.GONE
        
        updateOffice1MCUStatuses()
    }
    
    /**
     * Shows the Office 2 content and hides other offices
     */
    private fun showOffice2() {
        findViewById<View>(R.id.office1_content)?.visibility = View.GONE
        findViewById<View>(R.id.office2_content)?.visibility = View.VISIBLE
        findViewById<View>(R.id.office3_content)?.visibility = View.GONE
        findViewById<View>(R.id.office4_content)?.visibility = View.GONE
        
        updateOffice2MCUStatuses()
    }
    
    /**
     * Shows the Office 3 content and hides other offices
     */
    private fun showOffice3() {
        findViewById<View>(R.id.office1_content)?.visibility = View.GONE
        findViewById<View>(R.id.office2_content)?.visibility = View.GONE
        findViewById<View>(R.id.office3_content)?.visibility = View.VISIBLE
        findViewById<View>(R.id.office4_content)?.visibility = View.GONE
        
        updateOffice3MCUStatuses()
    }
    
    /**
     * Shows the Office 4 content and hides other offices
     */
    private fun showOffice4() {
        findViewById<View>(R.id.office1_content)?.visibility = View.GONE
        findViewById<View>(R.id.office2_content)?.visibility = View.GONE
        findViewById<View>(R.id.office3_content)?.visibility = View.GONE
        findViewById<View>(R.id.office4_content)?.visibility = View.VISIBLE
    }
    
    /**
     * Sets up all clickable regions in the app
     */
    private fun setupClickableRegions() {
        // Set up header click regions
        setupHeaderClickListeners()
        
        // Set up Office MCU click listeners
        setupOffice1MCUClickListeners()
        setupOffice2MCUClickListeners()
        setupOffice3MCUClickListeners()
        
        // Set up navigation bar click regions
        setupNavBarClickListeners()
    }

    /**
     * Sets up the click listeners for the header components
     */
    private fun setupHeaderClickListeners() {
        val headerView = findViewById<View>(R.id.header)
        val profileButton = headerView?.findViewById<View>(R.id.profile_icon)
        profileButton?.setOnClickListener {
            Toast.makeText(this, "Profile clicked", Toast.LENGTH_SHORT).show()
        }
    }
    
    /**
     * Sets up the click listeners for the navigation bar components
     */
    private fun setupNavBarClickListeners() {
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
    
    /**
     * Sets up click listeners for Office 1 MCUs
     */
    private fun setupOffice1MCUClickListeners() {
        // Set up Group 1 MCU click listeners
        setupOffice1Group1ClickListeners()
        
        // Set up Group 2 MCU click listeners
        setupOffice1Group2ClickListeners()
    }
    
    /**
     * Sets up click listeners for Office 1, Group 1 MCUs (1-3)
     */
    private fun setupOffice1Group1ClickListeners() {
        findViewById<View>(R.id.mcu1_device_card)?.setOnClickListener {
            onClickMCU_Office1_Group1(1)
        }
        
        findViewById<View>(R.id.mcu2_device_card)?.setOnClickListener {
            onClickMCU_Office1_Group1(2)
        }
        
        findViewById<View>(R.id.mcu3_device_card)?.setOnClickListener {
            onClickMCU_Office1_Group1(3)
        }
    }
    
    /**
     * Handler for clicks on Office 1, Group 1 MCUs
     */
    private fun onClickMCU_Office1_Group1(mcuId: Int) {
        openMCUDetailActivity(1, mcuId)
    }
    
    /**
     * Sets up click listeners for Office 1, Group 2 MCUs (4-6)
     */
    private fun setupOffice1Group2ClickListeners() {
        findViewById<View>(R.id.mcu4_device_card)?.setOnClickListener {
            onClickMCU_Office1_Group2(4)
        }
        
        findViewById<View>(R.id.mcu5_device_card)?.setOnClickListener {
            onClickMCU_Office1_Group2(5)
        }
        
        findViewById<View>(R.id.mcu6_device_card)?.setOnClickListener {
            onClickMCU_Office1_Group2(6)
        }
    }
    
    /**
     * Handler for clicks on Office 1, Group 2 MCUs
     */
    private fun onClickMCU_Office1_Group2(mcuId: Int) {
        openMCUDetailActivity(1, mcuId)
    }
    
    /**
     * Sets up click listeners for Office 2 MCUs
     */
    private fun setupOffice2MCUClickListeners() {
        // Set up Group 1 MCU click listeners
        setupOffice2Group1ClickListeners()
        
        // Set up Group 2 MCU click listeners
        setupOffice2Group2ClickListeners()
    }
    
    /**
     * Sets up click listeners for Office 2, Group 1 MCUs (1-3)
     */
    private fun setupOffice2Group1ClickListeners() {
        findViewById<View>(R.id.mcu1_office2_device_card)?.setOnClickListener {
            onClickMCU_Office2_Group1(1)
        }
        
        findViewById<View>(R.id.mcu2_office2_device_card)?.setOnClickListener {
            onClickMCU_Office2_Group1(2)
        }
        
        findViewById<View>(R.id.mcu3_office2_device_card)?.setOnClickListener {
            onClickMCU_Office2_Group1(3)
        }
    }
    
    /**
     * Handler for clicks on Office 2, Group 1 MCUs
     */
    private fun onClickMCU_Office2_Group1(mcuId: Int) {
        openMCUDetailActivity(2, mcuId)
    }
    
    /**
     * Sets up click listeners for Office 2, Group 2 MCUs (4-6)
     */
    private fun setupOffice2Group2ClickListeners() {
        findViewById<View>(R.id.mcu4_office2_device_card)?.setOnClickListener {
            onClickMCU_Office2_Group2(4)
        }
        
        findViewById<View>(R.id.mcu5_office2_device_card)?.setOnClickListener {
            onClickMCU_Office2_Group2(5)
        }
        
        findViewById<View>(R.id.mcu6_office2_device_card)?.setOnClickListener {
            onClickMCU_Office2_Group2(6)
        }
    }
    
    /**
     * Handler for clicks on Office 2, Group 2 MCUs
     */
    private fun onClickMCU_Office2_Group2(mcuId: Int) {
        openMCUDetailActivity(2, mcuId)
    }
    
    /**
     * Sets up click listeners for Office 3 MCUs
     */
    private fun setupOffice3MCUClickListeners() {
        // Set up Group 1 MCU click listeners
        setupOffice3Group1ClickListeners()
        
        // Set up Group 2 MCU click listeners
        setupOffice3Group2ClickListeners()
    }
    
    /**
     * Sets up click listeners for Office 3, Group 1 MCUs (1-3)
     */
    private fun setupOffice3Group1ClickListeners() {
        findViewById<View>(R.id.mcu1_office3_device_card)?.setOnClickListener {
            onClickMCU_Office3_Group1(1)
        }
        
        findViewById<View>(R.id.mcu2_office3_device_card)?.setOnClickListener {
            onClickMCU_Office3_Group1(2)
        }
        
        findViewById<View>(R.id.mcu3_office3_device_card)?.setOnClickListener {
            onClickMCU_Office3_Group1(3)
        }
    }
    
    /**
     * Handler for clicks on Office 3, Group 1 MCUs
     */
    private fun onClickMCU_Office3_Group1(mcuId: Int) {
        openMCUDetailActivity(3, mcuId)
    }
    
    /**
     * Sets up click listeners for Office 3, Group 2 MCUs (4-6)
     */
    private fun setupOffice3Group2ClickListeners() {
        findViewById<View>(R.id.mcu4_office3_device_card)?.setOnClickListener {
            onClickMCU_Office3_Group2(4)
        }
        
        findViewById<View>(R.id.mcu5_office3_device_card)?.setOnClickListener {
            onClickMCU_Office3_Group2(5)
        }
        
        findViewById<View>(R.id.mcu6_office3_device_card)?.setOnClickListener {
            onClickMCU_Office3_Group2(6)
        }
    }
    
    /**
     * Handler for clicks on Office 3, Group 2 MCUs
     */
    private fun onClickMCU_Office3_Group2(mcuId: Int) {
        openMCUDetailActivity(3, mcuId)
    }
    
    /**
     * Navigates to the room detail screen
     */
    private fun navigateToRoomDetail(roomName: String) {
        val intent = Intent(this, RoomDetailActivity::class.java)
        intent.putExtra("ROOM_NAME", roomName)
        intent.putExtra("ROOM_LOCATION", "A4 Building")
        intent.putExtra("ACTIVE_DEVICES", 3)
        intent.putExtra("ROOM_ICON", R.drawable.ic_room)
        startActivity(intent)
    }
} 