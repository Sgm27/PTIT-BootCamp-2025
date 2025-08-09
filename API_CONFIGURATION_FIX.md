# Sửa chữa API Configuration - Production URLs

## Vấn đề
- Nút lịch sử trò chuyện vẫn crash
- App có thể đang sử dụng localhost thay vì production API
- Cần đảm bảo tất cả API calls sử dụng đúng production endpoints từ .env

## Kiểm tra và sửa chữa

### 1. File .env (Production URLs)
```env
API_BASE_URL=https://backend-bootcamp.sonktx.online
API_HOST=backend-bootcamp.sonktx.online
API_PORT=443
API_PROTOCOL=https
ENVIRONMENT=production
```

### 2. ApiConfig.kt ✅ (Đã đúng)
**File:** `backend/GeminiLiveDemo/app/src/main/java/com/example/geminilivedemo/data/ApiConfig.kt`

```kotlin
private const val ENVIRONMENT = "production"
private const val PROD_BASE_URL = "https://backend-bootcamp.sonktx.online/"
private const val PROD_WS_URL = "wss://backend-bootcamp.sonktx.online/gemini-live"
```

### 3. Constants.kt (Đã sửa)
**File:** `backend/GeminiLiveDemo/app/src/main/java/com/example/geminilivedemo/Constants.kt`

**Trước:**
```kotlin
const val URL = "ws://backend-bootcamp.sonktx.online/gemini-live"  // HTTP
const val VOICE_NOTIFICATION_API = "https://backend-bootcamp.sonktx.online/api/generate-voice-notification"
```

**Sau:**
```kotlin
val URL = ApiConfig.WEBSOCKET_URL  // wss://backend-bootcamp.sonktx.online/gemini-live (HTTPS)
val VOICE_NOTIFICATION_API = "${ApiConfig.BASE_URL}api/generate-voice-notification"
```

**Lợi ích:**
- Đồng bộ với ApiConfig
- Tự động sử dụng HTTPS (wss://) cho WebSocket
- Centralized configuration

### 4. ApiClient.kt ✅ (Đã đúng)
**File:** `backend/GeminiLiveDemo/app/src/main/java/com/example/geminilivedemo/data/ApiClient.kt`

```kotlin
private val BASE_URL = ApiConfig.BASE_URL  // Sử dụng từ ApiConfig
```

### 5. Enhanced Logging (Đã thêm)
**Files:**
- `MainActivity.kt`: Thêm logging chi tiết khi mở ConversationHistory
- `ConversationHistoryActivity.kt`: Thêm logging chi tiết trong onCreate

**Logging bao gồm:**
- API configuration info
- User data status
- Step-by-step execution tracking
- Detailed error information

## API Endpoints được sử dụng

### Production URLs (từ .env)
```
Base URL: https://backend-bootcamp.sonktx.online/
WebSocket: wss://backend-bootcamp.sonktx.online/gemini-live
```

### Conversation API Endpoints
```
GET /api/conversations/{user_id}                    - Lấy danh sách conversations
GET /api/conversations/{user_id}/{conversation_id}  - Lấy chi tiết conversation
GET /api/conversations/{user_id}/search             - Tìm kiếm conversations
```

### Memoir API Endpoints
```
GET /api/memoirs/{user_id}                          - Lấy danh sách memoirs
GET /api/memoirs/{user_id}/{memoir_id}              - Lấy chi tiết memoir
POST /api/memoirs/{user_id}/search                  - Tìm kiếm memoirs
GET /api/memoirs/{user_id}/timeline                 - Lấy timeline
POST /api/memoirs/{user_id}/export                  - Export memoirs
```

## Verification Steps

### 1. Build và Test
```bash
cd backend/GeminiLiveDemo
./gradlew assembleDebug
./gradlew installDebug
```

### 2. Monitor Logs
```bash
adb logcat | grep -E "(MainActivity|ConversationHistory|ApiClient|ApiConfig)"
```

### 3. Test API Endpoints
```bash
# Test conversations API
curl "https://backend-bootcamp.sonktx.online/api/conversations/f5db7d59-1df3-4b83-a066-bbb95d7a28a0?limit=10"

# Test conversation detail
curl "https://backend-bootcamp.sonktx.online/api/conversations/f5db7d59-1df3-4b83-a066-bbb95d7a28a0/{conversation_id}"
```

## Debug Script
**File:** `debug_conversation_history.py`

Tính năng:
- Build và install app tự động
- Monitor logs real-time
- Hướng dẫn test manual
- Filter logs relevant

Sử dụng:
```bash
python debug_conversation_history.py
```

## Troubleshooting

### Nếu vẫn crash:

1. **Kiểm tra logs:**
   ```bash
   adb logcat | grep -E "(FATAL|AndroidRuntime|ConversationHistory)"
   ```

2. **Kiểm tra network connectivity:**
   ```bash
   adb shell ping backend-bootcamp.sonktx.online
   ```

3. **Kiểm tra app permissions:**
   - INTERNET permission
   - NETWORK_STATE permission

4. **Clear app data:**
   ```bash
   adb shell pm clear com.example.geminilivedemo
   ```

### Common Issues:

1. **SSL/TLS Issues:**
   - Đảm bảo device có thể kết nối HTTPS
   - Kiểm tra network security config

2. **User Data Issues:**
   - Kiểm tra UserPreferences có user ID không
   - Test với test user data

3. **Layout Issues:**
   - Kiểm tra layout resources
   - Verify drawable resources tồn tại

## Expected Behavior

Sau khi sửa:
- ✅ App sử dụng production API (https://backend-bootcamp.sonktx.online)
- ✅ WebSocket sử dụng WSS (secure)
- ✅ Không còn localhost references
- ✅ Centralized API configuration
- ✅ Detailed logging cho debugging
- ✅ Conversation history không crash

## Files đã thay đổi
- `backend/GeminiLiveDemo/app/src/main/java/com/example/geminilivedemo/Constants.kt`
- `backend/GeminiLiveDemo/app/src/main/java/com/example/geminilivedemo/MainActivity.kt`
- `backend/GeminiLiveDemo/app/src/main/java/com/example/geminilivedemo/ConversationHistoryActivity.kt`
- `debug_conversation_history.py` (new)

## Next Steps
1. Build và install app
2. Test conversation history feature
3. Monitor logs để identify exact crash cause
4. Fix any remaining issues based on logs 