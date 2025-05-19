package com.example.iot

data class Sensor(
    var name: String = "New Sensor",
    var type: String = "Type",
    var status: String = "Online",
    val id: String = java.util.UUID.randomUUID().toString()
) 