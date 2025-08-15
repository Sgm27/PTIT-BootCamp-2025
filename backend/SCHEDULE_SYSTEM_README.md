# Hệ Thống Lịch Trình Thông Minh - Smart Schedule System

## Tổng Quan

Hệ thống lịch trình thông minh được thiết kế để giúp người già và gia đình quản lý các hoạt động hàng ngày một cách hiệu quả. Hệ thống tự động gửi thông báo voice khi đến giờ đã được lên lịch.

## Tính Năng Chính

### 1. Giao Diện Người Dùng
- **Profile Card**: Hiển thị tên người già với gradient đẹp mắt
- **Lịch Trình Hôm Nay**: Hiển thị các hoạt động trong ngày
- **Lịch Trình Hôm Qua**: Hiển thị các hoạt động đã hoàn thành
- **Nút Thêm**: Tạo lịch trình mới với giao diện thân thiện

### 2. Tạo Lịch Trình Mới
- **Tên lịch trình**: Nhập tên hoạt động (VD: Uống thuốc huyết áp)
- **Ngày và giờ**: Chọn ngày và thời gian cụ thể
- **Ghi chú**: Mô tả chi tiết về hoạt động
- **Phân loại**: Chọn loại hoạt động (Thuốc, Khám bệnh, Tập thể dục, Ăn uống, Khác)

### 3. Thông Báo Tự Động
- **Voice Notification**: Tự động phát âm thanh khi đến giờ
- **WebSocket Broadcasting**: Gửi thông báo real-time đến tất cả thiết bị
- **Trạng thái hoàn thành**: Đánh dấu hoạt động đã hoàn thành

## Cấu Trúc Hệ Thống

### Backend Components

#### 1. Schedule Service (`api_services/schedule_service.py`)
```python
# Tạo lịch trình mới
POST /api/schedules

# Lấy danh sách lịch trình
GET /api/schedules/{elderly_id}

# Cập nhật trạng thái
PUT /api/schedules/{schedule_id}/status

# Xóa lịch trình
DELETE /api/schedules/{schedule_id}
```

#### 2. Schedule Notification Service (`services/schedule_notification_service.py`)
- Kiểm tra lịch trình đến giờ mỗi phút
- Tự động gửi thông báo voice
- Broadcast qua WebSocket

#### 3. Database Models
- **Notification Table**: Lưu trữ thông tin lịch trình
- **Fields**: title, message, scheduled_at, category, priority, has_voice

### Android Components

#### 1. FamilyConnectionActivity
- Giao diện chính hiển thị lịch trình
- Tích hợp với backend để lấy dữ liệu
- Hiển thị lịch trình theo ngày

#### 2. CreateScheduleActivity
- Dialog tạo lịch trình mới
- Date picker và time picker
- Phân loại hoạt động
- Validation dữ liệu

#### 3. Layout Files
- `activity_family_connection.xml`: Giao diện chính
- `dialog_create_schedule.xml`: Dialog tạo lịch trình
- `item_schedule.xml`: Item hiển thị từng lịch trình

## Cách Sử Dụng

### 1. Khởi Tạo Hệ Thống
```bash
# Khởi động backend
cd backend
python run_server.py

# Khởi động Android app
# Mở project trong Android Studio và build
```

### 2. Tạo Lịch Trình
1. Mở app và vào "Kết nối yêu thương"
2. Nhấn nút "Thêm" (màu xanh)
3. Điền thông tin:
   - Tên lịch trình
   - Chọn ngày và giờ
   - Ghi chú (tùy chọn)
   - Chọn phân loại
4. Nhấn "Lưu Lịch Trình"

### 3. Nhận Thông Báo
- Khi đến giờ đã lên lịch, app sẽ tự động:
  - Phát âm thanh thông báo
  - Hiển thị thông tin trên màn hình
  - Gửi thông báo qua WebSocket

## Cấu Hình

### 1. Environment Variables
```bash
# .env file
DATABASE_URL=postgresql://user:password@localhost:5432/healthcare_db
GOOGLE_API_KEY=your_gemini_api_key
```

### 2. Database Setup
```sql
-- Tạo bảng notifications (đã có sẵn)
CREATE TABLE notifications (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    message TEXT,
    scheduled_at TIMESTAMP NOT NULL,
    notification_type VARCHAR(50),
    category VARCHAR(50),
    priority VARCHAR(10) DEFAULT 'normal',
    has_voice BOOLEAN DEFAULT false,
    is_sent BOOLEAN DEFAULT false,
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 3. Android Configuration
```kotlin
// ApiConfig.kt
object ApiConfig {
    val BASE_URL = "http://your-backend-url:8000"
}
```

## Tích Hợp Với Hệ Thống Hiện Tại

### 1. WebSocket Integration
- Sử dụng `websocket_manager` hiện có
- Broadcast thông báo đến tất cả clients
- Hỗ trợ real-time communication

### 2. Voice Service Integration
- Sử dụng `notification_voice_service` hiện có
- Tự động tạo voice từ text
- Hỗ trợ tiếng Việt

### 3. Database Integration
- Sử dụng `NotificationDBService` hiện có
- Tích hợp với user management system
- Hỗ trợ family relationship

## Monitoring và Debug

### 1. Log Files
```bash
# Backend logs
tail -f backend/server.log

# Android logs
adb logcat | grep "Schedule"
```

### 2. Health Check
```bash
# Kiểm tra trạng thái hệ thống
curl http://localhost:8000/health

# Kiểm tra WebSocket status
curl http://localhost:8000/api/websocket/status
```

### 3. Database Queries
```sql
-- Kiểm tra lịch trình
SELECT * FROM notifications WHERE scheduled_at >= NOW() ORDER BY scheduled_at;

-- Kiểm tra thông báo đã gửi
SELECT * FROM notifications WHERE is_sent = true;
```

## Troubleshooting

### 1. Thông Báo Không Hoạt Động
- Kiểm tra `schedule_notification_service` có đang chạy không
- Kiểm tra database connection
- Kiểm tra WebSocket connections

### 2. Voice Không Phát
- Kiểm tra `notification_voice_service`
- Kiểm tra Google API key
- Kiểm tra audio permissions trên Android

### 3. Lịch Trình Không Hiển Thị
- Kiểm tra API endpoints
- Kiểm tra database data
- Kiểm tra Android app logs

## Phát Triển Tương Lai

### 1. Tính Năng Mới
- Lịch trình lặp lại (hàng ngày, hàng tuần)
- Nhắc nhở trước giờ (15 phút, 30 phút)
- Tích hợp với calendar system
- Push notifications

### 2. Cải Tiến
- Machine learning để đề xuất lịch trình
- Tích hợp với health monitoring
- Multi-language support
- Offline mode

### 3. Analytics
- Tracking user behavior
- Performance metrics
- Usage statistics

## Liên Hệ

Để được hỗ trợ hoặc đóng góp ý kiến, vui lòng liên hệ:
- Email: support@healthcare-ai.com
- GitHub: https://github.com/your-repo
- Documentation: https://docs.healthcare-ai.com 