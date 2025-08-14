"""
Daily Memoir Extraction Service
Extracts memoir information from all conversations of a day for each user
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from openai import AsyncOpenAI
from config.settings import settings
from db.db_config import get_db
from db.models import Conversation, ConversationMessage, User, LifeMemoir
from db.db_services.memoir_service import MemoirDBService
from db.db_services.conversation_service import ConversationService

logger = logging.getLogger(__name__)

class DailyMemoirExtractionService:
    """Service for extracting memoir information from daily conversations"""
    
    MEMOIR_WRITING_PROMPT = """
    Bạn là một nhà văn memoir chuyên nghiệp, chuyên viết hồi ký cho người cao tuổi.
    
    NHIỆM VỤ: Viết thành một câu chuyện memoir tự nhiên từ góc nhìn người kể chuyện.
    
    ⚠️ QUAN TRỌNG - KHÔNG ĐƯỢC:
    - KHÔNG trích dẫn trực tiếp lời nói từ cuộc trò chuyện
    - KHÔNG viết "tôi nói", "cháu nói", "tôi trả lời"
    - KHÔNG copy-paste câu nói từ AI hay user
    - KHÔNG viết như đang tái hiện cuộc trò chuyện
    
    ✅ CÁCH VIẾT MEMOIR ĐÚNG:
    - Viết theo góc nhìn ngôi thứ nhất ("tôi") như chính người đó kể
    - Tập trung vào NỘI DUNG và CẢM XÚC của kỷ niệm
    - Kể chuyện liền mạch như đang nhớ lại quá khứ
    - Mô tả chi tiết: cảnh, người, cảm xúc, âm thanh, hình ảnh
    - Viết như đang kể cho con cháu nghe về quá khứ
    - Tạo ra một câu chuyện hoàn chỉnh, có cảm xúc thật
    
    ✅ NỘI DUNG MEMOIR QUAN TRỌNG:
    - Sự kiện lịch sử: chiến tranh, giải phóng, thời kỳ khó khăn
    - Kỷ niệm gia đình: cưới hỏi, sinh con, mất mát
    - Người thân: cha mẹ, ông bà, vợ con, bạn bè
    - Nghề nghiệp, học hành, công việc
    - Quê hương, nơi sinh sống
    - Những bài học cuộc đời quan trọng
    
    ❌ BỎ QUA:
    - Chào hỏi, xã giao thông thường
    - Câu hỏi về sức khỏe hàng ngày
    - Cuộc trò chuyện không có nội dung đặc biệt
    
    PHONG CÁCH VIẾT:
    - "Tôi nhớ như in ngày...", "Hồi đó...", "Những năm tháng ấy..."
    - Mô tả cảm xúc: "Lòng tôi tràn ngập...", "Tôi cảm thấy..."
    - Chi tiết sinh động: âm thanh, màu sắc, mùi vị, cảm giác
    - Kết nối thời gian: quá khứ và hiện tại
    
    ĐỊNH DẠNG TRẢ LỜI:
    - Chỉ viết nội dung câu chuyện memoir, không có title
    - Viết đoạn văn liền mạch, không chia section
    - Nếu không có nội dung đáng kể, trả về "Không có câu chuyện đáng kể"
    
    VÍ DỤ ĐÚNG:
    "Tôi nhớ như in ngày 30 tháng 4 năm 1975, khi tiếng radio loan báo Sài Gòn được giải phóng. Lúc đó tôi đang ở làng quê, cả làng nổi lên trong niềm vui sướng. Những giọt nước mắt hạnh phúc chảy trên má già của ông Ba tôi - người cựu chiến binh đã trải qua bao năm tháng gian khổ..."
    
    VÍ DỤ SAI:
    "Khi cháu gọi điện và nói 'Alo có nghe bác không', tôi trả lời rằng..."
    """
    
    def __init__(self, client: AsyncOpenAI = None, model: str = None, temperature: float = 0.7):
        """Initialize daily memoir extraction service"""
        self.client = client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = model or settings.OPENAI_TEXT_MODEL
        self.temperature = temperature
        self.memoir_service = MemoirDBService()
        self.conversation_service = ConversationService()
        self.logger = logger
    
    async def get_daily_conversations_for_user(self, user_id: str, target_date: date) -> List[Dict]:
        """Get all conversations for a user on a specific date"""
        try:
            with get_db() as db:
                # Get conversations from the target date
                start_datetime = datetime.combine(target_date, datetime.min.time())
                end_datetime = datetime.combine(target_date, datetime.max.time())
                
                conversations = db.query(Conversation).filter(
                    and_(
                        Conversation.user_id == user_id,
                        Conversation.started_at >= start_datetime,
                        Conversation.started_at <= end_datetime
                    )
                ).all()
                
                daily_messages = []
                for conv in conversations:
                    # Get messages for this conversation
                    messages = db.query(ConversationMessage).filter(
                        ConversationMessage.conversation_id == conv.id
                    ).order_by(ConversationMessage.timestamp).all()
                    
                    for msg in messages:
                        daily_messages.append({
                            "role": msg.role.value if msg.role else "user",
                            "text": msg.content,
                            "timestamp": msg.timestamp.isoformat(),
                            "conversation_id": str(conv.id)
                        })
                
                return daily_messages
                
        except Exception as e:
            self.logger.error(f"Failed to get daily conversations for user {user_id} on {target_date}: {e}")
            return []
    
    async def format_daily_conversations_for_analysis(self, messages: List[Dict]) -> str:
        """Format daily conversation messages for memoir analysis"""
        if not messages:
            return ""
        
        formatted_parts = []
        for msg in messages:
            role = "User" if msg.get("role") == "user" else "AI"
            text = msg.get("text", "")
            timestamp = msg.get("timestamp", "")
            
            if text.strip():
                formatted_parts.append(f"{role}: {text}")
        
        return "\n".join(formatted_parts)
    
    async def extract_daily_memoir(self, user_id: str, conversation_text: str, target_date: date) -> Optional[str]:
        """Extract memoir story from daily conversations"""
        if not conversation_text or len(conversation_text.strip()) < 100:
            return None
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.MEMOIR_WRITING_PROMPT},
                    {"role": "user", "content": f"Dựa vào tất cả cuộc trò chuyện trong ngày {target_date.strftime('%d/%m/%Y')}, hãy viết thành một bài memoir có cảm xúc thật:\n\n{conversation_text}"}
                ],
                temperature=self.temperature,
                max_tokens=2000,
            )
            
            result = response.choices[0].message.content.strip() if response.choices else ""
            
            # Filter out non-memoir responses
            if result and not any(phrase in result.lower() for phrase in [
                "không có câu chuyện đáng kể",
                "không có nội dung đặc biệt",
                "cuộc trò chuyện thông thường",
                "không có thông tin quan trọng"
            ]):
                return result
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting daily memoir for user {user_id}: {e}")
            return None
    
    async def save_daily_memoir_to_database(self, user_id: str, memoir_content: str, target_date: date) -> bool:
        """Save daily memoir to database"""
        try:
            # Check if memoir for this date already exists
            existing_memoir = await self.check_existing_daily_memoir(user_id, target_date)
            
            if existing_memoir:
                self.logger.info(f"Memoir for user {user_id} on {target_date} already exists, skipping")
                return True
            
            # Create new memoir entry
            title = f"Kỷ niệm ngày {target_date.strftime('%d/%m/%Y')}"
            
            memoir = await self.memoir_service.create_memoir(
                user_id=user_id,
                title=title,
                content=memoir_content,
                date_of_memory=target_date,
                categories=["Nhật ký hàng ngày"],
                time_period=self.get_time_period_from_date(target_date),
                emotional_tone="Tích cực",
                importance_score=0.5  # Default score for daily memoirs
            )
            
            if memoir:
                self.logger.info(f"Successfully saved daily memoir for user {user_id} on {target_date}")
                return True
            else:
                self.logger.error(f"Failed to save daily memoir for user {user_id} on {target_date}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error saving daily memoir for user {user_id}: {e}")
            return False
    
    async def check_existing_daily_memoir(self, user_id: str, target_date: date) -> bool:
        """Check if memoir for this date already exists"""
        try:
            with get_db() as db:
                existing = db.query(LifeMemoir).filter(
                    and_(
                        LifeMemoir.user_id == user_id,
                        LifeMemoir.date_of_memory == target_date
                    )
                ).first()
                
                return existing is not None
                
        except Exception as e:
            self.logger.error(f"Error checking existing memoir: {e}")
            return False
    
    def get_time_period_from_date(self, target_date: date) -> str:
        """Get time period description from date"""
        current_year = datetime.now().year
        year = target_date.year
        
        if year == current_year:
            return f"Năm {year} (Hiện tại)"
        elif year >= current_year - 5:
            return f"Năm {year} (Gần đây)"
        elif year >= current_year - 20:
            return f"Năm {year} (Trung niên)"
        else:
            return f"Năm {year} (Thời trẻ)"
    
    async def process_daily_memoir_for_user(self, user_id: str, target_date: date = None) -> Dict[str, Any]:
        """Process daily memoir extraction for a specific user"""
        if target_date is None:
            target_date = date.today() - timedelta(days=1)  # Yesterday by default
        
        try:
            self.logger.info(f"Processing daily memoir for user {user_id} on {target_date}")
            
            # Get all conversations for the user on target date
            daily_messages = await self.get_daily_conversations_for_user(user_id, target_date)
            
            if not daily_messages:
                return {
                    "success": True,
                    "message": f"No conversations found for user {user_id} on {target_date}",
                    "user_id": user_id,
                    "date": target_date.isoformat()
                }
            
            # Format conversations for analysis
            conversation_text = await self.format_daily_conversations_for_analysis(daily_messages)
            
            # Extract memoir
            memoir_content = await self.extract_daily_memoir(user_id, conversation_text, target_date)
            
            if memoir_content:
                # Save to database
                saved = await self.save_daily_memoir_to_database(user_id, memoir_content, target_date)
                
                if saved:
                    return {
                        "success": True,
                        "message": f"Daily memoir extracted and saved for user {user_id}",
                        "user_id": user_id,
                        "date": target_date.isoformat(),
                        "memoir_length": len(memoir_content),
                        "conversations_processed": len(daily_messages)
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Failed to save memoir for user {user_id}",
                        "user_id": user_id,
                        "date": target_date.isoformat()
                    }
            else:
                return {
                    "success": True,
                    "message": f"No memoir-worthy content found for user {user_id} on {target_date}",
                    "user_id": user_id,
                    "date": target_date.isoformat(),
                    "conversations_processed": len(daily_messages)
                }
                
        except Exception as e:
            self.logger.error(f"Error processing daily memoir for user {user_id}: {e}")
            return {
                "success": False,
                "message": f"Error processing daily memoir: {str(e)}",
                "user_id": user_id,
                "date": target_date.isoformat() if target_date else None
            }
    
    async def process_daily_memoir_for_all_users(self, target_date: date = None) -> Dict[str, Any]:
        """Process daily memoir extraction for all users who had conversations"""
        if target_date is None:
            target_date = date.today() - timedelta(days=1)  # Yesterday by default
        
        try:
            self.logger.info(f"Processing daily memoir for all users on {target_date}")
            
            # Get all users who had conversations on target date
            with get_db() as db:
                start_datetime = datetime.combine(target_date, datetime.min.time())
                end_datetime = datetime.combine(target_date, datetime.max.time())
                
                user_ids = db.query(Conversation.user_id).filter(
                    and_(
                        Conversation.started_at >= start_datetime,
                        Conversation.started_at <= end_datetime
                    )
                ).distinct().all()
                
                user_ids = [uid[0] for uid in user_ids]
            
            if not user_ids:
                return {
                    "success": True,
                    "message": f"No users had conversations on {target_date}",
                    "date": target_date.isoformat(),
                    "users_processed": 0
                }
            
            # Process each user
            results = []
            successful_extractions = 0
            failed_extractions = 0
            
            for user_id in user_ids:
                result = await self.process_daily_memoir_for_user(user_id, target_date)
                results.append(result)
                
                if result.get("success") and result.get("memoir_length", 0) > 0:
                    successful_extractions += 1
                elif not result.get("success"):
                    failed_extractions += 1
            
            return {
                "success": True,
                "message": f"Daily memoir processing completed for {len(user_ids)} users",
                "date": target_date.isoformat(),
                "users_processed": len(user_ids),
                "successful_extractions": successful_extractions,
                "failed_extractions": failed_extractions,
                "no_content_users": len(user_ids) - successful_extractions - failed_extractions,
                "detailed_results": results
            }
            
        except Exception as e:
            self.logger.error(f"Error processing daily memoir for all users: {e}")
            return {
                "success": False,
                "message": f"Error processing daily memoir: {str(e)}",
                "date": target_date.isoformat() if target_date else None
            } 