package com.example.iot.fragments

import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.fragment.app.Fragment
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.iot.domain.models.Device
import com.example.iot.domain.models.DeviceType
import com.example.iot.domain.models.Mode
import com.example.iot.domain.models.Room
import com.example.iot.domain.managers.RoomManager
import com.example.iot.domain.models.SensorData
import com.example.iot.domain.models.SensorType
import com.example.iot.domain.models.Threshold
import com.google.android.material.tabs.TabLayout
import java.util.*
import kotlin.concurrent.fixedRateTimer
import com.example.iot.ui.adapters.DeviceAdapter
import com.example.iot.R
import com.example.iot.domain.models.MCU
import com.example.iot.domain.models.Component

/**
 * ControlFragment - Displays and controls actuators from all devices (MCUs) in each room
 * Shows room tabs dynamically based on actual office rooms from JSON data
 * Each room displays all actuators from all devices in that room for control purposes
 */
class ControlFragment : Fragment() {
    // Dynamic room devices map
    private val roomDevicesMap = mutableMapOf<String, MutableList<Device>>()
    private var roomsList = mutableListOf<Room>()

    // Device adapter
    private lateinit var deviceAdapter: DeviceAdapter

    // UI references
    private lateinit var roomTitle: TextView
    private lateinit var devicesGrid: RecyclerView
//    private var temperatureValue: TextView? = null
//    private var humidityValue: TextView? = null
    private lateinit var modeRadioGroup: RadioGroup
    private lateinit var modeDescription: TextView
    private lateinit var thresholdContainer: LinearLayout
    private lateinit var disabledMessage: TextView
    private lateinit var tabLayout: TabLayout

    // Current selected room
    private var currentRoom = ""

    // Current mode
    private val _currentMode = MutableLiveData(Mode.MANUAL)
    private val currentMode: LiveData<Mode> = _currentMode

    // Sensor data
//    private val _sensorData = MutableLiveData(SensorData())
//    private val sensorData: LiveData<SensorData> = _sensorData

    // Thresholds map
    private val thresholds = mutableMapOf<DeviceType, Threshold>()

    // Timer for sensor simulation
//    private var sensorTimer: Timer? = null

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_control, container, false)
        
        try {
            // Initialize device data from RoomManager
            initializeDeviceDataFromRooms()
            // Initialize thresholds
            initializeThresholds()
            // Setup UI
            setupUI(view)
            // Setup dynamic tabs
            setupDynamicTabs()
            // Setup click listeners
            setupClickListeners(view)
            // Setup mode control
            setupModeControl()
            // Start sensor simulation
//            startSensorSimulation()
        } catch (e: Exception) {
            e.printStackTrace()
            // Return a simple view if there's an error
            return inflater.inflate(android.R.layout.simple_list_item_1, container, false)
        }
        
        return view
    }

    override fun onDestroyView() {
        super.onDestroyView()
//        sensorTimer?.cancel()
    }

    private fun initializeDeviceDataFromRooms() {
        try {
            roomDevicesMap.clear()
            roomsList.clear()
            
            val rooms = RoomManager.getRooms()
            if (rooms.isEmpty()) {
                return // No rooms available
            }
            
            roomsList.addAll(rooms)
            
            roomsList.forEach { room ->
                val devices = mutableListOf<Device>()
                
                // Convert only actuators from all MCU devices in the room to Device objects for control
                room.devices.forEach { mcu ->
                    // Add only actuators as controllable devices (skip sensors)
                    mcu.actuators.forEach { actuator ->
                        val deviceType = when (actuator.type.lowercase()) {
                            "fan" -> DeviceType.FAN
                            "led4rgb", "led", "light", "indicator" -> DeviceType.BULB
                            "lighting" -> DeviceType.CEILING_LIGHT
                            "ac", "air_conditioner" -> DeviceType.AC
                            "purifier" -> DeviceType.PURIFIER
                            else -> DeviceType.BULB
                        }
                        
                        val iconRes = when (actuator.type.lowercase()) {
                            "fan" -> R.drawable.ic_fan
                            "led4rgb" -> R.drawable.ic_bulb // We could use ic_led4rgb if it exists
                            "led", "light", "indicator" -> R.drawable.ic_bulb
                            "lighting" -> R.drawable.ic_ceiling_light
                            "ac", "air_conditioner" -> R.drawable.ic_ac
                            "purifier" -> R.drawable.ic_purifier
                            else -> R.drawable.ic_bulb
                        }
                        
                        devices.add(Device(
                            id = "actuator_${actuator.id}",
                            name = actuator.name,
                            type = deviceType,
                            iconResId = iconRes,
                            isOn = false, // Default to off
                            room = room.name
                        ))
                    }
                }
                
                roomDevicesMap[room.name] = devices
            }
        } catch (e: Exception) {
            e.printStackTrace()
            // Ensure we have empty but valid data structures
            roomDevicesMap.clear()
            roomsList.clear()
        }
    }

    private fun initializeThresholds() {
        thresholds[DeviceType.FAN] = Threshold(28.0f, 26.0f, SensorType.TEMPERATURE)
        thresholds[DeviceType.AC] = Threshold(26.0f, 24.0f, SensorType.TEMPERATURE)
        thresholds[DeviceType.CEILING_LIGHT] = Threshold(50.0f, 70.0f, SensorType.LIGHT)
        thresholds[DeviceType.BULB] = Threshold(50.0f, 70.0f, SensorType.LIGHT)
        thresholds[DeviceType.PURIFIER] = Threshold(75.0f, 50.0f, SensorType.PM25)
    }

    private fun setupUI(view: View) {
        roomTitle = view.findViewById(R.id.room_title)
        devicesGrid = view.findViewById(R.id.devices_grid)
//        temperatureValue = view.findViewById(R.id.temperature_value) // May be null if sensor group is not included
//        humidityValue = view.findViewById(R.id.humidity_value) // May be null if sensor group is not included
        modeRadioGroup = view.findViewById(R.id.mode_radio_group)
        modeDescription = view.findViewById(R.id.mode_description)
        thresholdContainer = view.findViewById(R.id.threshold_container)
        disabledMessage = view.findViewById(R.id.disabled_message)
        tabLayout = view.findViewById(R.id.room_tabs)
        // Setup RecyclerView
        deviceAdapter = DeviceAdapter { device, isOn ->
            onDeviceToggled(device, isOn)
        }
        devicesGrid.layoutManager = GridLayoutManager(requireContext(), 2)
        devicesGrid.adapter = deviceAdapter
        
        // Setup sensor observers
//        setupSensorObservers()
    }

