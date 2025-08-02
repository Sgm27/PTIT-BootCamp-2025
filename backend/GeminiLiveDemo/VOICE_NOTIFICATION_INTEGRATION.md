# Voice Notification Feature Integration

## Tổng quan
Tính năng Voice Notification đã được tích hợp vào app Android GeminiLiveDemo để tự động tạo thông báo giọng nói từ các phản hồi của AI và sự kiện chăm sóc sức khỏe.

## Cấu trúc tích hợp

### 1. Backend Components
- **API Endpoint**: `/api/generate-voice-notification` (đã có sẵn)
- **WebSocket Handler**: `_handle_voice_notification_request` trong `GeminiService`
- **NotificationVoiceService**: Service để tạo voice từ text

### 2. Android Components

#### Core Classes
1. **VoiceNotificationData.kt**: Data class cho voice notification response
2. **VoiceNotificationManager.kt**: HTTP API manager cho voice notifications
3. **VoiceNotificationWebSocketManager.kt**: WebSocket manager cho voice notifications
4. **VoiceNotificationHelper.kt**: Helper để tự động tạo notifications từ AI responses

#### Integration Points
- **MainActivity**: Tích hợp managers và xử lý callbacks
- **GeminiListeningService**: Hỗ trợ voice notifications trong background service
- **Response.kt**: Parse voice notification responses
- **WebSocketManager**: Thêm `sendRawMessage()` method

### 3. Constants
- **VOICE_NOTIFICATION_API**: URL cho HTTP API (đã có trong Constants.kt)

## Cách hoạt động

### Automatic Voice Notifications
1. Khi AI trả lời, `VoiceNotificationHelper.processAIResponse()` phân tích text
2. Tự động tạo voice notifications cho:
   - Nhắc nhở uống thuốc (khi AI mention "thuốc", "uống thuốc")
   - Lịch hẹn bác sĩ (khi AI mention "khám", "bác sĩ", "lịch hẹn")
   - Tình huống khẩn cấp (khi AI mention "khẩn cấp", "nguy hiểm")
   - Nhắc nhở tập thể dục (khi AI mention "tập", "vận động")

### Manual Health Reminders
```kotlin
// Nhắc nhở uống thuốc
voiceNotificationHelper.generateHealthReminder(
    VoiceNotificationHelper.HealthReminderType.MEDICINE,
    mapOf(
        "medicine" to "Paracetamol 500mg",
        "time" to "8:00 sáng"
    )
)

// Lịch hẹn bác sĩ
voiceNotificationHelper.generateHealthReminder(
    VoiceNotificationHelper.HealthReminderType.APPOINTMENT,
    mapOf(
        "doctor" to "Bác sĩ Nguyễn Văn A",
        "time" to "14:30 ngày mai"
    )
)

// Thông báo khẩn cấp
voiceNotificationHelper.generateHealthReminder(
    VoiceNotificationHelper.HealthReminderType.EMERGENCY,
    mapOf("message" to "Phát hiện nhịp tim bất thường")
)
```

### WebSocket vs HTTP
- **WebSocket**: Ưu tiên sử dụng khi connection available (real-time)
- **HTTP API**: Fallback khi WebSocket không khả dụng

## Audio Playback
- Voice notifications được play thông qua `AudioManager.ingestAudioChunkToPlay()`
- Format: PCM 24kHz audio (base64 encoded)
- Tự động xử lý trong background service và main app

## Testing

### Demo Methods (đã thêm vào MainActivity)
```kotlin
// Test các loại notification
testVoiceNotifications()

// Test emergency notification
testEmergencyNotification()
```

### Manual Testing
1. Nói với AI về thuốc: "Tôi cần nhớ uống thuốc paracetamol"
2. AI sẽ trả lời và tự động tạo voice notification nhắc nhở
3. Voice notification sẽ được phát qua loa

## Backend WebSocket Protocol

### Request Format
```json
{
  "voice_notification_request": {
    "action": "generate_voice_notification",
    "text": "Đã đến giờ uống thuốc",
    "type": "info",
    "request_id": "optional_id"
  }
}
```

### Response Format
```json
{
  "type": "voice_notification_response",
  "success": true,
  "data": {
    "notification_text": "Đã đến giờ uống thuốc",
    "audio_base64": "base64_encoded_audio",
    "audio_format": "audio/pcm",
    "notification_type": "info",
    "timestamp": "2025-08-03T..."
  },
  "request_id": "optional_id"
}
```

## Lưu ý quan trọng

### Performance
- Voice notifications có delay 2 giây giữa các notification để tránh overlap
- Background service tự động xử lý voice notifications
- Auto-cleanup khi app destroy

### Error Handling
- WebSocket fallback to HTTP nếu connection issue
- Comprehensive error logging
- Graceful degradation khi service unavailable

### User Experience
- Không cần UI button - tất cả tự động
- Voice notifications phát qua AudioManager hiện tại
- Tích hợp seamless với voice chat flow

## Future Enhancements
1. Scheduled notifications (timer-based)
2. Custom voice notification templates
3. Voice notification history
4. User preferences cho notification types
5. Volume control riêng cho notifications

## Files Changed
- `MainActivity.kt`: Tích hợp managers
- `GeminiListeningService.kt`: Background support
- `Response.kt`: Parsing support
- `WebSocketManager.kt`: Raw message support
- `services/gemini_service.py`: WebSocket handler

## Files Added
- `VoiceNotificationData.kt`
- `VoiceNotificationManager.kt` 
- `VoiceNotificationWebSocketManager.kt`
- `VoiceNotificationHelper.kt`
