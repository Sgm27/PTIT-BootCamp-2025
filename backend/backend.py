import asyncio
import json
import os
import base64
import datetime
from typing import Optional, Dict, Any

from fastapi import FastAPI, WebSocket, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from google import genai
from google.genai import types
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Initialize FastAPI app
app = FastAPI(
    title="AI Healthcare Assistant API",
    description="Backend API for AI Healthcare Assistant with Gemini Live and Medicine Scanner",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
gemini_api_key = os.getenv('GOOGLE_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')
MODEL = "gemini-live-2.5-flash-preview"

if not gemini_api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is required")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

gemini_client = genai.Client(api_key=gemini_api_key)
openai_client = AsyncOpenAI(api_key=openai_api_key)

# Pydantic models
class MedicineScanRequest(BaseModel):
    input: str  # Base64 string or URL

class TextExtractRequest(BaseModel):
    text: str

class HealthResponse(BaseModel):
    success: bool
    result: str
    error: Optional[str] = None

# Session management functions
def load_previous_session_handle():
    try:
        with open('session_handle.json', 'r') as f:
            data = json.load(f)
            handle = data.get('previous_session_handle', None)
            session_time = data.get('session_time', None)
            
            if handle and session_time:
                session_datetime = datetime.datetime.fromisoformat(session_time)
                current_time = datetime.datetime.now()
                time_diff = current_time - session_datetime
                
                if time_diff.total_seconds() < 60:
                    print(f"Loaded previous session handle: {handle} (created {time_diff.total_seconds():.1f}s ago)")
                    return handle
                else:
                    print(f"Previous session handle expired ({time_diff.total_seconds():.1f}s ago, > 60s)")
                    return None
            else:
                print("No valid session handle or time found")
                return None
    except FileNotFoundError:
        print("No previous session file found")
        return None
    except Exception as e:
        print(f"Error loading session handle: {e}")
        return None

def save_previous_session_handle(handle):
    current_time = datetime.datetime.now().isoformat()
    with open('session_handle.json', 'w') as f:
        json.dump({
            'previous_session_handle': handle,
            'session_time': current_time
        }, f)
    print(f"Saved session handle with timestamp: {current_time}")

# Medicine Scanner Class
class MedicineScanner:
    """A class for scanning and identifying medicines from images using OpenAI's vision model."""
    
    SYSTEM_PROMPT = """
    Bạn là một chuyên gia trong việc nhận diện và cung cấp thông tin về thuốc.
    Bạn sẽ nhận được một hình ảnh hoặc URL của một hình ảnh thuốc và trả về tên thuốc đó
    Không cần trả lời thêm bất kỳ thông tin nào khác ngoài tên thuốc.
    """
    
    def __init__(self, client: AsyncOpenAI, model: str = "gpt-4o", temperature: float = 0.2):
        self.client = client
        self.model = model
        self.temperature = temperature
    
    @staticmethod
    def encode_image(image_path: str) -> str:
        """Encodes an image file to a base64 string."""
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_string
        except FileNotFoundError:
            raise FileNotFoundError(f"Image file not found: {image_path}")
        except Exception as e:
            raise IOError(f"Error reading image file: {e}")
    
    async def _create_completion(self, content_list: list) -> Dict[str, Any]:
        """Create a completion request to OpenAI."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": content_list}
                ],
                temperature=self.temperature,
            )
            
            return {
                "result": response.choices[0].message.content.strip(),
                "success": True
            }
        except Exception as e:
            return {
                "result": f"Lỗi khi gọi API: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    async def scan_from_url(self, image_url: str) -> Dict[str, Any]:
        """Scan medicine from an image URL."""
        if not image_url:
            return {
                "result": "URL hình ảnh không được cung cấp.",
                "success": False,
                "error": "Missing image URL"
            }
        
        content_list = [
            {
                "type": "image_url",
                "image_url": {"url": image_url}
            }
        ]
        
        return await self._create_completion(content_list)
    
    async def scan_from_base64(self, base64_string: str) -> Dict[str, Any]:
        """Scan medicine from a base64 encoded image string."""
        if not base64_string:
            return {
                "result": "Chuỗi base64 không được cung cấp.",
                "success": False,
                "error": "Missing base64 string"
            }
        
        try:
            content_list = [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_string}"
                    }
                }
            ]
            
            return await self._create_completion(content_list)
        except Exception as e:
            return {
                "result": f"Lỗi xử lý chuỗi base64: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    async def scan_medicine(self, input_data: str) -> Dict[str, Any]:
        """Get medicine information from an image URL or base64 string."""
        if not input_data:
            raise ValueError("Input must be provided.")
        
        if input_data.startswith("http"):
            return await self.scan_from_url(input_data)
        else:
            return await self.scan_from_base64(input_data)

# Text Extraction Class
class TextExtractor:
    """A class for extracting information from text for memoir purposes."""
    
    SYSTEM_PROMPT = """
    Bạn là chuyên gia trong việc trích xuất thông tin từ văn bản. 
    Nhiệm vụ của bạn là phân tích văn bản và trích xuất các thông tin quan trọng,
    bao gồm các sự kiện, nhân vật, địa điểm và các chi tiết liên quan khác.
    Hãy đảm bảo rằng thông tin được trích xuất rõ ràng và có cấu trúc
    để dễ dàng sử dụng trong việc viết hồi ký.

    Bạn được cung cấp một đoạn hội thoại với người dùng và AI
    để trích xuất thông tin từ văn bản.
    Hãy trả lời bằng cách cung cấp các thông tin đã được trích xuất.
    Chỉ trả lời văn bản trích xuất, không cần giải thích hay bình luận thêm.
    """
    
    def __init__(self, client: AsyncOpenAI, model: str = "gpt-4o-mini", temperature: float = 0.7):
        self.client = client
        self.model = model
        self.temperature = temperature
    
    async def extract_info_for_memoir(self, text: str) -> str:
        """Extracts information from the provided text for memoir purposes."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": text}
                ],
                temperature=self.temperature,
                seed=42,
            )
            
            return response.choices[0].message.content.strip() if response.choices else ""
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error extracting text: {str(e)}")

