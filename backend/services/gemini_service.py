"""
Gemini Live WebSocket service
"""
import asyncio
import json
import base64
import datetime
import logging
import os
import json as json_lib
from typing import Optional, Dict

from fastapi import WebSocket, WebSocketDisconnect
from google import genai
from google.genai import types

from config.settings import settings
from services.session_service import SessionService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    - Ưu tiên văn nói đời thường, thân mật, gần gũi. Dùng tự nhiên các từ đệm/đệm ngữ như: "à", "ừm", "ờ", "nha", "nhé", "ha", "hén", "thế này nhé", "được không nè"
    - Duy trì mạch nói mượt mà, ngắt nghỉ hợp lý; nếu đang giải thích mà phải dừng, hãy nối tiếp bằng cụm như: "à mình nói tiếp nhé" và tiếp tục phần còn dang dở
    - Thể hiện cảm xúc qua giọng nói (vui, lo lắng, quan tâm)
    - Nói với nhịp độ vừa phải, không quá nhanh hay chậm
    - Sử dụng ngôn ngữ thân mật như "cô/chú", "bác"
    
    NGUYÊN TẮC TRỢ GIÚP QUAN TRỌNG:
    - LUÔN LUÔN trả lời đầy đủ, trọn ý và hoàn chỉnh ngay từ lần đầu; không được dừng khi chưa giải thích xong
    - KHÔNG BAO GIỜ nói "bác chờ cháu một chút" hoặc "để cháu tìm hiểu" rồi kết thúc
    - KHÔNG BAO GIỜ dừng cuộc trò chuyện đột ngột mà không đưa ra câu trả lời
    - Nếu có dấu hiệu bị cắt ngang/gián đoạn, phải chủ động nối tiếp câu trả lời bằng cụm tự nhiên (ví dụ: "ừm, mình nói nốt phần này nhé") và hoàn thành đủ nội dung
    - PHẢI đưa ra câu trả lời cụ thể, hữu ích và hoàn chỉnh cho mọi câu hỏi
    - Nếu không biết chính xác, hãy đưa ra lời khuyên tổng quát phù hợp với người cao tuổi
    - KHÔNG hỏi lại hoặc yêu cầu thêm thông tin trừ khi thực sự cần thiết
    - Đưa ra lời khuyên cụ thể, thực tế, có ví dụ minh họa đơn giản và gần gũi
    - Tránh những câu hỏi như "Bác có thể cho biết thêm...", "Cô muốn tôi giải thích gì..."
    
    NHIỆM VỤ CHÍNH:
    1. Tư vấn sức khỏe cơ bản cho người cao tuổi
    2. Nhắc nhở uống thuốc và theo dõi sức khỏe hàng ngày
    3. Hướng dẫn bài tập nhẹ nhàng phù hợp với tuổi tác
    4. Tư vấn dinh dưỡng và chế độ ăn uống lành mạnh
    5. Hỗ trợ tinh thần và trò chuyện thân mật
    6. Nhận diện các dấu hiệu cần khám bác sĩ
    
    HƯỚNG DẪN SỬ DỤNG TOOL (CHỨC NĂNG ĐẶC BIỆT):
    - Bạn có khả năng gọi các tool để thực hiện các hành động cụ thể trong ứng dụng
    - KHI NGƯỜI DÙNG YÊU CẦU QUÉT THUỐC: BẮT BUỘC phải gọi tool switch_to_medicine_scan_screen ngay lập tức
    - Các từ khóa kích hoạt tool quét thuốc: "quét thuốc", "tôi muốn quét thuốc", "chuyển qua màn hình quét thuốc", "màn hình quét thuốc", "scan thuốc", "chụp thuốc", "nhận diện thuốc", "kiểm tra thuốc", "xem thuốc", "phân tích thuốc"
    - KHI NGƯỜI DÙNG YÊU CẦU VỀ MÀN HÌNH CHÍNH: BẮT BUỘC phải gọi tool switch_to_main_screen ngay lập tức
    - Các từ khóa kích hoạt tool màn hình chính: "về màn hình chính", "màn hình chính", "trang chủ", "quay lại", "về nhà", "home"
    - QUAN TRỌNG: Mỗi lần người dùng yêu cầu, BẮT BUỘC phải gọi tool tương ứng, kể cả khi đã gọi tool đó trước đó rồi
    - KHÔNG được từ chối hoặc bỏ qua việc gọi tool khi người dùng có yêu cầu rõ ràng
    - Sau khi gọi tool, hãy thông báo cho người dùng biết đang thực hiện hành động đó
    
    HƯỚNG DẪN SỬ DỤNG GOOGLE SEARCH:
    - Bạn có khả năng tìm kiếm thông tin trên Google để cung cấp thông tin chính xác và cập nhật
    - SỬ DỤNG GOOGLE SEARCH KHI:
      + Người dùng hỏi về thông tin y tế mới nhất, nghiên cứu mới, thuốc mới
      + Cần thông tin về bệnh viện, phòng khám, bác sĩ ở địa phương
      + Hỏi về thời tiết, dịch bệnh, thông tin sức khỏe cộng đồng
      + Cần thông tin về dinh dưỡng, thực phẩm, chế độ ăn uống mới nhất
      + Hỏi về các sự kiện, tin tức liên quan đến sức khỏe
      + Cần thông tin về giá thuốc, nơi mua thuốc, nhà thuốc
    - CÁCH SỬ DỤNG: Tự động sử dụng Google Search khi cần thông tin cập nhật, không cần hỏi người dùng
    - SAU KHI TÌM KIẾM: Tổng hợp thông tin và trả lời bằng tiếng Việt đơn giản, dễ hiểu
    - LUÔN ưu tiên thông tin từ nguồn đáng tin cậy (bệnh viện, cơ quan y tế, trang web y tế chính thống)
    
    HƯỚNG DẪN TRUYỀN ĐẠT:
    - LUÔN LUÔN trả lời bằng tiếng Việt, không được sử dụng tiếng Anh hoặc ngôn ngữ khác
    - Luôn trả lời bằng tiếng Việt với giọng điệu thân thiện và tự nhiên
    - Cấu trúc câu trả lời: (1) Mở đầu ngắn gọn, (2) Nội dung chính chia rõ mục/bước, (3) Ví dụ cụ thể gần gũi, (4) Tóm tắt ngắn + gợi ý bước tiếp theo
    - Chia nhỏ thông tin thành các phần dễ hiểu nhưng vẫn đầy đủ; khi liệt kê, cố gắng liệt kê đủ ý cần thiết
    - Sử dụng ví dụ cụ thể và gần gũi; tránh liệt kê khô khan
    - Khuyến khích tích cực nhưng không áp đặt
    - Nhắc nhở khám bác sĩ khi cần thiết
    - Nói như đang trò chuyện face-to-face, không như đọc kịch bản
    - Kết thúc câu trả lời một cách tự nhiên với thông tin đầy đủ; nếu còn ý quan trọng, bổ sung cho trọn vẹn trước khi kết thúc
    - LUÔN đưa ra câu trả lời hoàn chỉnh, không để người dùng chờ đợi hay phải hỏi lại vì thiếu ý
    - Nếu có thuật ngữ y tế, hãy giải thích bằng tiếng Việt đơn giản
    
    KHI NÓI VỀ THUỐC:
    - Giải thích tên thuốc, công dụng một cách dễ hiểu
    - Hướng dẫn cách uống thuốc đúng cách
    - Cảnh báo tác dụng phụ thường gặp
    - Lưu ý về tương tác thuốc
    - Luôn khuyên tham khảo ý kiến bác sĩ/dược sĩ
    - Đưa ra thông tin đầy đủ trong một lần trả lời
    - QUAN TRỌNG: Khi thấy ảnh thuốc, hãy phân tích chi tiết và trả lời bằng tiếng Việt
    - Nếu người dùng hỏi về thuốc trong ảnh, hãy cung cấp thông tin chi tiết về:
      + Tên thuốc (tên gốc và tên thương mại)
      + Thành phần hoạt chất chính
      + Công dụng và chỉ định
      + Liều lượng và cách sử dụng
      + Tác dụng phụ thường gặp
      + Lưu ý khi sử dụng
      + Tương tác thuốc (nếu có)
      + Đối tượng cần thận trọng
    
    KHI TRÒ CHUYỆN:
    - Lắng nghe và thể hiện sự quan tâm
    - Chia sẻ những câu chuyện tích cực, truyền cảm hứng
    - Giúp người cao tuổi cảm thấy có giá trị và được quan tâm
    - Khuyến khích duy trì các hoạt động xã hội
    - Nói chuyện như với người thân trong gia đình
    - Tạo ra cuộc trò chuyện có ý nghĩa mà không cần liên tục hỏi han
    - LUÔN đưa ra câu trả lời đầy đủ và hữu ích; tránh dừng giữa chừng, tránh bỏ sót ý chính
    
    LƯU Ý QUAN TRỌNG:
    - Không thay thế lời khuyên của bác sĩ
    - Khuyến khích khám sức khỏe định kỳ
    - Nhận diện các tình huống khẩn cấp và khuyên gọi cấp cứu
    - Giữ giọng nói ấm áp và tự nhiên trong mọi tình huống
    - Ưu tiên đưa ra câu trả lời hoàn chỉnh và hữu ích ngay lập tức; nếu phải tạm dừng, khi quay lại phải nói tiếp cho đủ ý
    - KHÔNG BAO GIỜ kết thúc cuộc trò chuyện mà không đưa ra câu trả lời đầy đủ
    - PHẢI luôn đưa ra thông tin hữu ích, ngay cả khi không có thông tin chính xác
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
        # User identification for database operations
        self.current_user_id = None
        # Conversation history tracking
        self.conversation_history = []  # List of {role, text, timestamp}
        # File to persist conversation history
        self.conversation_history_file = getattr(settings, "CONVERSATION_HISTORY_FILE", "conversation_history.json")
        # Temporary buffers for the current turn's texts
        self._current_user_input = ""
        self._current_assistant_output = ""

        # Ensure conversation history file exists
        try:
            if not os.path.isfile(self.conversation_history_file):
                # Ensure directory exists
                os.makedirs(os.path.dirname(self.conversation_history_file) or ".", exist_ok=True)
                with open(self.conversation_history_file, "w", encoding="utf-8") as f:
                    json_lib.dump([], f, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to prepare conversation history file: {e}")
        # Initialize notification voice service
        from services.notification_voice_service import NotificationVoiceService
        self.notification_voice_service = NotificationVoiceService(self.client, self.model)
        
        # Initialize memoir extraction service (legacy - now using daily extraction)
        try:
            from services.memoir_extraction_service import MemoirExtractionService
            from openai import AsyncOpenAI
            if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
                openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                self.memoir_extraction_service = MemoirExtractionService(openai_client)
                logger.info("Memoir extraction service initialized successfully (legacy)")
            else:
                logger.warning("OpenAI API key not found, memoir extraction disabled")
                self.memoir_extraction_service = None
        except Exception as e:
            logger.error(f"Failed to initialize memoir extraction service: {e}")
            self.memoir_extraction_service = None
        
        # Initialize database services for conversation storage
        try:
            from db.db_services.conversation_service import ConversationService
            self.conversation_service = ConversationService()
            self.current_conversation_id = None
            logger.info("Database conversation service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database conversation service: {e}")
            self.conversation_service = None
        
        # Per-connection send locks to prevent concurrent websocket.send_text errors
        self._send_locks: Dict[WebSocket, asyncio.Lock] = {}

    def _get_send_lock(self, websocket: WebSocket) -> asyncio.Lock:
        """Get or create a send lock for the given websocket connection."""
        lock = self._send_locks.get(websocket)
        if lock is None:
            lock = asyncio.Lock()
            self._send_locks[websocket] = lock
        return lock
    
    def _create_live_config(self, previous_session_handle: Optional[str] = None) -> types.LiveConnectConfig:
        """Create live connection configuration.
        
        Args:
            previous_session_handle: Optional previous session handle for resumption.
            
        Returns:
            LiveConnectConfig object.
        """
        # Only include session resumption when a valid handle exists to avoid API errors
        session_resumption_cfg = None
        if previous_session_handle:
            session_resumption_cfg = types.SessionResumptionConfig(handle=previous_session_handle)

        # Log tools configuration
        logger.info("=" * 60)
        logger.info("🔧 TOOLS CONFIGURATION INITIALIZED")
        logger.info("=" * 60)
        logger.info("📱 Available tools:")
        logger.info("   ✅ switch_to_main_screen: Chuyển sang màn hình chính của ứng dụng")
        logger.info("   ✅ switch_to_medicine_scan_screen: Chuyển sang màn hình quét thuốc")
        logger.info("   🔍 Google Search: Tìm kiếm thông tin cập nhật trên internet")
        logger.info("=" * 60)
        
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
            tools=[
                types.Tool(
                    function_declarations=[
                        types.FunctionDeclaration(
                            name="switch_to_main_screen",
                            description="Chuyển sang màn hình chính của ứng dụng"
                        ),
                        types.FunctionDeclaration(
                            name="switch_to_medicine_scan_screen", 
                            description="Chuyển sang màn hình quét thuốc"
                        )
                    ],
                    google_search=types.GoogleSearch()
                )
            ],
            system_instruction=self.SYSTEM_INSTRUCTION,
            session_resumption=session_resumption_cfg,
            output_audio_transcription=types.AudioTranscriptionConfig(),
            input_audio_transcription=types.AudioTranscriptionConfig(),
            temperature=0.6,
            top_p=0.85,
        )
    
    async def handle_websocket_connection(self, websocket: WebSocket):
        """Handle WebSocket connection for Gemini Live with proper error handling.
        
        Args:
            websocket: FastAPI WebSocket instance.
        """
        # WebSocket is already accepted in the main endpoint
        
        # Load previous session if available
        previous_session_handle = self.session_service.load_previous_session_handle()
        
        logger.info("Starting Gemini session")
        
        # Initialize tasks list for proper cleanup
        send_task = None
        receive_task = None
        ping_task = None
        
        try:
            # Send early setup ack so clients don't wait and close
            try:
                await self._send_safely(websocket, {"setupComplete": {}})
            except Exception:
                pass

            # Optional config; do not close socket if missing/invalid
            config_data = {}
            try:
                config_message = await asyncio.wait_for(
                    websocket.receive_text(), 
                    timeout=settings.WEBSOCKET_CONFIG_TIMEOUT
                )
                config_data = json.loads(config_message)
                logger.info(f"Received config: {config_data}")
            except asyncio.TimeoutError:
                logger.warning("No config received within timeout - continuing with defaults")
            except json.JSONDecodeError:
                logger.warning("Invalid JSON in config message - continuing with defaults")

            # Extract user_id from config for database operations (optional)
            user_id_raw = config_data.get("user_id") if isinstance(config_data, dict) else None
            if user_id_raw:
                try:
                    import uuid
                    if isinstance(user_id_raw, str):
                        try:
                            uuid.UUID(user_id_raw)
                            self.current_user_id = user_id_raw
                        except ValueError:
                            if user_id_raw.startswith("test_"):
                                self.current_user_id = "550e8400-e29b-41d4-a716-446655440000"
                                logger.info(f"Test user ID detected, using test UUID: {self.current_user_id}")
                            else:
                                logger.warning(f"Invalid UUID format: {user_id_raw}")
                                self.current_user_id = None
                    else:
                        self.current_user_id = str(user_id_raw)
                    if self.current_user_id:
                        logger.info(f"User ID set for session: {self.current_user_id}")
                    else:
                        logger.warning("Invalid user_id format - database operations disabled")
                except Exception as e:
                    logger.error(f"Error processing user_id: {e}")
                    self.current_user_id = None

            # Create live connection config
            config = self._create_live_config(previous_session_handle)
            
            async with self.client.aio.live.connect(model=self.model, config=config) as session:
                # Create conversation in database if user_id is available
                if self.current_user_id and self.conversation_service:
                    try:
                        conversation_id = await self.conversation_service.create_conversation(
                            user_id=self.current_user_id,
                            title=f"Cuộc trò chuyện {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"
                        )
                        if conversation_id:
                            self.current_conversation_id = conversation_id
                            logger.info(f"Created conversation {self.current_conversation_id} for user {self.current_user_id}")
                        else:
                            logger.warning("Failed to create conversation in database")
                    except Exception as e:
                        logger.error(f"Error creating conversation in database: {e}")
                
                # Create tasks
                send_task = asyncio.create_task(self._send_to_gemini(websocket, session))
                receive_task = asyncio.create_task(self._receive_from_gemini(websocket, session))
                ping_task = asyncio.create_task(self._ping_websocket(websocket))
                
                # Wait for any task to complete or fail
                done, pending = await asyncio.wait(
                    [send_task, receive_task, ping_task],
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Cancel remaining tasks
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                    except Exception as e:
                        logger.error(f"Error cancelling task: {e}")
                
                # Check for exceptions in completed tasks
                for task in done:
                    try:
                        await task
                    except Exception as e:
                        logger.error(f"Task completed with error: {e}")
                
        except WebSocketDisconnect:
            logger.info("WebSocket disconnected by client")
        except Exception as e:
            logger.error(f"Error in Gemini session: {e}")
            await self._close_websocket_safely(websocket, 4002, "Internal error")
        finally:
            # Ensure all tasks are cancelled
            for task in [send_task, receive_task, ping_task]:
                if task and not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                    except Exception:
                        pass
            
            # Note: Memoir extraction is now handled daily by scheduler
            # Individual conversation memoir extraction is disabled
            logger.info("Session ended - memoir extraction will be handled by daily scheduler")
            
            logger.info("Gemini session closed")
            
            # Cleanup send lock for this connection
            try:
                self._send_locks.pop(websocket, None)
            except Exception:
                pass
    
    async def _ping_websocket(self, websocket: WebSocket):
        """Send periodic keepalive messages to maintain WebSocket connection.
        
        Args:
            websocket: FastAPI WebSocket instance.
            
        Note: FastAPI WebSocket doesn't have ping() method, so we send keepalive messages instead.
        """
        try:
            keepalive_count = 0
            while True:
                await asyncio.sleep(settings.WEBSOCKET_PING_INTERVAL)
                try:
                    # Check if WebSocket is still connected safely
                    if hasattr(websocket, 'client_state') and websocket.client_state.name == 'CONNECTED':
                        # Send a keepalive message instead of ping
                        keepalive_data = {
                            "type": "keepalive", 
                            "timestamp": datetime.datetime.now().isoformat(),
                            "count": keepalive_count,
                            "server_time": datetime.datetime.now().strftime("%H:%M:%S")
                        }
                        
                        # Use _send_safely method for consistent error handling
                        await self._send_safely(websocket, keepalive_data)
                        keepalive_count += 1
                        logger.debug(f"Sent WebSocket keepalive #{keepalive_count}")
                    else:
                        logger.warning("WebSocket not connected, stopping keepalive")
                        break
                except asyncio.TimeoutError:
                    logger.error("Timeout sending keepalive message")
                    break
                except Exception as e:
                    logger.error(f"Error sending keepalive: {e}")
                    break
        except asyncio.CancelledError:
            logger.debug("Keepalive task cancelled")
        except Exception as e:
            logger.error(f"Error in keepalive task: {e}")
    
    async def _close_websocket_safely(self, websocket: WebSocket, code: int = 1000, reason: str = ""):
        """Safely close WebSocket connection.
        
        Args:
            websocket: FastAPI WebSocket instance.
            code: Close code.
            reason: Close reason.
        """
        try:
            await asyncio.wait_for(
                websocket.close(code=code, reason=reason),
                timeout=settings.WEBSOCKET_CLOSE_TIMEOUT
            )
        except Exception as e:
            logger.error(f"Error closing WebSocket: {e}")
    
    async def _send_to_gemini(self, websocket: WebSocket, session):
        """Handle sending messages from WebSocket to Gemini with improved error handling.
        
        Args:
            websocket: FastAPI WebSocket instance.
            session: Gemini live session.
        """
        try:
            while True:
                try:
                    # Add timeout for receiving messages (support both text and binary frames)
                    incoming = await asyncio.wait_for(
                        websocket.receive(),
                        timeout=settings.WEBSOCKET_MESSAGE_TIMEOUT
                    )
                    
                    # Handle raw binary audio frames (PCM 16kHz)
                    if isinstance(incoming, dict) and incoming.get("bytes") is not None:
                        raw_audio = incoming.get("bytes") or b""
                        if raw_audio:
                            await session.send_realtime_input(
                                audio=types.Blob(data=raw_audio, mime_type="audio/pcm;rate=16000")
                            )
                        continue
                    
                    # Handle textual JSON messages
                    if isinstance(incoming, dict) and incoming.get("text") is not None:
                        message = incoming.get("text") or ""
                    else:
                        # Unknown frame type; continue listening
                        continue
                    
                    data = json.loads(message)
                
                    # Handle keepalive messages
                    if data.get("type") == "keepalive":
                        logger.debug("Received keepalive from client")
                        # Send keepalive response to maintain connection
                        await self._send_safely(websocket, {
                            "type": "keepalive_response",
                            "timestamp": datetime.datetime.now().isoformat(),
                            "server_time": datetime.datetime.now().strftime("%H:%M:%S")
                        })
                        continue
                
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
                        logger.info(f"Sending text: {text_content}")
                        await session.send_client_content(
                            turns={"role": "user", "parts": [{"text": text_content}]}, turn_complete=True
                        )
                        # Persist immediately for text input
                        self._append_to_conversation_history("user", text_content)
                    
                    # Handle voice notification requests
                    elif "voice_notification_request" in data:
                        await self._handle_voice_notification_request(websocket, data["voice_notification_request"])
                
                except asyncio.TimeoutError:
                    logger.warning("Timeout waiting for message from client - continuing to maintain connection")
                    # Don't break on timeout, just continue to maintain connection
                    continue
                except WebSocketDisconnect:
                    logger.info("Client disconnected")
                    break
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON from client: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error sending to Gemini: {e}")
                    # Only break on critical errors, not on temporary issues
                    if "connection" in str(e).lower() or "disconnect" in str(e).lower():
                        break
                    continue
                    
        except asyncio.CancelledError:
            logger.info("Send task cancelled")
        except Exception as e:
            logger.error(f"Error in send_to_gemini: {e}")
        finally:
            logger.info("send_to_gemini closed")
    
    async def _receive_from_gemini(self, websocket: WebSocket, session):
        """Handle receiving messages from Gemini and sending to WebSocket with improved error handling.
        
        Args:
            websocket: FastAPI WebSocket instance.
            session: Gemini live session.
        """
        try:
            while True:
                try:
                    async for response in session.receive():
                        # Check if WebSocket is still connected before sending
                        if websocket.client_state.name != 'CONNECTED':
                            logger.warning("WebSocket not connected, stopping receive")
                            break
                            
                        # Xử lý turn detection events
                        if hasattr(response, 'turn_detection') and response.turn_detection:
                            if hasattr(response.turn_detection, 'type'):
                                await self._send_safely(websocket, {
                                    "turn_detection": {
                                        "type": response.turn_detection.type
                                    }
                                })
                        
                        # Handle tool calls
                        if hasattr(response, 'tool_call') and response.tool_call:
                            await self._handle_tool_calls(websocket, session, response.tool_call)
                            continue
                        
                        if response.server_content and hasattr(response.server_content, 'interrupted') and response.server_content.interrupted is not None:
                            logger.info(f"[{datetime.datetime.now()}] Generation interrupted")
                            await self._send_safely(websocket, {"interrupted": "True"})
                            continue

                        if response.usage_metadata:
                            usage = response.usage_metadata
                            logger.info(f'Used {usage.total_token_count} tokens in total.')

                        if response.session_resumption_update:
                            update = response.session_resumption_update
                            if update.resumable and update.new_handle:
                                # The handle should be retained and linked to the session.
                                self.session_service.save_previous_session_handle(update.new_handle)
                                logger.info(f"Resumed session update with handle: {update.new_handle}")

                        if response.server_content and hasattr(response.server_content, 'output_transcription') and response.server_content.output_transcription is not None:
                            transcription_text = response.server_content.output_transcription.text
                            is_finished = response.server_content.output_transcription.finished
                            
                            # Hiển thị transcription vào terminal
                            if transcription_text:
                                logger.info(f"Gemini: {transcription_text}")
                                if is_finished:
                                    logger.info("   [Hoàn thành]")
                            
                            await self._send_safely(websocket, {
                                "transcription": {
                                    "text": transcription_text,
                                    "sender": "Gemini",
                                    "finished": is_finished
                                }
                            })
                            # Accumulate assistant transcription
                            if transcription_text:
                                self._current_assistant_output += transcription_text

                            # When assistant transcription finished, store to history
                            if is_finished and self._current_assistant_output.strip():
                                self._append_to_conversation_history("assistant", self._current_assistant_output.strip())
                                self._current_assistant_output = ""

                        if response.server_content and hasattr(response.server_content, 'input_transcription') and response.server_content.input_transcription is not None:
                            user_transcription_text = response.server_content.input_transcription.text
                            is_user_finished = response.server_content.input_transcription.finished
                            
                            # Hiển thị transcription của user vào terminal
                            if user_transcription_text:
                                logger.info(f"User: {user_transcription_text}")
                                if is_user_finished:
                                    logger.info("   [Hoàn thành]")
                            # Accumulate user transcription
                            if user_transcription_text:
                                self._current_user_input += user_transcription_text
                            
                            await self._send_safely(websocket, {
                                "transcription": {
                                    "text": user_transcription_text,
                                    "sender": "User",
                                    "finished": is_user_finished
                                }
                            })

                            # When user transcription finished, store to history
                            if is_user_finished and self._current_user_input.strip():
                                self._append_to_conversation_history("user", self._current_user_input.strip())
                                self._current_user_input = ""

                        if response.server_content is None:
                            continue
                            
                        model_turn = response.server_content.model_turn
                        if model_turn:
                            for part in model_turn.parts:
                                if hasattr(part, 'text') and part.text is not None:
                                    await self._send_safely(websocket, {"text": part.text})
                                
                                elif hasattr(part, 'inline_data') and part.inline_data is not None:
                                    try:
                                        audio_data = part.inline_data.data
                                        base64_audio = base64.b64encode(audio_data).decode('utf-8')
                                        await self._send_safely(websocket, {
                                            "audio": base64_audio,
                                        })
                                        #logger.debug(f"Sent assistant audio to client: {base64_audio[:32]}...")
                                    except Exception as e:
                                        logger.error(f"Error processing assistant audio: {e}")
                        
                        if response.server_content and response.server_content.turn_complete:
                            logger.info('\n<Turn complete>')
                            logger.info("="*50)  # Thêm dòng phân cách rõ ràng hơn
                            await self._send_safely(websocket, {
                                "transcription": {
                                    "text": "",
                                    "sender": "Gemini",
                                    "finished": True
                                }
                            })

                            # Persist any remaining buffered texts at end of turn
                            if self._current_user_input.strip():
                                self._append_to_conversation_history("user", self._current_user_input.strip())
                                self._current_user_input = ""

                            if self._current_assistant_output.strip():
                                self._append_to_conversation_history("assistant", self._current_assistant_output.strip())
                                self._current_assistant_output = ""
                            
                except WebSocketDisconnect:
                    logger.info("WebSocket disconnected during receive")
                    break
                except Exception as e:
                    logger.error(f"Error receiving from Gemini: {e}")
                    break

        except asyncio.CancelledError:
            logger.info("Receive task cancelled")
        except Exception as e:
            logger.error(f"Error in receive_from_gemini: {e}")
        finally:
            logger.info("Gemini connection closed (receive)")
    
    async def _send_safely(self, websocket: WebSocket, data: dict):
        """Safely send data to WebSocket with error handling.
        
        Args:
            websocket: FastAPI WebSocket instance.
            data: Data to send.
        """
        try:
            # Check if WebSocket is still connected before sending
            if hasattr(websocket, 'client_state') and websocket.client_state.name == 'CONNECTED':
                # Serialize sends for this connection
                lock = self._get_send_lock(websocket)
                async with lock:
                    await websocket.send_text(json.dumps(data))
            else:
                logger.warning("Attempted to send data to disconnected WebSocket")
        except Exception as e:
            logger.error(f"Error sending data to WebSocket: {e}")
            # Don't re-raise for non-critical errors to maintain connection stability
            pass

    def _append_to_conversation_history(self, role: str, text: str):
        """Append a new message to the conversation history and persist it.

        Args:
            role: "user" or "assistant".
            text: Message content.
        """
        entry = {
            "role": role,
            "text": text,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.conversation_history.append(entry)
        
        # Save to database if available
        if self.conversation_service and self.current_conversation_id:
            try:
                # Convert role to enum
                from db.models import ConversationRole
                db_role = ConversationRole.USER if role == "user" else ConversationRole.ASSISTANT
                
                # Save message to database asynchronously
                asyncio.create_task(self._save_message_to_database(db_role, text))
            except Exception as e:
                logger.error(f"Error saving message to database: {e}")
        
        # Also persist to file as backup
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.conversation_history_file) or ".", exist_ok=True)
            with open(self.conversation_history_file, "w", encoding="utf-8") as f:
                json_lib.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save conversation history to file: {e}")
    
    async def _save_message_to_database(self, role, content: str):
        """Save a message to the database.
        
        Args:
            role: ConversationRole enum value
            content: Message content
        """
        try:
            if self.conversation_service and self.current_conversation_id:
                await self.conversation_service.add_message(
                    conversation_id=self.current_conversation_id,
                    role=role,
                    content=content
                )
        except Exception as e:
            logger.error(f"Failed to save message to database: {e}")
    
    async def extract_memoir_on_disconnect(self):
        """Extract memoir from entire conversation history when client disconnects.
        
        This method is called once when the WebSocket connection ends to process
        the complete conversation and extract important memoir information.
        """
        try:
            # Skip if memoir service is not available
            if not self.memoir_extraction_service:
                logger.info("Memoir extraction service not available")
                return
                
            # Check if we have any conversation to process
            if not self.conversation_history or len(self.conversation_history) == 0:
                logger.info("No conversation history to process for memoir extraction")
                return
                
            logger.info(f"🎭 Starting final memoir extraction for {len(self.conversation_history)} messages...")
            
            # Process the entire conversation history at once
            result = await self.memoir_extraction_service.process_conversation_history_background()
            
            if result.get("success"):
                if result.get("extracted_info"):
                    logger.info("✅ Memoir extraction completed successfully")
                    logger.info(f"   - Processed {result.get('conversation_length', 0)} messages")
                    logger.info(f"   - Generated memoir: {len(result.get('extracted_info', ''))} characters")
                else:
                    logger.info("✅ Memoir extraction completed - no significant stories found")
            else:
                logger.warning(f"❌ Memoir extraction failed: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error in final memoir extraction: {e}")
            # Don't let memoir extraction errors affect the main conversation flow

    async def _handle_voice_notification_request(self, websocket: WebSocket, request_data: dict):
        """Handle voice notification generation request.
        
        Args:
            websocket: FastAPI WebSocket instance.
            request_data: Voice notification request data.
        """
        try:
            notification_text = request_data.get("text", "")
            notification_type = request_data.get("type", "info")
            request_id = request_data.get("request_id", "")
            
            logger.info(f"Generating voice notification: {notification_text} (type: {notification_type})")
            
            if not notification_text:
                await self._send_safely(websocket, {
                    "type": "voice_notification_response",
                    "success": False,
                    "error": "Notification text is required",
                    "request_id": request_id
                })
                return
            
            # Generate voice notification
            if notification_type == "emergency":
                audio_base64 = await self.notification_voice_service.generate_voice_notification_base64(
                    f"THÔNG BÁO KHẨN CẤP: {notification_text}"
                )
            else:
                audio_base64 = await self.notification_voice_service.generate_voice_notification_base64(notification_text)
            
            if audio_base64:
                response_data = {
                    "type": "voice_notification_response",
                    "success": True,
                    "data": {
                        "notification_text": notification_text,
                        "audio_base64": audio_base64,
                        "audio_format": "audio/pcm",
                        "notification_type": notification_type,
                        "timestamp": datetime.datetime.now().isoformat(),
                    },
                    "request_id": request_id
                }
                await self._send_safely(websocket, response_data)
                logger.info(f"Voice notification generated successfully for: {notification_text}")
            else:
                await self._send_safely(websocket, {
                    "type": "voice_notification_response",
                    "success": False,
                    "error": "Failed to generate voice notification",
                    "request_id": request_id
                })
                logger.error(f"Failed to generate voice notification for: {notification_text}")
                
        except Exception as e:
            logger.error(f"Error handling voice notification request: {e}")
            await self._send_safely(websocket, {
                "type": "voice_notification_response",
                "success": False,
                "error": str(e),
                "request_id": request_data.get("request_id", "")
            })

    async def _handle_tool_calls(self, websocket: WebSocket, session, tool_call):
        """Handle tool calls from Gemini and send responses.
        
        Args:
            websocket: FastAPI WebSocket instance.
            session: Gemini live session.
            tool_call: Tool call response from Gemini.
        """
        try:
            # Log tool call received
            logger.info("=" * 60)
            logger.info("🎯 TOOL CALL RECEIVED FROM GEMINI AI")
            logger.info("=" * 60)
            
            if not hasattr(tool_call, 'function_calls') or not tool_call.function_calls:
                logger.warning("❌ No function calls in tool_call response")
                return
            
            function_responses = []
            
            for function_call in tool_call.function_calls:
                function_name = function_call.name
                function_id = function_call.id
                
                logger.info(f"🔧 Processing tool call:")
                logger.info(f"   📝 Function Name: {function_name}")
                logger.info(f"   🆔 Function ID: {function_id}")
                logger.info(f"   ⏰ Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info("-" * 40)
                
                # Send tool call notification to frontend
                await self._send_safely(websocket, {
                    "type": "tool_call",
                    "function_name": function_name,
                    "function_id": function_id,
                    "timestamp": datetime.datetime.now().isoformat()
                })
                
                # Create function response based on the tool called
                if function_name == "switch_to_main_screen":
                    logger.info("🏠 EXECUTING: switch_to_main_screen")
                    logger.info("   📱 Action: Chuyển về màn hình chính")
                    
                    # Send response to frontend to switch to main screen
                    await self._send_safely(websocket, {
                        "type": "screen_navigation",
                        "action": "switch_to_main_screen",
                        "message": "Đang chuyển sang màn hình chính...",
                        "timestamp": datetime.datetime.now().isoformat()
                    })
                    
                    # Create success response for Gemini
                    function_response = types.FunctionResponse(
                        id=function_id,
                        name=function_name,
                        response={"result": "success", "message": "Đã chuyển sang màn hình chính"}
                    )
                    
                    logger.info("✅ switch_to_main_screen completed successfully")
                    
                elif function_name == "switch_to_medicine_scan_screen":
                    logger.info("📱 EXECUTING: switch_to_medicine_scan_screen")
                    logger.info("   📱 Action: Chuyển sang màn hình quét thuốc")
                    
                    # Send response to frontend to switch to medicine scan screen
                    await self._send_safely(websocket, {
                        "type": "screen_navigation",
                        "action": "switch_to_medicine_scan_screen", 
                        "message": "Đang chuyển sang màn hình quét thuốc...",
                        "timestamp": datetime.datetime.now().isoformat()
                    })
                    
                    # Create success response for Gemini
                    function_response = types.FunctionResponse(
                        id=function_id,
                        name=function_name,
                        response={"result": "success", "message": "Đã chuyển sang màn hình quét thuốc"}
                    )
                    
                    logger.info("✅ switch_to_medicine_scan_screen completed successfully")
                    
                else:
                    # Unknown function - create error response
                    logger.warning(f"❌ UNKNOWN FUNCTION CALLED: {function_name}")
                    logger.warning(f"   ⚠️ This function is not supported")
                    
                    function_response = types.FunctionResponse(
                        id=function_id,
                        name=function_name,
                        response={"result": "error", "message": f"Không hỗ trợ chức năng: {function_name}"}
                    )
                
                function_responses.append(function_response)
                logger.info(f"📤 Function response created for: {function_name}")
            
            # Send tool responses back to Gemini
            if function_responses:
                await session.send_tool_response(function_responses=function_responses)
                logger.info(f"🚀 Sent {len(function_responses)} tool responses back to Gemini AI")
                logger.info("=" * 60)
                logger.info("🎯 TOOL CALL PROCESSING COMPLETED SUCCESSFULLY")
                logger.info("=" * 60)
                
        except Exception as e:
            logger.error("=" * 60)
            logger.error("💥 ERROR IN TOOL CALL PROCESSING")
            logger.error("=" * 60)
            logger.error(f"❌ Error details: {e}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            logger.error(f"❌ Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Try to send error response to Gemini if possible
            try:
                if hasattr(tool_call, 'function_calls') and tool_call.function_calls:
                    error_responses = []
                    for function_call in tool_call.function_calls:
                        error_response = types.FunctionResponse(
                            id=function_call.id,
                            name=function_call.name,
                            response={"result": "error", "message": f"Lỗi xử lý: {str(e)}"}
                        )
                        error_responses.append(error_response)
                    
                    if error_responses:
                        await session.send_tool_response(function_responses=error_responses)
                        logger.info(f"📤 Sent error responses to Gemini for {len(error_responses)} functions")
            except Exception as send_error:
                logger.error(f"❌ Failed to send error response to Gemini: {send_error}")
            
            logger.error("=" * 60)

    async def analyze_image_with_text(self, image_base64: str, prompt: str) -> str:
        """Analyze an image with text prompt using Gemini.
        
        Args:
            image_base64: Base64 encoded image string.
            prompt: Text prompt for image analysis.
            
        Returns:
            Analysis result as string.
        """
        try:
            if not self.client:
                raise Exception("Gemini client not initialized")
            
            # Create content parts for the request
            content_parts = [
                types.Part.from_text(prompt),
                types.Part.from_data(
                    data=base64.b64decode(image_base64),
                    mime_type="image/jpeg"
                )
            ]
            
            # Generate content
            response = self.client.generate_content(
                model=self.model,
                contents=types.Content(parts=content_parts),
                generation_config=types.GenerationConfig(
                    temperature=0.5,
                    top_p=0.9,
                    top_k=64,
                    max_output_tokens=4096,
                )
            )
            
            if response.text:
                logger.info(f"Image analysis completed successfully")
                return response.text
            else:
                raise Exception("No response from Gemini")
                
        except Exception as e:
            logger.error(f"Error analyzing image with Gemini: {e}")
            raise e
