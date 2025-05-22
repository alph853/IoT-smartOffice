package com.example.iot

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

class ControlActivity : AppCompatActivity() {
    
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
    private val _currentMode = MutableLiveData(Mode.MANUAL)
    private val currentMode: LiveData<Mode> = _currentMode
    
    // Sensor data
    private val _sensorData = MutableLiveData(SensorData())
    private val sensorData: LiveData<SensorData> = _sensorData
    
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
        
        setContentView(R.layout.activity_control)
        
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
    
    private fun setupSensorObservers() {
        sensorData.observe(this) { data ->
            // Update UI
            temperatureValue.text = String.format(Locale.US, "%.1f °C", data.temperature)
            humidityValue.text = String.format(Locale.US, "%.1f %%", data.humidity)
            
            // If in auto mode, apply auto logic
            if (currentMode.value == Mode.AUTO) {
                applyAutoLogic(data)
            }
        }
    }
    
    private fun onDeviceToggled(device: Device, isOn: Boolean) {
        // Only process in manual mode
        if (currentMode.value != Mode.MANUAL) return
        
        val status = if (isOn) "on" else "off"
        Toast.makeText(this, "${device.name} turned $status", Toast.LENGTH_SHORT).show()
    }
    
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
    
    private fun setupModeControl() {
        modeRadioGroup.setOnCheckedChangeListener { _, checkedId ->
            when (checkedId) {
                R.id.mode_manual -> {
                    _currentMode.value = Mode.MANUAL
                    modeDescription.text = getString(R.string.mode_manual_desc)
                    thresholdContainer.visibility = View.GONE
                    disabledMessage.visibility = View.GONE
                    devicesGrid.visibility = View.VISIBLE
                }
                R.id.mode_auto -> {
                    _currentMode.value = Mode.AUTO
                    modeDescription.text = getString(R.string.mode_auto_desc)
                    thresholdContainer.visibility = View.VISIBLE
                    disabledMessage.visibility = View.GONE
                    devicesGrid.visibility = View.GONE
                    applyAutoLogic(sensorData.value ?: SensorData())
                }
                R.id.mode_disabled -> {
                    _currentMode.value = Mode.DISABLED
                    modeDescription.text = getString(R.string.mode_disabled_desc)
                    thresholdContainer.visibility = View.GONE
                    disabledMessage.visibility = View.VISIBLE
                    devicesGrid.visibility = View.GONE
                    disableAllDevices()
                }
            }
        }
    }
    
