#!/usr/bin/env python3
"""
Script to add sample conversation data, memoir data, and notifications for user son123@gmail.com
User ID: dd8d892b-fa77-4a71-9520-71baf601c3ba
Password: 12345678
"""
import sys
import os
from datetime import datetime, timedelta
import uuid
import json

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.db_config import get_db
from db.models import (
    User, UserType, Conversation, ConversationMessage, ConversationRole,
    LifeMemoir, NotificationType
)

# User information
TARGET_EMAIL = "son123@gmail.com"
TARGET_USER_ID = "dd8d892b-fa77-4a71-9520-71baf601c3ba"
TARGET_PASSWORD = "12345678"

def verify_user_info():
    """Verify user exists with correct information"""
    with get_db() as session:
        try:
            user = session.query(User).filter(User.email == TARGET_EMAIL).first()
            
            if not user:
                print(f"❌ User with email {TARGET_EMAIL} not found!")
                return False
            
            if str(user.id) != TARGET_USER_ID:
                print(f"❌ User ID mismatch!")
                print(f"   Expected: {TARGET_USER_ID}")
                print(f"   Found: {user.id}")
                return False
            
            print(f"✅ User verified:")
            print(f"   Email: {user.email}")
            print(f"   ID: {user.id}")
            print(f"   Name: {user.full_name}")
            print(f"   Phone: {user.phone}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error verifying user: {e}")
            return False

