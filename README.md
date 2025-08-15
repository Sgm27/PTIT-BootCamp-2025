# 🏥 AI Healthcare Assistant - PTIT BootCamp 2025

## 📋 Tổng quan

**AI Healthcare Assistant** là một hệ thống chăm sóc sức khỏe thông minh được phát triển cho người cao tuổi và gia đình của họ. Hệ thống tích hợp công nghệ AI tiên tiến với các tính năng chăm sóc sức khỏe toàn diện, bao gồm quản lý thuốc, theo dõi sức khỏe, nhắc nhở lịch trình và trích xuất ký ức cuộc sống tự động.

## 🚀 Tính năng chính

### 🤖 AI-Powered Healthcare
- **Gemini Live Integration**: Tích hợp Google Gemini Live 2.5 Flash Preview cho tương tác AI thời gian thực
- **OpenAI Vision**: Hỗ trợ phân tích hình ảnh và quét thuốc thông minh
- **Voice Recognition**: Nhận diện giọng nói tiếng Việt và xử lý âm thanh
- **Natural Language Processing**: Xử lý ngôn ngữ tự nhiên cho giao tiếp

### 👥 Quản lý người dùng
- **Hai loại người dùng**: Người cao tuổi và thành viên gia đình
- **Quản lý mối quan hệ**: Liên kết người cao tuổi với gia đình
- **Hồ sơ sức khỏe**: Theo dõi tình trạng sức khỏe và tiền sử bệnh
- **Xác thực bảo mật**: JWT token và mã hóa mật khẩu

### 💊 Quản lý thuốc và sức khỏe
- **Quét thuốc thông minh**: Sử dụng camera để nhận diện thuốc
- **Nhắc nhở uống thuốc**: Hệ thống thông báo tự động
- **Theo dõi dấu hiệu sinh tồn**: Huyết áp, nhịp tim, nhiệt độ
- **Lịch sử y tế**: Ghi chép và theo dõi bệnh án

### 📅 Lịch trình và nhắc nhở
- **Quản lý lịch hẹn**: Lịch hẹn bác sĩ và kiểm tra sức khỏe
- **Nhắc nhở thông minh**: Push notification, email, SMS
- **Đồng bộ gia đình**: Thành viên gia đình có thể quản lý lịch trình
- **Tùy chỉnh thông báo**: Cài đặt theo sở thích cá nhân

### 🧠 Trích xuất ký ức cuộc sống
- **Xử lý tự động hàng ngày**: Trích xuất ký ức từ cuộc trò chuyện
- **Lưu trữ thông minh**: Phân loại và tổ chức ký ức theo chủ đề
- **Tìm kiếm nâng cao**: Tìm kiếm ký ức theo từ khóa và thời gian
- **Chia sẻ gia đình**: Chia sẻ ký ức với thành viên gia đình

### 🔌 WebSocket Real-time
- **Kết nối ổn định**: Tối ưu hóa cho kết nối dài hạn
- **Truyền âm thanh/video**: Hỗ trợ streaming thời gian thực
- **Auto-reconnect**: Tự động kết nối lại khi mất kết nối
- **Thread-safe**: Xử lý an toàn đa luồng

## 🏗️ Kiến trúc hệ thống

### Backend Architecture
```
backend/
├── run_server.py              # Entry point chính
├── config/                    # Cấu hình ứng dụng
├── api_services/              # REST API endpoints
├── db/                        # Database models và services
├── services/                  # Business logic services
└── models/                    # Data models
```

### Frontend Architecture
```
frontend/GeminiLiveDemo/
├── app/                       # Android application
├── src/main/                  # Source code chính
│   ├── java/                  # Kotlin/Java code
│   ├── res/                   # Resources (layouts, drawables)
│   └── AndroidManifest.xml    # App configuration
└── build.gradle.kts           # Build configuration
```

### Database Schema
- **Users**: Quản lý người dùng và phân quyền
- **ElderlyProfiles**: Hồ sơ chi tiết người cao tuổi
- **FamilyProfiles**: Hồ sơ thành viên gia đình
- **HealthRecords**: Ghi chép sức khỏe và dấu hiệu sinh tồn
- **Medicines**: Quản lý thuốc và liều lượng
- **Conversations**: Lịch sử trò chuyện với AI
- **LifeMemoirs**: Ký ức cuộc sống được trích xuất
- **Notifications**: Hệ thống thông báo và nhắc nhở

## 🛠️ Công nghệ sử dụng

