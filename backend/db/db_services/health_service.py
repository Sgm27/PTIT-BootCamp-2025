"""
Health Data Management Service
Handles health records, vital signs, and health monitoring data
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func

from db.db_config import get_db
from db.models import HealthRecord, User

logger = logging.getLogger(__name__)

class HealthService:
    """Service for managing health data and records"""
    
    def __init__(self):
        self.logger = logger
    
    async def create_health_record(
        self,
        user_id: str,
        record_type: str,
        recorded_at: Optional[datetime] = None,
        blood_pressure_systolic: Optional[int] = None,
        blood_pressure_diastolic: Optional[int] = None,
        heart_rate: Optional[int] = None,
        temperature: Optional[float] = None,
        weight: Optional[float] = None,
        blood_sugar: Optional[float] = None,
        symptoms: Optional[List[str]] = None,
        pain_level: Optional[int] = None,
        mood: Optional[str] = None,
        energy_level: Optional[str] = None,
        sleep_quality: Optional[str] = None,
        appetite: Optional[str] = None,
        notes: Optional[str] = None,
        recorded_by: str = "user"
    ) -> Optional[HealthRecord]:
        """Create a new health record"""
        try:
            with get_db() as db:
                health_record = HealthRecord(
                    user_id=user_id,
                    record_type=record_type,
                    recorded_at=recorded_at or datetime.utcnow(),
                    blood_pressure_systolic=blood_pressure_systolic,
                    blood_pressure_diastolic=blood_pressure_diastolic,
                    heart_rate=heart_rate,
                    temperature=temperature,
                    weight=weight,
                    blood_sugar=blood_sugar,
                    symptoms=symptoms or [],
                    pain_level=pain_level,
                    mood=mood,
                    energy_level=energy_level,
                    sleep_quality=sleep_quality,
                    appetite=appetite,
                    notes=notes,
                    recorded_by=recorded_by
                )
                
                db.add(health_record)
                db.commit()
                db.refresh(health_record)
                
                self.logger.info(f"Created health record {health_record.id} for user {user_id}")
                return health_record
                
        except Exception as e:
            self.logger.error(f"Failed to create health record: {e}")
            return None
    
    async def get_health_record(self, record_id: str) -> Optional[HealthRecord]:
        """Get a specific health record"""
        try:
            with get_db() as db:
                record = db.query(HealthRecord).filter(
                    HealthRecord.id == record_id
                ).first()
                return record
        except Exception as e:
            self.logger.error(f"Failed to get health record {record_id}: {e}")
            return None
    
    async def get_user_health_records(
        self,
        user_id: str,
        record_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[HealthRecord]:
        """Get health records for a user with optional filtering"""
        try:
            with get_db() as db:
                query = db.query(HealthRecord).filter(HealthRecord.user_id == user_id)
                
                if record_type:
                    query = query.filter(HealthRecord.record_type == record_type)
                
                if start_date:
                    query = query.filter(HealthRecord.recorded_at >= start_date)
                
                if end_date:
                    query = query.filter(HealthRecord.recorded_at <= end_date)
                
                records = query.order_by(
                    desc(HealthRecord.recorded_at)
                ).offset(offset).limit(limit).all()
                
                return records
                
        except Exception as e:
            self.logger.error(f"Failed to get health records for user {user_id}: {e}")
            return []
    
    async def get_vital_signs_history(
        self,
        user_id: str,
        vital_type: str,
        days_back: int = 30
    ) -> List[Dict]:
        """Get history of specific vital signs"""
        try:
            with get_db() as db:
                start_date = datetime.utcnow() - timedelta(days=days_back)
                
                records = db.query(HealthRecord).filter(
                    and_(
                        HealthRecord.user_id == user_id,
                        HealthRecord.recorded_at >= start_date
                    )
                ).order_by(HealthRecord.recorded_at).all()
                
                vital_history = []
                for record in records:
                    data_point = {
                        'recorded_at': record.recorded_at.isoformat(),
                        'recorded_by': record.recorded_by
                    }
                    
                    if vital_type == "blood_pressure" and record.blood_pressure_systolic:
                        data_point['systolic'] = record.blood_pressure_systolic
                        data_point['diastolic'] = record.blood_pressure_diastolic
                        vital_history.append(data_point)
                    elif vital_type == "heart_rate" and record.heart_rate:
                        data_point['heart_rate'] = record.heart_rate
                        vital_history.append(data_point)
                    elif vital_type == "temperature" and record.temperature:
                        data_point['temperature'] = record.temperature
                        vital_history.append(data_point)
                    elif vital_type == "weight" and record.weight:
                        data_point['weight'] = record.weight
                        vital_history.append(data_point)
                    elif vital_type == "blood_sugar" and record.blood_sugar:
                        data_point['blood_sugar'] = record.blood_sugar
                        vital_history.append(data_point)
                
                return vital_history
                
        except Exception as e:
            self.logger.error(f"Failed to get vital signs history for user {user_id}: {e}")
            return []
    
    async def get_latest_vital_signs(self, user_id: str) -> Dict[str, Any]:
        """Get the most recent vital signs for a user"""
        try:
            with get_db() as db:
                # Get most recent record with vital signs
                recent_records = db.query(HealthRecord).filter(
                    HealthRecord.user_id == user_id
                ).order_by(desc(HealthRecord.recorded_at)).limit(10).all()
                
                latest_vitals = {}
                
                for record in recent_records:
                    if record.blood_pressure_systolic and 'blood_pressure' not in latest_vitals:
                        latest_vitals['blood_pressure'] = {
                            'systolic': record.blood_pressure_systolic,
                            'diastolic': record.blood_pressure_diastolic,
                            'recorded_at': record.recorded_at.isoformat()
                        }
                    
                    if record.heart_rate and 'heart_rate' not in latest_vitals:
                        latest_vitals['heart_rate'] = {
                            'value': record.heart_rate,
                            'recorded_at': record.recorded_at.isoformat()
                        }
                    
                    if record.temperature and 'temperature' not in latest_vitals:
                        latest_vitals['temperature'] = {
                            'value': record.temperature,
                            'recorded_at': record.recorded_at.isoformat()
                        }
                    
                    if record.weight and 'weight' not in latest_vitals:
                        latest_vitals['weight'] = {
                            'value': record.weight,
                            'recorded_at': record.recorded_at.isoformat()
                        }
                    
                    if record.blood_sugar and 'blood_sugar' not in latest_vitals:
                        latest_vitals['blood_sugar'] = {
                            'value': record.blood_sugar,
                            'recorded_at': record.recorded_at.isoformat()
                        }
                
                return latest_vitals
                
        except Exception as e:
            self.logger.error(f"Failed to get latest vital signs for user {user_id}: {e}")
            return {}
    
    async def check_vital_signs_alerts(self, user_id: str) -> List[Dict]:
        """Check for concerning vital signs and generate alerts"""
        try:
            latest_vitals = await self.get_latest_vital_signs(user_id)
            alerts = []
            
            # Blood pressure alerts
            if 'blood_pressure' in latest_vitals:
                bp = latest_vitals['blood_pressure']
                systolic = bp['systolic']
                diastolic = bp['diastolic']
                
                if systolic >= 180 or diastolic >= 110:
                    alerts.append({
                        'type': 'blood_pressure',
                        'severity': 'urgent',
                        'message': f'Huyết áp rất cao: {systolic}/{diastolic} mmHg. Cần liên hệ bác sĩ ngay.',
                        'value': f'{systolic}/{diastolic}',
                        'recorded_at': bp['recorded_at']
                    })
                elif systolic >= 140 or diastolic >= 90:
                    alerts.append({
                        'type': 'blood_pressure',
                        'severity': 'high',
                        'message': f'Huyết áp cao: {systolic}/{diastolic} mmHg. Nên theo dõi và tham khảo bác sĩ.',
                        'value': f'{systolic}/{diastolic}',
                        'recorded_at': bp['recorded_at']
                    })
            
            # Heart rate alerts
            if 'heart_rate' in latest_vitals:
                hr = latest_vitals['heart_rate']
                heart_rate = hr['value']
                
                if heart_rate > 100:
                    alerts.append({
                        'type': 'heart_rate',
                        'severity': 'moderate',
                        'message': f'Nhịp tim nhanh: {heart_rate} bpm. Nên nghỉ ngơi và theo dõi.',
                        'value': heart_rate,
                        'recorded_at': hr['recorded_at']
                    })
                elif heart_rate < 60:
                    alerts.append({
                        'type': 'heart_rate',
                        'severity': 'moderate',
                        'message': f'Nhịp tim chậm: {heart_rate} bpm. Nên kiểm tra với bác sĩ.',
                        'value': heart_rate,
                        'recorded_at': hr['recorded_at']
                    })
            
            # Temperature alerts
            if 'temperature' in latest_vitals:
                temp = latest_vitals['temperature']
                temperature = temp['value']
                
                if temperature >= 38.5:
                    alerts.append({
                        'type': 'temperature',
                        'severity': 'high',
                        'message': f'Sốt cao: {temperature}°C. Cần uống thuốc hạ sốt và theo dõi.',
                        'value': temperature,
                        'recorded_at': temp['recorded_at']
                    })
                elif temperature >= 37.5:
                    alerts.append({
                        'type': 'temperature',
                        'severity': 'moderate',
                        'message': f'Sốt nhẹ: {temperature}°C. Nên nghỉ ngơi và uống nhiều nước.',
                        'value': temperature,
                        'recorded_at': temp['recorded_at']
                    })
            
            # Blood sugar alerts (for diabetic patients)
            if 'blood_sugar' in latest_vitals:
                bs = latest_vitals['blood_sugar']
                blood_sugar = bs['value']
                
                if blood_sugar > 250:
                    alerts.append({
                        'type': 'blood_sugar',
                        'severity': 'urgent',
                        'message': f'Đường huyết rất cao: {blood_sugar} mg/dL. Cần liên hệ bác sĩ ngay.',
                        'value': blood_sugar,
                        'recorded_at': bs['recorded_at']
                    })
                elif blood_sugar < 70:
                    alerts.append({
                        'type': 'blood_sugar',
                        'severity': 'urgent',
                        'message': f'Đường huyết thấp: {blood_sugar} mg/dL. Cần ăn ngay và theo dõi.',
                        'value': blood_sugar,
                        'recorded_at': bs['recorded_at']
                    })
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Failed to check vital signs alerts for user {user_id}: {e}")
            return []
    
    async def get_health_trends(
        self,
        user_id: str,
        vital_type: str,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Analyze health trends for a specific vital sign"""
        try:
            history = await self.get_vital_signs_history(user_id, vital_type, days_back)
            
            if not history:
                return {'trend': 'no_data', 'message': 'Không có dữ liệu'}
            
            if len(history) < 3:
                return {'trend': 'insufficient_data', 'message': 'Cần thêm dữ liệu để phân tích'}
            
            # Simple trend analysis
            if vital_type == "blood_pressure":
                systolic_values = [record['systolic'] for record in history if 'systolic' in record]
                if len(systolic_values) >= 3:
                    recent_avg = sum(systolic_values[-3:]) / 3
                    older_avg = sum(systolic_values[:3]) / 3
                    
                    if recent_avg > older_avg + 10:
                        trend = 'increasing'
                        message = 'Huyết áp có xu hướng tăng'
                    elif recent_avg < older_avg - 10:
                        trend = 'decreasing'
                        message = 'Huyết áp có xu hướng giảm'
                    else:
                        trend = 'stable'
                        message = 'Huyết áp ổn định'
                    
                    return {
                        'trend': trend,
                        'message': message,
                        'recent_average': round(recent_avg, 1),
                        'older_average': round(older_avg, 1),
                        'data_points': len(systolic_values)
                    }
            
            elif vital_type == "weight":
                weight_values = [record['weight'] for record in history if 'weight' in record]
                if len(weight_values) >= 3:
                    recent_avg = sum(weight_values[-3:]) / 3
                    older_avg = sum(weight_values[:3]) / 3
                    
                    if recent_avg > older_avg + 2:
                        trend = 'increasing'
                        message = 'Cân nặng có xu hướng tăng'
                    elif recent_avg < older_avg - 2:
                        trend = 'decreasing'
                        message = 'Cân nặng có xu hướng giảm'
                    else:
                        trend = 'stable'
                        message = 'Cân nặng ổn định'
                    
                    return {
                        'trend': trend,
                        'message': message,
                        'recent_average': round(recent_avg, 1),
                        'older_average': round(older_avg, 1),
                        'data_points': len(weight_values)
                    }
            
            # Add similar analysis for other vital signs
            
            return {'trend': 'stable', 'message': 'Chỉ số ổn định'}
            
        except Exception as e:
            self.logger.error(f"Failed to analyze health trends for user {user_id}: {e}")
            return {'trend': 'error', 'message': 'Lỗi phân tích dữ liệu'}
    
    async def get_health_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive health summary for a user"""
        try:
            with get_db() as db:
                # Recent health records count
                recent_records = db.query(HealthRecord).filter(
                    and_(
                        HealthRecord.user_id == user_id,
                        HealthRecord.recorded_at >= datetime.utcnow() - timedelta(days=30)
                    )
                ).count()
                
                # Latest vital signs
                latest_vitals = await self.get_latest_vital_signs(user_id)
                
                # Health alerts
                alerts = await self.check_vital_signs_alerts(user_id)
                
                # Record types count
                record_types = db.query(
                    HealthRecord.record_type,
                    func.count(HealthRecord.id)
                ).filter(
                    HealthRecord.user_id == user_id
                ).group_by(HealthRecord.record_type).all()
                
                record_type_counts = {record_type: count for record_type, count in record_types}
                
                return {
                    'recent_records_30_days': recent_records,
                    'latest_vital_signs': latest_vitals,
                    'active_alerts': alerts,
                    'record_type_distribution': record_type_counts,
                    'last_updated': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get health summary for user {user_id}: {e}")
            return {}
    
    async def update_health_record(
        self,
        record_id: str,
        **updates
    ) -> bool:
        """Update health record information"""
        try:
            with get_db() as db:
                record = db.query(HealthRecord).filter(
                    HealthRecord.id == record_id
                ).first()
                
                if not record:
                    return False
                
                for key, value in updates.items():
                    if hasattr(record, key) and value is not None:
                        setattr(record, key, value)
                
                db.commit()
                self.logger.info(f"Updated health record {record_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to update health record {record_id}: {e}")
            return False
    
    async def delete_health_record(self, record_id: str) -> bool:
        """Delete a health record"""
        try:
            with get_db() as db:
                record = db.query(HealthRecord).filter(
                    HealthRecord.id == record_id
                ).first()
                
                if not record:
                    return False
                
                db.delete(record)
                db.commit()
                
                self.logger.info(f"Deleted health record {record_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to delete health record {record_id}: {e}")
            return False 