package com.example.iot

/**
 * SensorData lưu trữ giá trị từ các cảm biến
 */
data class SensorData(
    val temperature: Float = 25.0f,    // Nhiệt độ mặc định 25°C
    val humidity: Float = 60.0f,       // Độ ẩm mặc định 60%
    val light: Float = 100.0f,         // Ánh sáng mặc định 100 Lux
    val pm25: Float = 30.0f,           // PM2.5 mặc định 30 μg/m³
    val motion: Boolean = false        // Không có chuyển động mặc định
) 