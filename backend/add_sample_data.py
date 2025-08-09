#!/usr/bin/env python3
"""
Script to add sample conversation data for testing
"""
import sys
import os
from datetime import datetime, timedelta
import uuid

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.db_config import get_db
from db.models import User, UserType, Conversation, ConversationMessage, ConversationRole

def add_sample_data():
    """Add sample conversation data for sondaitai27@gmail.com"""
    
    # Get database session
    with get_db() as session:
        try:
            # Check if user exists
            user = session.query(User).filter(User.email == "sondaitai27@gmail.com").first()
            
            if not user:
                # Create user if doesn't exist - using available enum value
                user = User(
                    user_type=UserType.FAMILY_MEMBER,  # Use FAMILY_MEMBER instead
                    email="sondaitai27@gmail.com",
                    full_name="Sơn Đại Tài",
                    phone="0123456789",
                    is_active=True,
                    preferred_language="vi"
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                print(f"Created user: {user.full_name} ({user.email})")
            else:
                print(f"User already exists: {user.full_name} ({user.email})")
            
            # Create sample conversations
            conversations_data = [
                {
                    "title": "Tư vấn về thuốc huyết áp",
                    "started_at": datetime.now() - timedelta(days=7),
                    "ended_at": datetime.now() - timedelta(days=7, hours=-1),
                    "summary": "Thảo luận về việc uống thuốc huyết áp đúng giờ và tác dụng phụ",
                    "topics": ["thuốc huyết áp", "sức khỏe tim mạch", "tư vấn y tế"],
                    "messages": [
                        {"role": "user", "content": "Chào bác sĩ, tôi muốn hỏi về thuốc huyết áp"},
                        {"role": "assistant", "content": "Chào bác! Tôi rất sẵn lòng tư vấn về thuốc huyết áp. Bác đang dùng loại thuốc nào và có gặp vấn đề gì không ạ?"},
                        {"role": "user", "content": "Tôi đang uống Amlodipine 5mg, nhưng có khi quên uống"},
                        {"role": "assistant", "content": "Amlodipine là thuốc rất tốt để kiểm soát huyết áp. Việc uống đúng giờ rất quan trọng. Bác nên đặt báo thức hoặc để thuốc ở nơi dễ nhìn thấy để nhớ uống nhé."},
                        {"role": "user", "content": "Cảm ơn bác sĩ, tôi sẽ chú ý hơn"}
                    ]
                },
                {
                    "title": "Chia sẻ kỷ niệm thời trẻ",
                    "started_at": datetime.now() - timedelta(days=5),
                    "ended_at": datetime.now() - timedelta(days=5, hours=-2),
                    "summary": "Kể về thời niên thiếu và những kỷ niệm đẹp với gia đình",
                    "topics": ["kỷ niệm", "gia đình", "thời trẻ"],
                    "messages": [
                        {"role": "user", "content": "Hôm nay tôi nhớ lại thời còn trẻ"},
                        {"role": "assistant", "content": "Thật tuyệt vời! Bác có muốn chia sẻ những kỷ niệm đẹp thời trẻ không ạ? Tôi rất thích nghe những câu chuyện của bác."},
                        {"role": "user", "content": "Ngày xưa tôi làm giáo viên, dạy học ở vùng quê"},
                        {"role": "assistant", "content": "Nghề giáo viên thật cao quý! Chắc bác có nhiều kỷ niệm đẹp với học trò. Bác có nhớ học sinh nào đặc biệt không ạ?"},
                        {"role": "user", "content": "Có một em học sinh rất chăm chỉ, sau này thành bác sĩ"},
                        {"role": "assistant", "content": "Thật tự hào! Bác đã góp phần nuôi dưỡng một bác sĩ tương lai. Những kỷ niệm như vậy thật quý giá và đáng trân trọng."}
                    ]
                },
                {
                    "title": "Hỏi về chế độ ăn uống",
                    "started_at": datetime.now() - timedelta(days=3),
                    "ended_at": datetime.now() - timedelta(days=3, hours=-1),
                    "summary": "Tư vấn về chế độ ăn uống phù hợp cho người cao tuổi",
                    "topics": ["dinh dưỡng", "chế độ ăn", "sức khỏe"],
                    "messages": [
                        {"role": "user", "content": "Tôi muốn hỏi về chế độ ăn uống"},
                        {"role": "assistant", "content": "Dạ, tôi sẵn sàng tư vấn về dinh dưỡng cho bác. Bác có vấn đề gì về ăn uống cần quan tâm không ạ?"},
                        {"role": "user", "content": "Tôi bị tiểu đường, nên ăn gì?"},
                        {"role": "assistant", "content": "Với tiểu đường, bác nên ăn nhiều rau xanh, hạn chế đường và tinh bột. Nên ăn ít nhiều bữa và kiểm soát lượng cơm. Bác có thể ăn cá, thịt nạc, trứng và các loại hạt."}
                    ]
                },
                {
                    "title": "Trò chuyện về thời tiết",
                    "started_at": datetime.now() - timedelta(days=1),
                    "ended_at": datetime.now() - timedelta(days=1, hours=-0.5),
                    "summary": "Nói chuyện về thời tiết và ảnh hưởng đến sức khỏe",
                    "topics": ["thời tiết", "sức khỏe", "chăm sóc"],
                    "messages": [
                        {"role": "user", "content": "Hôm nay trời lạnh quá"},
                        {"role": "assistant", "content": "Dạ, thời tiết lạnh bác cần giữ ấm cơ thể. Bác nhớ mặc đủ ấm và uống nước ấm nhé!"},
                        {"role": "user", "content": "Tôi hay bị đau khớp khi trời lạnh"},
                        {"role": "assistant", "content": "Đau khớp khi trời lạnh là hiện tượng phổ biến ở người cao tuổi. Bác nên giữ ấm các khớp, có thể xoa bóp nhẹ nhàng và vận động nhẹ trong nhà."}
                    ]
                }
            ]
            
            # Add conversations
            for conv_data in conversations_data:
                # Create conversation
                conversation = Conversation(
                    user_id=user.id,
                    title=conv_data["title"],
                    started_at=conv_data["started_at"],
                    ended_at=conv_data["ended_at"],
                    is_active=False,
                    total_messages=len(conv_data["messages"]),
                    conversation_summary=conv_data["summary"],
                    topics_discussed=conv_data["topics"]
                )
                session.add(conversation)
                session.commit()
                session.refresh(conversation)
                
                # Add messages
                for i, msg_data in enumerate(conv_data["messages"]):
                    # Convert string role to enum
                    role_enum = ConversationRole.USER if msg_data["role"] == "user" else ConversationRole.ASSISTANT
                    
                    message = ConversationMessage(
                        conversation_id=conversation.id,
                        role=role_enum,
                        content=msg_data["content"],
                        message_order=i + 1,
                        timestamp=conv_data["started_at"] + timedelta(minutes=i*5)
                    )
                    session.add(message)
                
                session.commit()
                print(f"Created conversation: {conv_data['title']} with {len(conv_data['messages'])} messages")
            
            print(f"\n✅ Successfully added sample data for user: {user.email}")
            print(f"Total conversations created: {len(conversations_data)}")
            
        except Exception as e:
            print(f"❌ Error adding sample data: {e}")
            raise

if __name__ == "__main__":
    add_sample_data() 