package com.example.iot

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
} 