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
import com.example.iot.domain.models.Room
import com.example.iot.domain.managers.RoomManager
import com.example.iot.domain.models.SensorData
import com.example.iot.domain.models.SensorType
import com.example.iot.domain.models.Threshold
import com.google.android.material.tabs.TabLayout
import java.util.*
import kotlin.concurrent.fixedRateTimer
import com.example.iot.ui.adapters.DeviceAdapter
import com.example.iot.ui.adapters.MCUAdapterControl
import com.example.iot.R
import com.example.iot.domain.models.MCU
import com.example.iot.domain.models.Component
import com.example.iot.domain.managers.WebSocketManager
import okhttp3.*
import java.io.IOException

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
    private lateinit var thresholdContainer: LinearLayout
    private lateinit var disabledMessage: TextView
    private lateinit var tabLayout: TabLayout
    private lateinit var mcuGrid: RecyclerView

    // Current selected room
    private var currentRoom = ""

    // Sensor data
//    private val _sensorData = MutableLiveData(SensorData())
//    private val sensorData: LiveData<SensorData> = _sensorData

    // Thresholds map
    private val thresholds = mutableMapOf<DeviceType, Threshold>()

    // Timer for sensor simulation
//    private var sensorTimer: Timer? = null

    private lateinit var mcuAdapter: MCUAdapterControl
    private val roomMcusMap = mutableMapOf<String, MutableList<MCU>>()

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_control, container, false)
        
        try {
            // Initialize device data from RoomManager
            initializeDeviceDataFromRooms()
            // Initialize MCU data
            initializeMcuData()
            // Initialize thresholds
            initializeThresholds()
            // Setup UI
            setupUI(view)
            // Setup dynamic tabs
            setupDynamicTabs()
            // Setup click listeners
            setupClickListeners(view)
            // Register WebSocket device update callback
            WebSocketManager.setOnDeviceUpdateListener {
                requireActivity().runOnUiThread {
                    // Reinitialize all data
                    initializeDeviceDataFromRooms()
                    initializeMcuData()
                    setupDynamicTabs()
                    
                    // Update the current room's devices if we have a selected room
                    if (currentRoom.isNotEmpty()) {
                        showRoom(currentRoom)
                    }
                    
                    // Notify adapters of data changes
                    deviceAdapter.notifyDataSetChanged()
                    mcuAdapter.notifyDataSetChanged()
                }
            }
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
                            "led4rgb" -> DeviceType.LED4RGB
                            "led", "light", "indicator" -> DeviceType.BULB
                            "lighting" -> DeviceType.CEILING_LIGHT
                            "ac", "air_conditioner" -> DeviceType.AC
                            "purifier" -> DeviceType.PURIFIER
                            else -> DeviceType.BULB
                        }
                          val iconRes = when (actuator.type.lowercase()) {
                            "fan" -> R.drawable.ic_fan
                            "led4rgb" -> R.drawable.ic_led4rgb
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
                            room = room.name,
                            mode = actuator.mode // Copy mode from actuator
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

    private fun initializeMcuData() {
        try {
            roomMcusMap.clear()
            
            roomsList.forEach { room ->
                val mcus = mutableListOf<MCU>()
                room.devices.forEach { mcu ->
                    mcus.add(mcu)
                }
                roomMcusMap[room.name] = mcus
                // Debug log
                android.util.Log.d("ControlFragment", "Room ${room.name} has ${mcus.size} MCUs")
            }
        } catch (e: Exception) {
            e.printStackTrace()
            android.util.Log.e("ControlFragment", "Error initializing MCU data: ${e.message}")
            roomMcusMap.clear()
        }
    }

    private fun initializeThresholds() {
        thresholds[DeviceType.FAN] = Threshold(28.0f, 26.0f, SensorType.TEMPERATURE)
        thresholds[DeviceType.AC] = Threshold(26.0f, 24.0f, SensorType.TEMPERATURE)
        thresholds[DeviceType.CEILING_LIGHT] = Threshold(50.0f, 70.0f, SensorType.LIGHT)
        thresholds[DeviceType.BULB] = Threshold(50.0f, 70.0f, SensorType.LIGHT)
        thresholds[DeviceType.LED4RGB] = Threshold(50.0f, 70.0f, SensorType.LIGHT)
        thresholds[DeviceType.PURIFIER] = Threshold(75.0f, 50.0f, SensorType.PM25)
    }

    private fun setupUI(view: View) {
        roomTitle = view.findViewById(R.id.room_title)
        devicesGrid = view.findViewById(R.id.devices_grid)
//        temperatureValue = view.findViewById(R.id.temperature_value) // May be null if sensor group is not included
//        humidityValue = view.findViewById(R.id.humidity_value) // May be null if sensor group is not included
//        thresholdContainer = view.findViewById(R.id.threshold_container)
//        disabledMessage = view.findViewById(R.id.disabled_message)
        tabLayout = view.findViewById(R.id.room_tabs)
        mcuGrid = view.findViewById(R.id.mcu_grid)

        // Setup RecyclerView for devices
        deviceAdapter = DeviceAdapter(
            onToggleListener = { device, isOn ->
                onDeviceToggled(device, isOn)
            },
            onLED4RGBSetListener = { device ->
                onLED4RGBSet(device)
            },
            onModeChangedListener = { device, newMode ->
                onDeviceModeChanged(device, newMode)
            }
        )
        devicesGrid.layoutManager = GridLayoutManager(requireContext(), 2)
        devicesGrid.adapter = deviceAdapter
        
        // Setup RecyclerView for MCUs
        mcuGrid.layoutManager = GridLayoutManager(context, 2)
        mcuAdapter = MCUAdapterControl(emptyList()) { mcu, isOn ->
            onMcuToggled(mcu, isOn)
        }
        mcuGrid.adapter = mcuAdapter
        
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

    private fun onLED4RGBSet(device: Device) {
        showColorPickerDialog(device)
    }
    
    // Data class to store RGB values
    private data class RGBColor(var red: Int = 255, var green: Int = 0, var blue: Int = 0)

    private fun showColorPickerDialog(device: Device) {
        // Store colors for each LED
        val ledColors = arrayOf(
            RGBColor(), // LED 1 initial red
            RGBColor(0, 255, 0), // LED 2 initial green
            RGBColor(0, 0, 255), // LED 3 initial blue
            RGBColor(255, 255, 255) // LED 4 initial white
        )
        var currentBrightness = 100

        val dialog = android.app.AlertDialog.Builder(requireContext())
            .setView(R.layout.dialog_led4rgb)
            .create()

        dialog.show()

        // Get dialog views
        val brightnessInput = dialog.findViewById<com.google.android.material.textfield.TextInputEditText>(R.id.brightness_input)
        val color1Button = dialog.findViewById<Button>(R.id.color1_button)
        val color2Button = dialog.findViewById<Button>(R.id.color2_button)
        val color3Button = dialog.findViewById<Button>(R.id.color3_button)
        val color4Button = dialog.findViewById<Button>(R.id.color4_button)
        val btnCancel = dialog.findViewById<Button>(R.id.btn_cancel)
        val btnConfirm = dialog.findViewById<Button>(R.id.btn_confirm)
        
        // Set initial brightness value and button colors
        brightnessInput?.setText("100")
        color1Button?.backgroundTintList = android.content.res.ColorStateList.valueOf(
            android.graphics.Color.rgb(ledColors[0].red, ledColors[0].green, ledColors[0].blue))
        color2Button?.backgroundTintList = android.content.res.ColorStateList.valueOf(
            android.graphics.Color.rgb(ledColors[1].red, ledColors[1].green, ledColors[1].blue))
        color3Button?.backgroundTintList = android.content.res.ColorStateList.valueOf(
            android.graphics.Color.rgb(ledColors[2].red, ledColors[2].green, ledColors[2].blue))
        color4Button?.backgroundTintList = android.content.res.ColorStateList.valueOf(
            android.graphics.Color.rgb(ledColors[3].red, ledColors[3].green, ledColors[3].blue))

        // Color picker listener for buttons
        val showColorPicker = { button: Button, index: Int ->
            // Create dialog with custom layout
            val pickerDialog = android.app.AlertDialog.Builder(requireContext())
                .setView(R.layout.dialog_rgb_picker)
                .create()

            pickerDialog.show()

            // Get views from the picker dialog
            val redInput = pickerDialog.findViewById<com.google.android.material.textfield.TextInputEditText>(R.id.red_input)
            val greenInput = pickerDialog.findViewById<com.google.android.material.textfield.TextInputEditText>(R.id.green_input)
            val blueInput = pickerDialog.findViewById<com.google.android.material.textfield.TextInputEditText>(R.id.blue_input)
            val colorPreview = pickerDialog.findViewById<View>(R.id.color_preview)
            val btnCancelRgb = pickerDialog.findViewById<Button>(R.id.btn_cancel_rgb)
            val btnConfirmRgb = pickerDialog.findViewById<Button>(R.id.btn_confirm_rgb)

            // Set initial RGB values from stored colors
            redInput?.setText(ledColors[index].red.toString())
            greenInput?.setText(ledColors[index].green.toString())
            blueInput?.setText(ledColors[index].blue.toString())

            // Update preview when any input changes
            val updatePreview = {
                try {
                    val red = redInput?.text.toString().toIntOrNull() ?: 0
                    val green = greenInput?.text.toString().toIntOrNull() ?: 0
                    val blue = blueInput?.text.toString().toIntOrNull() ?: 0

                    if (red in 0..255 && green in 0..255 && blue in 0..255) {
                        val color = android.graphics.Color.rgb(red, green, blue)
                        colorPreview?.setBackgroundColor(color)
                    }
                } catch (e: Exception) {
                    // Invalid input, ignore
                }
            }

            // Add text change listeners
            redInput?.addTextChangedListener(object : android.text.TextWatcher {
                override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
                override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
                override fun afterTextChanged(s: android.text.Editable?) { updatePreview() }
            })

            greenInput?.addTextChangedListener(object : android.text.TextWatcher {
                override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
                override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
                override fun afterTextChanged(s: android.text.Editable?) { updatePreview() }
            })

            blueInput?.addTextChangedListener(object : android.text.TextWatcher {
                override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
                override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
                override fun afterTextChanged(s: android.text.Editable?) { updatePreview() }
            })

            // Initialize color preview
            updatePreview()

            btnCancelRgb?.setOnClickListener {
                pickerDialog.dismiss()
            }

            btnConfirmRgb?.setOnClickListener {
                try {
                    val red = redInput?.text.toString().toIntOrNull() ?: 0
                    val green = greenInput?.text.toString().toIntOrNull() ?: 0
                    val blue = blueInput?.text.toString().toIntOrNull() ?: 0

                    if (red !in 0..255 || green !in 0..255 || blue !in 0..255) {
                        Toast.makeText(requireContext(), "RGB values must be between 0 and 255", Toast.LENGTH_SHORT).show()
                        return@setOnClickListener
                    }

                    // Save the colors
                    ledColors[index].red = red
                    ledColors[index].green = green
                    ledColors[index].blue = blue

                    // Update button color
                    val color = android.graphics.Color.rgb(red, green, blue)
                    button.backgroundTintList = android.content.res.ColorStateList.valueOf(color)
                    pickerDialog.dismiss()
                } catch (e: Exception) {
                    Toast.makeText(requireContext(), "Invalid RGB values", Toast.LENGTH_SHORT).show()
                }
            }
        }

        // Set button click listeners with their indices
        color1Button?.setOnClickListener { showColorPicker(color1Button, 0) }
        color2Button?.setOnClickListener { showColorPicker(color2Button, 1) }
        color3Button?.setOnClickListener { showColorPicker(color3Button, 2) }
        color4Button?.setOnClickListener { showColorPicker(color4Button, 3) }

        btnCancel?.setOnClickListener {
            dialog.dismiss()
        }

        btnConfirm?.setOnClickListener {
            // Validate brightness input
            val brightnessText = brightnessInput?.text?.toString()
            if (brightnessText.isNullOrEmpty()) {
                Toast.makeText(requireContext(), "Please enter brightness value", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            try {
                currentBrightness = brightnessText.toInt()
                if (currentBrightness !in 0..100) {
                    Toast.makeText(requireContext(), "Brightness must be between 0 and 100", Toast.LENGTH_SHORT).show()
                    return@setOnClickListener
                }
            } catch (e: NumberFormatException) {
                Toast.makeText(requireContext(), "Invalid brightness value", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            // Create the WebSocket message
            val colors = ledColors.map { listOf(it.red, it.green, it.blue) }
            val jsonMessage = com.google.gson.JsonObject().apply {
                addProperty("method", "setLighting")
                add("params", com.google.gson.JsonObject().apply {
                    addProperty("actuator_id", device.id.split("_")[1].toInt())
                    addProperty("brightness", currentBrightness)
                    add("color", com.google.gson.JsonArray().apply {
                        colors.forEach { rgbList ->
                            add(com.google.gson.JsonArray().apply {
                                rgbList.forEach { add(it) }
                            })
                        }
                    })
                })
            }

            // Send the message via WebSocket
            WebSocketManager.sendMessage(jsonMessage)

            // Update device state
            val isOn = currentBrightness > 0
            val updatedDevice = device.copy(isOn = isOn)
            
            // Update the device in the list
            val devices = getDevicesForCurrentRoom().map {
                if (it.id == device.id) updatedDevice else it
            }
            deviceAdapter.updateDevices(devices)
            
            // Update the source list
            roomDevicesMap[currentRoom]?.clear()
            roomDevicesMap[currentRoom]?.addAll(devices)
            
            // Show feedback
            val feedbackMessage = if (isOn) {
                val colorsStr = ledColors.mapIndexed { index, rgb -> 
                    "L${index + 1}(${rgb.red},${rgb.green},${rgb.blue})"
                }.joinToString(", ")
                "LED ${device.name} set to [$colorsStr] at ${currentBrightness}% brightness"
            } else {
                "LED ${device.name} turned off"
            }
            Toast.makeText(requireContext(), feedbackMessage, Toast.LENGTH_SHORT).show()
            
            dialog.dismiss()
        }
    }    private fun onDeviceToggled(device: Device, isOn: Boolean) {
        when (device.type) {
            DeviceType.FAN -> {
                WebSocketManager.sendMessage(com.google.gson.JsonObject().apply {
                    addProperty("method", "setFanState")
                    add("params", com.google.gson.JsonObject().apply {
                        addProperty("actuator_id", device.id.split("_")[1].toInt())
                        addProperty("state", isOn)
                    })
                })
            }
            else -> return
        }
        
        // Update device state and UI
        val devices = getDevicesForCurrentRoom().map {
            if (it.id == device.id) it.copy(isOn = isOn) else it
        }
        deviceAdapter.updateDevices(devices)
        roomDevicesMap[currentRoom]?.clear()
        roomDevicesMap[currentRoom]?.addAll(devices)
        
        // Show feedback
        Toast.makeText(
            requireContext(),
            if (isOn) getString(R.string.device_turned_on, device.name)
            else getString(R.string.device_turned_off, device.name),
            Toast.LENGTH_SHORT
        ).show()
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
//        view.findViewById<Button>(R.id.save_thresholds_button)?.setOnClickListener {
//            saveThresholds()
//        }
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

    private fun showRoom(roomName: String) {
        currentRoom = roomName
        roomTitle.text = roomName

        // Update devices
        val devices = roomDevicesMap[roomName] ?: emptyList()
        deviceAdapter.updateDevices(devices)

        // Update MCUs
        val mcus = roomMcusMap[roomName] ?: emptyList()
        mcuAdapter = MCUAdapterControl(mcus) { mcu, isOn ->
            onMcuToggled(mcu, isOn)
        }
        mcuGrid.adapter = mcuAdapter
    }

    private fun getDevicesForCurrentRoom(): List<Device> {
        return roomDevicesMap[currentRoom] ?: emptyList()
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
                showRoom(currentRoom)
            }
        } catch (e: Exception) {
            e.printStackTrace()
            // Fallback: add a default tab
            tabLayout?.addTab(tabLayout.newTab().setText("Error"))
        }
    }

    private fun onMcuToggled(mcu: MCU, isOn: Boolean) {
        val url = if (isOn) {
            "https://10diemiot.ngrok.io/devices/enable/${mcu.id}"
        } else {
            "https://10diemiot.ngrok.io/devices/disable/${mcu.id}"
        }
        val client = OkHttpClient()
        val request = Request.Builder()
            .url(url)
            .post(RequestBody.create(null, ByteArray(0)))
            .build()
        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                requireActivity().runOnUiThread {
                    Toast.makeText(requireContext(), "Failed to ${if (isOn) "enable" else "disable"} MCU: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
            override fun onResponse(call: Call, response: Response) {
                requireActivity().runOnUiThread {
                    if (response.isSuccessful) {
                        // Update MCU state and UI
                        val mcus = getMcusForCurrentRoom().map {
                            if (it.id == mcu.id) it.copy(status = if (isOn) "Online" else "Offline") else it
                        }
                        mcuAdapter = MCUAdapterControl(mcus) { mcu, isOn ->
                            onMcuToggled(mcu, isOn)
                        }
                        mcuGrid.adapter = mcuAdapter
                        roomMcusMap[currentRoom]?.clear()
                        roomMcusMap[currentRoom]?.addAll(mcus)
                        Toast.makeText(requireContext(), "MCU ${if (isOn) "enabled" else "disabled"}", Toast.LENGTH_SHORT).show()
                    } else {
                        Toast.makeText(requireContext(), "Failed to ${if (isOn) "enable" else "disable"} MCU", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        })
    }

    private fun getMcusForCurrentRoom(): List<MCU> {
        return roomMcusMap[currentRoom] ?: emptyList()
    }

    private fun onDeviceModeChanged(device: Device, newMode: String) {
        // Update device mode in the list
        val devices = getDevicesForCurrentRoom().map {
            if (it.id == device.id) it.copy(mode = newMode) else it
        }
        deviceAdapter.updateDevices(devices)
        roomDevicesMap[currentRoom]?.clear()
        roomDevicesMap[currentRoom]?.addAll(devices)

        // Send mode change to WebSocket
        WebSocketManager.sendMessage(com.google.gson.JsonObject().apply {
            addProperty("method", "setMode")
            add("params", com.google.gson.JsonObject().apply {
                addProperty("actuator_id", device.id.split("_")[1].toInt())
                addProperty("mode", newMode.lowercase())
            })
        })

        // Show feedback
        Toast.makeText(
            requireContext(),
            "${device.name} mode changed to $newMode",
            Toast.LENGTH_SHORT
        ).show()
    }

    companion object {
        fun newInstance() = ControlFragment()
    }
}
