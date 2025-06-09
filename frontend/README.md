# IoT Android App - Codebase Structure & Refactor Guide

## 1. Mục tiêu refactor
- Tách các module, class, data model, adapter, viewmodel, manager... thành các file riêng biệt, đặt đúng package.
- Giữ nguyên logic, tên class, function, biến như codebase cũ để dev dễ làm việc.
- Chỉ tách file/module để dễ quan sát, maintain, mở rộng, không đổi cách code truyền thống của team.

## 2. Cấu trúc thư mục mới
```
app/src/main/java/com/example/iot/
├── ui/
│   ├── activities/         # Các Activity (MainActivity, RoomDetailActivity, MCUDetailActivity)
│   ├── adapters/           # Các Adapter cho RecyclerView (RoomAdapter, MCUAdapter, NotificationAdapter...)
│   └── navigation/         # NavigationBar và logic navigation
├── fragments/              # Các Fragment (ControlFragment,            NotificationFragment, CameraFragment...)
├── domain/
│   ├── models/             # Data class/model (Room, MCU, Sensor, Actuator, Device...)
│   └── managers/           # Singleton quản lý data (RoomManager, MCUManager, SensorManager...)
└── data/
    └── viewmodels/         # ViewModel và các model liên quan (NotificationViewModel, Notification, NotificationFilter)
```

## 3. Những thay đổi chính
- **Activities**: Chuyển từ thư mục gốc vào `ui/activities/`
- **Adapters**: Chuyển từ thư mục gốc vào `ui/adapters/`
- **Fragments**: Giữ nguyên trong thư mục `fragments/`
- **Models**: Chuyển từ thư mục gốc vào `domain/models/`
- **Managers**: Chuyển từ thư mục gốc vào `domain/managers/`
- **ViewModels**: Chuyển từ thư mục gốc vào `data/viewmodels/`

## 4. Nguyên tắc giữ lại từ codebase cũ
- **Không thay đổi logic**: Tất cả logic xử lý, flow data, UI giữ nguyên như cũ
- **Giữ nguyên tên**: Không đổi tên class, function, biến nếu không cần thiết
- **Inner class**: Các inner class (ví dụ: `Component` trong `MCU`) vẫn giữ trong file cha
- **Coding style**: Giữ nguyên coding style và convention của team

## 5. Các điểm cần lưu ý
- **Component**: Định nghĩa duy nhất trong `MCU.kt` (inner class), không tách ra file riêng
- **Notification**: Các class liên quan (`Notification`, `NotificationFilter`, `NotificationViewModel`) đặt trong `data/viewmodels/`
- **Import**: Cập nhật lại các import statement cho đúng package mới
- **Package declaration**: Cập nhật package declaration trong mỗi file cho đúng vị trí mới

## 6. Hướng dẫn cho dev team
- **Thêm file mới**: Tạo file trong đúng package tương ứng với chức năng
- **Sửa code**: Giữ nguyên tên biến/class nếu không thực sự cần đổi
- **Inner class**: Nếu class chỉ dùng nội bộ, có thể để inner class như cũ
- **Import**: Luôn import từ package mới, không dùng import cũ
- **Package**: Luôn khai báo package đúng với vị trí file

## 7. Lợi ích của cấu trúc mới
- **Dễ maintain**: Mỗi loại file có vị trí riêng, dễ tìm và sửa
- **Dễ mở rộng**: Thêm tính năng mới dễ dàng, không ảnh hưởng code cũ
- **Dễ review**: Code được tổ chức rõ ràng, dễ review và phát hiện lỗi
- **Dễ onboard**: Dev mới dễ hiểu cấu trúc và tìm file cần sửa

## 8. Quy tắc khi làm việc với codebase
- Không tạo file mới ngoài cấu trúc thư mục đã định
- Không thay đổi logic nếu không cần thiết
- Giữ nguyên coding style và convention
- Cập nhật README nếu có thay đổi cấu trúc

---
**Mọi thay đổi đều hướng tới việc codebase dễ maintain và mở rộng, không thay đổi logic hay convention của team** 