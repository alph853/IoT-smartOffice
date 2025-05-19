package com.example.iot

data class Component(
    var name: String = "Component Name",
    var type: String = "Component Type",
    var status: Boolean = true // true = active (green), false = inactive (red)
)

data class MCU(
    var name: String = "New MCU",
    var description: String = "New Device",
    var status: String = "Online",
    var location: String = "Not set",
    var registerAt: String = "Not registered",
    var macAddress: String = "Not set",
    var firmwareVersion: String = "1.0.0",
    var lastSeenAs: String = "Never",
    var model: String = "Default Model",
    val id: String = java.util.UUID.randomUUID().toString(),
    var components: MutableList<Component> = mutableListOf()
) 