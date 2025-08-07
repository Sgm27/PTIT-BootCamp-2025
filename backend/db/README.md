# Healthcare AI Database Documentation

## Tổng quan

Hệ thống cơ sở dữ liệu của Healthcare AI được thiết kế để hỗ trợ hai loại người dùng chính:

1. **Người cao tuổi** - Người sử dụng ứng dụng trực tiếp
2. **Thành viên gia đình** - Con cháu hoặc người chăm sóc

## Kiến trúc Database

### Các bảng chính:

#### 1. User Management
- `users` - Thông tin người dùng cơ bản
- `elderly_profiles` - Hồ sơ mở rộng cho người cao tuổi
- `family_profiles` - Hồ sơ mở rộng cho thành viên gia đình
- `family_relationships` - Quan hệ giữa người cao tuổi và gia đình

#### 2. Conversation & Memory
- `conversations` - Các cuộc trò chuyện với AI
- `conversation_messages` - Tin nhắn trong cuộc trò chuyện
- `life_memoirs` - Những câu chuyện đời được trích xuất

#### 3. Health Management
- `health_records` - Dữ liệu sức khỏe và chỉ số sinh tồn
- `medicine_records` - Thông tin thuốc và đơn thuốc
- `medication_logs` - Nhật ký uống thuốc

#### 4. Notification System
- `notifications` - Thông báo và nhắc nhở
- `user_sessions` - Quản lý phiên đăng nhập

#### 5. System Management
- `system_settings` - Cấu hình hệ thống
- `audit_logs` - Nhật ký kiểm toán

## Cài đặt và Khởi tạo

### 1. Sử dụng Docker (Khuyến nghị)

```bash
# Khởi động database với Docker
cd backend/db
docker-compose up -d

# Kiểm tra trạng thái
docker-compose ps

# Xem logs
docker-compose logs postgres
```

### 2. Cài đặt thủ công PostgreSQL

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql-server postgresql-contrib

# macOS
brew install postgresql

# Windows - Tải từ https://www.postgresql.org/download/windows/
```

### 3. Tạo database và user

```sql
-- Kết nối PostgreSQL với quyền admin
sudo -u postgres psql

-- Tạo database
CREATE DATABASE healthcare_ai;

-- Tạo user (tuỳ chọn)
CREATE USER healthcare_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE healthcare_ai TO healthcare_user;
```

### 4. Cấu hình môi trường

Tạo file `.env` trong thư mục `backend/`:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=healthcare_ai
DB_USER=postgres
DB_PASSWORD=postgres
DB_DEBUG=false

# API Keys (giữ nguyên)
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key
```

### 5. Cài đặt dependencies

```bash
cd backend/
pip install -r requirements.txt
```

### 6. Khởi động server

```bash
python run_server.py
```

Server sẽ tự động:
- Kết nối database
- Tạo các bảng cần thiết
- Chạy script khởi tạo
- Khởi động API server

## Database Services

### UserService
Quản lý người dùng và quan hệ gia đình:

```python
from db.db_services import UserService

user_service = UserService()

# Tạo người dùng cao tuổi
elderly_user = await user_service.create_user(
    user_type=UserType.ELDERLY,
    full_name="Nguyễn Văn A",
    phone="0123456789",
    date_of_birth=date(1950, 1, 1)
)

# Tạo thành viên gia đình
family_member = await user_service.create_user(
    user_type=UserType.FAMILY_MEMBER,
    full_name="Nguyễn Thị B",
    email="nguyenthib@email.com"
)

# Tạo quan hệ gia đình
relationship = await user_service.create_family_relationship(
    elderly_user_id=elderly_user.id,
    family_member_id=family_member.id,
    relationship_type=RelationshipType.CHILD
)
```

### ConversationService
Quản lý cuộc trò chuyện:

