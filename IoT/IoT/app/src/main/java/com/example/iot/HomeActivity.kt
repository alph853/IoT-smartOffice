package com.example.iot

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.tabs.TabLayout
import com.google.android.material.bottomnavigation.BottomNavigationView
import java.util.*
import kotlin.concurrent.fixedRateTimer

class HomeActivity : AppCompatActivity() {
    
    companion object {
        private const val TAG = "HomeActivity"
    }
    
    // Room devices lists
    private val bedroomDevices = mutableListOf<Device>()
    private val livingRoomDevices = mutableListOf<Device>()
    private val kitchenDevices = mutableListOf<Device>()
    private val bathroomDevices = mutableListOf<Device>()
    
    // Device adapter
    private lateinit var deviceAdapter: DeviceAdapter
    
    // UI references
    private lateinit var roomTitle: TextView
    private lateinit var devicesGrid: RecyclerView
    private lateinit var temperatureValue: TextView
    private lateinit var humidityValue: TextView
    private lateinit var modeRadioGroup: RadioGroup
    private lateinit var modeDescription: TextView
    private lateinit var thresholdContainer: LinearLayout
    private lateinit var disabledMessage: TextView
    
    // Current selected room
    private var currentRoom = "Bedroom"
    
    // Current mode
    private val _currentMode = MutableLiveData<Mode>(Mode.MANUAL)
    val currentMode: LiveData<Mode> = _currentMode
    
    // Sensor data
    private val _sensorData = MutableLiveData(SensorData())
    val sensorData: LiveData<SensorData> = _sensorData
    
    // Thresholds map
    private val thresholds = mutableMapOf<DeviceType, Threshold>()
    
    // Timer for sensor simulation
    private var sensorTimer: Timer? = null
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Make the app draw edge-to-edge
        WindowCompat.setDecorFitsSystemWindows(window, false)
        
        // Hide the status bar
        val windowInsetsController = WindowCompat.getInsetsController(window, window.decorView)
        windowInsetsController.hide(WindowInsetsCompat.Type.statusBars())
        windowInsetsController.systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        
        setContentView(R.layout.activity_home)
        
        // Initialize device data
        initializeDeviceData()
        
        // Initialize thresholds
        initializeThresholds()
        
        // Setup UI
        setupUI()
        
        // Setup click listeners
        setupClickListeners()
        
        // Setup mode control
        setupModeControl()
        
