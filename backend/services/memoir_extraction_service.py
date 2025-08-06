"""
Memoir extraction service for important conversation history information
Simplified for one-time extraction on conversation end
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from openai import AsyncOpenAI
from fastapi import HTTPException
from config.settings import settings


class MemoirExtractionService:
    """Service for extracting important information from conversation history for memoir purposes.
    
    Features:
    - One-time extraction on conversation end
    - Daily memoir consolidation (one story per date)
    - Automatic story combination for same-day conversations
    """
    
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
        """Initialize memoir extraction service.
        
        Args:
            client: OpenAI client instance. Creates new if None.
            model: Model to use for text processing. Uses default from settings if None.
            temperature: Temperature for creative writing.
        """
        self.client = client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = model or settings.OPENAI_TEXT_MODEL
        self.temperature = temperature
        self.conversation_file = Path("conversation_history.json")
        self.memoir_file = Path("my_life_stories.txt")
        
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
                temperature=self.temperature,
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
        """Append memoir story to memoir file, grouping by date.
        
        Args:
            memoir_story: Written memoir story to save.
            
        Returns:
            True if successfully saved, False otherwise.
        """
        if not memoir_story or memoir_story.strip() == "":
            return False
        
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Read existing content if file exists
            existing_content = ""
            existing_stories = {}  # date -> story content
            
            if self.memoir_file.exists():
                with open(self.memoir_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse existing stories by date
                parts = content.split("--------------------------------------------------")
                for part in parts:
                    part = part.strip()
                    if part and "[" in part and "]" in part:
                        # Extract date from timestamp [YYYY-MM-DD HH:MM:SS]
                        start_bracket = part.find("[")
                        end_bracket = part.find("]")
                        if start_bracket != -1 and end_bracket != -1:
                            timestamp_str = part[start_bracket+1:end_bracket]
                            if len(timestamp_str) >= 10:  # At least YYYY-MM-DD
                                date_part = timestamp_str[:10]
                                story_content = part[end_bracket+1:].strip()
                                if story_content:
                                    existing_stories[date_part] = story_content
            
            # Check if we already have a story for today
            if today in existing_stories:
                # Combine existing story with new story using AI
                combined_story = await self.combine_stories_for_date(existing_stories[today], memoir_story)
                existing_stories[today] = combined_story
            else:
                # New story for today
                existing_stories[today] = memoir_story
            
            # Rebuild the entire file with consolidated stories
            with open(self.memoir_file, 'w', encoding='utf-8') as f:
                f.write("CÂU CHUYỆN HỒI KÝ\n")
                f.write("Những câu chuyện đời được viết lại từ trái tim\n\n")
                
                # Write stories sorted by date
                for date in sorted(existing_stories.keys()):
                    f.write(f"[{date}]\n\n")
                    f.write(f"{existing_stories[date]}\n\n")
                    f.write("-" * 50 + "\n\n")
            
            return True
            
        except Exception as e:
            print(f"Error saving memoir story: {e}")
            return False
    
    async def combine_stories_for_date(self, existing_story: str, new_story: str) -> str:
        """Combine existing memoir story with new story for the same date.
        
        Args:
            existing_story: The existing memoir story for the date.
            new_story: The new memoir story to combine.
            
        Returns:
            Combined memoir story.
        """
        try:
            combine_prompt = f"""
            Bạn là một nhà văn memoir chuyên nghiệp. Nhiệm vụ của bạn là gộp hai đoạn memoir về cùng một ngày thành một câu chuyện hoàn chỉnh, liền mạch.
            
            NGUYÊN TẮC GỘP:
            - Tạo ra MỘT đoạn văn duy nhất, liền mạch
            - Loại bỏ thông tin trùng lặp
            - Giữ nguyên phong cách memoir ngôi thứ nhất
            - Sắp xếp nội dung theo trình tự logic, cảm xúc
            - Đảm bảo câu chuyện có đầu, giữa, cuối tự nhiên
            - Không để lộ việc gộp từ hai đoạn riêng biệt
            
            ĐOẠN MEMOIR CŨ:
            {existing_story}
            
            ĐOẠN MEMOIR MỚI:
            {new_story}
            
            Hãy viết lại thành một câu chuyện memoir hoàn chỉnh, tự nhiên:
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": combine_prompt}
                ],
                temperature=0.5,  # Lower temperature for more consistent combining
                max_tokens=2000,  # More tokens for longer combined stories
            )
            
            combined_result = response.choices[0].message.content.strip() if response.choices else ""
            
            # Return combined story or fallback to new story if combination fails
            return combined_result if combined_result else new_story
            
        except Exception as e:
            print(f"Error combining stories: {e}")
            # Fallback: return new story if combination fails
            return new_story
    
    async def process_conversation_history_background(self) -> Dict:
        """Process conversation history to extract memoir information.
        
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
                return {
                    "success": True,
                    "message": "No memoir-worthy stories found in current conversation",
                    "conversation_length": len(messages)
                }
                
        except Exception as e:
            return {"success": False, "message": f"Error processing conversation: {str(e)}"} 