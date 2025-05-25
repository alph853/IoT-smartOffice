package com.example.iot.data.viewmodels

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.map
import com.example.iot.domain.managers.NotificationManager

enum class NotificationFilter { ALL, READ, UNREAD }

class NotificationViewModel : ViewModel() {
    private val _notifications = MutableLiveData<List<Notification>>(emptyList())
    private val _filter = MutableLiveData(NotificationFilter.ALL)

    val filteredNotifications: LiveData<List<Notification>> = _notifications.map { list ->
        val filtered = when (_filter.value) {
            NotificationFilter.READ -> list.filter { it.read_status }
            NotificationFilter.UNREAD -> list.filter { !it.read_status }
            else -> list
        }
        // Sort by ID descending (newest first, assuming higher ID = newer)
        filtered.sortedByDescending { it.id }
    }

    fun setFilter(filter: NotificationFilter) {
        _filter.value = filter
        // Trigger update
        _notifications.value = _notifications.value
    }

    fun loadNotifications() {
        _notifications.value = NotificationManager.getNotifications().toList()
    }

    fun loadSampleNotifications() {
        _notifications.value = listOf(
            Notification(5, "Kiểm tra thiết bị lọc không khí trong phòng họp. Bộ lọc cần được thay thế.", false, "reminder", "Nhắc nhở bảo trì", 3, "12:00 24-05-2025"),
            Notification(4, "Hệ thống đã cập nhật thành công lên phiên bản mới nhất.", true, "system", "Cập nhật hệ thống", 0, "11:00 24-05-2025"),
            Notification(3, "Nhiệt độ phòng khách vượt ngưỡng 30°C! Vui lòng kiểm tra hệ thống điều hòa.", false, "alert", "Cảnh báo nhiệt độ cao", 2, "10:00 24-05-2025"),
            Notification(2, "Thiết bị cảm biến nhiệt độ DHT20 đã được thêm vào phòng 101.", false, "device", "Thiết bị mới được thêm", 1, "09:15 24-05-2025"),
            Notification(1, "Chào mừng bạn đến với hệ thống IoT. Hệ thống đã sẵn sàng để sử dụng.", false, "info", "Welcome to IoT System!", 0, "09:00 24-05-2025")
        )
    }

    fun toggleRead(notification: Notification) {
        // Update in NotificationManager
        val managerNotification = NotificationManager.getNotificationByID(notification.id)
        managerNotification?.read_status = !notification.read_status

        // Update local list and force refresh
        val updatedList = _notifications.value?.map {
            if (it.id == notification.id) it.copy(read_status = !it.read_status) else it
        }
        _notifications.value = updatedList?: emptyList()

        // Force immediate update by triggering filter refresh
        setFilter(_filter.value ?: NotificationFilter.ALL)
    }

    fun deleteNotification(notification: Notification) {
        // Remove from NotificationManager
        NotificationManager.removeNotificationByID(notification.id)

        // Update local list
        _notifications.value = _notifications.value?.filter { it.id != notification.id }
    }

    fun markAllRead() {
        // Update in NotificationManager
        NotificationManager.markAllAsRead()

        // Update local list
        _notifications.value = _notifications.value?.map { it.copy(read_status = true) }
    }

    fun markAllUnread() {
        // Update in NotificationManager
        NotificationManager.markAllAsUnread()

        // Update local list
        _notifications.value = _notifications.value?.map { it.copy(read_status = false) }
    }

    fun deleteAll() {
        // Clear NotificationManager
        NotificationManager.clearNotifications()

        // Update local list
        _notifications.value = emptyList()
    }
} 