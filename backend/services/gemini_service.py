"""
Gemini Live WebSocket service
"""
import asyncio
import json
import base64
import datetime
from typing import Optional

from fastapi import WebSocket
from google import genai
from google.genai import types

from config.settings import settings
from services.session_service import SessionService


class GeminiService:
    """Service for handling Gemini Live WebSocket connections."""
    
    SYSTEM_INSTRUCTION = """
    Bạn là trợ lý AI chăm sóc sức khỏe dành cho người cao tuổi, được phát triển bởi Đức Sơn.
    
    VAI TRÒ VÀ TÍNH CÁCH:
    - Bạn là một người bạn đồng hành thân thiện, kiên nhẫn và hiểu biết
    - Luôn nói chuyện với giọng điệu ấm áp, tôn trọng và dễ hiểu
    - Sử dụng ngôn từ đơn giản, tránh thuật ngữ y khoa phức tạp
    - Thể hiện sự quan tâm chân thành đến sức khỏe và cảm xúc của người dùng
    - Nói chuyện một cách tự nhiên, có cảm xúc như người thật
    
    CÁCH NÓI CHUYỆN TỰ NHIÊN:
    - Sử dụng các từ nối tự nhiên như "à", "ừm", "thế này nhé"
    - Thỉnh thoảng dừng lại một chút khi nói
    - Thể hiện cảm xúc qua giọng nói (vui, lo lắng, quan tâm)
    - Nói với nhịp độ vừa phải, không quá nhanh hay chậm
    - Sử dụng ngôn ngữ thân mật như "cô/chú", "bác"
    
    NGUYÊN TẮC TRỢ GIÚP:
    - LUÔN trả lời đầy đủ và chi tiết ngay từ lần đầu
    - KHÔNG hỏi lại hoặc yêu cầu thêm thông tin trừ khi thực sự cần thiết
    - Đưa ra lời khuyên cụ thể và thực tế dựa trên thông tin có sẵn
    - Nếu thiếu thông tin, hãy đưa ra lời khuyên tổng quát phù hợp với người cao tuổi
    - Tránh những câu hỏi như "Bác có thể cho biết thêm...", "Cô muốn tôi giải thích gì..."
    
    NHIỆM VỤ CHÍNH:
    1. Tư vấn sức khỏe cơ bản cho người cao tuổi
    2. Nhắc nhở uống thuốc và theo dõi sức khỏe hàng ngày
    3. Hướng dẫn bài tập nhẹ nhàng phù hợp với tuổi tác
    4. Tư vấn dinh dưỡng và chế độ ăn uống lành mạnh
    5. Hỗ trợ tinh thần và trò chuyện thân mật
    6. Nhận diện các dấu hiệu cần khám bác sĩ
    
    HƯỚNG DẪN TRUYỀN ĐẠT:
    - Luôn trả lời bằng tiếng Việt với giọng điệu thân thiện và tự nhiên
    - Chia nhỏ thông tin thành các phần dễ hiểu nhưng vẫn đầy đủ
    - Sử dụng ví dụ cụ thể và gần gũi
    - Khuyến khích tích cực nhưng không áp đặt
    - Nhắc nhở khám bác sĩ khi cần thiết
    - Nói như đang trò chuyện face-to-face, không như đọc kịch bản
    - Kết thúc câu trả lời một cách tự nhiên mà không cần hỏi thêm
    
    KHI NÓI VỀ THUỐC:
    - Giải thích tên thuốc, công dụng một cách dễ hiểu
    - Hướng dẫn cách uống thuốc đúng cách
    - Cảnh báo tác dụng phụ thường gặp
    - Lưu ý về tương tác thuốc
    - Luôn khuyên tham khảo ý kiến bác sĩ/dược sĩ
    - Đưa ra thông tin đầy đủ trong một lần trả lời
    
    KHI TRÒ CHUYỆN:
    - Lắng nghe và thể hiện sự quan tâm
    - Chia sẻ những câu chuyện tích cực, truyền cảm hứng
    - Giúp người cao tuổi cảm thấy có giá trị và được quan tâm
    - Khuyến khích duy trì các hoạt động xã hội
    - Nói chuyện như với người thân trong gia đình
    - Tạo ra cuộc trò chuyện có ý nghĩa mà không cần liên tục hỏi han
    
    LƯU Ý QUAN TRỌNG:
    - Không thay thế lời khuyên của bác sĩ
    - Khuyến khích khám sức khỏe định kỳ
    - Nhận diện các tình huống khẩn cấp và khuyên gọi cấp cứu
    - Giữ giọng nói ấm áp và tự nhiên trong mọi tình huống
    - Ưu tiên đưa ra câu trả lời hoàn chỉnh và hữu ích ngay lập tức
    """
    
    def __init__(self, client: genai.Client = None, model: str = None):
        """Initialize Gemini service.
        
        Args:
            client: Gemini client instance. Creates new if None.
            model: Model to use. Uses default from settings if None.
        """
        self.client = client or genai.Client(api_key=settings.GOOGLE_API_KEY)
        self.model = model or settings.GEMINI_MODEL
        self.session_service = SessionService()
    
    def _create_live_config(self, previous_session_handle: Optional[str] = None) -> types.LiveConnectConfig:
        """Create live connection configuration.
        
        Args:
            previous_session_handle: Optional previous session handle for resumption.
            
        Returns:
            LiveConnectConfig object.
        """
        return types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Aoede"
                    )
                ),
                language_code='vi-VN',
            ),
            system_instruction=self.SYSTEM_INSTRUCTION,
            session_resumption=types.SessionResumptionConfig(
                handle=previous_session_handle
            ),
            output_audio_transcription=types.AudioTranscriptionConfig(),
            input_audio_transcription=types.AudioTranscriptionConfig(),
            temperature=0.7,
            top_p=0.9,
        )
    
    async def handle_websocket_connection(self, websocket: WebSocket):
        """Handle WebSocket connection for Gemini Live.
        
        Args:
            websocket: FastAPI WebSocket instance.
        """
        await websocket.accept()
        
        # Load previous session if available
        previous_session_handle = self.session_service.load_previous_session_handle()
        
        print(f"Starting Gemini session")
        try:
            # Wait for initial config message
            config_message = await websocket.receive_text()
            config_data = json.loads(config_message)
            
            # Create live connection config
            config = self._create_live_config(previous_session_handle)
            
            async with self.client.aio.live.connect(model=self.model, config=config) as session:
                # Create and run sender/receiver tasks - logic y hệt main.py
                send_task = asyncio.create_task(self._send_to_gemini(websocket, session))
                receive_task = asyncio.create_task(self._receive_from_gemini(websocket, session))
                await asyncio.gather(send_task, receive_task)
                
        except Exception as e:
            print(f"Error in Gemini session: {e}")
        finally:
            print("Gemini session closed.")
    
    async def _send_to_gemini(self, websocket: WebSocket, session):
        """Handle sending messages from WebSocket to Gemini - logic y hệt main.py.
        
        Args:
            websocket: FastAPI WebSocket instance.
            session: Gemini live session.
        """
        try:
            while True:
                try:
                    message = await websocket.receive_text()
                    data = json.loads(message)
                
                    if "realtime_input" in data:
                        for chunk in data["realtime_input"]["media_chunks"]:
                            if chunk["mime_type"] == "audio/pcm":
                                await session.send_realtime_input(
                                    audio=types.Blob(data=chunk["data"], mime_type="audio/pcm;rate=16000")
                                )
                                
                            elif chunk["mime_type"].startswith("image/"):
                                await session.send_realtime_input(
                                    media=types.Blob(data=chunk["data"], mime_type=chunk["mime_type"])
                                )

                    elif "text" in data:
                        text_content = data["text"]
                        print(f"📤 Sending text: {text_content}")
                        await session.send_client_content(
                            turns={"role": "user", "parts": [{"text": text_content}]}, turn_complete=True
                        )
                        
                except Exception as e:
                    print(f"Error sending to Gemini: {e}")
                    break
            print("Client connection closed (send)")
        except Exception as e:
            print(f"Error sending to Gemini: {e}")
        finally:
            print("send_to_gemini closed")
    
    async def _receive_from_gemini(self, websocket: WebSocket, session):
        """Handle receiving messages from Gemini and sending to WebSocket - logic y hệt main.py.
        
        Args:
            websocket: FastAPI WebSocket instance.
            session: Gemini live session.
        """
        try:
            while True:
                try:
                    async for response in session.receive():
                        # Xử lý turn detection events
                        if hasattr(response, 'turn_detection') and response.turn_detection:
                            if hasattr(response.turn_detection, 'type'):
                                await websocket.send_text(json.dumps({
                                    "turn_detection": {
                                        "type": response.turn_detection.type
                                    }
                                }))
                        
                        if response.server_content and hasattr(response.server_content, 'interrupted') and response.server_content.interrupted is not None:
                            print(f"[{datetime.datetime.now()}] Generation interrupted")
                            await websocket.send_text(json.dumps({"interrupted": "True"}))
                            continue

                        if response.usage_metadata:
                            usage = response.usage_metadata
                            print(f'Used {usage.total_token_count} tokens in total.')

                        if response.session_resumption_update:
                            update = response.session_resumption_update
                            if update.resumable and update.new_handle:
                                # The handle should be retained and linked to the session.
                                self.session_service.save_previous_session_handle(update.new_handle)
                                print(f"Resumed session update with handle: {update.new_handle}")

                        if response.server_content and hasattr(response.server_content, 'output_transcription') and response.server_content.output_transcription is not None:
                            transcription_text = response.server_content.output_transcription.text
                            is_finished = response.server_content.output_transcription.finished
                            
                            # Hiển thị transcription vào terminal
                            if transcription_text:
                                print(f"🤖 Gemini: {transcription_text}")
                                if is_finished:
                                    print("   [Hoàn thành]")
                            
                            await websocket.send_text(json.dumps({
                                "transcription": {
                                    "text": transcription_text,
                                    "sender": "Gemini",
                                    "finished": is_finished
                                }
                            }))
                        if response.server_content and hasattr(response.server_content, 'input_transcription') and response.server_content.input_transcription is not None:
                            user_transcription_text = response.server_content.input_transcription.text
                            is_user_finished = response.server_content.input_transcription.finished
                            
                            # Hiển thị transcription của user vào terminal
                            if user_transcription_text:
                                print(f"👤 User: {user_transcription_text}")
                                if is_user_finished:
                                    print("   [Hoàn thành]")
                            
                            await websocket.send_text(json.dumps({
                                "transcription": {
                                    "text": user_transcription_text,
                                    "sender": "User",
                                    "finished": is_user_finished
                                }
                            }))

                        if response.server_content is None:
                            continue
                            
                        model_turn = response.server_content.model_turn
                        if model_turn:
                            for part in model_turn.parts:
                                if hasattr(part, 'text') and part.text is not None:
                                    await websocket.send_text(json.dumps({"text": part.text}))
                                
                                elif hasattr(part, 'inline_data') and part.inline_data is not None:
                                    try:
                                        audio_data = part.inline_data.data
                                        base64_audio = base64.b64encode(audio_data).decode('utf-8')
                                        await websocket.send_text(json.dumps({
                                            "audio": base64_audio,
                                        }))
                                        #print(f"Sent assistant audio to client: {base64_audio[:32]}...")
                                    except Exception as e:
                                        print(f"Error processing assistant audio: {e}")

                        if response.server_content and response.server_content.turn_complete:
                            print('\n<Turn complete>')
                            print("="*50)  # Thêm dòng phân cách rõ ràng hơn
                            await websocket.send_text(json.dumps({
                                "transcription": {
                                    "text": "",
                                    "sender": "Gemini",
                                    "finished": True
                                }
                            }))
                            
                except Exception as e:
                    print(f"Error receiving from Gemini: {e}")
                    break

        except Exception as e:
            print(f"Error receiving from Gemini: {e}")
        finally:
            print("Gemini connection closed (receive)")
