# AI Healthcare Assistant API - Restructured

## Cấu trúc mới

Dự án đã được restructure để dễ dàng test và maintain hơn:

```
backend/
├── backend.py              # Main FastAPI app (file cũ)
├── backend_new.py          # Main FastAPI app (restructured)
├── config/
│   ├── __init__.py
│   └── settings.py         # Cấu hình app và environment variables
├── models/
│   ├── __init__.py
│   └── api_models.py       # Pydantic models
├── services/
│   ├── __init__.py
│   ├── session_service.py  # Quản lý session Gemini Live
│   ├── medicine_service.py # Service scan thuốc
│   ├── text_extraction_service.py # Service trích xuất text
│   └── gemini_service.py   # Service WebSocket Gemini Live
└── tests/
    ├── __init__.py
    └── test_services.py    # Examples test cho các services
```

## Các thay đổi chính

### 1. **Separation of Concerns**
- Mỗi service được tách thành file riêng
- Logic business được tách ra khỏi FastAPI routes
- Configuration được centralized

### 2. **Testability**
- Mỗi service có thể được test độc lập
- Dependency injection cho OpenAI và Gemini clients
- Mock-friendly architecture

### 3. **Maintainability**
- Code được organize theo chức năng
- Dễ dàng thêm features mới
- Clear separation giữa API layer và business logic

## Cách sử dụng

### Chạy app mới:
```bash
cd backend
python backend_new.py
```

### Chạy tests:
```bash
cd backend
python tests/test_services.py
```

## Services

### 1. MedicineService
- Scan thuốc từ URL hoặc base64
- Scan từ uploaded files
- Configurable OpenAI model và temperature

### 2. TextExtractionService  
- Trích xuất thông tin từ text cho memoir
- Structured information extraction
- Error handling

### 3. GeminiService
- Handle WebSocket connections
- Process real-time audio/text
- Session management integration

### 4. SessionService
- Load/save session handles
- Session timeout management
- File-based persistence

## Configuration

Tất cả settings được centralized trong `config/settings.py`:
- API keys
- Model configurations  
- CORS settings
- Session settings

## API Endpoints

Các endpoints giữ nguyên interface:
- `GET /` - Root endpoint
- `GET /health` - Health check (enhanced)
- `GET /api/services/status` - Service status (new)
- `POST /api/scan-medicine` - Scan medicine
- `POST /api/scan-medicine-file` - Scan from file
- `POST /api/extract-memoir-info` - Extract text info
- `WebSocket /gemini-live` - Gemini Live chat

## Benefits

1. **Easier Testing**: Mỗi service có thể test riêng biệt
2. **Better Organization**: Code được chia theo chức năng rõ ràng
3. **Scalability**: Dễ dàng thêm services mới
4. **Maintenance**: Dễ debug và fix bugs
5. **Reusability**: Services có thể reuse ở các phần khác của app
