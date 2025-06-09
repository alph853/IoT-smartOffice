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

/**
 * Đại diện cho một thiết bị IoT
 */
data class Device(
    val id: String,                // ID duy nhất của thiết bị
    val name: String,              // Tên hiển thị
    val type: DeviceType,          // Loại thiết bị
    val iconResId: Int,            // Resource ID của icon
    var isOn: Boolean = false,     // Trạng thái bật/tắt
    val room: String = "",         // Phòng chứa thiết bị
    var mode: String = "Manual"    // Chế độ hoạt động (Manual, Auto, Schedule)
) {
    /**
     * Kiểm tra thiết bị có phải là actuator hay không (thiết bị có thể điều khiển)
     */    fun isActuator(): Boolean {
        return type == DeviceType.FAN || 
               type == DeviceType.AC || 
               type == DeviceType.CEILING_LIGHT || 
               type == DeviceType.BULB || 
               type == DeviceType.LED4RGB ||
               type == DeviceType.PURIFIER
    }
    
    /**
     * Kiểm tra thiết bị có phải là cảm biến hay không
     */
    fun isSensor(): Boolean {
        return type == DeviceType.TEMPERATURE_SENSOR || 
               type == DeviceType.HUMIDITY_SENSOR || 
               type == DeviceType.LIGHT_SENSOR || 
               type == DeviceType.MOTION_SENSOR || 
               type == DeviceType.AIR_QUALITY_SENSOR
    }
}

/**
 * Các loại thiết bị được hỗ trợ
 */
enum class DeviceType {
    // MCU


    // Actuators (thiết bị điều khiển)
    FAN,            // Quạt
    AC,             // Điều hòa
    CEILING_LIGHT,  // Đèn trần
    BULB,           // Bóng đèn
    LED4RGB,        // LED RGB 4 màu
    PURIFIER,       // Máy lọc không khí
    CLIMATE,        // Thiết bị điều hòa nhiệt độ
    
    // Sensors (cảm biến)
    TEMPERATURE_SENSOR,    // Cảm biến nhiệt độ
    HUMIDITY_SENSOR,       // Cảm biến độ ẩm
    LIGHT_SENSOR,          // Cảm biến ánh sáng
    MOTION_SENSOR,         // Cảm biến chuyển động
    AIR_QUALITY_SENSOR     // Cảm biến chất lượng không khí
} 