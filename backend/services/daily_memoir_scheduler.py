"""
Daily Memoir Scheduler Service
Schedules and manages daily memoir extraction tasks
"""
import logging
import asyncio
from datetime import datetime, date, time, timedelta
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from services.daily_memoir_extraction_service import DailyMemoirExtractionService

logger = logging.getLogger(__name__)

class DailyMemoirScheduler:
    """Scheduler for daily memoir extraction tasks"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.memoir_service = DailyMemoirExtractionService()
        self.logger = logger
        self.is_running = False
    
    async def daily_memoir_extraction_job(self):
        """Job function that runs daily memoir extraction for all users"""
        try:
            # Get yesterday's date (since we run this at end of day)
            yesterday = date.today() - timedelta(days=1)
            
            self.logger.info(f"🎭 Starting daily memoir extraction job for {yesterday}")
            
            # Process memoir extraction for all users
            result = await self.memoir_service.process_daily_memoir_for_all_users(yesterday)
            
            if result.get("success"):
                self.logger.info(f"✅ Daily memoir extraction completed successfully:")
                self.logger.info(f"   - Date: {result.get('date')}")
                self.logger.info(f"   - Users processed: {result.get('users_processed', 0)}")
                self.logger.info(f"   - Successful extractions: {result.get('successful_extractions', 0)}")
                self.logger.info(f"   - Failed extractions: {result.get('failed_extractions', 0)}")
                self.logger.info(f"   - No content users: {result.get('no_content_users', 0)}")
            else:
                self.logger.error(f"❌ Daily memoir extraction failed: {result.get('message')}")
                
        except Exception as e:
            self.logger.error(f"Error in daily memoir extraction job: {e}")
    
    async def manual_memoir_extraction(self, target_date: Optional[date] = None, user_id: Optional[str] = None):
        """Manually trigger memoir extraction for a specific date or user"""
        try:
            if target_date is None:
                target_date = date.today() - timedelta(days=1)
            
            self.logger.info(f"🎭 Manual memoir extraction triggered for {target_date}")
            
            if user_id:
                # Extract for specific user
                result = await self.memoir_service.process_daily_memoir_for_user(user_id, target_date)
                self.logger.info(f"Manual extraction result for user {user_id}: {result}")
            else:
                # Extract for all users
                result = await self.memoir_service.process_daily_memoir_for_all_users(target_date)
                self.logger.info(f"Manual extraction result for all users: {result}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in manual memoir extraction: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def start_scheduler(self):
        """Start the daily memoir extraction scheduler"""
        try:
            if self.is_running:
                self.logger.warning("Scheduler is already running")
                return
            
            # Schedule daily memoir extraction at 23:59 every day
            self.scheduler.add_job(
                self.daily_memoir_extraction_job,
                trigger=CronTrigger(hour=23, minute=59),
                id='daily_memoir_extraction',
                name='Daily Memoir Extraction',
                replace_existing=True,
                max_instances=1,  # Prevent overlapping jobs
                misfire_grace_time=300  # 5 minutes grace time
            )
            
            # Optional: Add a backup job that runs every 6 hours to catch missed extractions
            self.scheduler.add_job(
                self._check_missed_extractions,
                trigger=IntervalTrigger(hours=6),
                id='check_missed_extractions',
                name='Check Missed Memoir Extractions',
                replace_existing=True,
                max_instances=1
            )
            
            # Start scheduler - this will be called from async context
            try:
                self.scheduler.start()
                self.is_running = True
                
                self.logger.info("✅ Daily memoir extraction scheduler started")
                self.logger.info("   - Daily extraction: 23:59 every day")
                self.logger.info("   - Missed extraction check: every 6 hours")
                
            except RuntimeError as e:
                if "no running event loop" in str(e):
                    # Scheduler will be started later when event loop is available
                    self.logger.info("📅 Daily memoir scheduler configured (will start with event loop)")
                    self.is_running = False  # Mark as not running yet
                else:
                    raise e
            
        except Exception as e:
            self.logger.error(f"Failed to start memoir extraction scheduler: {e}")
    
    async def start_scheduler_async(self):
        """Start the scheduler in async context"""
        try:
            if not self.is_running and not self.scheduler.running:
                self.scheduler.start()
                self.is_running = True
                self.logger.info("✅ Daily memoir extraction scheduler started in async context")
                return True
            return True
        except Exception as e:
            self.logger.error(f"Failed to start scheduler in async context: {e}")
            return False
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        try:
            if not self.is_running:
                self.logger.warning("Scheduler is not running")
                return
            
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            self.logger.info("Daily memoir extraction scheduler stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping scheduler: {e}")
    
    async def _check_missed_extractions(self):
        """Check for missed memoir extractions and process them"""
        try:
            self.logger.info("🔍 Checking for missed memoir extractions...")
            
            # Check last 3 days for missed extractions
            for days_back in range(1, 4):
                check_date = date.today() - timedelta(days=days_back)
                
                # Check if we have any users who had conversations but no memoirs for this date
                missed_users = await self._get_users_with_missed_extractions(check_date)
                
                if missed_users:
                    self.logger.info(f"Found {len(missed_users)} users with missed extractions for {check_date}")
                    
                    for user_id in missed_users:
                        try:
                            result = await self.memoir_service.process_daily_memoir_for_user(user_id, check_date)
                            if result.get("success") and result.get("memoir_length", 0) > 0:
                                self.logger.info(f"✅ Processed missed extraction for user {user_id} on {check_date}")
                        except Exception as e:
                            self.logger.error(f"Failed to process missed extraction for user {user_id}: {e}")
                            
        except Exception as e:
            self.logger.error(f"Error checking missed extractions: {e}")
    
    async def _get_users_with_missed_extractions(self, check_date: date) -> list:
        """Get users who had conversations but no memoir for a specific date"""
        try:
            from db.db_config import get_db
            from db.models import Conversation, LifeMemoir
            from sqlalchemy import and_
            
            with get_db() as db:
                # Get users who had conversations on check_date
                start_datetime = datetime.combine(check_date, datetime.min.time())
                end_datetime = datetime.combine(check_date, datetime.max.time())
                
                users_with_conversations = db.query(Conversation.user_id).filter(
                    and_(
                        Conversation.started_at >= start_datetime,
                        Conversation.started_at <= end_datetime
                    )
                ).distinct().all()
                
                conversation_user_ids = {uid[0] for uid in users_with_conversations}
                
                # Get users who already have memoirs for this date
                users_with_memoirs = db.query(LifeMemoir.user_id).filter(
                    LifeMemoir.date_of_memory == check_date
                ).distinct().all()
                
                memoir_user_ids = {uid[0] for uid in users_with_memoirs}
                
                # Find users with conversations but no memoirs
                missed_users = list(conversation_user_ids - memoir_user_ids)
                
                return missed_users
                
        except Exception as e:
            self.logger.error(f"Error getting users with missed extractions: {e}")
            return []
    
    def get_scheduler_status(self) -> dict:
        """Get current scheduler status and job information"""
        try:
            if not self.is_running:
                return {
                    "running": False,
                    "message": "Scheduler is not running"
                }
            
            jobs = []
            for job in self.scheduler.get_jobs():
                next_run = job.next_run_time
                jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run": next_run.isoformat() if next_run else None,
                    "trigger": str(job.trigger)
                })
            
            return {
                "running": True,
                "jobs": jobs,
                "scheduler_state": self.scheduler.state
            }
            
        except Exception as e:
            self.logger.error(f"Error getting scheduler status: {e}")
            return {
                "running": False,
                "error": str(e)
            }
    
    async def test_memoir_extraction(self, user_id: Optional[str] = None, days_back: int = 1):
        """Test memoir extraction for debugging purposes"""
        try:
            test_date = date.today() - timedelta(days=days_back)
            
            self.logger.info(f"🧪 Testing memoir extraction for {test_date}")
            
            if user_id:
                result = await self.memoir_service.process_daily_memoir_for_user(user_id, test_date)
            else:
                result = await self.memoir_service.process_daily_memoir_for_all_users(test_date)
            
            self.logger.info(f"Test result: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in test memoir extraction: {e}")
            return {"success": False, "message": f"Test error: {str(e)}"}

# Global scheduler instance
daily_memoir_scheduler = DailyMemoirScheduler() 