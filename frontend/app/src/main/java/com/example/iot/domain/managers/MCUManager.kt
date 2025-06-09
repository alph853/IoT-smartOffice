package com.example.iot.domain.managers

import com.example.iot.domain.models.MCU

object MCUManager {
    private val mcus = mutableListOf<MCU>()

    fun getMCUs() = mcus
    
    fun getMCUCount() = mcus.size
    
    fun addMCU(mcu: MCU) {
        mcus.add(mcu)
    }
    
    fun removeMCU(index: Int) {
        if (index >= 0 && index < mcus.size) {
            mcus.removeAt(index)
        }
    }

    fun updateMCU(oldMCU: MCU, newMCU: MCU) {
        val index = mcus.indexOf(oldMCU)
        if (index != -1) {
            mcus[index] = newMCU
        }
    }

    fun getMCUByName(name: String): MCU? {
        return mcus.find { it.name == name }
    }
} 