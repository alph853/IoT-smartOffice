package com.example.iot

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