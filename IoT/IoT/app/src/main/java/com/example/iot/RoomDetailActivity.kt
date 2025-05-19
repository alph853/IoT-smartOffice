package com.example.iot

//Android Framework
import android.os.Bundle
import android.view.View
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import android.util.Log

import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.widget.SwitchCompat
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.bottomnavigation.BottomNavigationView

/**
 * Activity for displaying and controlling devices in a specific room
 */
class RoomDetailActivity : AppCompatActivity() {
    
    companion object {
        private const val TAG = "RoomDetailActivity"
    }
    
    // List of devices in this room
    private val roomDevices = mutableListOf<Device>()
    
    // Device adapter
    private lateinit var deviceAdapter: DeviceAdapter
    
    // UI references
    private lateinit var roomTitle: TextView
    private lateinit var devicesGrid: RecyclerView
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Make the app draw edge-to-edge
        WindowCompat.setDecorFitsSystemWindows(window, false)
        
        // Hide the status bar (giao diện rộng tràn toàn màn hình, khi cần, chỉ cần vuốt cạnh màn hình là sẽ tạm hiện lại các thanh hệ thống)
        val windowInsetsController = WindowCompat.getInsetsController(window, window.decorView)
        windowInsetsController.hide(WindowInsetsCompat.Type.statusBars())
        windowInsetsController.systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        
        setContentView(R.layout.activity_room_detail)
        
        // Get the room name from the intent
        val roomName = intent.getStringExtra("ROOM_NAME") ?: getString(R.string.app_name)
        val roomLocation = intent.getStringExtra("ROOM_LOCATION") ?: "Unknown"
        val activeDevices = intent.getIntExtra("ACTIVE_DEVICES", 0)
        
        // Initialize room devices based on room name
        initializeRoomDevices(roomName)
        
        // Setup UI
        setupUI(roomName, roomLocation, activeDevices)
        
        // Setup click listeners
        setupClickListeners()
    }
    
    /**
     * Initialize devices for this room
     */
    private fun initializeRoomDevices(roomName: String) {
        // In a real app, these devices would be fetched from a database or API
        // This is just a stub (Hard code) (phần khầy Trung ne call server REST APO/GraphQL de lay ds devices/local database (Room, Realm, SQLite.. nếu lưu cục bộ) )
        when (roomName) {
            "Bedroom" -> {
                roomDevices.add(Device("bed_fan", "Fan", DeviceType.FAN, R.drawable.ic_fan, false, "bedroom"))
                roomDevices.add(Device("bed_ac", "AC", DeviceType.AC, R.drawable.ic_ac, true, "bedroom"))
                roomDevices.add(Device("bed_ceiling", "Ceiling Light", DeviceType.CEILING_LIGHT, R.drawable.ic_ceiling_light, true, "bedroom"))
                roomDevices.add(Device("bed_bulb", "Bulb", DeviceType.BULB, R.drawable.ic_bulb, false, "bedroom"))
                roomDevices.add(Device("bed_purifier", "Purifier", DeviceType.PURIFIER, R.drawable.ic_purifier, false, "bedroom"))
                roomDevices.add(Device("bed_climate", "Climate", DeviceType.CLIMATE, R.drawable.ic_climate, true, "bedroom"))
            }
            "Living Room" -> {
                roomDevices.add(Device("living_fan", "Fan", DeviceType.FAN, R.drawable.ic_fan, true, "living_room"))
                roomDevices.add(Device("living_ac", "AC", DeviceType.AC, R.drawable.ic_ac, false, "living_room"))
                roomDevices.add(Device("living_ceiling", "Ceiling Light", DeviceType.CEILING_LIGHT, R.drawable.ic_ceiling_light, true, "living_room"))
                roomDevices.add(Device("living_bulb", "Bulb", DeviceType.BULB, R.drawable.ic_bulb, true, "living_room"))
            }
            "Kitchen" -> {
                roomDevices.add(Device("kitchen_fan", "Fan", DeviceType.FAN, R.drawable.ic_fan, false, "kitchen"))
                roomDevices.add(Device("kitchen_ceiling", "Ceiling Light", DeviceType.CEILING_LIGHT, R.drawable.ic_ceiling_light, true, "kitchen"))
                roomDevices.add(Device("kitchen_bulb", "Bulb", DeviceType.BULB, R.drawable.ic_bulb, true, "kitchen"))
            }
            "Bathroom" -> {
                roomDevices.add(Device("bath_fan", "Fan", DeviceType.FAN, R.drawable.ic_fan, false, "bathroom"))
                roomDevices.add(Device("bath_ceiling", "Ceiling Light", DeviceType.CEILING_LIGHT, R.drawable.ic_ceiling_light, false, "bathroom"))
                roomDevices.add(Device("bath_bulb", "Bulb", DeviceType.BULB, R.drawable.ic_bulb, false, "bathroom"))
            }
        }
    }
    
    /**
     * Setup UI elements
     */
    private fun setupUI(roomName: String, roomLocation: String, activeDevices: Int) {
        // Set room title
        roomTitle = findViewById(R.id.room_detail_title)
        roomTitle.text = roomName
        
        // Set back button click listener
        findViewById<View>(R.id.back_button)?.setOnClickListener {
            finish()
        }
        
        // Setup RecyclerView
        devicesGrid = findViewById(R.id.devices_grid)
        
        deviceAdapter = DeviceAdapter(roomDevices) { device, isOn ->
            onDeviceToggled(device, isOn)
        }
        
        devicesGrid.layoutManager = GridLayoutManager(this, 2)
        devicesGrid.adapter = deviceAdapter
    }
    
    /**
     * Handle device toggle events
     */
    private fun onDeviceToggled(device: Device, isOn: Boolean) {
        val status = if (isOn) "on" else "off"
        Toast.makeText(this, "${device.name} turned $status", Toast.LENGTH_SHORT).show()
        
        // Placeholder để implement (In a real app, you would send commands to the actual IoT device here)
    }
    
    /**
     * Setup click listeners
     */
    private fun setupClickListeners() {
        // Setup add device button
        findViewById<View>(R.id.add_device_button)?.setOnClickListener {
            Toast.makeText(this, "Add device feature will be implemented", Toast.LENGTH_SHORT).show()
        }
        
        // Setup navigation bar click regions
        setupNavBarClickListeners()
    }
    
    /**
     * Setup navigation bar click listeners
     */
    private fun setupNavBarClickListeners() {
        // Set up navigation bar click regions
        val bottomNavigation = findViewById<BottomNavigationView>(R.id.bottom_navigation)
        
        bottomNavigation.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_home -> {
                    finish() // Go back to home screen
                    true
                }
                R.id.nav_control -> {
                    Log.d(TAG, "Control button clicked")
                    Toast.makeText(this, "Control screen will be implemented", Toast.LENGTH_SHORT).show()
                    true
                }
                R.id.nav_camera -> {
                    Log.d(TAG, "Camera button clicked")
                    Toast.makeText(this, "Camera screen will be implemented", Toast.LENGTH_SHORT).show()
                    true
                }
                R.id.nav_notifications -> {
                    Toast.makeText(this, "Notifications screen will be implemented", Toast.LENGTH_SHORT).show()
                    true
                }
                R.id.nav_settings -> {
                    Toast.makeText(this, "Settings screen will be implemented", Toast.LENGTH_SHORT).show()
                    true
                }
                else -> false
            }
        }
    }
} 