```python
from db.db_services import ConversationService

conversation_service = ConversationService()

# Tạo cuộc trò chuyện mới
conversation = await conversation_service.create_conversation(
    user_id=user_id,
    session_id=session_id
)

# Thêm tin nhắn
message = await conversation_service.add_message(
    conversation_id=conversation.id,
    role=ConversationRole.USER,
    content="Chào bạn!"
)
```

### HealthService
Quản lý dữ liệu sức khỏe:

```python
from db.db_services import HealthService

health_service = HealthService()

# Ghi nhận chỉ số sinh tồn
health_record = await health_service.create_health_record(
    user_id=user_id,
    record_type="vital_signs",
    blood_pressure_systolic=120,
    blood_pressure_diastolic=80,
    heart_rate=72,
    temperature=36.5
)

# Kiểm tra cảnh báo sức khỏe
alerts = await health_service.check_vital_signs_alerts(user_id)
```

### MedicineDBService
Quản lý thuốc và nhật ký uống thuốc:

```python
from db.db_services import MedicineDBService

medicine_service = MedicineDBService()

# Thêm thuốc mới
medicine = await medicine_service.create_medicine_record(
    user_id=user_id,
    medicine_name="Paracetamol",
    dosage="500mg",
    frequency="2 lần/ngày",
    start_date=date.today()
)

# Ghi nhận uống thuốc
log = await medicine_service.log_medication_taken(
    medicine_id=medicine.id,
    user_id=user_id,
    scheduled_time=datetime.now(),
    status="taken"
)
```

### NotificationDBService
Quản lý thông báo:

```python
from db.db_services import NotificationDBService

notification_service = NotificationDBService()

# Tạo nhắc nhở uống thuốc
reminder = await notification_service.create_medicine_reminder(
    user_id=user_id,
    medicine_name="Paracetamol",
    dosage="500mg",
    scheduled_time=datetime.now() + timedelta(hours=8)
)
```

## Migration và Backup

### Database Migration

```bash
# Tạo migration script
alembic revision --autogenerate -m "Add new feature"

# Chạy migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Backup Database

```bash
# Backup toàn bộ database
docker exec healthcare_postgres pg_dump -U postgres healthcare_ai > backup.sql

# Restore
docker exec -i healthcare_postgres psql -U postgres healthcare_ai < backup.sql
```

## Monitoring và Performance

### Database Performance Views

```sql
-- Xem active sessions
SELECT * FROM active_sessions;

-- Xem health alerts
SELECT * FROM health_alerts WHERE severity = 'urgent';

-- User summary
SELECT * FROM user_summary WHERE user_type = 'elderly';
```

### Indexes

Database đã được tối ưu với các indexes:
- Full-text search cho conversations, memoirs, medicines
- Composite indexes cho queries thường dùng
- Partial indexes cho active records

## Troubleshooting

### Lỗi thường gặp:

1. **Connection refused**
   ```bash
   # Kiểm tra PostgreSQL đang chạy
   docker-compose ps
   sudo systemctl status postgresql
   ```

2. **Permission denied**
   ```bash
   # Kiểm tra quyền user
   sudo -u postgres psql -c "\du"
   ```

3. **Table doesn't exist**
   ```bash
   # Chạy lại initialization
   python -c "from db.db_config import init_database; init_database()"
   ```

4. **Migration errors**
   ```bash
   # Reset migrations
   alembic downgrade base
   alembic upgrade head
   ```

## Security

### Best Practices:
- Sử dụng environment variables cho credentials
- Enable SSL cho production
- Regular backup và testing
- Monitor audit logs
- Implement row-level security cho multi-tenant

### Access Control:
- Family members chỉ có thể truy cập data của elderly users được phép
- Health data requires explicit permission
- Audit logging cho tất cả sensitive operations

## Tích hợp với Backend

Backend sẽ tự động:
- Khởi tạo database khi start server
- Fallback về file-based storage nếu database không available
- Migration services từ JSON/text files sang database

## Liên hệ hỗ trợ

Nếu gặp vấn đề với database, vui lòng:
1. Kiểm tra logs trong `server.log`
2. Verify database connection
3. Check Docker containers status
4. Review environment variables 