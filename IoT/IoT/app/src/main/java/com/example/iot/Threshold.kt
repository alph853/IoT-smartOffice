package com.example.iot

/**
 * Threshold lưu trữ ngưỡng bật/tắt cho mỗi thiết bị trong chế độ Auto
 * Giúp thực hiện logic hysteresis, tránh bật/tắt liên tục
 */
data class Threshold(
    val on: Float,    // Giá trị để bật thiết bị
    val off: Float,   // Giá trị để tắt thiết bị
    val sensorType: SensorType // Loại cảm biến áp dụng ngưỡng này
) 