package com.example.iot.domain.managers

import android.os.Handler
import android.os.Looper
import com.example.iot.data.viewmodels.Notification

/**
 * Singleton class to manage notification data across activity recreations
 */
object NotificationManager {
    // The shared list of notifications
    private val notificationList = mutableListOf<Notification>()
    
    // Listeners for notification updates
    private val listeners = mutableListOf<() -> Unit>()
    
    // Handler to ensure listener notifications happen on main thread
    private val mainHandler = Handler(Looper.getMainLooper())

    // Get the current list of notifications
    fun getNotifications(): MutableList<Notification> {
        return notificationList
    }

    fun getNotificationByID(id: Int): Notification? {
        return notificationList.find { it.id == id }
    }    // Add a new notification
    fun addNotification(notification: Notification) {
        // Add to the beginning of the list to show newest first
        notificationList.add(0, notification)
        android.util.Log.d("NotificationManager", "Added notification: ${notification.title}, Total: ${notificationList.size}")
        notifyListeners()
    }

    // Update an existing notification
    fun updateNotification(notification: Notification) {
        val index = notificationList.indexOfFirst { it.id == notification.id }
        if (index != -1) {
            notificationList[index] = notification
            notifyListeners()
        }
    }

    // Delete a notification
    fun deleteNotification(notification: Notification) {
        notificationList.removeAll { it.id == notification.id }
        notifyListeners()
    }

    // Remove a notification at specified position
    fun removeNotification(position: Int) {
        if (position >= 0 && position < notificationList.size) {
            notificationList.removeAt(position)
            notifyListeners()
        }
    }

    // Remove notification by ID
    fun removeNotificationByID(id: Int) {
        notificationList.removeAll { it.id == id }
        notifyListeners()
    }

    // Clear all notifications
    fun clearNotifications() {
        notificationList.clear()
        notifyListeners()
    }

    // Get count of notifications
    fun getNotificationCount(): Int {
        return notificationList.size
    }

    // Get unread notifications count
    fun getUnreadCount(): Int {
        return notificationList.count { !it.read_status }
    }

    // Mark all notifications as read
    fun markAllAsRead() {
        notificationList.forEach { it.read_status = true }
        notifyListeners()
    }

    // Mark all notifications as unread
    fun markAllAsUnread() {
        notificationList.forEach { it.read_status = false }
        notifyListeners()
    }
    
    // Add a listener for notification updates
    fun addListener(listener: () -> Unit) {
        listeners.add(listener)
    }

    // Remove a listener
    fun removeListener(listener: () -> Unit) {
        listeners.remove(listener)
    }    // Notify all listeners of changes
    private fun notifyListeners() {
        android.util.Log.d("NotificationManager", "Notifying ${listeners.size} listeners")
        mainHandler.post {
            listeners.forEach { it() }
        }
    }
}