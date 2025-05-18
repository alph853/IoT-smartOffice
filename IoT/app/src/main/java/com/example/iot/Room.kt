package com.example.iot

data class Room(
    var name: String = "Room",
    var description: String = "Building",
    private val mcuList: MutableList<MCU> = mutableListOf()
) {
    val deviceCount: Int
        get() = mcuList.size

    fun addMCU(mcu: MCU) {
        mcuList.add(mcu)
    }

    fun removeMCU(mcu: MCU) {
        mcuList.remove(mcu)
    }

    fun updateMCU(oldMCU: MCU, updatedMCU: MCU) {
        val index = mcuList.indexOfFirst { it.id == oldMCU.id }
        if (index != -1) {
            mcuList[index] = updatedMCU.copy(id = oldMCU.id)
        }
    }

    fun getMCUs(): List<MCU> = mcuList.toList()

    fun clearMCUs() {
        mcuList.clear()
    }
} 