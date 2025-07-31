# Giao diện Thông tin Người dùng (Profile UI)

## Mô tả
Giao diện thông tin người dùng được thiết kế theo Material Design với ngôn ngữ tiếng Việt, bao gồm các tính năng:

## Tính năng chính
1. **Thông tin cá nhân**
   - Avatar người dùng với khả năng chỉnh sửa
   - Tên, email và số điện thoại
   - Chỉnh sửa thông tin cá nhân

2. **Cài đặt ứng dụng**
   - Bật/tắt thông báo
   - Chọn giao diện (Sáng/Tối/Theo hệ thống)
   - Lịch sử y tế

3. **Hỗ trợ**
   - Trợ giúp & Hỗ trợ
   - Chính sách bảo mật
   - Đăng xuất

## Cách sử dụng
1. Từ MainActivity, nhấn vào nút Profile ở góc trên bên trái
2. Trong màn hình Profile:
   - Nhấn vào avatar để thay đổi ảnh đại diện
   - Nhấn "Chỉnh sửa thông tin cá nhân" để cập nhật thông tin
   - Sử dụng switch để bật/tắt thông báo
   - Nhấn "Giao diện" để thay đổi theme
   - Nhấn "Đăng xuất" để thoát khỏi ứng dụng

## Files đã tạo
- `activity_profile.xml` - Layout chính cho màn hình profile
- `dialog_edit_profile.xml` - Dialog chỉnh sửa thông tin
- `ProfileActivity.kt` - Activity xử lý logic
- Các drawable icons và background
- Cập nhật MainActivity và UIManager để thêm navigation

## Lưu trữ dữ liệu
- Sử dụng SharedPreferences để lưu thông tin người dùng
- Dữ liệu được tự động tải khi mở ứng dụng
- Hỗ trợ lưu cài đặt theme và thông báo