        // Start sensor simulation
        startSensorSimulation()
    }
    
    override fun onDestroy() {
        super.onDestroy()
        sensorTimer?.cancel()
    }
    
    /**
     * Initialize mock device data for all rooms
     */
    private fun initializeDeviceData() {
        // Bedroom devices
        bedroomDevices.add(Device("bed_fan", "Fan", DeviceType.FAN, R.drawable.ic_fan, false, "bedroom"))
        bedroomDevices.add(Device("bed_ac", "AC", DeviceType.AC, R.drawable.ic_ac, true, "bedroom"))
        bedroomDevices.add(Device("bed_ceiling", "Ceiling Light", DeviceType.CEILING_LIGHT, R.drawable.ic_ceiling_light, true, "bedroom"))
        bedroomDevices.add(Device("bed_bulb", "Bulb", DeviceType.BULB, R.drawable.ic_bulb, false, "bedroom"))
        bedroomDevices.add(Device("bed_purifier", "Purifier", DeviceType.PURIFIER, R.drawable.ic_purifier, false, "bedroom"))
        bedroomDevices.add(Device("bed_climate", "Climate", DeviceType.CLIMATE, R.drawable.ic_climate, true, "bedroom"))
        
        // Living room devices
        livingRoomDevices.add(Device("living_fan", "Fan", DeviceType.FAN, R.drawable.ic_fan, true, "living_room"))
        livingRoomDevices.add(Device("living_ac", "AC", DeviceType.AC, R.drawable.ic_ac, false, "living_room"))
        livingRoomDevices.add(Device("living_ceiling", "Ceiling Light", DeviceType.CEILING_LIGHT, R.drawable.ic_ceiling_light, true, "living_room"))
        livingRoomDevices.add(Device("living_bulb", "Bulb", DeviceType.BULB, R.drawable.ic_bulb, true, "living_room"))
        
        // Kitchen devices
        kitchenDevices.add(Device("kitchen_fan", "Fan", DeviceType.FAN, R.drawable.ic_fan, false, "kitchen"))
        kitchenDevices.add(Device("kitchen_ceiling", "Ceiling Light", DeviceType.CEILING_LIGHT, R.drawable.ic_ceiling_light, true, "kitchen"))
        kitchenDevices.add(Device("kitchen_bulb", "Bulb", DeviceType.BULB, R.drawable.ic_bulb, true, "kitchen"))
        
        // Bathroom devices
        bathroomDevices.add(Device("bath_fan", "Fan", DeviceType.FAN, R.drawable.ic_fan, false, "bathroom"))
        bathroomDevices.add(Device("bath_ceiling", "Ceiling Light", DeviceType.CEILING_LIGHT, R.drawable.ic_ceiling_light, false, "bathroom"))
        bathroomDevices.add(Device("bath_bulb", "Bulb", DeviceType.BULB, R.drawable.ic_bulb, false, "bathroom"))
    }
    
    /**
     * Initialize default thresholds for devices
     */
    private fun initializeThresholds() {
        // FAN: bật khi Temp ≥ 28°C, tắt khi Temp < 26°C
        thresholds[DeviceType.FAN] = Threshold(28.0f, 26.0f, SensorType.TEMPERATURE)
        
        // AC: bật khi Temp ≥ 26°C, tắt khi Temp < 24°C
        thresholds[DeviceType.AC] = Threshold(26.0f, 24.0f, SensorType.TEMPERATURE)
        
        // Ceiling Light: bật khi Lux < 50, tắt khi Lux ≥ 70
        thresholds[DeviceType.CEILING_LIGHT] = Threshold(50.0f, 70.0f, SensorType.LIGHT)
        
        // Bulb: bật khi Lux < 50 và có motion=true
        thresholds[DeviceType.BULB] = Threshold(50.0f, 70.0f, SensorType.LIGHT)
        
        // Purifier: bật khi PM2.5 > 75, tắt khi PM2.5 < 50
        thresholds[DeviceType.PURIFIER] = Threshold(75.0f, 50.0f, SensorType.PM25)
    }
    
    /**
     * Setup UI elements
     */
    private fun setupUI() {
        // Get UI references
        roomTitle = findViewById(R.id.room_title)
        devicesGrid = findViewById(R.id.devices_grid)
        temperatureValue = findViewById(R.id.temperature_value)
        humidityValue = findViewById(R.id.humidity_value)
        modeRadioGroup = findViewById(R.id.mode_radio_group)
        modeDescription = findViewById(R.id.mode_description)
        thresholdContainer = findViewById(R.id.threshold_container)
        disabledMessage = findViewById(R.id.disabled_message)
        
        // Setup RecyclerView
        deviceAdapter = DeviceAdapter(bedroomDevices) { device, isOn ->
            onDeviceToggled(device, isOn)
        }
        
        devicesGrid.layoutManager = GridLayoutManager(this, 2)
        devicesGrid.adapter = deviceAdapter
        
        // Setup sensor observers
        setupSensorObservers()
    }
    
    /**
     * Setup observers for sensor data
     */
    private fun setupSensorObservers() {
        sensorData.observe(this) { data ->
            // Update UI
            temperatureValue.text = String.format("%.1f °C", data.temperature)
            humidityValue.text = String.format("%.1f %%", data.humidity)
            
            // If in auto mode, apply auto logic
            if (currentMode.value == Mode.AUTO) {
                applyAutoLogic(data)
            }
        }
    }
    
    /**
     * Handle device toggle events
     */
    private fun onDeviceToggled(device: Device, isOn: Boolean) {
        // Only process in manual mode
        if (currentMode.value != Mode.MANUAL) return
        
        val status = if (isOn) "on" else "off"
        Toast.makeText(this, "${device.name} turned $status", Toast.LENGTH_SHORT).show()
        
        // In a real app, you would send commands to the actual IoT device here
    }
    
    /**
     * Setup click listeners for tabs and buttons
     */
    private fun setupClickListeners() {
        // Setup room tabs selection listener
        val tabLayout = findViewById<TabLayout>(R.id.room_tabs)
        tabLayout?.addOnTabSelectedListener(object : TabLayout.OnTabSelectedListener {
            override fun onTabSelected(tab: TabLayout.Tab?) {
                when (tab?.position) {
                    0 -> showRoom("Bedroom")
                    1 -> showRoom("Living Room")
                    2 -> showRoom("Kitchen")
                    3 -> showRoom("Bathroom")
                }
            }

            override fun onTabUnselected(tab: TabLayout.Tab?) {
                // Not needed
            }

            override fun onTabReselected(tab: TabLayout.Tab?) {
                // Not needed
            }
        })
        
        // Setup add device button
        findViewById<View>(R.id.add_device_button)?.setOnClickListener {
            Toast.makeText(this, "Add device feature will be implemented", Toast.LENGTH_SHORT).show()
        }
        
        // Setup navigation bar click regions
        setupNavBarClickListeners()
        
        // Setup save thresholds button
        findViewById<Button>(R.id.save_thresholds_button)?.setOnClickListener {
            saveThresholds()
        }
    }
    
    /**
     * Save threshold values from UI
     */
    private fun saveThresholds() {
        try {
            // Get values from EditTexts
            val fanOnTemp = findViewById<EditText>(R.id.fan_on_threshold).text.toString().toFloat()
            val fanOffTemp = findViewById<EditText>(R.id.fan_off_threshold).text.toString().toFloat()
            thresholds[DeviceType.FAN] = Threshold(fanOnTemp, fanOffTemp, SensorType.TEMPERATURE)
            
            val acOnTemp = findViewById<EditText>(R.id.ac_on_threshold).text.toString().toFloat()
            val acOffTemp = findViewById<EditText>(R.id.ac_off_threshold).text.toString().toFloat()
            thresholds[DeviceType.AC] = Threshold(acOnTemp, acOffTemp, SensorType.TEMPERATURE)
            
            val lightOnLux = findViewById<EditText>(R.id.light_on_threshold).text.toString().toFloat()
            val lightOffLux = findViewById<EditText>(R.id.light_off_threshold).text.toString().toFloat()
            thresholds[DeviceType.CEILING_LIGHT] = Threshold(lightOnLux, lightOffLux, SensorType.LIGHT)
            
            // Apply auto logic immediately
            applyAutoLogic(sensorData.value ?: SensorData())
            
            Toast.makeText(this, "Thresholds saved successfully", Toast.LENGTH_SHORT).show()
        } catch (e: Exception) {
            Toast.makeText(this, "Error saving thresholds: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }
    
    /**
     * Setup mode control UI and logic
     */
    private fun setupModeControl() {
        modeRadioGroup.setOnCheckedChangeListener { _, checkedId ->
            when (checkedId) {
                R.id.mode_manual -> {
                    _currentMode.value = Mode.MANUAL
                    modeDescription.text = "Manual mode: Toggle devices on/off manually"
                    thresholdContainer.visibility = View.GONE
                    disabledMessage.visibility = View.GONE
                    devicesGrid.visibility = View.VISIBLE
                }
                R.id.mode_auto -> {
                    _currentMode.value = Mode.AUTO
                    modeDescription.text = "Auto mode: Devices activate based on sensor thresholds"
                    thresholdContainer.visibility = View.VISIBLE
                    disabledMessage.visibility = View.GONE
                    devicesGrid.visibility = View.GONE
                    
                    // Apply auto logic immediately
                    applyAutoLogic(sensorData.value ?: SensorData())
                }
                R.id.mode_disabled -> {
                    _currentMode.value = Mode.DISABLED
                    modeDescription.text = "Disabled mode: All devices are turned off"
                    thresholdContainer.visibility = View.GONE
                    disabledMessage.visibility = View.VISIBLE
                    devicesGrid.visibility = View.GONE
                    
                    // Turn off all devices
                    disableAllDevices()
                }
            }
        }
    }
    
    /**
     * Apply auto logic based on sensor data and thresholds
     */
    private fun applyAutoLogic(data: SensorData) {
        // Only apply in AUTO mode
        if (currentMode.value != Mode.AUTO) return
        
        val currentDevices = when (currentRoom) {
            "Bedroom" -> bedroomDevices
            "Living Room" -> livingRoomDevices
            "Kitchen" -> kitchenDevices
            "Bathroom" -> bathroomDevices
            else -> bedroomDevices
        }
        
        for (device in currentDevices) {
            val threshold = thresholds[device.type] ?: continue
            
            when (threshold.sensorType) {
                SensorType.TEMPERATURE -> {
                    if (data.temperature >= threshold.on && !device.isOn) {
                        device.isOn = true
                        notifyDeviceChange(device, true)
                    } else if (data.temperature < threshold.off && device.isOn) {
                        device.isOn = false
                        notifyDeviceChange(device, false)
                    }
                }
                SensorType.LIGHT -> {
                    if (device.type == DeviceType.BULB) {
                        // Bulb requires both light threshold and motion
                        if (data.light < threshold.on && data.motion && !device.isOn) {
                            device.isOn = true
                            notifyDeviceChange(device, true)
                        } else if ((data.light >= threshold.off || !data.motion) && device.isOn) {
                            device.isOn = false
                            notifyDeviceChange(device, false)
                        }
                    } else {
                        // Regular light control
                        if (data.light < threshold.on && !device.isOn) {
                            device.isOn = true
                            notifyDeviceChange(device, true)
                        } else if (data.light >= threshold.off && device.isOn) {
                            device.isOn = false
                            notifyDeviceChange(device, false)
                        }
                    }
                }
                SensorType.PM25 -> {
                    if (data.pm25 > threshold.on && !device.isOn) {
                        device.isOn = true
                        notifyDeviceChange(device, true)
                    } else if (data.pm25 < threshold.off && device.isOn) {
                        device.isOn = false
                        notifyDeviceChange(device, false)
                    }
                }
                else -> {
                    // Other sensor types not implemented yet
                }
            }
        }
        
        // Notify adapter to update UI
        deviceAdapter.notifyDataSetChanged()
    }
    
    /**
     * Notify device state change
     */
    private fun notifyDeviceChange(device: Device, isOn: Boolean) {
        val status = if (isOn) "on" else "off"
        Toast.makeText(this, "[AUTO] ${device.name} turned $status", Toast.LENGTH_SHORT).show()
    }
    
    /**
     * Disable all devices
     */
    private fun disableAllDevices() {
        // Turn off all devices in all rooms
        val allDevices = bedroomDevices + livingRoomDevices + kitchenDevices + bathroomDevices
        for (device in allDevices) {
            if (device.isOn) {
                device.isOn = false
                Toast.makeText(this, "[DISABLED] ${device.name} turned off", Toast.LENGTH_SHORT).show()
            }
        }
        
        // Notify adapter to update UI
        deviceAdapter.notifyDataSetChanged()
    }
    
    /**
     * Show the selected room and its devices
     */
    private fun showRoom(roomName: String) {
        currentRoom = roomName
        roomTitle.text = roomName
        
        // Update device list in adapter based on selected room
        when (roomName) {
            "Bedroom" -> deviceAdapter.updateDevices(bedroomDevices)
            "Living Room" -> deviceAdapter.updateDevices(livingRoomDevices)
            "Kitchen" -> deviceAdapter.updateDevices(kitchenDevices)
            "Bathroom" -> deviceAdapter.updateDevices(bathroomDevices)
        }
        
        // If in AUTO mode, apply auto logic with current sensor data
        if (currentMode.value == Mode.AUTO) {
            applyAutoLogic(sensorData.value ?: SensorData())
        }
    }
    
    /**
     * Sets up the click listeners for the navigation bar components
     */
    private fun setupNavBarClickListeners() {
        val bottomNavigation = findViewById<BottomNavigationView>(R.id.bottom_navigation)
        
        bottomNavigation.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_home -> {
                    Toast.makeText(this, "Already on Home screen", Toast.LENGTH_SHORT).show()
                    true
                }
                R.id.nav_control -> {
                    Toast.makeText(this, "Control screen will be implemented", Toast.LENGTH_SHORT).show()
                    true
                }
                R.id.nav_camera -> {
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
    
    /**
     * Start sensor simulation timer
     */
    private fun startSensorSimulation() {
        sensorTimer = fixedRateTimer("sensor-timer", period = 5000) {
            // Generate realistic sensor values with some fluctuation
            val currentData = _sensorData.value ?: SensorData()
            val tempChange = (Math.random() * 0.4 - 0.2).toFloat()
            val humidityChange = (Math.random() * 2 - 1).toFloat()
            val lightChange = (Math.random() * 10 - 5).toFloat()
            val pm25Change = (Math.random() * 5 - 2.5).toFloat()
            val motionChance = Math.random() > 0.7 // 30% chance of motion
            
            val newData = SensorData(
                temperature = currentData.temperature + tempChange,
                humidity = (currentData.humidity + humidityChange).coerceIn(20f, 90f),
                light = (currentData.light + lightChange).coerceIn(10f, 200f),
                pm25 = (currentData.pm25 + pm25Change).coerceIn(10f, 150f),
                motion = motionChance
            )
            
            runOnUiThread {
                _sensorData.value = newData
            }
        }
    }
    
    /**
     * Navigates to the room detail screen
     */
    private fun navigateToRoomDetail(roomName: String) {
        val intent = Intent(this, RoomDetailActivity::class.java)
        intent.putExtra("ROOM_NAME", roomName)
        intent.putExtra("ROOM_LOCATION", "A4 Building")
        intent.putExtra("ACTIVE_DEVICES", 3)
        startActivity(intent)
    }
} 