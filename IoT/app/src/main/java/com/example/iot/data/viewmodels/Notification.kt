package com.example.iot.data.viewmodels

import com.example.iot.R

data class Notification(
    var id: Int,
    var message: String,
    var read_status: Boolean,
    var type: String,
    var title: String,
    var device_id: Int,
    var ts: String,
    val iconRes: Int = R.drawable.ic_notifications
) 