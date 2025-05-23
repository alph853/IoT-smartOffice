package com.example.iot

/**
 * Mode định nghĩa các chế độ hoạt động cho các thiết bị
 */
enum class Mode {
    MANUAL,    // Chế độ thủ công - người dùng điều khiển bật/tắt
    AUTO,      // Chế độ tự động - hệ thống điều khiển dựa trên ngưỡng cảm biến
    DISABLED   // Chế độ vô hiệu hóa - tất cả thiết bị tắt
} 