package com.example.iot.data.viewmodels

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import android.os.Handler
import android.os.Looper
import com.example.iot.domain.managers.NotificationManager
import com.example.iot.data.viewmodels.Notification

enum class NotificationFilter { ALL, READ, UNREAD }

class NotificationViewModel : ViewModel() {
    private val _notifications = MutableLiveData<List<Notification>>()
    val notifications: LiveData<List<Notification>> = _notifications

    private val _filteredNotifications = MutableLiveData<List<Notification>>()
    val filteredNotifications: LiveData<List<Notification>> = _filteredNotifications
    private var currentFilter = NotificationFilter.ALL
    
    private val mainHandler = Handler(Looper.getMainLooper())
    private val notificationListener: () -> Unit = {
        // Ensure UI updates happen on the main thread
        mainHandler.post {
            android.util.Log.d("NotificationViewModel", "Received notification update, reloading notifications")
            loadNotifications()
        }
    }

    init {
        // Register for notification updates
        NotificationManager.addListener(notificationListener)
        loadNotifications()
    }

    override fun onCleared() {
        super.onCleared()
        // Unregister listener when ViewModel is cleared
        NotificationManager.removeListener(notificationListener)
    }    fun loadNotifications() {
        val allNotifications = NotificationManager.getNotifications()
        android.util.Log.d("NotificationViewModel", "Loading ${allNotifications.size} notifications from manager")
        _notifications.value = allNotifications
        applyFilter()
    }

    fun setFilter(filter: NotificationFilter) {
        currentFilter = filter
        applyFilter()
    }

    private fun applyFilter() {
        val filtered = when (currentFilter) {
            NotificationFilter.ALL -> _notifications.value ?: emptyList()
            NotificationFilter.READ -> _notifications.value?.filter { it.read_status } ?: emptyList()
            NotificationFilter.UNREAD -> _notifications.value?.filter { !it.read_status } ?: emptyList()
        }
        _filteredNotifications.value = filtered
    }

    fun toggleRead(notification: Notification) {
        val currentList = _notifications.value?.toMutableList() ?: mutableListOf()
        val index = currentList.indexOfFirst { it.id == notification.id }
        if (index != -1) {
            val updatedNotification = notification.copy(read_status = !notification.read_status)
            currentList[index] = updatedNotification
            _notifications.value = currentList
            NotificationManager.updateNotification(updatedNotification)
            applyFilter()
        }
    }

    fun deleteNotification(notification: Notification) {
        val currentList = _notifications.value?.toMutableList() ?: mutableListOf()
        currentList.removeAll { it.id == notification.id }
        _notifications.value = currentList
        NotificationManager.deleteNotification(notification)
        applyFilter()
    }

    fun markAllRead() {
        val currentList = _notifications.value?.toMutableList() ?: mutableListOf()
        val updatedList = currentList.map { it.copy(read_status = true) }
        _notifications.value = updatedList
        NotificationManager.markAllAsRead()
        applyFilter()
    }

    fun markAllUnread() {
        val currentList = _notifications.value?.toMutableList() ?: mutableListOf()
        val updatedList = currentList.map { it.copy(read_status = false) }
        _notifications.value = updatedList
        NotificationManager.markAllAsUnread()
        applyFilter()
    }

    fun deleteAll() {
        _notifications.value = emptyList()
        NotificationManager.clearNotifications()
        applyFilter()
    }
} 