//    private fun setupSensorObservers() {
//        sensorData.observe(viewLifecycleOwner) { data ->
//            temperatureValue?.text = String.format(Locale.US, "%.1f °C", data.temperature)
//            humidityValue?.text = String.format(Locale.US, "%.1f %%", data.humidity)
//            if (currentMode.value == Mode.AUTO) {
//                applyAutoLogic(data)
//            }
//        }
//    }

    private fun onDeviceToggled(device: Device, isOn: Boolean) {
        if (currentMode.value != Mode.MANUAL) return
        val status = if (isOn) getString(R.string.device_turned_on, device.name) else getString(R.string.device_turned_off, device.name)
        Toast.makeText(requireContext(), status, Toast.LENGTH_SHORT).show()
        // Clone list mới và update trạng thái thiết bị
        val devices = getDevicesForCurrentRoom().map {
            if (it.id == device.id) it.copy(isOn = isOn) else it
        }
        deviceAdapter.updateDevices(devices)
        // Nếu cần, cập nhật lại list gốc cho phòng hiện tại
        roomDevicesMap[currentRoom]?.clear()
        roomDevicesMap[currentRoom]?.addAll(devices)
    }

    private fun setupClickListeners(view: View) {
        tabLayout?.addOnTabSelectedListener(object : TabLayout.OnTabSelectedListener {
            override fun onTabSelected(tab: TabLayout.Tab?) {
                val position = tab?.position ?: 0
                if (position < roomsList.size) {
                    showRoom(roomsList[position].name)
                }
            }
            override fun onTabUnselected(tab: TabLayout.Tab?) {}
            override fun onTabReselected(tab: TabLayout.Tab?) {}
        })
        view.findViewById<Button>(R.id.save_thresholds_button)?.setOnClickListener {
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
//                    applyAutoLogic(sensorData.value ?: SensorData())
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

//    private fun applyAutoLogic(data: SensorData) {
//        if (currentMode.value != Mode.AUTO) return
//        val currentDevices = getDevicesForCurrentRoom()
//        var changed = false
//        currentDevices.forEachIndexed { index, device ->
//            val threshold = thresholds[device.type] ?: return@forEachIndexed
//            when (threshold.sensorType) {
//                SensorType.TEMPERATURE -> {
//                    if (data.temperature >= threshold.on && !device.isOn) {
//                        device.isOn = true
//                        Toast.makeText(requireContext(), getString(R.string.device_auto_turned_on, device.name), Toast.LENGTH_SHORT).show()
//                        deviceAdapter.notifyItemChanged(index)
//                        changed = true
//                    } else if (data.temperature < threshold.off && device.isOn) {
//                        device.isOn = false
//                        Toast.makeText(requireContext(), getString(R.string.device_auto_turned_off, device.name), Toast.LENGTH_SHORT).show()
//                        deviceAdapter.notifyItemChanged(index)
//                        changed = true
//                    }
//                }
//                SensorType.LIGHT -> {
//                    if (device.type == DeviceType.BULB) {
//                        if (data.light < threshold.on && data.motion && !device.isOn) {
//                            device.isOn = true
//                            Toast.makeText(requireContext(), getString(R.string.device_auto_turned_on, device.name), Toast.LENGTH_SHORT).show()
//                            deviceAdapter.notifyItemChanged(index)
//                            changed = true
//                        } else if ((data.light >= threshold.off || !data.motion) && device.isOn) {
//                            device.isOn = false
//                            Toast.makeText(requireContext(), getString(R.string.device_auto_turned_off, device.name), Toast.LENGTH_SHORT).show()
//                            deviceAdapter.notifyItemChanged(index)
//                            changed = true
//                        }
//                    } else {
//                        if (data.light < threshold.on && !device.isOn) {
//                            device.isOn = true
//                            Toast.makeText(requireContext(), getString(R.string.device_auto_turned_on, device.name), Toast.LENGTH_SHORT).show()
//                            deviceAdapter.notifyItemChanged(index)
//                            changed = true
//                        } else if (data.light >= threshold.off && device.isOn) {
//                            device.isOn = false
//                            Toast.makeText(requireContext(), getString(R.string.device_auto_turned_off, device.name), Toast.LENGTH_SHORT).show()
//                            deviceAdapter.notifyItemChanged(index)
//                            changed = true
//                        }
//                    }
//                }
//                SensorType.PM25 -> {
//                    if (data.pm25 > threshold.on && !device.isOn) {
//                        device.isOn = true
//                        Toast.makeText(requireContext(), getString(R.string.device_auto_turned_on, device.name), Toast.LENGTH_SHORT).show()
//                        deviceAdapter.notifyItemChanged(index)
//                        changed = true
//                    } else if (data.pm25 < threshold.off && device.isOn) {
//                        device.isOn = false
//                        Toast.makeText(requireContext(), getString(R.string.device_auto_turned_off, device.name), Toast.LENGTH_SHORT).show()
//                        deviceAdapter.notifyItemChanged(index)
//                        changed = true
//                    }
//                }
//                else -> {}
//            }
//        }
//        if (!changed) return
//    }

    private fun disableAllDevices() {
        getDevicesForCurrentRoom().forEachIndexed { index, device ->
            if (device.isOn) {
                device.isOn = false
                Toast.makeText(requireContext(), getString(R.string.device_turned_off, device.name), Toast.LENGTH_SHORT).show()
                deviceAdapter.notifyItemChanged(index)
            }
        }
    }

    private fun showRoom(room: String) {
        currentRoom = room
        roomTitle.text = room
        val devices = roomDevicesMap[room] ?: mutableListOf()
        deviceAdapter.updateDevices(devices)
    }

    private fun getDevicesForCurrentRoom(): List<Device> {
        return roomDevicesMap[currentRoom] ?: mutableListOf()
    }

    private fun saveThresholds() {
        Toast.makeText(requireContext(), getString(R.string.thresholds_saved), Toast.LENGTH_SHORT).show()
    }

//    private fun startSensorSimulation() {
//        sensorTimer = fixedRateTimer("sensorTimer", period = 5000) {
//            val currentData = _sensorData.value ?: SensorData()
//            val newTemperature = (currentData.temperature + (Math.random() * 2 - 1)).toFloat().coerceIn(15.0f, 40.0f)
//            val newHumidity = (currentData.humidity + (Math.random() * 4 - 2)).toFloat().coerceIn(30.0f, 90.0f)
//            Handler(Looper.getMainLooper()).post {
//                _sensorData.value = SensorData(
//                    temperature = newTemperature,
//                    humidity = newHumidity
//                )
//            }
//        }
//    }

    private fun setupDynamicTabs() {
        try {
            tabLayout?.removeAllTabs()
            
            if (roomsList.isEmpty()) {
                // If no rooms available, add a default tab
                tabLayout?.addTab(tabLayout.newTab().setText("No Rooms"))
                return
            }
            
            roomsList.forEach { room ->
                tabLayout?.addTab(tabLayout.newTab().setText(room.name))
            }
            
            // Set the first room as current if available
            if (roomsList.isNotEmpty()) {
                currentRoom = roomsList[0].name
                roomTitle.text = currentRoom
                deviceAdapter.updateDevices(roomDevicesMap[currentRoom] ?: mutableListOf())
            }
        } catch (e: Exception) {
            e.printStackTrace()
            // Fallback: add a default tab
            tabLayout?.addTab(tabLayout.newTab().setText("Error"))
        }
    }

    companion object {
        fun newInstance() = ControlFragment()
    }
}
