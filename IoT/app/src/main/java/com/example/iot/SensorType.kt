package com.example.iot

/**
 * SensorType định nghĩa các loại cảm biến được sử dụng trong hệ thống
 */
enum class SensorType {
    TEMPERATURE,  // Nhiệt độ (°C)
    HUMIDITY,     // Độ ẩm (%)
    LIGHT,        // Ánh sáng (Lux)
    PM25,         // Bụi mịn PM2.5 (μg/m³)
    MOTION        // Chuyển động (boolean)
} 