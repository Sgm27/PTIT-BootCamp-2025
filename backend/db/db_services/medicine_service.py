"""
Medicine Management Service
Handles medication records, prescriptions, and medicine scanning results
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, and_, or_

from db.db_config import get_db
from db.models import MedicineRecord, MedicationLog, User

logger = logging.getLogger(__name__)

class MedicineDBService:
    """Service for managing medicine records and medication tracking"""
    
    def __init__(self):
        self.logger = logger
    
    async def create_medicine_record(
        self,
        user_id: str,
        medicine_name: str,
        dosage: str,
        frequency: str,
        start_date: date,
        generic_name: Optional[str] = None,
        end_date: Optional[date] = None,
        instructions: Optional[str] = None,
        side_effects: Optional[List[str]] = None,
        contraindications: Optional[List[str]] = None,
        prescribed_by: Optional[str] = None,
        prescription_date: Optional[date] = None,
        pharmacy: Optional[str] = None,
        scan_image_path: Optional[str] = None,
        scan_confidence: Optional[float] = None,
        scan_result: Optional[Dict] = None
    ) -> Optional[MedicineRecord]:
        """Create a new medicine record"""
        try:
            with get_db() as db:
                medicine = MedicineRecord(
                    user_id=user_id,
                    medicine_name=medicine_name,
                    generic_name=generic_name,
                    dosage=dosage,
                    frequency=frequency,
                    start_date=start_date,
                    end_date=end_date,
                    instructions=instructions,
                    side_effects=side_effects or [],
                    contraindications=contraindications or [],
                    prescribed_by=prescribed_by,
                    prescription_date=prescription_date,
                    pharmacy=pharmacy,
                    scan_image_path=scan_image_path,
                    scan_confidence=scan_confidence,
                    scan_result=scan_result
                )
                
                db.add(medicine)
                db.commit()
                db.refresh(medicine)
                
                self.logger.info(f"Created medicine record {medicine.id} for user {user_id}")
                return medicine
                
        except Exception as e:
            self.logger.error(f"Failed to create medicine record: {e}")
            return None
    
    async def get_medicine_record(self, medicine_id: str) -> Optional[MedicineRecord]:
        """Get a specific medicine record"""
        try:
            with get_db() as db:
                medicine = db.query(MedicineRecord).filter(
                    MedicineRecord.id == medicine_id
                ).first()
                return medicine
        except Exception as e:
            self.logger.error(f"Failed to get medicine record {medicine_id}: {e}")
            return None
    
    async def get_user_medicines(
        self,
        user_id: str,
        active_only: bool = True,
        limit: int = 50,
        offset: int = 0
    ) -> List[MedicineRecord]:
        """Get all medicine records for a user"""
        try:
            with get_db() as db:
                query = db.query(MedicineRecord).filter(MedicineRecord.user_id == user_id)
                
                if active_only:
                    today = date.today()
                    query = query.filter(
                        and_(
                            MedicineRecord.is_active == True,
                            MedicineRecord.start_date <= today,
                            or_(
                                MedicineRecord.end_date.is_(None),
                                MedicineRecord.end_date >= today
                            )
                        )
                    )
                
                medicines = query.order_by(
                    desc(MedicineRecord.created_at)
                ).offset(offset).limit(limit).all()
                
                return medicines
                
        except Exception as e:
            self.logger.error(f"Failed to get medicines for user {user_id}: {e}")
            return []
    
    async def search_medicines(
        self,
        user_id: str,
        query: str,
        limit: int = 20
    ) -> List[MedicineRecord]:
        """Search medicines by name or generic name"""
        try:
            with get_db() as db:
                medicines = db.query(MedicineRecord).filter(
                    and_(
                        MedicineRecord.user_id == user_id,
                        or_(
                            MedicineRecord.medicine_name.ilike(f"%{query}%"),
                            MedicineRecord.generic_name.ilike(f"%{query}%")
                        )
                    )
                ).order_by(desc(MedicineRecord.created_at)).limit(limit).all()
                
                return medicines
                
        except Exception as e:
            self.logger.error(f"Failed to search medicines for user {user_id}: {e}")
            return []
    
    async def update_medicine_record(
        self,
        medicine_id: str,
        **updates
    ) -> bool:
        """Update medicine record information"""
        try:
            with get_db() as db:
                medicine = db.query(MedicineRecord).filter(
                    MedicineRecord.id == medicine_id
                ).first()
                
                if not medicine:
                    return False
                
                for key, value in updates.items():
                    if hasattr(medicine, key) and value is not None:
                        setattr(medicine, key, value)
                
                medicine.updated_at = datetime.utcnow()
                db.commit()
                
                self.logger.info(f"Updated medicine record {medicine_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to update medicine record {medicine_id}: {e}")
            return False
    
    async def deactivate_medicine(self, medicine_id: str) -> bool:
        """Deactivate a medicine record"""
        return await self.update_medicine_record(
            medicine_id, 
            is_active=False, 
            end_date=date.today()
        )
    
    async def log_medication_taken(
        self,
        medicine_id: str,
        user_id: str,
        scheduled_time: datetime,
        actual_time: Optional[datetime] = None,
        status: str = "taken",
        notes: Optional[str] = None,
        side_effects_experienced: Optional[List[str]] = None,
        logged_by: str = "user"
    ) -> Optional[MedicationLog]:
        """Log medication intake"""
        try:
            with get_db() as db:
                log_entry = MedicationLog(
                    medicine_id=medicine_id,
                    user_id=user_id,
                    scheduled_time=scheduled_time,
                    actual_time=actual_time or datetime.utcnow(),
                    status=status,
                    notes=notes,
                    side_effects_experienced=side_effects_experienced or [],
                    logged_by=logged_by
                )
                
                db.add(log_entry)
                db.commit()
                db.refresh(log_entry)
                
                self.logger.info(f"Logged medication {medicine_id} for user {user_id}")
                return log_entry
                
        except Exception as e:
            self.logger.error(f"Failed to log medication: {e}")
            return None
    
    async def get_medication_logs(
        self,
        user_id: str,
        medicine_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100
    ) -> List[MedicationLog]:
        """Get medication logs with optional filtering"""
        try:
            with get_db() as db:
                query = db.query(MedicationLog).filter(MedicationLog.user_id == user_id)
                
                if medicine_id:
                    query = query.filter(MedicationLog.medicine_id == medicine_id)
                
                if start_date:
                    query = query.filter(MedicationLog.scheduled_time >= start_date)
                
                if end_date:
                    query = query.filter(MedicationLog.scheduled_time <= end_date)
                
                logs = query.order_by(
                    desc(MedicationLog.scheduled_time)
                ).limit(limit).all()
                
                return logs
                
        except Exception as e:
            self.logger.error(f"Failed to get medication logs for user {user_id}: {e}")
            return []
    
    async def get_missed_medications(
        self,
        user_id: str,
        days_back: int = 7
    ) -> List[Dict]:
        """Get medications that were missed in the last X days"""
        try:
            with get_db() as db:
                start_date = datetime.utcnow() - timedelta(days=days_back)
                
                missed_logs = db.query(MedicationLog).join(
                    MedicineRecord, MedicationLog.medicine_id == MedicineRecord.id
                ).filter(
                    and_(
                        MedicationLog.user_id == user_id,
                        MedicationLog.status.in_(["missed", "skipped"]),
                        MedicationLog.scheduled_time >= start_date
                    )
                ).options(joinedload(MedicationLog.medicine)).all()
                
                results = []
                for log in missed_logs:
                    results.append({
                        'log_id': str(log.id),
                        'medicine_name': log.medicine.medicine_name,
                        'dosage': log.medicine.dosage,
                        'scheduled_time': log.scheduled_time.isoformat(),
                        'status': log.status,
                        'notes': log.notes
                    })
                
                return results
                
        except Exception as e:
            self.logger.error(f"Failed to get missed medications for user {user_id}: {e}")
            return []
    
    async def get_medication_adherence(
        self,
        user_id: str,
        medicine_id: Optional[str] = None,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Calculate medication adherence statistics"""
        try:
            with get_db() as db:
                start_date = datetime.utcnow() - timedelta(days=days_back)
                
                query = db.query(MedicationLog).filter(
                    and_(
                        MedicationLog.user_id == user_id,
                        MedicationLog.scheduled_time >= start_date
                    )
                )
                
                if medicine_id:
                    query = query.filter(MedicationLog.medicine_id == medicine_id)
                
                logs = query.all()
                
                total_scheduled = len(logs)
                taken = len([log for log in logs if log.status == "taken"])
                missed = len([log for log in logs if log.status == "missed"])
                delayed = len([log for log in logs if log.status == "delayed"])
                skipped = len([log for log in logs if log.status == "skipped"])
                
                adherence_rate = (taken / total_scheduled * 100) if total_scheduled > 0 else 0
                
                return {
                    'total_scheduled': total_scheduled,
                    'taken': taken,
                    'missed': missed,
                    'delayed': delayed,
                    'skipped': skipped,
                    'adherence_rate': round(adherence_rate, 2)
                }
                
        except Exception as e:
            self.logger.error(f"Failed to calculate medication adherence for user {user_id}: {e}")
            return {
                'total_scheduled': 0,
                'taken': 0,
                'missed': 0,
                'delayed': 0,
                'skipped': 0,
                'adherence_rate': 0.0
            }
    
    async def get_upcoming_medications(
        self,
        user_id: str,
        hours_ahead: int = 24
    ) -> List[Dict]:
        """Get upcoming medication schedules"""
        try:
            with get_db() as db:
                # This is a simplified version - in reality, you'd need to implement
                # a proper scheduling system based on frequency patterns
                now = datetime.utcnow()
                future_time = now + timedelta(hours=hours_ahead)
                
                active_medicines = await self.get_user_medicines(user_id, active_only=True)
                
                upcoming = []
                for medicine in active_medicines:
                    # Generate next scheduled times based on frequency
                    # This is a simplified example - real implementation would be more complex
                    if "daily" in medicine.frequency.lower():
                        next_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
                        if next_time <= now:
                            next_time += timedelta(days=1)
                        
                        if next_time <= future_time:
                            upcoming.append({
                                'medicine_id': str(medicine.id),
                                'medicine_name': medicine.medicine_name,
                                'dosage': medicine.dosage,
                                'scheduled_time': next_time.isoformat(),
                                'instructions': medicine.instructions
                            })
                
                return sorted(upcoming, key=lambda x: x['scheduled_time'])
                
        except Exception as e:
            self.logger.error(f"Failed to get upcoming medications for user {user_id}: {e}")
            return []
    
    async def get_medicine_by_scan_result(
        self,
        user_id: str,
        scan_result: Dict
    ) -> Optional[MedicineRecord]:
        """Find existing medicine record by scan result"""
        try:
            with get_db() as db:
                # Look for similar scan results or medicine names
                medicine_name = scan_result.get('medicine_name', '')
                
                medicine = db.query(MedicineRecord).filter(
                    and_(
                        MedicineRecord.user_id == user_id,
                        MedicineRecord.medicine_name.ilike(f"%{medicine_name}%")
                    )
                ).first()
                
                return medicine
                
        except Exception as e:
            self.logger.error(f"Failed to find medicine by scan result: {e}")
            return None
    
    async def create_medicine_from_scan(
        self,
        user_id: str,
        scan_result: Dict,
        scan_image_path: str,
        scan_confidence: float
    ) -> Optional[MedicineRecord]:
        """Create medicine record from AI scan result"""
        try:
            # Extract information from scan result
            medicine_name = scan_result.get('medicine_name', 'Unknown Medicine')
            generic_name = scan_result.get('generic_name')
            dosage = scan_result.get('dosage', 'As prescribed')
            frequency = scan_result.get('frequency', 'As directed')
            instructions = scan_result.get('instructions')
            side_effects = scan_result.get('side_effects', [])
            contraindications = scan_result.get('contraindications', [])
            
            return await self.create_medicine_record(
                user_id=user_id,
                medicine_name=medicine_name,
                generic_name=generic_name,
                dosage=dosage,
                frequency=frequency,
                start_date=date.today(),
                instructions=instructions,
                side_effects=side_effects,
                contraindications=contraindications,
                scan_image_path=scan_image_path,
                scan_confidence=scan_confidence,
                scan_result=scan_result
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create medicine from scan: {e}")
            return None
    
    async def get_medicine_interactions(
        self,
        user_id: str,
        new_medicine_name: Optional[str] = None
    ) -> List[Dict]:
        """Check for potential drug interactions"""
        try:
            with get_db() as db:
                active_medicines = await self.get_user_medicines(user_id, active_only=True)
                
                interactions = []
                medicine_names = [med.medicine_name for med in active_medicines]
                
                if new_medicine_name:
                    medicine_names.append(new_medicine_name)
                
                # This is a simplified version - in reality, you'd integrate with
                # a drug interaction database or API
                for i, med1 in enumerate(medicine_names):
                    for med2 in medicine_names[i+1:]:
                        # Check for common interaction patterns
                        if self._check_interaction(med1, med2):
                            interactions.append({
                                'medicine1': med1,
                                'medicine2': med2,
                                'severity': 'moderate',
                                'description': f"Potential interaction between {med1} and {med2}"
                            })
                
                return interactions
                
        except Exception as e:
            self.logger.error(f"Failed to check medicine interactions for user {user_id}: {e}")
            return []
    
    def _check_interaction(self, med1: str, med2: str) -> bool:
        """Simple interaction check - should be replaced with real drug database"""
        # This is a placeholder - implement real drug interaction checking
        common_interactions = [
            ("warfarin", "aspirin"),
            ("metformin", "alcohol"),
            # Add more interaction pairs
        ]
        
        med1_lower = med1.lower()
        med2_lower = med2.lower()
        
        for interaction in common_interactions:
            if (med1_lower in interaction[0] and med2_lower in interaction[1]) or \
               (med1_lower in interaction[1] and med2_lower in interaction[0]):
                return True
        
        return False
    
    async def get_medicine_stats(self, user_id: str) -> Dict[str, Any]:
        """Get medicine statistics for a user"""
        try:
            with get_db() as db:
                # Total medicines
                total_medicines = db.query(MedicineRecord).filter(
                    MedicineRecord.user_id == user_id
                ).count()
                
                # Active medicines
                active_medicines = len(await self.get_user_medicines(user_id, active_only=True))
                
                # Recent adherence
                adherence = await self.get_medication_adherence(user_id, days_back=30)
                
                # Recent scans
                recent_scans = db.query(MedicineRecord).filter(
                    and_(
                        MedicineRecord.user_id == user_id,
                        MedicineRecord.scan_image_path.isnot(None)
                    )
                ).count()
                
                return {
                    'total_medicines': total_medicines,
                    'active_medicines': active_medicines,
                    'adherence_rate': adherence['adherence_rate'],
                    'recent_scans': recent_scans,
                    'missed_medications_30_days': adherence['missed']
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get medicine stats for user {user_id}: {e}")
            return {
                'total_medicines': 0,
                'active_medicines': 0,
                'adherence_rate': 0.0,
                'recent_scans': 0,
                'missed_medications_30_days': 0
            } 