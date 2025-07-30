import asyncio
import json
import os
import uuid
from google import genai
import base64
from google.genai import types

from websockets.server import WebSocketServerProtocol
import websockets.server
import io
from pydub import AudioSegment
import datetime
from dotenv import load_dotenv

load_dotenv(override=True)  

gemini_api_key = os.getenv('GOOGLE_API_KEY')
MODEL = "gemini-live-2.5-flash-preview"  

client = genai.Client(
    api_key=gemini_api_key,
)

def load_previous_session_handle():
    try:
        with open('session_handle.json', 'r') as f:
            data = json.load(f)
            handle = data.get('previous_session_handle', None)
            session_time = data.get('session_time', None)
            
            if handle and session_time:
                # Parse thời gian session
                session_datetime = datetime.datetime.fromisoformat(session_time)
                current_time = datetime.datetime.now()
                time_diff = current_time - session_datetime
                
                # Kiểm tra nếu thời gian chênh lệch < 1 phút (60 giây)
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

previous_session_handle = load_previous_session_handle()

async def gemini_session_handler(websocket: WebSocketServerProtocol):
    print(f"Starting Gemini session")
    try:
        config_message = await websocket.recv()
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
            output_audio_transcription=types.AudioTranscriptionConfig(
            ),
            temperature=0.7,
            top_p=0.9,
        )

        async with client.aio.live.connect(model=MODEL, config=config) as session:

            async def send_to_gemini():
                try:
                    async for message in websocket:
                        try:
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
                            print("receiving from gemini")
                            async for response in session.receive():
                                if response.server_content and hasattr(response.server_content, 'interrupted') and response.server_content.interrupted is not None:
                                    print(f"[{datetime.datetime.now()}] Generation interrupted")
                                    await websocket.send(json.dumps({"interrupted": "True"}))
                                    continue

                                if response.usage_metadata:
                                    usage = response.usage_metadata
                                    print(f'Used {usage.total_token_count} tokens in total.')

                                if response.session_resumption_update:
                                    update = response.session_resumption_update
                                    if update.resumable and update.new_handle:
                                        # The handle should be retained and linked to the session.
                                        previous_session_handle = update.new_handle
                                        save_previous_session_handle(previous_session_handle)
                                        print(f"Resumed session update with handle: {previous_session_handle}")

                                if response.server_content and hasattr(response.server_content, 'output_transcription') and response.server_content.output_transcription is not None:
                                    await websocket.send(json.dumps({
                                        "transcription": {
                                            "text": response.server_content.output_transcription.text,
                                            "sender": "Gemini",
                                            "finished": response.server_content.output_transcription.finished
                                        }
                                    }))
                                if response.server_content and hasattr(response.server_content, 'input_transcription') and response.server_content.input_transcription is not None:
                                    await websocket.send(json.dumps({
                                        "transcription": {
                                            "text": response.server_content.input_transcription.text,
                                            "sender": "User",
                                            "finished": response.server_content.input_transcription.finished
                                        }
                                    }))

                                if response.server_content is None:
                                    continue
                                    
                                model_turn = response.server_content.model_turn
                                if model_turn:
                                    for part in model_turn.parts:
                                        if hasattr(part, 'text') and part.text is not None:
                                            await websocket.send(json.dumps({"text": part.text}))
                                        
                                        elif hasattr(part, 'inline_data') and part.inline_data is not None:
                                            try:
                                                audio_data = part.inline_data.data
                                                base64_audio = base64.b64encode(audio_data).decode('utf-8')
                                                await websocket.send(json.dumps({
                                                    "audio": base64_audio,
                                                }))
                                                #print(f"Sent assistant audio to client: {base64_audio[:32]}...")
                                            except Exception as e:
                                                print(f"Error processing assistant audio: {e}")

                                if response.server_content and response.server_content.turn_complete:
                                    print('\n<Turn complete>')
                                    await websocket.send(json.dumps({
                                        "transcription": {
                                            "text": "",
                                            "sender": "Gemini",
                                            "finished": True
                                        }
                                    }))
                                    
                        except websockets.exceptions.ConnectionClosedOK:
                            print("Client connection closed normally (receive)")
                            break
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
    
async def main() -> None:
    server = await websockets.server.serve(
        gemini_session_handler,
        host="0.0.0.0", 
        port=9084,
        compression=None  
    )
    
    print("Running websocket server on 0.0.0.0:9084...")
    await asyncio.Future()  # Keep the server running indefinitely

if __name__ == "__main__":
    asyncio.run(main())
