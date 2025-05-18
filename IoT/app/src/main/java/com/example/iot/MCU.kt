package com.example.iot

data class MCU(
    var name: String = "New MCU",
    var description: String = "New Device",
    var mode: String = "Manual",
    var status: String = "Online",
    var location: String = "Not set",
    var registerAt: String = "Not registered",
    var macAddress: String = "Not set",
    var firmwareVersion: String = "1.0.0",
    var lastSeenAs: String = "Never",
    var model: String = "Default Model"
) 