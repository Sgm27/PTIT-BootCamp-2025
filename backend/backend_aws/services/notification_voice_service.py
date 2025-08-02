"""
Notification Voice service - gửi thông báo dạng voice
"""
import asyncio
import json
import base64
import datetime
from typing import Optional

from google import genai
from google.genai import types

from config.settings import settings


class NotificationVoiceService:
    """Service for generating voice notifications using Gemini."""
    
    NOTIFICATION_SYSTEM_INSTRUCTION = """
    Bạn là hệ thống thông báo giọng nói thân thiện cho ứng dụng chăm sóc sức khỏe người cao tuổi.
    
    VAI TRÒ:
    - Bạn chuyển đổi các thông báo văn bản thành giọng nói tự nhiên và ấm áp
    - Sử dụng giọng điệu thân thiện, dễ hiểu phù hợp với người cao tuổi
    - Nói chậm và rõ ràng để người nghe có thể hiểu dễ dàng
    
    CÁCH NÓI:
    - Sử dụng ngôn từ đơn giản, dễ hiểu
    - Giọng điệu ấm áp và quan tâm
    - Nói với tốc độ vừa phải, không quá nhanh
    - Thêm các từ nhấn mạnh phù hợp như "nhớ", "quan trọng", "chú ý"
    
    NHIỆM VỤ:
    - Đọc thông báo nhắc uống thuốc
    - Đọc thông báo lịch khám bệnh
    - Đọc thông báo tập thể dục
    - Đọc các thông báo chăm sóc sức khỏe khác
    - Đọc thông báo khẩn cấp với giọng điệu phù hợp
    
    LƯU Ý:
    - Chỉ đọc nội dung thông báo được cung cấp
    - Không thêm thông tin hoặc câu hỏi không cần thiết
    - Giữ giọng nói tự nhiên và thân thiện
    - Phát âm tiếng Việt chuẩn và rõ ràng
    """
    
    def __init__(self, client: genai.Client = None, model: str = None):
        """Initialize Notification Voice service.
        
        Args:
            client: Gemini client instance. Creates new if None.
            model: Model to use. Uses default from settings if None.
        """
        self.client = client or genai.Client(api_key=settings.GOOGLE_API_KEY)
        self.model = model or settings.GEMINI_MODEL
    
    def _create_voice_config(self) -> types.LiveConnectConfig:
        """Create voice generation configuration.
        
        Returns:
            LiveConnectConfig object for voice generation.
        """
        return types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Aoede"  # Giọng nữ tự nhiên
                    )
                ),
                language_code='vi-VN',
            ),
            system_instruction=self.NOTIFICATION_SYSTEM_INSTRUCTION,
            temperature=0.3,  # Giảm nhiệt độ để có giọng nói ổn định hơn
            top_p=0.8,
        )
    
    async def generate_voice_notification(self, notification_text: str) -> Optional[bytes]:
        """Generate voice from notification text.
        
        Args:
            notification_text: Text content to convert to voice.
            
        Returns:
            Audio data as bytes, or None if failed.
        """
        if not notification_text or not notification_text.strip():
            print("❌ Notification text is empty")
            return None
            
        print(f"🔊 Generating voice for: {notification_text}")
        
        try:
            config = self._create_voice_config()
            
            async with self.client.aio.live.connect(model=self.model, config=config) as session:
                # Gửi text để chuyển đổi thành giọng nói
                await session.send_client_content(
                    turns={"role": "user", "parts": [{"text": notification_text}]}, 
                    turn_complete=True
                )
                
                audio_chunks = []
                
                # Nhận phản hồi từ Gemini
                async for response in session.receive():
                    if response.server_content is None:
                        continue
                        
                    model_turn = response.server_content.model_turn
                    if model_turn:
                        for part in model_turn.parts:
                            # Xử lý audio response
                            if hasattr(part, 'inline_data') and part.inline_data is not None:
                                audio_data = part.inline_data.data
                                audio_chunks.append(audio_data)
                                print(f"📦 Received audio chunk: {len(audio_data)} bytes")
                    
                    # Kết thúc khi turn hoàn thành
                    if response.server_content and response.server_content.turn_complete:
                        print("✅ Voice generation completed")
                        break
                
                # Ghép tất cả audio chunks
                if audio_chunks:
                    full_audio = b''.join(audio_chunks)
                    print(f"🎵 Total audio size: {len(full_audio)} bytes")
                    return full_audio
                else:
                    print("❌ No audio data received")
                    return None
                    
        except Exception as e:
            print(f"❌ Error generating voice notification: {e}")
            return None
    
    async def generate_voice_notification_base64(self, notification_text: str) -> Optional[str]:
        """Generate voice from notification text and return as base64.
        
        Args:
            notification_text: Text content to convert to voice.
            
        Returns:
            Audio data as base64 string, or None if failed.
        """
        audio_data = await self.generate_voice_notification(notification_text)
        
        if audio_data:
            try:
                base64_audio = base64.b64encode(audio_data).decode('utf-8')
                print(f"🔗 Audio converted to base64: {len(base64_audio)} characters")
                return base64_audio
            except Exception as e:
                print(f"❌ Error encoding audio to base64: {e}")
                return None
        
        return None
    
    async def generate_emergency_voice_notification(self, notification_text: str) -> Optional[bytes]:
        """Generate urgent voice notification with appropriate tone.
        
        Args:
            notification_text: Emergency notification text.
            
        Returns:
            Audio data as bytes, or None if failed.
        """
        # Thêm prefix để Gemini biết đây là thông báo khẩn cấp
        urgent_text = f"THÔNG BÁO KHẨN CẤP: {notification_text}"
        
        print(f"🚨 Generating emergency voice notification")
        return await self.generate_voice_notification(urgent_text)
    
    def create_notification_response(self, audio_base64: str, notification_text: str) -> dict:
        """Create standardized notification response.
        
        Args:
            audio_base64: Base64 encoded audio data.
            notification_text: Original notification text.
            
        Returns:
            Standardized response dictionary.
        """
        return {
            "success": True,
            "message": "Voice notification generated successfully",
            "data": {
                "notification_text": notification_text,
                "audio_base64": audio_base64,
                "audio_format": "audio/pcm",
                "timestamp": datetime.datetime.now().isoformat(),
                "service": "notification_voice_service"
            }
        }
    
    def create_error_response(self, error_message: str, notification_text: str = "") -> dict:
        """Create standardized error response.
        
        Args:
            error_message: Error description.
            notification_text: Original notification text.
            
        Returns:
            Standardized error response dictionary.
        """
        return {
            "success": False,
            "message": error_message,
            "data": {
                "notification_text": notification_text,
                "audio_base64": None,
                "timestamp": datetime.datetime.now().isoformat(),
                "service": "notification_voice_service"
            }
        }


