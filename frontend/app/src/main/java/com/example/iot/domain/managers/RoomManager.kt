package com.example.iot.domain.managers

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.iot.domain.models.Room

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