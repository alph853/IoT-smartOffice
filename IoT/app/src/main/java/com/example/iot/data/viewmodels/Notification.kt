package com.example.iot.data.viewmodels

data class Notification(
    val id: Int,
    val iconRes: Int,
    val title: String,
    val summary: String,
    val time: String,
    var isRead: Boolean = false
) 