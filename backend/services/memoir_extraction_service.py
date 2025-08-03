"""
Memoir extraction service for important conversation history information
Optimized for performance and only extracting truly important details
"""
import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from openai import AsyncOpenAI
from fastapi import HTTPException
from config.settings import settings


class MemoirExtractionService:
    """Service for extracting important information from conversation history for memoir purposes."""
    
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
    
    def __init__(self, client: AsyncOpenAI = None, model: str = None, temperature: float = 0.3):
        """Initialize memoir extraction service.
        
        Args:
            client: OpenAI client instance. Creates new if None.
            model: Model to use for text processing. Uses default from settings if None.
            temperature: Lower temperature for more focused extraction.
        """
        self.client = client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = model or settings.OPENAI_TEXT_MODEL
        self.temperature = temperature
        self.conversation_file = Path("conversation_history.json")
        self.memoir_file = Path("my_life_stories.txt")
        self._background_task = None
        self._last_processed_count = 0  # Track processed message count
        self._auto_extraction_threshold = 3  # Auto extract after 3 new messages (more frequent)
        self._last_extraction_time = None  # Track last extraction time
        self._time_threshold_minutes = 5  # Also extract every 5 minutes regardless of message count
        
    async def load_conversation_history(self) -> List[Dict]:
        """Load conversation history from JSON file.
        
        Returns:
            List of conversation messages.
        """
        try:
            if self.conversation_file.exists():
                with open(self.conversation_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading conversation history: {e}")
            return []
    
    async def extract_important_info(self, conversation_text: str) -> str:
        """Extract and write memoir stories from conversation text.
        
        Args:
            conversation_text: Full conversation text to analyze.
            
        Returns:
            Written memoir story or empty string if none found.
        """
        if not conversation_text or len(conversation_text.strip()) < 50:
            return ""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.MEMOIR_WRITING_PROMPT},
                    {"role": "user", "content": f"Dựa vào cuộc trò chuyện này, hãy viết thành một bài memoir có cảm xúc thật:\n\n{conversation_text}"}
                ],
                temperature=0.7,  # Higher temperature for more creative writing
                max_tokens=1500,  # More tokens for complete memoir stories
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
            
            return ""
            
        except Exception as e:
            print(f"Error writing memoir story: {e}")
            return ""
    
    async def format_conversation_for_analysis(self, messages: List[Dict]) -> str:
        """Format conversation messages for analysis.
        
        Args:
            messages: List of conversation messages.
            
        Returns:
            Formatted conversation text.
        """
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
    
    async def append_to_memoir_file(self, memoir_story: str) -> bool:
        """Append memoir story to memoir file.
        
        Args:
            memoir_story: Written memoir story to save.
            
        Returns:
            True if successfully saved, False otherwise.
        """
        if not memoir_story or memoir_story.strip() == "":
            return False
        
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Create file if it doesn't exist
            if not self.memoir_file.exists():
                with open(self.memoir_file, 'w', encoding='utf-8') as f:
                    f.write("CÂU CHUYỆN HỒI KÝ\n")
                    f.write("Những câu chuyện đời được viết lại từ trái tim\n\n")
            
            # Append new memoir story
            with open(self.memoir_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}]\n\n")
                f.write(f"{memoir_story}\n\n")
                f.write("-" * 50 + "\n\n")
            
            return True
            
        except Exception as e:
            print(f"Error saving memoir story: {e}")
            return False
    
    async def process_conversation_history_background(self) -> Dict:
        """Process conversation history in background to extract important info.
        
        Returns:
            Dictionary with processing results.
        """
        try:
            # Load conversation history
            messages = await self.load_conversation_history()
            
            if not messages:
                return {"success": False, "message": "No conversation history found"}
            
            # Format for analysis
            conversation_text = await self.format_conversation_for_analysis(messages)
            
            if len(conversation_text) < 100:  # Skip very short conversations
                return {"success": False, "message": "Conversation too short for analysis"}
            
            # Extract and write memoir story
            memoir_story = await self.extract_important_info(conversation_text)
            
            if memoir_story:
                # Save to memoir file
                saved = await self.append_to_memoir_file(memoir_story)
                
                if saved:
                    # Update extraction time tracking
                    from datetime import datetime
                    self._last_extraction_time = datetime.now()
                    
                    return {
                        "success": True,
                        "message": "Memoir story written and saved",
                        "extracted_info": memoir_story,
                        "conversation_length": len(messages),
                        "info_length": len(memoir_story)
                    }
                else:
                    return {"success": False, "message": "Failed to save extracted information"}
            else:
                # Update extraction time even if no info found
                from datetime import datetime
                self._last_extraction_time = datetime.now()
                
                return {
                    "success": True,
                    "message": "No memoir-worthy stories found in current conversation",
                    "conversation_length": len(messages)
                }
                
        except Exception as e:
            return {"success": False, "message": f"Error processing conversation: {str(e)}"}
    
    def start_background_extraction(self):
        """Start background task for memoir extraction."""
        if self._background_task and not self._background_task.done():
            return {"message": "Background extraction already running"}
        
        self._background_task = asyncio.create_task(
            self.process_conversation_history_background()
        )
        return {"message": "Background extraction started"}
    
    async def get_background_task_status(self) -> Dict:
        """Get status of background extraction task.
        
        Returns:
            Dictionary with task status and results if completed.
        """
        if not self._background_task:
            return {"status": "not_started", "message": "No background task"}
        
        if self._background_task.done():
            try:
                result = await self._background_task
                return {"status": "completed", "result": result}
            except Exception as e:
                return {"status": "failed", "error": str(e)}
        else:
            return {"status": "running", "message": "Background extraction in progress"}
    
    async def get_memoir_file_info(self) -> Dict:
        """Get information about the memoir file.
        
        Returns:
            Dictionary with memoir file statistics.
        """
        try:
            if self.memoir_file.exists():
                with open(self.memoir_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                return {
                    "exists": True,
                    "file_size": len(content),
                    "line_count": len(content.split('\n')),
                    "last_modified": datetime.fromtimestamp(
                        self.memoir_file.stat().st_mtime
                    ).isoformat(),
                    "file_path": str(self.memoir_file)
                }
            else:
                return {
                    "exists": False,
                    "message": "Memoir file not yet created"
                }
        except Exception as e:
             return {"error": f"Error reading memoir file: {str(e)}"}
    
    async def should_auto_extract(self) -> bool:
        """Check if automatic extraction should be triggered.
        
        Returns:
            True if auto extraction should run, False otherwise.
        """
        try:
            messages = await self.load_conversation_history()
            current_count = len(messages)
            
            # Check message-based threshold (more frequent)
            if current_count - self._last_processed_count >= self._auto_extraction_threshold:
                return True
            
            # Check time-based threshold (extract every 5 minutes)
            if self._last_extraction_time:
                from datetime import datetime, timedelta
                current_time = datetime.now()
                time_diff = current_time - self._last_extraction_time
                if time_diff >= timedelta(minutes=self._time_threshold_minutes):
                    return True
            else:
                # First time - trigger if we have any messages
                if current_count > 0:
                    return True
            
            return False
        except Exception:
            return False
    
    async def update_conversation_and_extract(self, new_message: Dict) -> Dict:
        """Update conversation history and potentially trigger extraction.
        
        Args:
            new_message: New conversation message to add.
            
        Returns:
            Dictionary with update and extraction status.
        """
        try:
            # Load existing conversation
            messages = await self.load_conversation_history()
            
            # Add new message
            messages.append(new_message)
            
            # Save updated conversation
            with open(self.conversation_file, 'w', encoding='utf-8') as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
            
            # Check if auto extraction should trigger
            should_extract = await self.should_auto_extract()
            
            result = {
                "success": True,
                "message": "Conversation updated",
                "total_messages": len(messages),
                "auto_extract_triggered": False
            }
            
            # Trigger auto extraction if threshold met
            if should_extract:
                self.start_background_extraction()
                self._last_processed_count = len(messages)
                result["auto_extract_triggered"] = True
                result["message"] = "Conversation updated and auto extraction triggered"
            
            return result
            
        except Exception as e:
            return {"success": False, "error": f"Failed to update conversation: {str(e)}"}
    
    def get_auto_extraction_settings(self) -> Dict:
        """Get current auto extraction settings.
        
        Returns:
            Dictionary with auto extraction configuration.
        """
        return {
            "auto_extraction_threshold": self._auto_extraction_threshold,
            "time_threshold_minutes": self._time_threshold_minutes,
            "last_processed_count": self._last_processed_count,
            "last_extraction_time": self._last_extraction_time.isoformat() if self._last_extraction_time else None,
            "enabled": True
        }
    
    def update_auto_extraction_threshold(self, threshold: int) -> Dict:
        """Update auto extraction message threshold.
        
        Args:
            threshold: New message threshold for auto extraction.
            
        Returns:
            Dictionary with update status.
        """
        if threshold < 1:
            return {"success": False, "error": "Threshold must be at least 1"}
        
        self._auto_extraction_threshold = threshold
        return {
            "success": True,
            "message": f"Auto extraction threshold updated to {threshold}",
            "new_threshold": threshold
        }
    
    async def has_important_content(self, message_text: str) -> bool:
        """Quick check if a message might contain important information.
        
        Args:
            message_text: The message text to analyze.
            
        Returns:
            True if message might contain important info, False otherwise.
        """
        if not message_text or len(message_text.strip()) < 20:
            return False
        
        # Keywords that suggest important memoir content
        important_keywords = [
            # Historical events
            "năm", "ngày", "tháng", "thời", "lúc đó", "khi", "hồi",
            # Family and relationships  
            "ông", "bà", "ba", "má", "anh", "chị", "em", "con", "cháu", "gia đình",
            # Places
            "làng", "thành phố", "tỉnh", "quê", "nhà",
            # Important life events
            "sinh", "cưới", "chết", "mất", "học", "làm việc", "nghề",
            # Emotions and memories
            "nhớ", "quên", "cảm xúc", "vui", "buồn", "khóc", "cười",
            # War and historical periods
            "chiến tranh", "kháng chiến", "giải phóng", "độc lập", "cách mạng"
        ]
        
        text_lower = message_text.lower()
        
        # Check for important keywords
        keyword_count = sum(1 for keyword in important_keywords if keyword in text_lower)
        
        # Check for specific patterns that suggest memoir content
        memoir_patterns = [
            "tôi nhớ", "hồi đó", "ngày xưa", "thời", "năm", "khi tôi",
            "ông bà", "ba má", "gia đình tôi", "quê tôi", "làng tôi"
        ]
        
        pattern_matches = sum(1 for pattern in memoir_patterns if pattern in text_lower)
        
        # If message has multiple keywords or memoir patterns, likely important
        return keyword_count >= 2 or pattern_matches >= 1
    
    async def smart_extraction_check(self, new_message: Dict) -> bool:
        """Smart check if extraction should be triggered based on message content.
        
        Args:
            new_message: The new message to analyze.
            
        Returns:
            True if extraction should be triggered, False otherwise.
        """
        try:
            message_text = new_message.get("text", "")
            
            # Only check user messages for important content
            if new_message.get("role") == "user":
                if await self.has_important_content(message_text):
                    return True
            
            # Also check normal thresholds
            return await self.should_auto_extract()
            
        except Exception as e:
            print(f"Error in smart extraction check: {e}")
            # Fallback to normal threshold check
            return await self.should_auto_extract() 