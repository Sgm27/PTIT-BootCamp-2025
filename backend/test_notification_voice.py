"""
Test script for Notification Voice Service
Tự test chức năng tạo voice notification và lưu file audio
"""
import asyncio
import wave
import base64
import os
from datetime import datetime
from typing import Optional

from services.notification_voice_service import NotificationVoiceService, NotificationTemplates


class NotificationVoiceTestClient:
    """Test client for notification voice service."""
    
    def __init__(self):
        self.voice_service = NotificationVoiceService()
        self.output_dir = "test_audio_outputs"
        
        # Tạo thư mục output nếu chưa có
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"📁 Created output directory: {self.output_dir}")
    
    def save_audio_as_wav(self, audio_data: bytes, filename: str) -> str:
        """
        Lưu audio data thành file WAV với format 24kHz PCM.
        
        Args:
            audio_data: Raw audio bytes from Gemini
            filename: Tên file (không bao gồm extension)
            
        Returns:
            Path to saved WAV file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        wav_filename = f"{filename}_{timestamp}.wav"
        wav_path = os.path.join(self.output_dir, wav_filename)
        
        try:
            # Tạo file WAV với thông số 24kHz, 16-bit, mono
            with wave.open(wav_path, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(24000)  # 24kHz
                wav_file.writeframes(audio_data)
            
            file_size = os.path.getsize(wav_path)
            print(f"💾 Saved WAV file: {wav_path} ({file_size} bytes)")
            return wav_path
            
        except Exception as e:
            print(f"❌ Error saving WAV file: {e}")
            return None
    
    async def test_medicine_reminder(self):
        """Test medicine reminder notification."""
        print("\n" + "="*50)
        print("🧪 TESTING MEDICINE REMINDER")
        print("="*50)
        
        # Tạo thông báo nhắc uống thuốc
        notification_text = NotificationTemplates.medicine_reminder(
            medicine_name="Paracetamol 500mg",
            time="8:00 sáng"
        )
        
        print(f"📝 Notification text: {notification_text}")
        
        # Tạo voice notification
        audio_data = await self.voice_service.generate_voice_notification(notification_text)
        
        if audio_data:
            # Lưu file WAV
            wav_path = self.save_audio_as_wav(audio_data, "medicine_reminder")
            
            # Tạo base64 cho server
            base64_audio = base64.b64encode(audio_data).decode('utf-8')
            
            # Tạo response như sẽ gửi về server
            response = self.voice_service.create_notification_response(
                audio_base64=base64_audio,
                notification_text=notification_text
            )
            
            print(f"✅ Test completed successfully!")
            print(f"🔗 Base64 audio length: {len(base64_audio)} characters")
            print(f"📊 Response ready for backend")
            return True
        else:
            print("❌ Failed to generate voice notification")
            return False
    
    async def test_appointment_reminder(self):
        """Test appointment reminder notification."""
        print("\n" + "="*50)
        print("🧪 TESTING APPOINTMENT REMINDER")
        print("="*50)
        
        notification_text = NotificationTemplates.appointment_reminder(
            doctor_name="Nguyễn Văn A",
            time="14:30",
            date="ngày mai"
        )
        
        print(f"📝 Notification text: {notification_text}")
        
        audio_data = await self.voice_service.generate_voice_notification(notification_text)
        
        if audio_data:
            wav_path = self.save_audio_as_wav(audio_data, "appointment_reminder")
            base64_audio = base64.b64encode(audio_data).decode('utf-8')
            
            response = self.voice_service.create_notification_response(
                audio_base64=base64_audio,
                notification_text=notification_text
            )
            
            print(f"✅ Test completed successfully!")
            return True
        else:
            print("❌ Failed to generate voice notification")
            return False
    
    async def test_emergency_notification(self):
        """Test emergency notification."""
        print("\n" + "="*50)
        print("🧪 TESTING EMERGENCY NOTIFICATION")
        print("="*50)
        
        notification_text = "Phát hiện nhịp tim bất thường. Vui lòng liên hệ bác sĩ ngay lập tức."
        
        print(f"📝 Emergency text: {notification_text}")
        
        audio_data = await self.voice_service.generate_emergency_voice_notification(notification_text)
        
        if audio_data:
            wav_path = self.save_audio_as_wav(audio_data, "emergency_notification")
            base64_audio = base64.b64encode(audio_data).decode('utf-8')
            
            response = self.voice_service.create_notification_response(
                audio_base64=base64_audio,
                notification_text=f"THÔNG BÁO KHẨN CẤP: {notification_text}"
            )
            
            print(f"✅ Emergency test completed successfully!")
            return True
        else:
            print("❌ Failed to generate emergency voice notification")
            return False
    
    async def test_custom_notification(self, custom_text: str):
        """Test custom notification text."""
        print("\n" + "="*50)
        print("🧪 TESTING CUSTOM NOTIFICATION")
        print("="*50)
        
        print(f"📝 Custom text: {custom_text}")
        
        audio_data = await self.voice_service.generate_voice_notification(custom_text)
        
        if audio_data:
            wav_path = self.save_audio_as_wav(audio_data, "custom_notification")
            base64_audio = base64.b64encode(audio_data).decode('utf-8')
            
            response = self.voice_service.create_notification_response(
                audio_base64=base64_audio,
                notification_text=custom_text
            )
            
            print(f"✅ Custom test completed successfully!")
            return True
        else:
            print("❌ Failed to generate custom voice notification")
            return False
    
    async def test_water_reminder(self):
        """Test water drinking reminder."""
        print("\n" + "="*50)
        print("🧪 TESTING WATER REMINDER")
        print("="*50)
        
        notification_text = NotificationTemplates.water_reminder()
        
        print(f"📝 Notification text: {notification_text}")
        
        audio_data = await self.voice_service.generate_voice_notification(notification_text)
        
        if audio_data:
            wav_path = self.save_audio_as_wav(audio_data, "water_reminder")
            base64_audio = base64.b64encode(audio_data).decode('utf-8')
            
            response = self.voice_service.create_notification_response(
                audio_base64=base64_audio,
                notification_text=notification_text
            )
            
            print(f"✅ Water reminder test completed successfully!")
            return True
        else:
            print("❌ Failed to generate water reminder notification")
            return False
    
    async def run_all_tests(self):
        """Chạy tất cả các test cases."""
        print("🚀 STARTING NOTIFICATION VOICE SERVICE TESTS")
        print("=" * 60)
        
        test_results = []
        
        # Test các loại notification khác nhau
        tests = [
            ("Medicine Reminder", self.test_medicine_reminder()),
            ("Appointment Reminder", self.test_appointment_reminder()),
            ("Water Reminder", self.test_water_reminder()),
            ("Emergency Notification", self.test_emergency_notification()),
        ]
        
        for test_name, test_coro in tests:
            try:
                result = await test_coro
                test_results.append((test_name, result))
            except Exception as e:
                print(f"❌ Error in {test_name}: {e}")
                test_results.append((test_name, False))
        
        # Test custom notification
        try:
            custom_result = await self.test_custom_notification(
                "Chào bác, đây là thông báo thử nghiệm từ hệ thống chăm sóc sức khỏe. Hệ thống đang hoạt động bình thường."
            )
            test_results.append(("Custom Notification", custom_result))
        except Exception as e:
            print(f"❌ Error in Custom Notification: {e}")
            test_results.append(("Custom Notification", False))
        
        # Tổng kết kết quả
        print("\n" + "="*60)
        print("📊 TEST RESULTS SUMMARY")
        print("="*60)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name:<25} {status}")
            if result:
                passed += 1
        
        print("\n" + "="*60)
        print(f"📈 TOTAL: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Voice notification service is working correctly!")
        else:
            print("⚠️  Some tests failed. Please check the error messages above.")
        
        print(f"📁 Audio files saved in: {os.path.abspath(self.output_dir)}")
        
        return passed == total


async def main():
    """Main function để chạy tests."""
    try:
        # Khởi tạo test client
        test_client = NotificationVoiceTestClient()
        
        print("🎙️  NOTIFICATION VOICE SERVICE TEST SUITE")
        print("Testing voice generation and WAV file saving functionality")
        print("Audio format: WAV, 24kHz, 16-bit PCM, Mono")
        print()
        
        # Chạy tất cả tests
        success = await test_client.run_all_tests()
        
        if success:
            print("\n🎯 All tests completed successfully!")
            print("You can now use the voice notification service in your backend.")
        else:
            print("\n🚨 Some tests failed. Please check the configuration and try again.")
            
    except Exception as e:
        print(f"💥 Critical error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Chạy tests
    print("🔧 Initializing Notification Voice Service Tests...")
    asyncio.run(main())
