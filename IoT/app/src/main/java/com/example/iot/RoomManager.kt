package com.example.iot

/**
 * Singleton class to manage room data across activity recreations
 */
object RoomManager {
    // The shared list of rooms
    private val roomList = mutableListOf<Room>()

    // Get the current list of rooms
    fun getRooms(): MutableList<Room> {
        return roomList
    }

    fun getRoomByID(id: Int): Room? {
        return roomList.find { it.id == id }
    }

    // Add a new room
    fun addRoom(room: Room) {
        roomList.add(room)
    }

    // Remove a room at specified position
    fun removeRoom(position: Int) {
        if (position >= 0 && position < roomList.size) {
            roomList.removeAt(position)
        }
    }

    // Clear all rooms
    fun clearRooms() {
        roomList.clear()
    }

    // Get count of rooms
    fun getRoomCount(): Int {
        return roomList.size
    }
}