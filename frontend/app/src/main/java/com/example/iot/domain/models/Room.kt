package com.example.iot.domain.models

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.iot.R

data class Room(
    var id: Int,
    var room: String,
    var building: String,
    var description: String,
    var name: String,
    var devices: MutableList<MCU> = mutableListOf()
) {
    // Secondary constructor for backward compatibility
    constructor() : this(
        id = 0,
        room = "Unknown",
        building = "Unknown",
        description = "No description",
        name = "New Room",
        devices = mutableListOf()
    )

    val deviceCount: Int
        get() = devices.size

    fun addMCU(mcu: MCU) {
        devices.add(mcu)
    }

    fun removeMCU(mcu: MCU) {
        devices.remove(mcu)
    }

    fun updateMCU(oldMCU: MCU, updatedMCU: MCU) {
        val index = devices.indexOfFirst { it.id == oldMCU.id }
        if (index != -1) {
            devices[index] = updatedMCU.copy(id = oldMCU.id)
        }
    }

    fun getMCUs(): List<MCU> = devices.toList()

    fun clearMCUs() {
        devices.clear()
    }
}