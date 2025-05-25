package com.example.iot.ui.adapters

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.ImageView
import android.widget.TextView
import androidx.appcompat.widget.SwitchCompat
import androidx.cardview.widget.CardView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.iot.domain.models.Device
import com.example.iot.domain.models.DeviceType
import com.example.iot.domain.models.MCU
import com.example.iot.R

/**
 * Adapter for displaying IoT devices in a grid
 */
class DeviceAdapter(
    private val onToggleListener: (Device, Boolean) -> Unit
) : ListAdapter<Device, DeviceAdapter.DeviceViewHolder>(DeviceDiffCallback()) {

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
            // Set switch state without triggering listener
            deviceSwitch.setOnCheckedChangeListener(null)
            deviceSwitch.isChecked = device.isOn
            // Set switch listener (debounce, UI phản hồi ngay, callback nhẹ)
            deviceSwitch.setOnCheckedChangeListener { _, isChecked ->
                val now = System.currentTimeMillis()
                if (now - lastClickTime > 300) {
                    lastClickTime = now
                    if (device.isOn != isChecked) {
                        // UI phản hồi ngay
                        onToggleListener(device.copy(isOn = isChecked), isChecked)
                    }
                } else {
                    // revert UI nếu double click
                    deviceSwitch.isChecked = device.isOn
                }
            }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): DeviceViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.device_card_item, parent, false)
        return DeviceViewHolder(view)
    }

    override fun onBindViewHolder(holder: DeviceViewHolder, position: Int) {
        val device = getItem(position)
        holder.bind(device)
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