# Initialize service classes
medicine_scanner = MedicineScanner(openai_client)
text_extractor = TextExtractor(openai_client)

# API Routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AI Healthcare Assistant API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}

@app.post("/api/scan-medicine", response_model=HealthResponse)
async def scan_medicine_endpoint(request: MedicineScanRequest):
    """Scan medicine from image URL or base64 string."""
    try:
        result = await medicine_scanner.scan_medicine(request.input)
        return HealthResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scan-medicine-file")
async def scan_medicine_file_endpoint(file: UploadFile = File(...)):
    """Scan medicine from uploaded image file."""
    try:
        # Read file content
        content = await file.read()
        
        # Encode to base64
        base64_string = base64.b64encode(content).decode("utf-8")
        
        # Scan medicine
        result = await medicine_scanner.scan_from_base64(base64_string)
        return HealthResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/extract-memoir-info", response_model=HealthResponse)
async def extract_memoir_info_endpoint(request: TextExtractRequest):
    """Extract information from text for memoir purposes."""
    try:
        result = await text_extractor.extract_info_for_memoir(request.text)
        return HealthResponse(success=True, result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for Gemini Live (keeping the original functionality)
@app.websocket("/gemini-live")
async def gemini_live_websocket(websocket: WebSocket):
    """WebSocket endpoint for Gemini Live chat."""
    await websocket.accept()
    
    previous_session_handle = load_previous_session_handle()
    
    print(f"Starting Gemini session")
    try:
        config_message = await websocket.receive_text()
        config_data = json.loads(config_message)

        config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Aoede"
                    )
                ),
                language_code='vi-VN',
            ),
            system_instruction="""
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
            """,
            session_resumption=types.SessionResumptionConfig(
                handle=previous_session_handle
            ),
            output_audio_transcription=types.AudioTranscriptionConfig(),
            input_audio_transcription=types.AudioTranscriptionConfig(),
            temperature=0.7,
            top_p=0.9,
        )

        async with gemini_client.aio.live.connect(model=MODEL, config=config) as session:

            async def send_to_gemini():
                try:
                    async for message in websocket.iter_text():
                        try:
                            data = json.loads(message)
                        
                            if "realtime_input" in data:
                                for chunk in data["realtime_input"]["media_chunks"]:
                                    if chunk["mime_type"] == "audio/pcm":
                                        await session.send_realtime_input(
                                            audio=types.Blob(data=chunk["data"], mime_type="audio/pcm;rate=16000")
                                        )
                                    elif chunk["mime_type"].startswith("image/"):
                                        # Handle image input if needed
                                        pass

                            elif "text" in data:
                                text_content = data["text"]
                                print(f"📤 Sending text: {text_content}")
                                await session.send_client_content(
                                    turns={"role": "user", "parts": [{"text": text_content}]}, turn_complete=True
                                )
                                
                        except Exception as e:
                            print(f"Error sending to Gemini: {e}")
                    print("Client connection closed (send)")
                except Exception as e:
                    print(f"Error sending to Gemini: {e}")
                finally:
                    print("send_to_gemini closed")

            async def receive_from_gemini():
                try:
                    while True:
                        try:
                            async for response in session.receive():
                                # Handle turn detection events
                                if hasattr(response, 'turn_detection') and response.turn_detection:
                                    if hasattr(response.turn_detection, 'type'):
                                        pass
                                
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
                                        save_previous_session_handle(update.new_handle)

                                if response.server_content and hasattr(response.server_content, 'output_transcription') and response.server_content.output_transcription is not None:
                                    transcription_text = response.server_content.output_transcription.text
                                    is_finished = response.server_content.output_transcription.finished
                                    
                                    if transcription_text:
                                        print(f"🤖 Gemini: {transcription_text}")
                                    
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
                                    
                                    if user_transcription_text:
                                        print(f"👤 User: {user_transcription_text}")
                                    
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
                                        if hasattr(part, 'inline_data'):
                                            audio_data = part.inline_data.data
                                            await websocket.send_bytes(audio_data)

                                if response.server_content and response.server_content.turn_complete:
                                    print('\n<Turn complete>')
                                    print("="*50)
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

            # Start send and receive tasks
            send_task = asyncio.create_task(send_to_gemini())
            receive_task = asyncio.create_task(receive_from_gemini())
            await asyncio.gather(send_task, receive_task)

    except Exception as e:
        print(f"Error in Gemini session: {e}")
    finally:
        print("Gemini session closed.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
