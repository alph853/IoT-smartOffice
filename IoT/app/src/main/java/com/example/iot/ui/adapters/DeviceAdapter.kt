package com.example.iot.ui.adapters

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.content.res.Resources
import android.widget.*
import androidx.appcompat.widget.SwitchCompat
import androidx.cardview.widget.CardView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.iot.domain.models.Device
import com.example.iot.domain.models.DeviceType
import com.example.iot.R
import com.google.gson.JsonObject

/**
 * Adapter for displaying IoT devices in a grid
 */
class DeviceAdapter(
    private val onToggleListener: (Device, Boolean) -> Unit,
    private val onLED4RGBSetListener: ((Device) -> Unit)? = null,
    private val onModeChangedListener: ((Device, String) -> Unit)? = null
) : ListAdapter<Device, RecyclerView.ViewHolder>(DeviceDiffCallback()) {

    companion object {
        private const val VIEW_TYPE_STANDARD = 0
        private const val VIEW_TYPE_LED4RGB = 1
    }

    override fun getItemViewType(position: Int): Int {
        return when (getItem(position).type) {
            DeviceType.LED4RGB -> VIEW_TYPE_LED4RGB
            else -> VIEW_TYPE_STANDARD
        }
    }

    /**
     * ViewHolder for device items in the grid
     */
    inner class DeviceViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val deviceCard: CardView = itemView.findViewById(R.id.device_card)
        val deviceIcon: ImageView = itemView.findViewById(R.id.device_icon)
        val deviceName: TextView = itemView.findViewById(R.id.device_name)
        val deviceStatus: TextView = itemView.findViewById(R.id.device_status)
        val deviceSwitch: SwitchCompat = itemView.findViewById(R.id.device_switch)
        private var lastClickTime = 0L

        fun bind(device: Device) {
            // Set device icon
            deviceIcon.setImageResource(device.iconResId)
            // Set device name
            deviceName.text = device.name
            // Set device status text
            deviceStatus.text = if (device.isOn) deviceStatus.context.getString(R.string.turn_on) else deviceStatus.context.getString(R.string.turn_off)
            // Set device status text color
            deviceStatus.setTextColor(
                itemView.context.resources.getColor(
                    if (device.isOn) android.R.color.holo_orange_light else android.R.color.darker_gray,
                    itemView.context.theme
                )
            )

//            // Set up mode spinner
//            val modeSpinner = itemView.findViewById<Spinner>(R.id.mode_spinner)
//            modeSpinner?.let { spinner ->
//                // Set spinner selection without triggering listener
//                spinner.onItemSelectedListener = null
//                val currentMode = device.mode ?: "manual"
//                val position = resources.getStringArray(R.array.actuator_modes).indexOf(currentMode.capitalize())
//                if (position != -1) {
//                    spinner.setSelection(position)
//                }
//
//                // Set up spinner listener
//                spinner.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
//                    override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
//                        val selectedMode = parent?.getItemAtPosition(position).toString().lowercase()
//                        if (selectedMode != device.mode) {
//                            onModeChangedListener?.invoke(device, selectedMode)
//                        }
//                    }
//
//                    override fun onNothingSelected(parent: AdapterView<*>?) {}
//                }
//            }

            // Set up mode spinner
            val modeSpinner = itemView.findViewById<Spinner>(R.id.mode_spinner)
            modeSpinner?.let { spinner ->
                // Create and set custom adapter for spinner
                val adapter = ArrayAdapter.createFromResource(
                    itemView.context,
                    R.array.actuator_modes,
                    R.layout.item_spinner_mode
                ).apply {
                    setDropDownViewResource(R.layout.item_spinner_mode_dropdown)
                }
                spinner.adapter = adapter

                // Set spinner selection without triggering listener
                spinner.onItemSelectedListener = null
                val currentMode = device.mode
                val position = itemView.context.resources.getStringArray(R.array.actuator_modes)
                    .map { it.lowercase() }
                    .indexOf(currentMode.lowercase())
                if (position != -1) {
                    spinner.setSelection(position)
                }
                
                // Set up spinner listener with debounce
                spinner.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
                    override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                        val selectedMode = parent?.getItemAtPosition(position).toString()
                        if (selectedMode.lowercase() != device.mode.lowercase()) {
                            onModeChangedListener?.invoke(device, selectedMode.lowercase())
                        }
                    }
                    
                    override fun onNothingSelected(parent: AdapterView<*>?) {}
                }
            }

            // Set switch state without triggering listener
            deviceSwitch.setOnCheckedChangeListener(null)
            deviceSwitch.isChecked = device.isOn
            
            // Set switch listener with debounce
            deviceSwitch.setOnCheckedChangeListener { _, isChecked ->
                val now = System.currentTimeMillis()
                if (now - lastClickTime > 300) {
                    lastClickTime = now
                    if (device.isOn != isChecked) {
                        onToggleListener(device.copy(isOn = isChecked), isChecked)
                    }
                } else {
                    deviceSwitch.isChecked = device.isOn
                }
            }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        return when (viewType) {
            VIEW_TYPE_LED4RGB -> {
                val view = LayoutInflater.from(parent.context).inflate(R.layout.led4rgb_card_item, parent, false)
                LED4RGBViewHolder(view)
            }
            else -> {
                val view = LayoutInflater.from(parent.context).inflate(R.layout.item_actuator_control, parent, false)
                DeviceViewHolder(view)
            }
        }
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        val device = getItem(position)
        when (holder) {
            is DeviceViewHolder -> holder.bind(device)
            is LED4RGBViewHolder -> holder.bind(device)
        }
    }

    /**
     * ViewHolder for LED4RGB devices with clickable card
     */
    inner class LED4RGBViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val deviceCard: CardView = itemView.findViewById(R.id.led4rgb_card)
        val deviceIcon: ImageView = itemView.findViewById(R.id.led4rgb_icon)
        val deviceName: TextView = itemView.findViewById(R.id.led4rgb_name)
        val deviceStatus: TextView = itemView.findViewById(R.id.led4rgb_status)
        val colorPreview: View = itemView.findViewById(R.id.color_preview)
        val setButton: Button = itemView.findViewById(R.id.set_button)
        private var lastClickTime = 0L

        fun bind(device: Device) {
            // Set device icon
            deviceIcon.setImageResource(device.iconResId)
            // Set device name
            deviceName.text = device.name
            // Set device status
            deviceStatus.text = if (device.isOn) "On" else "Off"
            deviceStatus.setTextColor(
                itemView.context.resources.getColor(
                    if (device.isOn) android.R.color.holo_orange_light else android.R.color.darker_gray,
                    itemView.context.theme
                )
            )
            
            // Set color preview (you can extend Device class to store current color)
            colorPreview.backgroundTintList = android.content.res.ColorStateList.valueOf(
                if (device.isOn) android.graphics.Color.parseColor("#FF6B35") else android.graphics.Color.GRAY
            )

            // Set card click listener to open dialog
            deviceCard.setOnClickListener {
                val now = System.currentTimeMillis()
                if (now - lastClickTime > 300) {
                    lastClickTime = now
                    onLED4RGBSetListener?.invoke(device)
                }
            }
        }
    }

    /**
     * Updates the device list and refreshes the adapter
     */
    fun updateDevices(newDevices: List<Device>) {
        submitList(newDevices)
    }

    /**
     * Lọc danh sách thiết bị chỉ lấy Actuator
     */
    fun getActuators(): List<Device> {
        return getCurrentList().filter { it.isActuator() }
    }

    /**
     * Lọc danh sách thiết bị chỉ lấy Sensor
     */
    fun getSensors(): List<Device> {
        return getCurrentList().filter { it.isSensor() }
    }
}

class DeviceDiffCallback : DiffUtil.ItemCallback<Device>() {
    override fun areItemsTheSame(oldItem: Device, newItem: Device): Boolean = oldItem.id == newItem.id
    override fun areContentsTheSame(oldItem: Device, newItem: Device): Boolean = oldItem == newItem
} 