### Backend Technologies
- **FastAPI**: Web framework hiệu suất cao
- **PostgreSQL**: Database chính với SQLAlchemy ORM
- **Redis**: Cache và session management
- **WebSocket**: Real-time communication
- **APScheduler**: Background task scheduling
- **Google Gemini API**: AI language model
- **OpenAI API**: Vision và text processing

### Frontend Technologies
- **Kotlin**: Ngôn ngữ lập trình chính
- **Android SDK**: Native Android development
- **CameraX**: Camera integration
- **Retrofit**: HTTP client cho API calls
- **WebSocket**: Real-time communication
- **Material Design**: UI/UX components

### DevOps & Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-service orchestration
- **PostgreSQL**: Primary database
- **PgAdmin**: Database management interface
- **Redis**: Caching layer

## 🚀 Cài đặt và chạy

### Yêu cầu hệ thống
- Python 3.8+
- Node.js 16+
- Android Studio (cho development)
- Docker & Docker Compose
- PostgreSQL 13+
- Redis 6+

### Backend Setup

1. **Clone repository**
```bash
git clone https://github.com/your-username/PTIT-BootCamp-2025.git
cd PTIT-BootCamp-2025/backend
```

2. **Cài đặt dependencies**
```bash
pip install -r requirements.txt
```

3. **Cấu hình environment**
```bash
cp .env.example .env
# Chỉnh sửa .env với API keys và database credentials
```

4. **Khởi động database**
```bash
cd db
docker-compose up -d
```

5. **Chạy server**
```bash
python run_server.py
```

### Frontend Setup

1. **Mở project trong Android Studio**
```bash
cd frontend/GeminiLiveDemo
# Mở Android Studio và import project
```

2. **Cấu hình local.properties**
```properties
sdk.dir=/path/to/your/Android/Sdk
```

3. **Build và chạy**
```bash
./gradlew assembleDebug
# Hoặc sử dụng Android Studio UI
```

## 🔧 Cấu hình

### Environment Variables
```bash
# API Keys
GOOGLE_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/healthcare_ai
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET_KEY=your_jwt_secret
JWT_ALGORITHM=HS256

# Server
HOST=0.0.0.0
PORT=8000
```

### Database Configuration
```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:latest
    environment:
      POSTGRES_DB: healthcare_ai
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
  
  pgadmin:
    image: dpage/pgadmin4:latest
    ports:
      - "8080:80"
  
  redis:
    image: redis:latest
    ports:
      - "6379:6379"
```

## 📱 Tính năng Android App

### Core Features
- **Authentication**: Đăng nhập/đăng ký với JWT
- **Profile Management**: Quản lý hồ sơ cá nhân
- **Camera Integration**: Quét thuốc và chụp ảnh
- **Voice Chat**: Trò chuyện với AI qua giọng nói
- **Real-time Updates**: WebSocket cho cập nhật thời gian thực

### UI Components
- **Material Design**: Giao diện hiện đại và thân thiện
- **Responsive Layout**: Tối ưu cho nhiều kích thước màn hình
- **Dark/Light Theme**: Hỗ trợ chế độ tối và sáng
- **Accessibility**: Hỗ trợ người dùng khuyết tật

### Performance Optimizations
- **Coroutines**: Xử lý bất đồng bộ hiệu quả
- **Image Caching**: Cache hình ảnh để tăng tốc độ
- **Background Processing**: Xử lý tác vụ nặng trong background
- **Memory Management**: Quản lý bộ nhớ tối ưu

## 🔒 Bảo mật

### Authentication & Authorization
- **JWT Tokens**: Xác thực stateless
- **Role-based Access**: Phân quyền theo loại người dùng
- **Password Hashing**: Mã hóa mật khẩu với bcrypt
- **Session Management**: Quản lý phiên làm việc an toàn

### Data Protection
- **HTTPS/SSL**: Mã hóa dữ liệu truyền tải
- **Input Validation**: Kiểm tra và làm sạch dữ liệu đầu vào
- **SQL Injection Prevention**: Sử dụng parameterized queries
- **CORS Configuration**: Kiểm soát truy cập cross-origin

## 📊 API Documentation

### Core Endpoints
- `POST /api/auth/login` - Đăng nhập
- `POST /api/auth/register` - Đăng ký
- `GET /api/users/profile` - Lấy thông tin hồ sơ
- `PUT /api/users/profile` - Cập nhật hồ sơ

