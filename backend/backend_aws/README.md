# AI Healthcare Assistant API - Docker Setup

Hướng dẫn dockerize và chạy project AI Healthcare Assistant API.

## Cấu trúc Project

```
backend_aws/
├── backend.py              # Main FastAPI application
├── Dockerfile              # Docker image configuration
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables example
├── .dockerignore          # Docker ignore file
├── session_handle.json    # Session data
├── config/                # Configuration settings
├── models/                # API models
└── services/              # Business logic services
```

## Yêu cầu

- Docker >= 20.10
- Docker Compose >= 2.0
- API Keys: Google Gemini và OpenAI

## Cách cài đặt và chạy

### 1. Chuẩn bị môi trường

Tạo file `.env` từ file mẫu:
```bash
copy .env.example .env
```

Chỉnh sửa file `.env` và thêm API keys thực tế:
```env
GOOGLE_API_KEY=your_actual_google_api_key
OPENAI_API_KEY=your_actual_openai_api_key
```

### 2. Build và chạy với Docker Compose (Khuyến nghị)

```bash
# Build và chạy container
docker-compose up --build

# Chạy trong background
docker-compose up -d --build

# Xem logs
docker-compose logs -f

# Dừng container
docker-compose down
```

### 3. Build và chạy với Docker commands

```bash
# Build Docker image
docker build -t healthcare-api .

# Chạy container với environment variables
docker run -d \
  --name healthcare-container \
  -p 8000:8000 \
  -e GOOGLE_API_KEY=your_google_api_key \
  -e OPENAI_API_KEY=your_openai_api_key \
  -v ${PWD}/session_handle.json:/app/session_handle.json \
  healthcare-api

# Xem logs
docker logs -f healthcare-container

# Dừng container
docker stop healthcare-container
docker rm healthcare-container
```

## Kiểm tra ứng dụng

Sau khi container chạy thành công:

1. **API Documentation**: http://localhost:8000/docs
2. **Health Check**: http://localhost:8000/health
3. **Root Endpoint**: http://localhost:8000/

## API Endpoints

### Main Endpoints
- `GET /` - Root endpoint với thông tin ứng dụng
- `GET /health` - Health check endpoint
- `POST /api/scan-medicine` - Scan thuốc từ base64 hoặc URL
- `POST /api/scan-medicine-file` - Scan thuốc từ file upload
- `POST /api/extract-text` - Trích xuất thông tin từ text
- `WS /api/gemini-live` - WebSocket cho Gemini Live

### Health Check Response
```json
{
  "status": "healthy",
  "timestamp": "2025-08-02T10:22:46.722270",
  "services": {
    "medicine_service": "active",
    "text_extraction_service": "active", 
    "gemini_service": "active"
  }
}
```

## Troubleshooting

### 1. Container không start được
```bash
# Kiểm tra logs
docker-compose logs healthcare-backend

# Kiểm tra container status
docker-compose ps
```

### 2. API Keys không hoạt động
- Kiểm tra file `.env` có chứa đúng API keys
- Verify API keys còn hiệu lực
- Kiểm tra quyền truy cập APIs

### 3. Port conflict
Nếu port 8000 đã được sử dụng, thay đổi trong `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Thay đổi port host từ 8000 thành 8001
```

### 4. Session file issues
Đảm bảo file `session_handle.json` có quyền read/write:
```bash
# Windows
icacls session_handle.json /grant Everyone:F

# Linux/Mac
chmod 666 session_handle.json
```

## Development Mode

Để chạy trong development mode với auto-reload:

1. Thay đổi command trong `Dockerfile`:
```dockerfile
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

2. Mount source code làm volume:
```yaml
# Thêm vào docker-compose.yml
volumes:
  - .:/app
  - ./session_handle.json:/app/session_handle.json
```

## Production Deployment

Cho production environment:

1. Sử dụng production ASGI server như Gunicorn
2. Thêm reverse proxy (Nginx)
3. Implement proper logging
4. Use secrets management
5. Add monitoring và health checks

## Cấu hình nâng cao

### Environment Variables
Các biến môi trường có thể cấu hình:

- `GOOGLE_API_KEY` - Google Gemini API key (required)
- `OPENAI_API_KEY` - OpenAI API key (required)
- `PYTHONPATH` - Python path (default: /app)
- `PYTHONUNBUFFERED` - Python output buffering (default: 1)

### Volumes
- `./session_handle.json:/app/session_handle.json` - Session data persistence
- `./logs:/app/logs` - Log files storage

### Health Checks
Container có built-in health check:
- Endpoint: `http://localhost:8000/health`
- Interval: 30s
- Timeout: 10s
- Retries: 3
