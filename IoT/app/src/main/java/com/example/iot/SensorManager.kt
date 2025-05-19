package com.example.iot

object SensorManager {
    private val sensors = mutableListOf<Sensor>()

    fun getSensors() = sensors
    
    fun getSensorCount() = sensors.size
    
    fun addSensor(sensor: Sensor) {
        sensors.add(sensor)
    }
    
    fun removeSensor(index: Int) {
        if (index >= 0 && index < sensors.size) {
            sensors.removeAt(index)
        }
    }

    fun updateSensor(oldSensor: Sensor, newSensor: Sensor) {
        val index = sensors.indexOf(oldSensor)
        if (index != -1) {
            sensors[index] = newSensor
        }
    }

    fun getSensorByName(name: String): Sensor? {
        return sensors.find { it.name == name }
    }
} 