# Convenience functions for common notification types
class NotificationTemplates:
    """Pre-defined notification templates for common use cases."""
    
    @staticmethod
    def medicine_reminder(medicine_name: str, time: str) -> str:
        """Create medicine reminder notification text."""
        return f"Nhắc nhở uống thuốc: Đã đến giờ uống {medicine_name} lúc {time}. Nhớ uống thuốc đúng giờ để đảm bảo hiệu quả điều trị nhé."
    
    @staticmethod
    def appointment_reminder(doctor_name: str, time: str, date: str) -> str:
        """Create appointment reminder notification text."""
        return f"Nhắc nhở lịch khám: Bác có lịch khám với bác sĩ {doctor_name} vào {time} ngày {date}. Nhớ chuẩn bị đầy đủ giấy tờ và đến đúng giờ nhé."
    
    @staticmethod
    def exercise_reminder(exercise_type: str, duration: str) -> str:
        """Create exercise reminder notification text."""
        return f"Nhắc nhở tập thể dục: Đã đến giờ {exercise_type} trong {duration}. Tập thể dục đều đặn giúp cơ thể khỏe mạnh và tinh thần sảng khoái."
    
    @staticmethod
    def health_check_reminder(check_type: str) -> str:
        """Create health check reminder notification text."""
        return f"Nhắc nhở kiểm tra sức khỏe: Đã đến giờ {check_type}. Theo dõi sức khỏe định kỳ giúp phát hiện sớm các vấn đề và có biện pháp điều trị kịp thời."
    
    @staticmethod
    def emergency_alert(message: str) -> str:
        """Create emergency alert notification text."""
        return f"CẢNH BÁO KHẨN CẤP: {message}. Vui lòng chú ý và thực hiện ngay lập tức."
    
    @staticmethod
    def water_reminder() -> str:
        """Create water drinking reminder notification text."""
        return "Nhắc nhở uống nước: Đã đến giờ uống nước. Uống đủ nước giúp cơ thể hoạt động tốt và da dẻ khỏe mạnh."
    
    @staticmethod
    def meal_reminder(meal_type: str) -> str:
        """Create meal reminder notification text."""
        return f"Nhắc nhở ăn uống: Đã đến giờ {meal_type}. Ăn uống đúng giờ và đầy đủ dinh dưỡng giúp cơ thể khỏe mạnh."
