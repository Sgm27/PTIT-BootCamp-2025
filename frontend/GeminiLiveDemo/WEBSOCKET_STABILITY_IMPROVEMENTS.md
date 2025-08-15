# WebSocket Stability Improvements

## Vấn đề đã được sửa

### 1. WebSocketNotConnectedException
**Nguyên nhân:** WebSocket không được kết nối khi `MedicineInfoActivity` cố gắng gửi tin nhắn âm thanh.

**Giải pháp:**
- `GlobalConnectionManager` giờ đây duy trì WebSocket connection cho cả `MainActivity` và `MedicineInfoActivity`
- Thêm kiểm tra kết nối trước khi gửi tin nhắn
- Tự động reconnect khi mất kết nối
- Thêm delay để đảm bảo kết nối được thiết lập

### 2. CalledFromWrongThreadException
**Nguyên nhân:** Cố gắng cập nhật UI từ background thread (Dispatchers.IO).

**Giải pháp:**
- Sử dụng `runOnUiThread` cho tất cả Toast messages
- Sử dụng `withContext(Dispatchers.Main)` trong AudioManager callbacks
- Đảm bảo tất cả UI updates được thực hiện trên main thread

### 3. NullPointerException trong Layout
**Nguyên nhân:** Cố gắng truy cập layout properties trước khi chúng được khởi tạo.

**Giải pháp:**
- Thêm kiểm tra null safety
- Sử dụng try-catch blocks cho việc khởi tạo
- Logging chi tiết để debug

## Các thay đổi chính

### MedicineInfoActivity.kt
- Thêm kiểm tra WebSocket connection trước khi gửi tin nhắn
- Tự động reconnect khi mất kết nối
- Sử dụng `runOnUiThread` cho tất cả UI updates
- Thêm error handling và logging

### GlobalConnectionManager.kt
- Mở rộng quản lý connection cho `MedicineInfoActivity`
- Đảm bảo WebSocket được duy trì khi ở medicine info screen
- Cải thiện logic quản lý activity lifecycle

### WebSocketManager.kt
- Thêm kiểm tra connection state trước khi gửi
- Tự động reconnect khi cần thiết
- Cải thiện error handling

### AudioManager.kt
- Sử dụng `withContext(Dispatchers.Main)` cho callbacks
- Đảm bảo thread safety cho UI updates

## Cách hoạt động

1. **Khi mở MedicineInfoActivity:**
   - `GlobalConnectionManager` đăng ký activity
   - Đảm bảo WebSocket connection được thiết lập
   - Khởi tạo voice chat với connection check

2. **Khi gửi tin nhắn âm thanh:**
   - Kiểm tra WebSocket connection
   - Nếu không kết nối, tự động reconnect
   - Gửi tin nhắn sau khi kết nối thành công

3. **Thread Safety:**
   - Tất cả UI updates được thực hiện trên main thread
   - Audio processing trên background thread
   - Callbacks được gọi an toàn

## Testing

Để test các cải thiện:

1. Mở app và đăng nhập
2. Quét thuốc để vào MedicineInfoActivity
3. Nhấn nút voice chat
4. Kiểm tra xem app không bị crash
5. Kiểm tra WebSocket connection được duy trì

## Logs

Các log quan trọng để monitor:
- `MedicineInfoActivity: Initializing voice chat...`
- `MedicineInfoActivity: WebSocket connected successfully`
- `WebSocketManager: WebSocket is not open, attempting to reconnect...`
- `AudioManager: Sending audio chunk, base64 length: X`

## Troubleshooting

Nếu vẫn gặp vấn đề:

1. Kiểm tra log để xem connection state
2. Đảm bảo backend server đang chạy
3. Kiểm tra network connectivity
4. Restart app nếu cần thiết 