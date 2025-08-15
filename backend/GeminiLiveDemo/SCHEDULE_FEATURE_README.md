# Schedule Feature Documentation

## Overview
The Schedule feature provides comprehensive scheduling and reminder functionality for the AI Healthcare Assistant application.

## Features

### 1. Schedule Management
- Create, read, update, and delete schedules
- Support for different notification types
- Category-based organization
- Priority levels

### 2. Notification System
- Push notifications
- Voice notifications
- Email reminders
- SMS alerts

### 3. Family Connection Feature 🆕
The Family Connection feature allows family members to view and manage schedules for elderly family members they care for.

#### Key Components:
- **FamilyConnectionActivity**: Main screen for viewing elderly schedules
- **User Type Support**: 
  - Elderly users can view their own schedules
  - Family members can view schedules of elderly they care for
- **Real-time Sync**: All data is synchronized with backend database
- **Smart UI**: Adaptive interface based on user type

#### User Flow:
1. **Elderly User**:
   - Navigate to Profile → Kết nối yêu thương
   - View their own daily schedules
   - Create new schedules and reminders

2. **Family Member**:
   - Navigate to Profile → Kết nối yêu thương
   - Select which elderly person to view
   - View and manage their schedules
   - Create new schedules on their behalf

#### API Endpoints:
- `GET /api/schedules` - Get user schedules
- `GET /api/auth/elderly-patients/{family_user_id}` - Get elderly patients for family member
- `POST /api/schedules` - Create new schedule
- `PUT /api/schedules/{schedule_id}` - Update schedule
- `DELETE /api/schedules/{schedule_id}` - Delete schedule

#### Database Models:
- **User**: Base user model with user_type (elderly/family)
- **ElderlyProfile**: Extended profile for elderly users
- **FamilyProfile**: Extended profile for family members
- **FamilyRelationship**: Links elderly users with family members
- **Notification**: Stores schedules and reminders

## Technical Implementation

### Backend
- FastAPI-based REST API
- PostgreSQL database with SQLAlchemy ORM
- Authentication middleware for secure access
- WebSocket support for real-time updates

### Android App
- Kotlin-based native Android application
- Retrofit for API communication
- Coroutines for asynchronous operations
- Material Design components for UI

### Security Features
- JWT token authentication
- Role-based access control
- Secure API endpoints
- Data validation and sanitization

## Configuration

### Environment Variables
```bash
DATABASE_URL=postgresql://user:password@localhost/dbname
JWT_SECRET_KEY=your-secret-key
GOOGLE_API_KEY=your-google-api-key
```

### Database Setup
```sql
-- Run the initialization script
\i db/init_scripts/01_init_database.sql
```

## Usage Examples

### Creating a Schedule
```json
POST /api/schedules
{
  "title": "Uống thuốc huyết áp",
  "message": "Uống thuốc theo chỉ định của bác sĩ",
  "scheduled_at": "2024-01-15T08:00:00",
  "notification_type": "medicine_reminder",
  "category": "medicine",
  "priority": "high"
}
```

### Getting User Schedules
```bash
GET /api/schedules?user_id=123e4567-e89b-12d3-a456-426614174000
Authorization: Bearer <jwt-token>
```

## Testing

### API Testing
```bash
# Test family connection endpoints
python test_family_connection_api.py
```

### Android App Testing
1. Build and install the app
2. Login with test credentials
3. Navigate to Profile → Kết nối yêu thương
4. Test both elderly and family member flows

## Troubleshooting

### Common Issues
1. **Authentication Errors**: Check JWT token validity
2. **Database Connection**: Verify PostgreSQL is running
3. **API Timeouts**: Check network connectivity
4. **Schedule Notifications**: Verify notification permissions

### Debug Mode
Enable debug logging in the Android app:
```kotlin
Log.d("FamilyConnection", "Debug message")
```

## Future Enhancements
- [ ] Multi-language support
- [ ] Advanced scheduling (recurring, conditional)
- [ ] Integration with external calendar apps
- [ ] AI-powered schedule optimization
- [ ] Family group management
- [ ] Emergency contact integration

## Support
For technical support or feature requests, please contact the development team. 