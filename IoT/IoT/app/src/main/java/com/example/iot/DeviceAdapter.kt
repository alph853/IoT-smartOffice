package com.example.iot

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.appcompat.widget.SwitchCompat
import androidx.cardview.widget.CardView
import androidx.recyclerview.widget.RecyclerView

/**
 * Adapter for displaying IoT devices in a grid
 */
class DeviceAdapter(
    private var devices: List<Device>,
    private val onToggleListener: (Device, Boolean) -> Unit
) : RecyclerView.Adapter<DeviceAdapter.DeviceViewHolder>() {

    /**
     * ViewHolder for device items in the grid
     */
    class DeviceViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val deviceCard: CardView = itemView.findViewById(R.id.device_card)
        val deviceIcon: ImageView = itemView.findViewById(R.id.device_icon)
        val deviceName: TextView = itemView.findViewById(R.id.device_name)
        val deviceStatus: TextView = itemView.findViewById(R.id.device_status)
        val deviceSwitch: SwitchCompat = itemView.findViewById(R.id.device_switch)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): DeviceViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.device_card_item, parent, false)
        return DeviceViewHolder(view)
    }

    override fun onBindViewHolder(holder: DeviceViewHolder, position: Int) {
        val device = devices[position]
        
        // Set device icon
        holder.deviceIcon.setImageResource(device.iconResId)
        
        // Set device name
        holder.deviceName.text = device.name
        
        // Set device status text
        holder.deviceStatus.text = if (device.isOn) holder.deviceStatus.context.getString(R.string.turn_on) else holder.deviceStatus.context.getString(R.string.turn_off)
        
        // Set device status text color
        holder.deviceStatus.setTextColor(
            holder.itemView.context.resources.getColor(
                if (device.isOn) android.R.color.holo_orange_light else android.R.color.darker_gray,
                holder.itemView.context.theme
            )
        )
        
        // Set switch state without triggering listener
        holder.deviceSwitch.setOnCheckedChangeListener(null)
        holder.deviceSwitch.isChecked = device.isOn
        
        // Set switch listener
        holder.deviceSwitch.setOnCheckedChangeListener { _, isChecked ->
            if (device.isOn != isChecked) {
                device.isOn = isChecked
                onToggleListener(device, isChecked)
            }
        }
    }

    override fun getItemCount(): Int = devices.size
    
    /**
     * Updates the device list and refreshes the adapter
     */
    fun updateDevices(newDevices: List<Device>) {
        if (devices.size == newDevices.size && devices.map { it.id } == newDevices.map { it.id }) {
            devices.forEachIndexed { index, device ->
                if (device != newDevices[index]) {
                    devices = newDevices
                    notifyItemChanged(index)
                }
            }
        } else {
            devices = newDevices
            if (devices.size != newDevices.size) notifyDataSetChanged()
        }
    }

    /**
     * Lọc danh sách thiết bị chỉ lấy Actuator
     */
    fun getActuators(): List<Device> {
        return devices.filter { it.isActuator() }
    }

    /**
     * Lọc danh sách thiết bị chỉ lấy Sensor
     */
    fun getSensors(): List<Device> {
        return devices.filter { it.isSensor() }
    }
} 