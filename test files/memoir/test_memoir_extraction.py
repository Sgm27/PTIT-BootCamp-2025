"""
Test Memoir Extraction Feature
Tests the complete memoir extraction workflow from conversation to database storage
"""
import asyncio
import logging
from datetime import datetime, date
from typing import List, Dict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import services
from db.db_services.user_service import UserService
from db.db_services.conversation_service import ConversationService
from db.db_services.memoir_service import MemoirDBService
from services.daily_memoir_extraction_service import DailyMemoirExtractionService
from db.models import UserType, ConversationRole

class MemoirExtractionTester:
    """Test class for memoir extraction functionality"""
    
    def __init__(self):
        self.user_service = UserService()
        self.conversation_service = ConversationService()
        self.memoir_service = MemoirDBService()
        self.daily_memoir_service = DailyMemoirExtractionService()
        
    async def test_create_user_if_not_exists(self) -> str:
        """Create test user if not exists, return user ID"""
        try:
            # Check if user exists
            existing_user = self.user_service.get_user_by_contact(email="son123@gmail.com")
            
            if existing_user:
                logger.info(f"User already exists: {existing_user.id}")
                return str(existing_user.id)
            
            # Create new user
            user = self.user_service.create_user(
                user_type=UserType.ELDERLY,
                full_name="Nguyễn Văn Sơn",
                email="son123@gmail.com",
                phone="0123456789",
                date_of_birth=date(1950, 5, 15),
                gender="male",
                    address="123 Đường ABC, Quận 1, TP.HCM"
            )
            
            if user:
                logger.info(f"Created new user: {user['id']}")
                return user['id']
            else:
                raise Exception("Failed to create user")
                
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    async def test_create_sample_conversation(self, user_id: str) -> str:
        """Create a sample conversation with meaningful content"""
        try:
            # Create conversation
            conversation_id = await self.conversation_service.create_conversation(
                user_id=user_id,
                title="Kỷ niệm về thời chiến tranh",
                session_id="test_session_001"
            )
            
            if not conversation_id:
                raise Exception("Failed to create conversation")
            
            logger.info(f"Created conversation: {conversation_id}")
            
            # Add sample messages
            sample_messages = [
                {
                    "role": ConversationRole.USER,
                    "content": "Chào cháu, hôm nay bác muốn kể cho cháu nghe về những kỷ niệm thời chiến tranh của bác.",
                    "has_audio": False
                },
                {
                    "role": ConversationRole.ASSISTANT,
                    "content": "Chào bác! Cháu rất muốn nghe bác kể về những kỷ niệm thời chiến tranh. Bác có thể kể cho cháu nghe về một kỷ niệm đáng nhớ nhất không?",
                    "has_audio": False
                },
                {
                    "role": ConversationRole.USER,
                    "content": "Tôi nhớ như in ngày 30 tháng 4 năm 1975. Lúc đó tôi đang ở làng quê, cả làng nổi lên trong niềm vui sướng khi nghe tin Sài Gòn được giải phóng. Những giọt nước mắt hạnh phúc chảy trên má già của ông Ba tôi - người cựu chiến binh đã trải qua bao năm tháng gian khổ.",
                    "has_audio": False
                },
                {
                    "role": ConversationRole.ASSISTANT,
                    "content": "Thật là một kỷ niệm đáng nhớ và ý nghĩa bác ạ! Cháu có thể cảm nhận được niềm vui và xúc động của bác và cả làng vào ngày lịch sử đó. Bác có thể kể thêm về ông Ba của bác không?",
                    "has_audio": False
                },
                {
                    "role": ConversationRole.USER,
                    "content": "Ông Ba tôi là một người rất dũng cảm. Ông đã tham gia kháng chiến từ những ngày đầu, trải qua bao nhiêu trận đánh ác liệt. Ông thường kể cho tôi nghe về những đêm hành quân trong rừng, về tình đồng đội keo sơn gắn bó. Ông nói rằng dù gian khổ đến đâu, họ vẫn giữ vững ý chí chiến đấu vì độc lập tự do của Tổ quốc.",
                    "has_audio": False
                },
                {
                    "role": ConversationRole.ASSISTANT,
                    "content": "Thật là những câu chuyện đầy cảm động và ý nghĩa bác ạ! Những kỷ niệm về ông Ba và thời kỳ kháng chiến chắc chắn sẽ là những bài học quý giá cho thế hệ trẻ. Bác có muốn kể thêm về những kỷ niệm khác không?",
                    "has_audio": False
                },
                {
                    "role": ConversationRole.USER,
                    "content": "Có, tôi còn nhớ rõ ngày tôi lấy vợ. Đó là năm 1976, sau khi đất nước thống nhất. Vợ tôi là con gái làng bên, chúng tôi quen nhau từ nhỏ. Ngày cưới, cả hai làng đều vui mừng, mọi người đến chúc phúc. Đó là một ngày đẹp trời, nắng vàng rực rỡ, hoa cau thơm ngát khắp làng.",
                    "has_audio": False
                }
            ]
            
            # Add messages to conversation
            for i, msg_data in enumerate(sample_messages):
                message = await self.conversation_service.add_message(
                    conversation_id=conversation_id,
                    role=msg_data["role"],
                    content=msg_data["content"],
                    has_audio=msg_data["has_audio"]
                )
                
                if message:
                    logger.info(f"Added message {i+1}: {msg_data['role'].value}")
                else:
                    logger.warning(f"Failed to add message {i+1}")
            
            # End conversation
            await self.conversation_service.end_conversation(
                conversation_id=conversation_id,
                summary="Kỷ niệm về thời chiến tranh và ngày cưới",
                topics=["chiến tranh", "gia đình", "lịch sử", "tình yêu"]
            )
            
            logger.info("Sample conversation created and ended successfully")
            return conversation_id
            
        except Exception as e:
            logger.error(f"Error creating sample conversation: {e}")
            raise
    
    async def test_memoir_extraction(self, user_id: str, conversation_id: str):
        """Test memoir extraction from conversation"""
        try:
            logger.info("Testing memoir extraction...")
            
            # Get conversation messages
            messages = await self.conversation_service.get_conversation_messages(conversation_id)
            
            if not messages:
                raise Exception("No messages found in conversation")
            
            logger.info(f"Found {len(messages)} messages in conversation")
            
            # Format conversation for analysis
            conversation_text = await self.daily_memoir_service.format_daily_conversations_for_analysis([
                {
                    'role': msg.role.value,
                    'text': msg.content,
                    'timestamp': msg.timestamp.isoformat()
                }
                for msg in messages
            ])
            
            logger.info("Formatted conversation for analysis")
            
            # Extract memoir
            memoir_content = await self.daily_memoir_service.extract_daily_memoir(
                user_id=user_id,
                conversation_text=conversation_text,
                target_date=date.today()
            )
            
            if memoir_content:
                logger.info("Memoir extracted successfully")
                logger.info(f"Memoir content: {memoir_content[:200]}...")
                
                # Save to database
                success = await self.daily_memoir_service.save_daily_memoir_to_database(
                    user_id=user_id,
                    memoir_content=memoir_content,
                    target_date=date.today()
                )
                
                if success:
                    logger.info("Memoir saved to database successfully")
                else:
                    logger.error("Failed to save memoir to database")
            else:
                logger.warning("No memoir content extracted")
                
        except Exception as e:
            logger.error(f"Error in memoir extraction: {e}")
            raise
    
    async def test_verify_memoir_in_database(self, user_id: str):
        """Verify memoir was saved in database"""
        try:
            logger.info("Verifying memoir in database...")
            
            # Get user memoirs
            memoirs = await self.memoir_service.get_user_memoirs(user_id, limit=10)
            
            if memoirs:
                logger.info(f"Found {len(memoirs)} memoirs for user")
                
                for memoir in memoirs:
                    logger.info(f"Memoir ID: {memoir['id']}")
                    logger.info(f"Title: {memoir['title']}")
                    logger.info(f"Content preview: {memoir['content'][:100] if memoir['content'] else ''}...")
                    logger.info(f"Categories: {memoir['categories']}")
                    logger.info(f"Extracted at: {memoir['extracted_at']}")
                    logger.info("---")
            else:
                logger.warning("No memoirs found in database")
                
        except Exception as e:
            logger.error(f"Error verifying memoir in database: {e}")
            raise
    
    async def run_all_tests(self):
        """Run all tests in sequence"""
        try:
            logger.info("Starting Memoir Extraction Tests...")
            
            # Test 1: Create user
            user_id = await self.test_create_user_if_not_exists()
            logger.info(f"✓ User test completed. User ID: {user_id}")
            
            # Test 2: Create sample conversation
            conversation_id = await self.test_create_sample_conversation(user_id)
            logger.info(f"✓ Conversation test completed. Conversation ID: {conversation_id}")
            
            # Test 3: Extract memoir
            await self.test_memoir_extraction(user_id, conversation_id)
            logger.info("✓ Memoir extraction test completed")
            
            # Test 4: Verify in database
            await self.test_verify_memoir_in_database(user_id)
            logger.info("✓ Database verification test completed")
            
            logger.info("🎉 All tests completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            raise

async def main():
    """Main test function"""
    tester = MemoirExtractionTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 