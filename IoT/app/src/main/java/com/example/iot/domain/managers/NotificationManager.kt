package com.example.iot.domain.managers

import com.example.iot.data.viewmodels.Notification

/**
 * Singleton class to manage notification data across activity recreations
 */
object NotificationManager {
    // The shared list of notifications
    private val notificationList = mutableListOf<Notification>()

    // Get the current list of notifications
    fun getNotifications(): MutableList<Notification> {
        return notificationList
    }

    fun getNotificationByID(id: Int): Notification? {
        return notificationList.find { it.id == id }
    }

    // Add a new notification
    fun addNotification(notification: Notification) {
        notificationList.add(notification)
    }

    // Remove a notification at specified position
    fun removeNotification(position: Int) {
        if (position >= 0 && position < notificationList.size) {
            notificationList.removeAt(position)
        }
    }

    // Remove notification by ID
    fun removeNotificationByID(id: Int) {
        notificationList.removeAll { it.id == id }
    }

    // Clear all notifications
    fun clearNotifications() {
        notificationList.clear()
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
    }

    // Mark all notifications as unread
    fun markAllAsUnread() {
        notificationList.forEach { it.read_status = false }
    }
} 