def add_conversation_data():
    """Add sample conversation data"""
    
    with get_db() as session:
        try:
            user = session.query(User).filter(User.email == TARGET_EMAIL).first()
            
            conversations_data = [
                {
                    "title": "Chào hỏi và tư vấn sức khỏe",
                    "started_at": datetime.now() - timedelta(days=10),
                    "ended_at": datetime.now() - timedelta(days=10, hours=-1),
                    "summary": "Cuộc trò chuyện đầu tiên, chào hỏi và tư vấn về sức khỏe tổng quát",
                    "topics": ["chào hỏi", "sức khỏe", "tư vấn"],
                    "messages": [
                        {"role": "user", "content": "Alo, chào anh."},
                        {"role": "assistant", "content": "Chào bác ạ con là AI của Đức Sơn đây ạ rất vui được trò chuyện cùng bác ạ bác có khỏe không ạ"},
                        {"role": "user", "content": "ạ. Ừ bác vẫn khỏe."},
                        {"role": "assistant", "content": "Dạ vâng ạ con rất vui khi nghe bác nói bác khỏe ạ Bác ơi bác có câu hỏi gì về sức khỏe hay cần con hỗ trợ gì không ạ"},
                        {"role": "user", "content": "Mạ. Gia đình bác không hòa thuận lắm, con có cách nào để cho gia đình bác hòa thuận hơn được không?"},
                        {"role": "assistant", "content": "Dạ bác ơi con hiểu là bác đang lo lắng về chuyện gia đình không hòa thuận ạ Con xin chia sẻ một vài cách mà có thể giúp gia đình mình gắn kết hơn nha bác"}
                    ]
                },
                {
                    "title": "Tư vấn về thuốc và sức khỏe tim mạch",
                    "started_at": datetime.now() - timedelta(days=8),
                    "ended_at": datetime.now() - timedelta(days=8, hours=-1.5),
                    "summary": "Thảo luận về việc uống thuốc tim mạch và chế độ sinh hoạt",
                    "topics": ["thuốc tim mạch", "huyết áp", "chế độ ăn uống"],
                    "messages": [
                        {"role": "user", "content": "Con ơi, bác muốn hỏi về thuốc huyết áp"},
                        {"role": "assistant", "content": "Dạ bác, con sẵn sàng tư vấn về thuốc huyết áp ạ. Bác đang dùng loại thuốc nào và có gặp khó khăn gì không ạ?"},
                        {"role": "user", "content": "Bác đang uống thuốc Amlodipine, nhưng đôi khi quên"},
                        {"role": "assistant", "content": "Dạ bác, Amlodipine là thuốc rất tốt để kiểm soát huyết áp. Để không quên uống thuốc, bác có thể đặt báo thức hàng ngày hoặc để thuốc ở chỗ dễ thấy như bàn ăn ạ"},
                        {"role": "user", "content": "À được, con có thể nhắc bác uống thuốc được không?"},
                        {"role": "assistant", "content": "Dạ được ạ! Con có thể tạo lịch nhắc uống thuốc cho bác. Bác thường uống thuốc vào giờ nào ạ?"},
                        {"role": "user", "content": "Sáng 7 giờ và tối 7 giờ"},
                        {"role": "assistant", "content": "Dạ vâng ạ! Con sẽ nhắc bác uống thuốc vào 7 giờ sáng và 7 giờ tối hàng ngày. Bác nhớ uống đều đặn để kiểm soát huyết áp tốt nhất nhé ạ"}
                    ]
                },
                {
                    "title": "Chia sẻ kỷ niệm về nghề nghiệp",
                    "started_at": datetime.now() - timedelta(days=6),
                    "ended_at": datetime.now() - timedelta(days=6, hours=-2),
                    "summary": "Kể về thời gian làm việc và những kỷ niệm nghề nghiệp",
                    "topics": ["kỷ niệm", "nghề nghiệp", "thời trẻ"],
                    "messages": [
                        {"role": "user", "content": "Con ơi, hôm nay bác nhớ lại thời còn đi làm"},
                        {"role": "assistant", "content": "Dạ bác! Con rất thích nghe bác kể về thời gian đi làm ạ. Bác làm nghề gì vậy ạ?"},
                        {"role": "user", "content": "Bác làm kỹ sư ở nhà máy, làm việc 30 năm"},
                        {"role": "assistant", "content": "Wow! 30 năm làm kỹ sư thật tuyệt vời ạ! Chắc bác có nhiều kinh nghiệm và kỷ niệm đáng nhớ. Bác có nhớ dự án nào đặc biệt không ạ?"},
                        {"role": "user", "content": "Có, bác từng tham gia thiết kế một cây cầu lớn"},
                        {"role": "assistant", "content": "Thật tự hào! Thiết kế cây cầu là công việc rất quan trọng và có ý nghĩa. Cây cầu đó chắc giúp nhiều người đi lại thuận tiện. Bác cảm thấy thế nào khi thấy cây cầu mình thiết kế ạ?"},
                        {"role": "user", "content": "Bác rất tự hào, mỗi lần đi qua cầu là bác nhớ lại"},
                        {"role": "assistant", "content": "Dạ vâng ạ! Đó là niềm tự hào xứng đáng của bác. Những công trình như vậy sẽ tồn tại mãi và là minh chứng cho sự cống hiến của bác ạ"}
                    ]
                },
                {
                    "title": "Hỏi về chế độ ăn uống và vận động",
                    "started_at": datetime.now() - timedelta(days=4),
                    "ended_at": datetime.now() - timedelta(days=4, hours=-1),
                    "summary": "Tư vấn về dinh dưỡng và tập thể dục phù hợp với tuổi tác",
                    "topics": ["dinh dưỡng", "vận động", "sức khỏe"],
                    "messages": [
                        {"role": "user", "content": "Con ơi, bác muốn hỏi về chế độ ăn uống"},
                        {"role": "assistant", "content": "Dạ bác! Con sẵn sàng tư vấn về dinh dưỡng cho bác ạ. Bác có vấn đề gì cần lưu ý không ạ?"},
                        {"role": "user", "content": "Bác có tiểu đường nhẹ, nên ăn thế nào?"},
                        {"role": "assistant", "content": "Dạ với tiểu đường, bác nên ăn nhiều rau xanh, hạn chế đường và tinh bột. Nên ăn ít nhiều bữa trong ngày. Bác có thể ăn cá, thịt nạc, trứng và các loại hạt ạ"},
                        {"role": "user", "content": "Còn về tập thể dục thì sao con?"},
                        {"role": "assistant", "content": "Dạ bác! Với tuổi của bác, nên tập nhẹ nhàng như đi bộ 30 phút mỗi ngày, tập thái cực quyền hoặc yoga nhẹ. Bác có thể tập vào buổi sáng sớm khi trời mát ạ"},
                        {"role": "user", "content": "Bác thích đi bộ trong công viên"},
                        {"role": "assistant", "content": "Tuyệt vời ạ! Đi bộ trong công viên rất tốt, vừa tập thể dục vừa hít thở không khí trong lành. Bác nhớ mang nước và đi bộ đều đặn nhé ạ"}
                    ]
                },
                {
                    "title": "Trò chuyện về gia đình và con cháu",
                    "started_at": datetime.now() - timedelta(days=2),
                    "ended_at": datetime.now() - timedelta(days=2, hours=-1.5),
                    "summary": "Chia sẻ về gia đình, con cháu và những mối quan tâm",
                    "topics": ["gia đình", "con cháu", "tình cảm"],
                    "messages": [
                        {"role": "user", "content": "Con ơi, bác muốn kể về gia đình"},
                        {"role": "assistant", "content": "Dạ bác! Con rất thích nghe bác kể về gia đình ạ. Bác có bao nhiêu con và cháu vậy ạ?"},
                        {"role": "user", "content": "Bác có 2 con, con trai và con gái, và 3 cháu"},
                        {"role": "assistant", "content": "Thật hạnh phúc ạ! Gia đình bác đông đủ. Các con bác hiện tại làm nghề gì vậy ạ?"},
                        {"role": "user", "content": "Con trai làm bác sĩ, con gái làm giáo viên"},
                        {"role": "assistant", "content": "Wow! Hai nghề rất cao quý ạ! Chắc bác rất tự hào về các con. Các cháu của bác học giỏi không ạ?"},
                        {"role": "user", "content": "Các cháu đều học giỏi, cháu lớn nhất chuẩn bị thi đại học"},
                        {"role": "assistant", "content": "Dạ tuyệt vời ạ! Cháu thi đại học là việc lớn. Bác có lo lắng gì về cháu không ạ? Con có thể tư vấn cách động viên cháu ạ"},
                        {"role": "user", "content": "Bác muốn cháu bớt căng thẳng trong học tập"},
                        {"role": "assistant", "content": "Dạ vâng ạ! Bác có thể nói chuyện với cháu, khuyến khích cháu thư giãn bằng cách nghe nhạc, đọc sách hay tập thể dục. Quan trọng là cháu biết bác luôn yêu thương và ủng hộ cháu ạ"}
                    ]
                },
                {
                    "title": "Hỏi về thời tiết và sức khỏe",
                    "started_at": datetime.now() - timedelta(hours=12),
                    "ended_at": datetime.now() - timedelta(hours=11),
                    "summary": "Trò chuyện về thời tiết và ảnh hưởng đến sức khỏe",
                    "topics": ["thời tiết", "sức khỏe", "chăm sóc"],
                    "messages": [
                        {"role": "user", "content": "Con ơi, hôm nay trời nóng quá"},
                        {"role": "assistant", "content": "Dạ bác! Thời tiết nóng bác cần chú ý giữ mát cơ thể ạ. Bác nhớ uống nhiều nước, ở trong bóng mát và hạn chế ra ngoài vào giữa trưa nhé ạ"},
                        {"role": "user", "content": "Bác có nên bật điều hòa không?"},
                        {"role": "assistant", "content": "Dạ có ạ! Bác có thể bật điều hòa ở nhiệt độ 26-28 độ C, không quá lạnh. Nhớ uống nước thường xuyên và mặc quần áo thoáng mát ạ"},
                        {"role": "user", "content": "Cảm ơn con, bác sẽ chú ý"},
                        {"role": "assistant", "content": "Dạ không có gì ạ! Bác nhớ chăm sóc sức khỏe trong thời tiết nóng này. Nếu bác cảm thấy choáng váng hay mệt mỏi thì nghỉ ngơi ngay nhé ạ"}
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
                    # Convert string role to enum value
                    role_value = ConversationRole.USER.value if msg_data["role"] == "user" else ConversationRole.ASSISTANT.value
                    
                    message = ConversationMessage(
                        conversation_id=conversation.id,
                        role=role_value,
                        content=msg_data["content"],
                        message_order=i + 1,
                        timestamp=conv_data["started_at"] + timedelta(minutes=i*5)
                    )
                    session.add(message)
                
                session.commit()
                print(f"✅ Created conversation: {conv_data['title']} with {len(conv_data['messages'])} messages")
            
            print(f"\n✅ Successfully added {len(conversations_data)} conversations")
            
        except Exception as e:
            print(f"❌ Error adding conversation data: {e}")
            raise

def add_memoir_data():
    """Add sample memoir data"""
    
    with get_db() as session:
        try:
            user = session.query(User).filter(User.email == TARGET_EMAIL).first()
            
            memoirs_data = [
                {
                    "title": "Kỷ niệm thời đi học",
                    "content": "Hồi đó tôi học ở trường kỹ thuật. Thời gian đó tuy khó khăn nhưng rất vui. Tôi nhớ nhất là các buổi thực hành ở xưởng máy. Thầy giáo rất nghiêm khắc nhưng dạy rất tận tâm. Bạn bè trong lớp cũng rất thân thiết, ai cũng giúp đỡ nhau trong học tập.",
                    "categories": ["education", "youth", "friendship"],
                    "people_mentioned": ["teachers", "classmates"],
                    "places_mentioned": ["technical school", "workshop"],
                    "time_period": "1970s",
                    "emotional_tone": "nostalgic",
                    "importance_score": 0.8,
                    "date_of_memory": datetime.now() - timedelta(days=365*50)  # ~50 years ago
                },
                {
                    "title": "Ngày cưới của tôi",
                    "content": "Ngày cưới của tôi diễn ra vào mùa xuân năm 1985. Thời tiết rất đẹp, hoa đào nở rộ. Vợ tôi mặc áo dài trắng rất xinh đẹp. Gia đình hai bên đều rất vui mừng. Tiệc cưới tuy đơn sơ nhưng ấm cúng. Tôi nhớ mãi khoảnh khắc chúng tôi thề nguyện bên nhau.",
                    "categories": ["family", "love", "celebration"],
                    "people_mentioned": ["wife", "family members"],
                    "places_mentioned": ["wedding venue"],
                    "time_period": "1980s",
                    "emotional_tone": "joyful",
                    "importance_score": 0.9,
                    "date_of_memory": datetime(1985, 3, 15)
                },
                {
                    "title": "Công việc đầu tiên",
                    "content": "Sau khi tốt nghiệp, tôi xin việc ở một nhà máy cơ khí. Ngày đầu tiên đi làm tôi rất lo lắng và hồi hộp. Sếp và đồng nghiệp đều rất tốt bụng, họ hướng dẫn tôi rất nhiệt tình. Dù công việc ban đầu khó khăn nhưng tôi học hỏi được rất nhiều.",
                    "categories": ["work", "career", "learning"],
                    "people_mentioned": ["boss", "colleagues"],
                    "places_mentioned": ["mechanical factory"],
                    "time_period": "1970s",
                    "emotional_tone": "motivated",
                    "importance_score": 0.7,
                    "date_of_memory": datetime.now() - timedelta(days=365*48)
                },
                {
                    "title": "Sinh con đầu lòng",
                    "content": "Con trai đầu lòng của tôi sinh vào một đêm mưa bão. Tôi đưa vợ vào bệnh viện trong cơn lo lắng. Khi nghe tiếng khóc đầu tiên của con, tôi không kìm được nước mắt. Bé trai nhỏ bé nhưng rất khỏe mạnh. Đó là một trong những khoảnh khắc hạnh phúc nhất của cuộc đời tôi.",
                    "categories": ["family", "children", "happiness"],
                    "people_mentioned": ["wife", "first son"],
                    "places_mentioned": ["hospital"],
                    "time_period": "1980s",
                    "emotional_tone": "joyful",
                    "importance_score": 0.95,
                    "date_of_memory": datetime(1987, 8, 20)
                },
                {
                    "title": "Dự án thiết kế cây cầu",
                    "content": "Dự án lớn nhất trong sự nghiệp của tôi là thiết kế cây cầu bắc qua sông Hồng. Đó là một thử thách lớn, tôi phải làm việc ngày đêm trong nhiều tháng. Cả team đều rất nỗ lực. Khi cây cầu hoàn thành và đưa vào sử dụng, tôi cảm thấy rất tự hào về công trình mình đã góp phần xây dựng.",
                    "categories": ["work", "achievement", "engineering"],
                    "people_mentioned": ["team members"],
                    "places_mentioned": ["Red River", "bridge"],
                    "time_period": "1990s",
                    "emotional_tone": "proud",
                    "importance_score": 0.9,
                    "date_of_memory": datetime(1995, 6, 10)
                },
                {
                    "title": "Nghỉ hưu và thời gian rảnh rỗi",
                    "content": "Khi nghỉ hưu, ban đầu tôi cảm thấy hơi bối rối vì không biết làm gì với thời gian rảnh. Nhưng sau đó tôi bắt đầu tập thể dục, đọc sách và học cách nấu ăn. Tôi cũng có thời gian chăm sóc cháu nhỏ và trò chuyện với vợ nhiều hơn.",
                    "categories": ["retirement", "family", "hobbies"],
                    "people_mentioned": ["wife", "grandchildren"],
                    "places_mentioned": ["home"],
                    "time_period": "2010s",
                    "emotional_tone": "peaceful",
                    "importance_score": 0.6,
                    "date_of_memory": datetime(2015, 1, 1)
                },
                {
                    "title": "Chuyến du lịch Đà Lạt cùng gia đình",
                    "content": "Năm ngoái cả gia đình tôi đi du lịch Đà Lạt. Thời tiết mát mẻ, cảnh đẹp như tranh vẽ. Các cháu rất thích chụp ảnh ở vườn hoa. Chúng tôi cùng nhau đi thuyền trên hồ, thưởng thức đặc sản địa phương. Đó là một chuyến đi đáng nhớ với nhiều tiếng cười.",
                    "categories": ["family", "travel", "happiness"],
                    "people_mentioned": ["children", "grandchildren"],
                    "places_mentioned": ["Da Lat", "flower garden", "lake"],
                    "time_period": "2020s",
                    "emotional_tone": "joyful",
                    "importance_score": 0.8,
                    "date_of_memory": datetime(2024, 4, 15)
                }
            ]
            
            # Add memoirs
            for memoir_data in memoirs_data:
                memoir = LifeMemoir(
                    user_id=user.id,
                    title=memoir_data["title"],
                    content=memoir_data["content"],
                    categories=memoir_data["categories"],
                    people_mentioned=memoir_data["people_mentioned"],
                    places_mentioned=memoir_data["places_mentioned"],
                    time_period=memoir_data["time_period"],
                    emotional_tone=memoir_data["emotional_tone"],
                    importance_score=memoir_data["importance_score"],
                    date_of_memory=memoir_data["date_of_memory"],
                    extracted_at=datetime.now()
                )
                session.add(memoir)
                session.commit()
                print(f"✅ Created memoir: {memoir_data['title']}")
            
            print(f"\n✅ Successfully added {len(memoirs_data)} memoirs")
            
        except Exception as e:
            print(f"❌ Error adding memoir data: {e}")
            raise

def add_notification_schedules():
    """Add sample notification schedules"""
    
    # Import here to avoid circular imports
    import asyncio
    from db.db_services.notification_service import NotificationDBService
    
    async def create_notifications():
        try:
            notification_service = NotificationDBService()
            
            # Sample notifications for the next few days
            notifications_data = [
                {
                    "title": "Nhắc uống thuốc huyết áp sáng",
                    "message": "Bác ơi, đến giờ uống thuốc Amlodipine rồi ạ. Nhớ uống cùng với nước ấm nhé!",
                    "notification_type": "medicine_reminder",
                    "scheduled_at": datetime.now() + timedelta(hours=1),
                    "category": "medicine",
                    "priority": "high"
                },
                {
                    "title": "Nhắc đi khám định kỳ",
                    "message": "Bác nhớ lịch khám tim mạch định kỳ vào thứ 3 tuần sau nhé. Đừng quên mang theo sổ khám bệnh!",
                    "notification_type": "appointment_reminder",
                    "scheduled_at": datetime.now() + timedelta(days=2),
                    "category": "health",
                    "priority": "normal"
                },
                {
                    "title": "Nhắc uống thuốc huyết áp tối",
                    "message": "Bác ơi, đến giờ uống thuốc tối rồi ạ. Nhớ uống đúng liều lượng nhé!",
                    "notification_type": "medicine_reminder",
                    "scheduled_at": datetime.now() + timedelta(hours=13),
                    "category": "medicine",
                    "priority": "high"
                },
                {
                    "title": "Nhắc tập thể dục",
                    "message": "Bác ơi, thời tiết hôm nay đẹp, bác ra công viên đi bộ 30 phút nhé! Nhớ mang theo nước uống.",
                    "notification_type": "health_reminder",
                    "scheduled_at": datetime.now() + timedelta(hours=16),
                    "category": "exercise",
                    "priority": "normal"
                },
                {
                    "title": "Kiểm tra huyết áp",
                    "message": "Bác nhớ đo huyết áp và ghi chép vào sổ theo dõi nhé. Nếu có bất thường thì liên hệ bác sĩ ngay.",
                    "notification_type": "health_check",
                    "scheduled_at": datetime.now() + timedelta(days=1, hours=8),
                    "category": "health",
                    "priority": "normal"
                },
                {
                    "title": "Gọi điện cho con trai",
                    "message": "Bác nhớ gọi điện hỏi thăm con trai nhé. Con chắc rất nhớ và muốn nghe giọng bác đấy!",
                    "notification_type": "family_reminder",
                    "scheduled_at": datetime.now() + timedelta(days=1, hours=19),
                    "category": "family",
                    "priority": "low"
                },
                {
                    "title": "Uống nước đủ 2 lít",
                    "message": "Bác nhớ uống đủ nước trong ngày nhé! Đặc biệt là thời tiết nóng như vậy, cơ thể cần nhiều nước hơn.",
                    "notification_type": "health_reminder",
                    "scheduled_at": datetime.now() + timedelta(days=1, hours=14),
                    "category": "health",
                    "priority": "normal"
                },
                {
                    "title": "Thời gian nghỉ ngơi",
                    "message": "Bác nên nghỉ ngơi và thư giãn một chút. Có thể nghe nhạc nhẹ hoặc đọc báo để tinh thần thoải mái.",
                    "notification_type": "wellness_reminder",
                    "scheduled_at": datetime.now() + timedelta(days=2, hours=15),
                    "category": "wellness",
                    "priority": "low"
                }
            ]
            
            # Create notifications
            for notif_data in notifications_data:
                notification = await notification_service.create_notification(
                    user_id=TARGET_USER_ID,
                    notification_type=notif_data["notification_type"],
                    title=notif_data["title"],
                    message=notif_data["message"],
                    scheduled_at=notif_data["scheduled_at"],
                    priority=notif_data["priority"],
                    category=notif_data["category"],
                    has_voice=True
                )
                
                if notification:
                    print(f"✅ Created notification: {notif_data['title']}")
                else:
                    print(f"❌ Failed to create notification: {notif_data['title']}")
            
            print(f"\n✅ Successfully added {len(notifications_data)} notifications")
            
        except Exception as e:
            print(f"❌ Error adding notification data: {e}")
            raise
    
    # Run async function
    asyncio.run(create_notifications())

def main():
    """Main function to add all sample data"""
    
    print("=== Adding Sample Data for son123@gmail.com ===")
    print(f"User ID: {TARGET_USER_ID}")
    print(f"Email: {TARGET_EMAIL}")
    print("=" * 50)
    
    # Step 1: Verify user info
    print("\n1. Verifying user information...")
    if not verify_user_info():
        print("❌ User verification failed. Please check user information.")
        return False
    
    # Step 2: Add conversation data
    print("\n2. Adding conversation history...")
    try:
        add_conversation_data()
    except Exception as e:
        print(f"❌ Failed to add conversation data: {e}")
        return False
    
    # Step 3: Add memoir data
    print("\n3. Adding memoir data...")
    try:
        add_memoir_data()
    except Exception as e:
        print(f"❌ Failed to add memoir data: {e}")
        return False
    
    # Step 4: Add notification schedules
    print("\n4. Adding notification schedules...")
    try:
        add_notification_schedules()
    except Exception as e:
        print(f"❌ Failed to add notification data: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Successfully added all sample data!")
    print("✅ Conversation history: Added multiple conversations")
    print("✅ Memoir data: Added life stories and family memories")
    print("✅ Notifications: Added medicine reminders and health notifications")
    print("\nUser son123@gmail.com now has comprehensive sample data for testing.")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Sample data creation failed.")
        exit(1)
    else:
        print("\n🎉 Sample data creation completed successfully!")
