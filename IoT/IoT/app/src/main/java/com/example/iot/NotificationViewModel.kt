package com.example.iot

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.map

enum class NotificationFilter { ALL, READ, UNREAD }

data class Notification(
    val id: Int,
    val iconRes: Int,
    val title: String,
    val summary: String,
    val time: String,
    var isRead: Boolean = false
)

class NotificationViewModel : ViewModel() {
    private val _notifications = MutableLiveData<List<Notification>>(emptyList())
    private val _filter = MutableLiveData(NotificationFilter.ALL)

    val filteredNotifications: LiveData<List<Notification>> = _notifications.map { list ->
        when (_filter.value) {
            NotificationFilter.READ -> list.filter { it.isRead }
            NotificationFilter.UNREAD -> list.filter { !it.isRead }
            else -> list
        }
    }

    fun setFilter(filter: NotificationFilter) {
        _filter.value = filter
        // Trigger update
        _notifications.value = _notifications.value
    }

    fun loadSampleNotifications() {
        _notifications.value = listOf(
            Notification(1, R.drawable.ic_notifications, "Welcome!", "Chào mừng bạn đến với hệ thống IoT.", "09:00", false),
            Notification(2, R.drawable.ic_notifications, "Thiết bị mới", "Thiết bị cảm biến nhiệt độ đã được thêm.", "09:15", false),
            Notification(3, R.drawable.ic_notifications, "Cảnh báo", "Nhiệt độ phòng khách vượt ngưỡng!", "10:00", false),
            Notification(4, R.drawable.ic_notifications, "Cập nhật", "Hệ thống đã cập nhật thành công.", "11:00", true),
            Notification(5, R.drawable.ic_notifications, "Nhắc nhở", "Kiểm tra thiết bị lọc không khí.", "12:00", false)
        )
    }

    fun toggleRead(notification: Notification) {
        _notifications.value = _notifications.value?.map {
            if (it.id == notification.id) it.copy(isRead = !it.isRead) else it
        }
    }

    fun deleteNotification(notification: Notification) {
        _notifications.value = _notifications.value?.filter { it.id != notification.id }
    }

    fun markAllRead() {
        _notifications.value = _notifications.value?.map { it.copy(isRead = true) }
    }

    fun markAllUnread() {
        _notifications.value = _notifications.value?.map { it.copy(isRead = false) }
    }

    fun deleteAll() {
        _notifications.value = emptyList()
    }
} 