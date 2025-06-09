package com.example.iot.domain.models

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.iot.R

data class Sensor(
    var id: String,
    var name: String,
    var type: String,
    var unit: String?,
    var device_id: String,
    var status: String = "Online",
//    val id: String = java.util.UUID.randomUUID().toString()
) 