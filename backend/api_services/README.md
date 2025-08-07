# API Services Architecture

Thư mục này chứa các API service modules được tách riêng để dễ quản lý và maintain.

## Cấu trúc Services

### 1. `auth_service.py`
- Xử lý đăng ký, đăng nhập, quản lý profile
- Endpoints: `/api/auth/*`
- Chức năng:
  - User registration (elderly + family)
  - User login/authentication
  - Profile management
  - Family relationship management

### 2. `health_service.py`
- Health checks và system monitoring
- Endpoints: `/`, `/health`, `/api/services/status`, `/api/websocket/health`
- Chức năng:
  - System health monitoring
  - Service status checks
  - WebSocket health checks

### 3. `medicine_service.py`
- Medicine scanning và text extraction
- Endpoints: `/api/scan-medicine*`, `/api/extract-memoir-info`
- Chức năng:
  - Medicine image scanning
  - File upload processing
  - Text extraction for memoir

### 4. `memoir_service.py`
- Memoir extraction và conversation management
- Endpoints: `/api/memoir/*`
- Chức năng:
  - Background memoir extraction
  - Conversation history processing
  - Auto extraction settings

### 5. `notification_service.py`
- Voice notifications và broadcasting
- Endpoints: `/api/generate-voice-notification`, `/api/broadcast-voice-notification`
- Chức năng:
  - Voice notification generation
  - WebSocket broadcasting
  - Emergency notifications

## Cách sử dụng

Tất cả services được tự động tích hợp vào `backend.py` thông qua:

```python
from api_services.auth_service import add_auth_endpoints
from api_services.health_service import add_health_endpoints
from api_services.memoir_service import add_memoir_endpoints
from api_services.notification_service import add_notification_endpoints
from api_services.medicine_service import add_medicine_endpoints
```

## Chạy server

Chỉ cần chạy:
```bash
python run_server.py
```

Tất cả API endpoints sẽ được tự động load và hoạt động như trước.

## Lợi ích của kiến trúc mới

1. **Modularity**: Mỗi service độc lập, dễ maintain
2. **Scalability**: Dễ thêm/xóa services
3. **Testability**: Có thể test từng service riêng
4. **Code Organization**: Code được tổ chức rõ ràng theo chức năng
5. **Reusability**: Services có thể được sử dụng lại 