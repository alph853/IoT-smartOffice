package com.example.iot

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
import com.google.android.material.tabs.TabLayout
import java.util.*
import kotlin.concurrent.fixedRateTimer

class ControlFragment : Fragment() {
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

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_control, container, false)
        // Initialize device data
        initializeDeviceData()
        // Initialize thresholds
        initializeThresholds()
        // Setup UI
        setupUI(view)
        // Setup click listeners
        setupClickListeners(view)
        // Setup mode control
        setupModeControl()
        // Start sensor simulation
        startSensorSimulation()
        return view
    }

    override fun onDestroyView() {
        super.onDestroyView()
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
        thresholds[DeviceType.FAN] = Threshold(28.0f, 26.0f, SensorType.TEMPERATURE)
        thresholds[DeviceType.AC] = Threshold(26.0f, 24.0f, SensorType.TEMPERATURE)
        thresholds[DeviceType.CEILING_LIGHT] = Threshold(50.0f, 70.0f, SensorType.LIGHT)
        thresholds[DeviceType.BULB] = Threshold(50.0f, 70.0f, SensorType.LIGHT)
        thresholds[DeviceType.PURIFIER] = Threshold(75.0f, 50.0f, SensorType.PM25)
    }

    private fun setupUI(view: View) {
        roomTitle = view.findViewById(R.id.room_title)
        devicesGrid = view.findViewById(R.id.devices_grid)
        temperatureValue = view.findViewById(R.id.temperature_value)
        humidityValue = view.findViewById(R.id.humidity_value)
        modeRadioGroup = view.findViewById(R.id.mode_radio_group)
        modeDescription = view.findViewById(R.id.mode_description)
        thresholdContainer = view.findViewById(R.id.threshold_container)
        disabledMessage = view.findViewById(R.id.disabled_message)
        // Setup RecyclerView
        deviceAdapter = DeviceAdapter { device, isOn ->
            onDeviceToggled(device, isOn)
        }
        devicesGrid.layoutManager = GridLayoutManager(requireContext(), 2)
        devicesGrid.adapter = deviceAdapter
        
        // Fix: cập nhật thiết bị phòng Bedroom ngay lần đầu
        deviceAdapter.updateDevices(bedroomDevices)
        
        // Setup sensor observers
        setupSensorObservers()
    }

    private fun setupSensorObservers() {
        sensorData.observe(viewLifecycleOwner) { data ->
            temperatureValue.text = String.format(Locale.US, "%.1f °C", data.temperature)
            humidityValue.text = String.format(Locale.US, "%.1f %%", data.humidity)
            if (currentMode.value == Mode.AUTO) {
                applyAutoLogic(data)
            }
        }
    }

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
        when (currentRoom) {
            getString(R.string.room_bedroom) -> {
                bedroomDevices.clear(); bedroomDevices.addAll(devices)
            }
            getString(R.string.room_living_room) -> {
                livingRoomDevices.clear(); livingRoomDevices.addAll(devices)
            }
            getString(R.string.room_kitchen) -> {
                kitchenDevices.clear(); kitchenDevices.addAll(devices)
            }
            getString(R.string.room_bathroom) -> {
                bathroomDevices.clear(); bathroomDevices.addAll(devices)
            }
        }
    }

    private fun setupClickListeners(view: View) {
        val tabLayout = view.findViewById<TabLayout>(R.id.room_tabs)
        tabLayout?.addOnTabSelectedListener(object : TabLayout.OnTabSelectedListener {
            override fun onTabSelected(tab: TabLayout.Tab?) {
                when (tab?.position) {
                    0 -> showRoom(getString(R.string.room_bedroom))
                    1 -> showRoom(getString(R.string.room_living_room))
                    2 -> showRoom(getString(R.string.room_kitchen))
                    3 -> showRoom(getString(R.string.room_bathroom))
                }
            }
            override fun onTabUnselected(tab: TabLayout.Tab?) {}
            override fun onTabReselected(tab: TabLayout.Tab?) {}
        })
        view.findViewById<View>(R.id.add_device_button)?.setOnClickListener {
            Toast.makeText(requireContext(), getString(R.string.add_device_coming_soon), Toast.LENGTH_SHORT).show()
        }
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
        if (currentMode.value != Mode.AUTO) return
        val currentDevices = getDevicesForCurrentRoom()
        var changed = false
        currentDevices.forEachIndexed { index, device ->
            val threshold = thresholds[device.type] ?: return@forEachIndexed
            when (threshold.sensorType) {
                SensorType.TEMPERATURE -> {
                    if (data.temperature >= threshold.on && !device.isOn) {
                        device.isOn = true
                        Toast.makeText(requireContext(), getString(R.string.device_auto_turned_on, device.name), Toast.LENGTH_SHORT).show()
                        deviceAdapter.notifyItemChanged(index)
                        changed = true
                    } else if (data.temperature < threshold.off && device.isOn) {
                        device.isOn = false
                        Toast.makeText(requireContext(), getString(R.string.device_auto_turned_off, device.name), Toast.LENGTH_SHORT).show()
                        deviceAdapter.notifyItemChanged(index)
                        changed = true
                    }
                }
                SensorType.LIGHT -> {
                    if (device.type == DeviceType.BULB) {
                        if (data.light < threshold.on && data.motion && !device.isOn) {
                            device.isOn = true
                            Toast.makeText(requireContext(), getString(R.string.device_auto_turned_on, device.name), Toast.LENGTH_SHORT).show()
                            deviceAdapter.notifyItemChanged(index)
                            changed = true
                        } else if ((data.light >= threshold.off || !data.motion) && device.isOn) {
                            device.isOn = false
                            Toast.makeText(requireContext(), getString(R.string.device_auto_turned_off, device.name), Toast.LENGTH_SHORT).show()
                            deviceAdapter.notifyItemChanged(index)
                            changed = true
                        }
                    } else {
                        if (data.light < threshold.on && !device.isOn) {
                            device.isOn = true
                            Toast.makeText(requireContext(), getString(R.string.device_auto_turned_on, device.name), Toast.LENGTH_SHORT).show()
                            deviceAdapter.notifyItemChanged(index)
                            changed = true
                        } else if (data.light >= threshold.off && device.isOn) {
                            device.isOn = false
                            Toast.makeText(requireContext(), getString(R.string.device_auto_turned_off, device.name), Toast.LENGTH_SHORT).show()
                            deviceAdapter.notifyItemChanged(index)
                            changed = true
                        }
                    }
                }
                SensorType.PM25 -> {
                    if (data.pm25 > threshold.on && !device.isOn) {
                        device.isOn = true
                        Toast.makeText(requireContext(), getString(R.string.device_auto_turned_on, device.name), Toast.LENGTH_SHORT).show()
                        deviceAdapter.notifyItemChanged(index)
                        changed = true
                    } else if (data.pm25 < threshold.off && device.isOn) {
                        device.isOn = false
                        Toast.makeText(requireContext(), getString(R.string.device_auto_turned_off, device.name), Toast.LENGTH_SHORT).show()
                        deviceAdapter.notifyItemChanged(index)
                        changed = true
                    }
                }
                else -> {}
            }
        }
        if (!changed) return
    }

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
        val devices = when (room) {
            getString(R.string.room_bedroom) -> bedroomDevices
            getString(R.string.room_living_room) -> livingRoomDevices
            getString(R.string.room_kitchen) -> kitchenDevices
            getString(R.string.room_bathroom) -> bathroomDevices
            else -> bedroomDevices
        }
        deviceAdapter.updateDevices(devices)
    }

    private fun getDevicesForCurrentRoom(): List<Device> {
        return when (currentRoom) {
            getString(R.string.room_bedroom) -> bedroomDevices
            getString(R.string.room_living_room) -> livingRoomDevices
            getString(R.string.room_kitchen) -> kitchenDevices
            getString(R.string.room_bathroom) -> bathroomDevices
            else -> bedroomDevices
        }
    }

    private fun saveThresholds() {
        Toast.makeText(requireContext(), getString(R.string.thresholds_saved), Toast.LENGTH_SHORT).show()
    }

    private fun startSensorSimulation() {
        sensorTimer = fixedRateTimer("sensorTimer", period = 5000) {
            val currentData = _sensorData.value ?: SensorData()
            val newTemperature = (currentData.temperature + (Math.random() * 2 - 1)).toFloat().coerceIn(15.0f, 40.0f)
            val newHumidity = (currentData.humidity + (Math.random() * 4 - 2)).toFloat().coerceIn(30.0f, 90.0f)
            Handler(Looper.getMainLooper()).post {
                _sensorData.value = SensorData(
                    temperature = newTemperature,
                    humidity = newHumidity
                )
            }
        }
    }
} 