    private fun applyAutoLogic(data: SensorData) {
        // Only apply in AUTO mode
        if (currentMode.value != Mode.AUTO) return

        val currentDevices = getDevicesForCurrentRoom()
        var changed = false
        currentDevices.forEachIndexed { index, device ->
            val threshold = thresholds[device.type] ?: return@forEachIndexed
            when (threshold.sensorType) {
                SensorType.TEMPERATURE -> {
                    if (data.temperature >= threshold.on && !device.isOn) {
                        device.isOn = true
                        Toast.makeText(this, "[AUTO] ${device.name} turned on", Toast.LENGTH_SHORT).show()
                        deviceAdapter.notifyItemChanged(index)
                        changed = true
                    } else if (data.temperature < threshold.off && device.isOn) {
                        device.isOn = false
                        Toast.makeText(this, "[AUTO] ${device.name} turned off", Toast.LENGTH_SHORT).show()
                        deviceAdapter.notifyItemChanged(index)
                        changed = true
                    }
                }
                SensorType.LIGHT -> {
                    if (device.type == DeviceType.BULB) {
                        if (data.light < threshold.on && data.motion && !device.isOn) {
                            device.isOn = true
                            Toast.makeText(this, "[AUTO] ${device.name} turned on", Toast.LENGTH_SHORT).show()
                            deviceAdapter.notifyItemChanged(index)
                            changed = true
                        } else if ((data.light >= threshold.off || !data.motion) && device.isOn) {
                            device.isOn = false
                            Toast.makeText(this, "[AUTO] ${device.name} turned off", Toast.LENGTH_SHORT).show()
                            deviceAdapter.notifyItemChanged(index)
                            changed = true
                        }
                    } else {
                        if (data.light < threshold.on && !device.isOn) {
                            device.isOn = true
                            Toast.makeText(this, "[AUTO] ${device.name} turned on", Toast.LENGTH_SHORT).show()
                            deviceAdapter.notifyItemChanged(index)
                            changed = true
                        } else if (data.light >= threshold.off && device.isOn) {
                            device.isOn = false
                            Toast.makeText(this, "[AUTO] ${device.name} turned off", Toast.LENGTH_SHORT).show()
                            deviceAdapter.notifyItemChanged(index)
                            changed = true
                        }
                    }
                }
                SensorType.PM25 -> {
                    if (data.pm25 > threshold.on && !device.isOn) {
                        device.isOn = true
                        Toast.makeText(this, "[AUTO] ${device.name} turned on", Toast.LENGTH_SHORT).show()
                        deviceAdapter.notifyItemChanged(index)
                        changed = true
                    } else if (data.pm25 < threshold.off && device.isOn) {
                        device.isOn = false
                        Toast.makeText(this, "[AUTO] ${device.name} turned off", Toast.LENGTH_SHORT).show()
                        deviceAdapter.notifyItemChanged(index)
                        changed = true
                    }
                }
                else -> {}
            }
        }
        // Nếu không có gì thay đổi, không cần notifyDataSetChanged
        if (!changed) return
    }
    
    private fun disableAllDevices() {
        getDevicesForCurrentRoom().forEachIndexed { index, device ->
            if (device.isOn) {
                device.isOn = false
                Toast.makeText(this, "${device.name} turned off", Toast.LENGTH_SHORT).show()
                deviceAdapter.notifyItemChanged(index)
            }
        }
    }
    
    private fun showRoom(room: String) {
        currentRoom = room
        roomTitle.text = room
        // Update device list based on room
        val devices = when (room) {
            "Bedroom" -> bedroomDevices
            "Living Room" -> livingRoomDevices
            "Kitchen" -> kitchenDevices
            "Bathroom" -> bathroomDevices
            else -> bedroomDevices
        }
        deviceAdapter.updateDevices(devices)
    }
    
    private fun getDevicesForCurrentRoom(): List<Device> {
        return when (currentRoom) {
            "Bedroom" -> bedroomDevices
            "Living Room" -> livingRoomDevices
            "Kitchen" -> kitchenDevices
            "Bathroom" -> bathroomDevices
            else -> bedroomDevices
        }
    }
    
    private fun saveThresholds() {
        // In a real app, you would save the thresholds to persistent storage
        Toast.makeText(this, "Thresholds saved", Toast.LENGTH_SHORT).show()
    }
    
    private fun startSensorSimulation() {
        sensorTimer = fixedRateTimer("sensorTimer", period = 5000) {
            // Simulate sensor data changes
            val currentData = _sensorData.value ?: SensorData()
            val newTemperature = (currentData.temperature + (Math.random() * 2 - 1)).toFloat().coerceIn(15.0f, 40.0f)
            val newHumidity = (currentData.humidity + (Math.random() * 4 - 2)).toFloat().coerceIn(30.0f, 90.0f)
            
            runOnUiThread {
                _sensorData.value = SensorData(
                    temperature = newTemperature,
                    humidity = newHumidity
                )
            }
        }
    }
    
    private fun setupNavBarClickListeners() {
        val bottomNavigation = findViewById<BottomNavigationView>(R.id.bottom_navigation)
        
        bottomNavigation.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_home -> {
                    finish() // Go back to home screen
                    true
                }
                R.id.nav_control -> {
                    Toast.makeText(this, "Already on Control screen", Toast.LENGTH_SHORT).show()
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
} 