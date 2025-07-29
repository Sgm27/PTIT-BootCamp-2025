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
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Charon")
                ),
                language_code='vi-VN',
            ),
            system_instruction="""
            Bạn là AI được phát triển bởi Đức Sơn.
            Nhiệm vụ của bạn là trả lời các câu hỏi thật chi tiết và chính xác.
            Luôn trả lời bằng tiếng Việt.
            Nếu ai đó hỏi bạn về người tạo ra bạn, hãy nói rằng bạn được phát triển bởi Đức Sơn.
            Khi ai đó hỏi về thuốc thì hãy mô tả thật chi tiết bao gồm tên thuốc, công dụng, cách dùng, tác dụng phụ, và cách phòng ngừa.
            Khi ai đó muốn kể chuyện thì hãy kể một câu chuyện thật dài và li kỳ
            """,
            session_resumption=types.SessionResumptionConfig(
                handle=previous_session_handle
            ),
            output_audio_transcription=types.AudioTranscriptionConfig(
            ),
            temperature=0.0,
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
