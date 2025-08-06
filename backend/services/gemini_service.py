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
from typing import Optional

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
        
        # Initialize memoir extraction service
        try:
            from services.memoir_extraction_service import MemoirExtractionService
            from openai import AsyncOpenAI
            if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
                openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                self.memoir_extraction_service = MemoirExtractionService(openai_client)
                logger.info("Memoir extraction service initialized successfully")
            else:
                logger.warning("OpenAI API key not found, memoir extraction disabled")
                self.memoir_extraction_service = None
        except Exception as e:
            logger.error(f"Failed to initialize memoir extraction service: {e}")
            self.memoir_extraction_service = None
    
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
        """Handle WebSocket connection for Gemini Live with proper error handling.
        
        Args:
            websocket: FastAPI WebSocket instance.
        """
        await websocket.accept()
        
        # Load previous session if available
        previous_session_handle = self.session_service.load_previous_session_handle()
        
        logger.info("Starting Gemini session")
        
        # Initialize tasks list for proper cleanup
        send_task = None
        receive_task = None
        ping_task = None
        
        try:
            # Wait for initial config message with timeout
            try:
                config_message = await asyncio.wait_for(
                    websocket.receive_text(), 
                    timeout=30.0  # 30 second timeout for config
                )
                config_data = json.loads(config_message)
                logger.info(f"Received config: {config_data}")
            except asyncio.TimeoutError:
                logger.error("Timeout waiting for config message")
                await self._close_websocket_safely(websocket, 4000, "Config timeout")
                return
            except json.JSONDecodeError:
                logger.error("Invalid JSON in config message")
                await self._close_websocket_safely(websocket, 4001, "Invalid config")
                return
            
            # Create live connection config
            config = self._create_live_config(previous_session_handle)
            
            async with self.client.aio.live.connect(model=self.model, config=config) as session:
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
            
            # Extract memoir from entire conversation when session ends
            try:
                await self.extract_memoir_on_disconnect()
            except Exception as e:
                logger.error(f"Error during final memoir extraction: {e}")
            
            logger.info("Gemini session closed")
    
    async def _ping_websocket(self, websocket: WebSocket):
        """Send periodic keepalive messages to maintain WebSocket connection.
        
        Args:
            websocket: FastAPI WebSocket instance.
            
        Note: FastAPI WebSocket doesn't have ping() method, so we send keepalive messages instead.
        """
        try:
            while True:
                await asyncio.sleep(settings.WEBSOCKET_PING_INTERVAL)
                try:
                    # Check if WebSocket is still connected
                    if websocket.client_state.name == 'CONNECTED':
                        # Send a keepalive message instead of ping
                        await websocket.send_text(json.dumps({"type": "keepalive", "timestamp": datetime.datetime.now().isoformat()}))
                        logger.debug("Sent WebSocket keepalive")
                    else:
                        logger.warning("WebSocket not connected, stopping keepalive")
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
                    # Add timeout for receiving messages
                    message = await asyncio.wait_for(
                        websocket.receive_text(),
                        timeout=120.0  # 2 minute timeout
                    )
                    data = json.loads(message)
                
                    # Handle keepalive messages
                    if data.get("type") == "keepalive":
                        logger.debug("Received keepalive from client")
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
                    logger.warning("Timeout waiting for message from client")
                    break
                except WebSocketDisconnect:
                    logger.info("Client disconnected")
                    break
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON from client: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error sending to Gemini: {e}")
                    break
                    
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
            if websocket.client_state.name == 'CONNECTED':
                await websocket.send_text(json.dumps(data))
            else:
                logger.warning("Attempted to send data to disconnected WebSocket")
        except Exception as e:
            logger.error(f"Error sending data to WebSocket: {e}")
            raise  # Re-raise to let calling function handle

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
        # Persist to file
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.conversation_history_file) or ".", exist_ok=True)
            with open(self.conversation_history_file, "w", encoding="utf-8") as f:
                json_lib.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
                
            # Auto extraction disabled - will extract only on disconnect
            
        except Exception as e:
            logger.error(f"Failed to save conversation history: {e}")
    
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
