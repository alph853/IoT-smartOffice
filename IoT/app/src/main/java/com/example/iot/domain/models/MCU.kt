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
import com.example.iot.domain.models.Sensor
import com.example.iot.domain.models.Actuator


data class Component(
    var name: String = "Component Name",
    var type: String = "Component Type",
    var status: Boolean = true // true = active (green), false = inactive (red)
)

data class MCU(
    var id: Int,
    var name: String,
    var registered_at: String,
    var mac_addr: String,
    var description: String,
    var location: String,
    var fw_version: String,
    var last_seen_at: String,
    var model: String,
    var office_id: Int,
    var gateway_id: Int,
    var status: String,
    var access_token: String?,
    var sensors: MutableList<Sensor> = mutableListOf(),
    var actuators: MutableList<Actuator> = mutableListOf(),
    var components: MutableList<Component> = mutableListOf() // Keep for backward compatibility
) {
    // Secondary constructor for backward compatibility
    constructor() : this(
        id = 0,
        name = "New MCU",
        registered_at = "Not registered",
        mac_addr = "Not set",
        description = "New Device",
        location = "Unknown",
        fw_version = "1.0.0",
        last_seen_at = "Never",
        model = "Default Model",
        office_id = 0,
        gateway_id = 0,
        status = "Online",
        access_token = null,
        sensors = mutableListOf(),
        actuators = mutableListOf(),
        components = mutableListOf()
    )
}

data class MCUUpdateRequest(
    val name: String,
    val description: String,
    val fw_version: String,
    val model: String,
    val office_id: Int,
    val gateway_id: Int,
    val status: String,
    val access_token: String?,
    val last_seen_at: String,
    val actuators: MutableList<Actuator>,
    val sensors: MutableList<Sensor>
)