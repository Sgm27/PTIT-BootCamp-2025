#!/usr/bin/env python3
"""
Test script để kiểm tra video avatar trong ứng dụng Android
"""

import os
import sys
import time

def test_video_avatar_files():
    """Kiểm tra xem các file video avatar có tồn tại không"""
    print("=== Kiểm tra file video avatar ===")
    
    # Đường dẫn đến các file video
    waiting_video = "backend/GeminiLiveDemo/app/src/main/res/raw/waiting_avatar.mp4"
    talking_video = "backend/GeminiLiveDemo/app/src/main/res/raw/talking_avatar.mp4"
    
    # Kiểm tra file waiting_avatar.mp4
    if os.path.exists(waiting_video):
        size = os.path.getsize(waiting_video)
        print(f"✅ waiting_avatar.mp4 tồn tại - Kích thước: {size:,} bytes ({size/1024/1024:.1f} MB)")
    else:
        print(f"❌ waiting_avatar.mp4 không tồn tại tại: {waiting_video}")
    
    # Kiểm tra file talking_avatar.mp4
    if os.path.exists(talking_video):
        size = os.path.getsize(talking_video)
        print(f"✅ talking_avatar.mp4 tồn tại - Kích thước: {size:,} bytes ({size/1024/1024:.1f} MB)")
    else:
        print(f"❌ talking_avatar.mp4 không tồn tại tại: {talking_video}")
    
    return os.path.exists(waiting_video) and os.path.exists(talking_video)

def test_layout_changes():
    """Kiểm tra xem layout đã được cập nhật chưa"""
    print("\n=== Kiểm tra thay đổi layout ===")
    
    layout_file = "backend/GeminiLiveDemo/app/src/main/res/layout/activity_main.xml"
    
    if not os.path.exists(layout_file):
        print(f"❌ Layout file không tồn tại: {layout_file}")
        return False
    
    with open(layout_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Kiểm tra xem có VideoView không
    if 'VideoView' in content:
        print("✅ VideoView đã được thêm vào layout")
    else:
        print("❌ VideoView chưa được thêm vào layout")
        return False
    
    # Kiểm tra xem có avatarVideoView không
    if 'avatarVideoView' in content:
        print("✅ avatarVideoView ID đã được định nghĩa")
    else:
        print("❌ avatarVideoView ID chưa được định nghĩa")
        return False
    
    # Kiểm tra xem có còn ImageView không
    if 'imageView' in content:
        print("⚠️  imageView vẫn còn trong layout (có thể là comment)")
    else:
        print("✅ imageView đã được loại bỏ khỏi layout")
    
    return True

def test_ui_manager_changes():
    """Kiểm tra xem UIManager đã được cập nhật chưa"""
    print("\n=== Kiểm tra thay đổi UIManager ===")
    
    ui_manager_file = "backend/GeminiLiveDemo/app/src/main/java/com/example/geminilivedemo/UIManager.kt"
    
    if not os.path.exists(ui_manager_file):
        print(f"❌ UIManager file không tồn tại: {ui_manager_file}")
        return False
    
    with open(ui_manager_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Kiểm tra xem có VideoView import không
    if 'import android.widget.VideoView' in content:
        print("✅ VideoView import đã được thêm")
    else:
        print("❌ VideoView import chưa được thêm")
        return False
    
    # Kiểm tra xem có avatarVideoView variable không
    if 'avatarVideoView: VideoView' in content:
        print("✅ avatarVideoView variable đã được định nghĩa")
    else:
        print("❌ avatarVideoView variable chưa được định nghĩa")
        return False
    
    # Kiểm tra xem có các phương thức video không
    methods_to_check = [
        'playWaitingAvatar()',
        'playTalkingAvatar()',
        'updateAvatarVideo()',
        'setDefaultAvatarVideo()'
    ]
    
    for method in methods_to_check:
        if method in content:
            print(f"✅ {method} đã được thêm")
        else:
            print(f"❌ {method} chưa được thêm")
            return False
    
    return True

def test_main_activity_changes():
    """Kiểm tra xem MainActivity đã được cập nhật chưa"""
    print("\n=== Kiểm tra thay đổi MainActivity ===")
    
    main_activity_file = "backend/GeminiLiveDemo/app/src/main/java/com/example/geminilivedemo/MainActivity.kt"
    
    if not os.path.exists(main_activity_file):
        print(f"❌ MainActivity file không tồn tại: {main_activity_file}")
        return False
    
    with open(main_activity_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Kiểm tra xem có comment về việc không hiển thị image không
    if "We no longer display captured images on the main screen" in content:
        print("✅ Comment về việc không hiển thị image đã được thêm")
    else:
        print("❌ Comment về việc không hiển thị image chưa được thêm")
        return False
    
    # Kiểm tra xem có gọi getVideoView() không
    if 'getVideoView()' in content:
        print("✅ getVideoView() đã được sử dụng")
    else:
        print("⚠️  getVideoView() chưa được sử dụng (có thể không cần thiết)")
    
    return True

def test_manifest_changes():
    """Kiểm tra xem AndroidManifest đã được cập nhật chưa"""
    print("\n=== Kiểm tra thay đổi AndroidManifest ===")
    
    manifest_file = "backend/GeminiLiveDemo/app/src/main/AndroidManifest.xml"
    
    if not os.path.exists(manifest_file):
        print(f"❌ AndroidManifest file không tồn tại: {manifest_file}")
        return False
    
    with open(manifest_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Kiểm tra xem có quyền READ_MEDIA_VIDEO không
    if 'READ_MEDIA_VIDEO' in content:
        print("✅ READ_MEDIA_VIDEO permission đã được thêm")
    else:
        print("❌ READ_MEDIA_VIDEO permission chưa được thêm")
        return False
    
    return True

def main():
    """Hàm chính để chạy tất cả các test"""
    print("🎬 Bắt đầu kiểm tra video avatar implementation")
    print("=" * 50)
    
    tests = [
        ("Video Files", test_video_avatar_files),
        ("Layout Changes", test_layout_changes),
        ("UIManager Changes", test_ui_manager_changes),
        ("MainActivity Changes", test_main_activity_changes),
        ("AndroidManifest Changes", test_manifest_changes)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
        
        print()
    
    print("=" * 50)
    print(f"📊 Kết quả: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Tất cả tests đều passed! Video avatar đã được implement thành công.")
        print("\n📝 Hướng dẫn test thực tế:")
        print("1. Build và cài đặt ứng dụng Android")
        print("2. Mở ứng dụng và đăng nhập")
        print("3. Quan sát màn hình chính:")
        print("   - Khi AI rảnh: phát video waiting_avatar.mp4 (lặp lại)")
        print("   - Khi AI nói chuyện: phát video talking_avatar.mp4 (lặp lại)")
        print("4. Kiểm tra âm thanh: video phải tắt âm thanh, chỉ nghe âm thanh AI")
    else:
        print("⚠️  Một số tests failed. Vui lòng kiểm tra lại implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 