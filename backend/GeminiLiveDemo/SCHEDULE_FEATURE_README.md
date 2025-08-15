# Tính năng Lịch trình (Schedule) - Kết nối yêu thương

## Tổng quan
Tính năng lịch trình cho phép người dùng tạo và quản lý các lịch trình hàng ngày như uống thuốc, khám bệnh, tập thể dục, v.v. Khi đến giờ đã định, ứng dụng sẽ gửi thông báo voice để nhắc nhở người già.

## Tính năng chính

### 1. Giao diện người dùng
- **Profile Card**: Hiển thị tên người già với gradient background đẹp mắt
- **Lịch trình hôm nay**: Hiển thị các schedule của ngày hiện tại
- **Lịch trình hôm qua**: Hiển thị các schedule đã hoàn thành của ngày trước
- **Nút "Thêm"**: Tạo lịch trình mới

### 2. Tạo lịch trình mới
- **Tên lịch trình**: Nhập tên cho schedule (VD: "Uống thuốc huyết áp")
- **Ngày và giờ**: Chọn ngày và giờ cụ thể
- **Ghi chú**: Mô tả chi tiết về schedule
- **Phân loại**: Chọn loại schedule
  - Uống thuốc
  - Khám bệnh
  - Tập thể dục
  - Ăn uống
  - Khác

### 3. Thông báo voice tự động
- **Text-to-Speech**: Sử dụng TTS của Android để đọc thông báo
- **Backend Integration**: Gửi thông báo đến backend để tạo voice từ Gemini
- **WebSocket Broadcasting**: Gửi thông báo đến tất cả thiết bị kết nối

## Cấu trúc kỹ thuật

### Backend
- **API Endpoints**: `/api/schedules` cho CRUD operations
- **Database**: Sử dụng bảng `notifications` với trường `scheduled_at`
- **Voice Service**: Tích hợp với Gemini để tạo voice notifications
- **WebSocket**: Broadcast thông báo real-time

### Android App
- **ScheduleNotificationService**: Service chạy background để theo dõi schedule
- **AlarmManager**: Đặt alarm cho từng schedule
- **BroadcastReceiver**: Nhận thông báo khi đến giờ
- **TextToSpeech**: Đọc thông báo ngay lập tức

## Cách sử dụng

### 1. Khởi động tính năng
```kotlin
// Service sẽ tự động khởi động khi mở FamilyConnectionActivity
ScheduleNotificationService.startService(this)
```

### 2. Tạo schedule mới
```kotlin
val result = ApiClient.createSchedule(
    title = "Uống thuốc huyết áp",
    message = "Uống thuốc theo chỉ định của bác sĩ",
    scheduledAt = "2024-08-07T08:00:00",
    notificationType = "medicine_reminder",
    category = "medicine"
)
```

### 3. Lấy danh sách schedule
```kotlin
val result = ApiClient.getUserSchedules()
```

### 4. Đánh dấu hoàn thành
```kotlin
val result = ApiClient.markScheduleComplete(scheduleId)
```

## Cấu hình

### Permissions
```xml
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
<uses-permission android:name="android.permission.WAKE_LOCK" />
```

### Service Registration
```xml
<service
    android:name=".ScheduleNotificationService"
    android:exported="false"
    android:foregroundServiceType="dataSync" />

<receiver
    android:name=".ScheduleNotificationReceiver"
    android:exported="false" />
```

## Database Schema

### Bảng notifications
```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    notification_type VARCHAR(50),
    title VARCHAR(255),
    message TEXT,
    scheduled_at TIMESTAMP,
    sent_at TIMESTAMP,
    is_sent BOOLEAN DEFAULT FALSE,
    is_read BOOLEAN DEFAULT FALSE,
    has_voice BOOLEAN DEFAULT FALSE,
    voice_file_path VARCHAR(500),
    priority VARCHAR(10) DEFAULT 'normal',
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Luồng hoạt động

1. **Tạo Schedule**: User tạo schedule → Lưu vào database → Đặt alarm
2. **Đến giờ**: AlarmManager kích hoạt → BroadcastReceiver nhận → TTS đọc thông báo
3. **Backend Sync**: Gửi thông báo đến backend → Tạo voice từ Gemini → Broadcast qua WebSocket
4. **Cập nhật trạng thái**: Đánh dấu schedule đã hoàn thành

## Troubleshooting

### Vấn đề thường gặp
1. **Service không chạy**: Kiểm tra permission và battery optimization
2. **Thông báo không hiện**: Kiểm tra notification channel và settings
3. **Voice không phát**: Kiểm tra TTS language support và audio settings

### Debug
```kotlin
// Log để debug
Log.d("ScheduleNotification", "Received notification: $title")
Log.d("ScheduleNotification", "Voice notification sent to backend")
```

## Tương lai

### Tính năng dự kiến
- **Recurring Schedules**: Lịch trình lặp lại (hàng ngày, hàng tuần)
- **Smart Reminders**: Nhắc nhở thông minh dựa trên thói quen
- **Family Coordination**: Đồng bộ schedule giữa các thành viên gia đình
- **Voice Commands**: Tạo schedule bằng giọng nói

### Tối ưu hóa
- **Battery Optimization**: Sử dụng WorkManager thay vì AlarmManager
- **Push Notifications**: Sử dụng FCM cho thông báo đáng tin cậy hơn
- **Offline Support**: Cache schedule và sync khi có internet 