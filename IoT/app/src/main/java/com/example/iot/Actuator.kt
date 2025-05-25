package com.example.iot

data class Actuator(
    val id: Int,
    val name: String,
    val type: String,
    val device_id: Int,
    val mode: String,
    val status: String = "Online"
//    val id: String = java.util.UUID.randomUUID().toString()
)
