package com.example.iot

data class Sensor(
    var id: String,
    var name: String,
    var type: String,
    var unit: String?,
    var device_id: String,
    var status: String = "Online",
//    val id: String = java.util.UUID.randomUUID().toString()
) 