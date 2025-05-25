package com.example.iot

object ActuatorManager {
    private val actuators = mutableListOf<Actuator>()

    fun getActuators() = actuators

    fun getActuatorCount() = actuators.size

    fun addActuator(actuator: Actuator) {
        actuators.add(actuator)
    }

    fun removeActuator(index: Int) {
        if (index >= 0 && index < actuators.size) {
            actuators.removeAt(index)
        }
    }

    fun updateActuator(oldActuator: Actuator, newActuator: Actuator) {
        val index = actuators.indexOf(oldActuator)
        if (index != -1) {
            actuators[index] = newActuator
        }
    }

    fun getActuatorByName(name: String): Actuator? {
        return actuators.find { it.name == name }
    }
}