### Health Management
- `GET /api/health/records` - Lấy hồ sơ sức khỏe
- `POST /api/health/records` - Tạo hồ sơ sức khỏe
- `GET /api/health/vitals` - Lấy dấu hiệu sinh tồn

### Medicine Management
- `POST /api/medicines/scan` - Quét thuốc
- `GET /api/medicines/list` - Danh sách thuốc
- `POST /api/medicines/reminders` - Tạo nhắc nhở

### Schedule Management
- `GET /api/schedules` - Lấy lịch trình
- `POST /api/schedules` - Tạo lịch trình
- `PUT /api/schedules/{id}` - Cập nhật lịch trình

### WebSocket Endpoints
- `/gemini-live` - Real-time AI chat
- `/health-monitor` - Monitoring sức khỏe

## 🧪 Testing

### Backend Testing
```bash
# Unit tests
pytest tests/

# API tests
pytest tests/api/

# Database tests
pytest tests/db/
```

### Frontend Testing
```bash
# Unit tests
./gradlew test

# Instrumented tests
./gradlew connectedAndroidTest
```

### Integration Testing
```bash
# End-to-end tests
pytest tests/integration/

# Performance tests
pytest tests/performance/
```

## 📈 Monitoring & Logging

### Logging Configuration
- **Structured Logging**: JSON format cho dễ phân tích
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Rotation**: Tự động xoay vòng log files
- **Centralized Logging**: Tập trung logs vào một nơi

### Performance Monitoring
- **Response Time**: Theo dõi thời gian phản hồi API
- **Error Rates**: Tỷ lệ lỗi và exceptions
- **Resource Usage**: CPU, memory, database connections
- **WebSocket Metrics**: Connection stability và throughput

## 🚀 Deployment

### Production Environment
- **Load Balancer**: Nginx hoặc HAProxy
- **Process Manager**: PM2 hoặc systemd
- **Database**: PostgreSQL cluster với replication
- **Cache**: Redis cluster với persistence
- **Monitoring**: Prometheus + Grafana

### Docker Deployment
```bash
# Build images
docker build -t healthcare-backend .
docker build -t healthcare-frontend .

# Run with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables (Production)
```bash
# Production settings
DEBUG=false
LOG_LEVEL=WARNING
DATABASE_URL=postgresql://user:pass@prod-db:5432/healthcare_ai
REDIS_URL=redis://prod-redis:6379
```

## 🤝 Đóng góp

### Development Workflow
1. Fork repository
2. Tạo feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Tạo Pull Request

### Code Standards
- **Python**: PEP 8, Black formatter, Flake8 linter
- **Kotlin**: Kotlin coding conventions
- **Git**: Conventional commits
- **Documentation**: Google docstring format

### Testing Requirements
- **Coverage**: Tối thiểu 80% code coverage
- **Unit Tests**: Tất cả functions phải có unit tests
- **Integration Tests**: API endpoints phải có integration tests
- **Performance Tests**: Load testing cho critical paths

## 📚 Tài liệu tham khảo

### Technical Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Android Developer Guide](https://developer.android.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Google Gemini API](https://ai.google.dev/docs)

### Architecture Patterns
- **Clean Architecture**: Separation of concerns
- **Repository Pattern**: Data access abstraction
- **Service Layer**: Business logic encapsulation
- **Event-Driven Architecture**: Asynchronous processing

## 🆘 Hỗ trợ

### Common Issues
1. **Database Connection**: Kiểm tra PostgreSQL service
2. **WebSocket Issues**: Verify network connectivity
3. **API Errors**: Check authentication và permissions
4. **Build Failures**: Verify dependencies và versions

### Getting Help
- **Issues**: Tạo issue trên GitHub
- **Discussions**: Sử dụng GitHub Discussions
- **Documentation**: Kiểm tra docs/ folder
- **Team Contact**: Liên hệ development team

## 📄 License

Project này được phát triển trong khuôn khổ **PTIT BootCamp 2025** và được cấp phép theo [MIT License](LICENSE).

## 🙏 Acknowledgments

- **PTIT BootCamp 2025** - Cơ hội học tập và phát triển
- **Google Gemini Team** - AI technology support
- **OpenAI** - Vision và language processing
- **FastAPI Community** - Web framework excellence
- **Android Developer Community** - Mobile development resources

---

**Made with ❤️ by PTIT BootCamp 2025 Team**

*Hệ thống chăm sóc sức khỏe thông minh cho người cao tuổi và gia đình*