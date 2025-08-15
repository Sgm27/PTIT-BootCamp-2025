#!/usr/bin/env python3
"""
Simple script to create test user and conversations using raw SQL
"""
import psycopg2
import uuid
from datetime import datetime, timedelta
from db.db_config import DB_CONFIG

def create_test_data():
    """Create test user and conversations using raw SQL"""
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Check if user exists
        cur.execute("SELECT id, full_name FROM users WHERE email = %s", ("sondaitai27@gmail.com",))
        user_result = cur.fetchone()
        
        if user_result:
            user_id = user_result[0]
            print(f"User already exists: {user_result[1]} (ID: {user_id})")
        else:
            # Create user with raw SQL using available enum value
            user_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO users (id, user_type, email, full_name, phone, is_active, preferred_language, country)
                VALUES (%s, 'family', %s, %s, %s, %s, %s, %s)
            """, (user_id, "sondaitai27@gmail.com", "Sơn Đại Tài", "0123456789", True, "vi", "Vietnam"))
            print(f"Created user: Sơn Đại Tài (ID: {user_id})")
        
        # Create sample conversations
        conversations_data = [
            {
                "title": "Tư vấn về thuốc huyết áp",
                "started_at": datetime.now() - timedelta(days=7),
                "ended_at": datetime.now() - timedelta(days=7, hours=-1),
                "summary": "Thảo luận về việc uống thuốc huyết áp đúng giờ và tác dụng phụ",
                "topics": ["thuốc huyết áp", "sức khỏe tim mạch", "tư vấn y tế"],
                "messages": [
                    {"role": "USER", "content": "Chào bác sĩ, tôi muốn hỏi về thuốc huyết áp"},
                    {"role": "ASSISTANT", "content": "Chào bác! Tôi rất sẵn lòng tư vấn về thuốc huyết áp. Bác đang dùng loại thuốc nào và có gặp vấn đề gì không ạ?"},
                    {"role": "USER", "content": "Tôi đang uống Amlodipine 5mg, nhưng có khi quên uống"},
                    {"role": "ASSISTANT", "content": "Amlodipine là thuốc rất tốt để kiểm soát huyết áp. Việc uống đúng giờ rất quan trọng. Bác nên đặt báo thức hoặc để thuốc ở nơi dễ nhìn thấy để nhớ uống nhé."},
                    {"role": "USER", "content": "Cảm ơn bác sĩ, tôi sẽ chú ý hơn"}
                ]
            },
            {
                "title": "Chia sẻ kỷ niệm thời trẻ",
                "started_at": datetime.now() - timedelta(days=5),
                "ended_at": datetime.now() - timedelta(days=5, hours=-2),
                "summary": "Kể về thời niên thiếu và những kỷ niệm đẹp với gia đình",
                "topics": ["kỷ niệm", "gia đình", "thời trẻ"],
                "messages": [
                    {"role": "USER", "content": "Hôm nay tôi nhớ lại thời còn trẻ"},
                    {"role": "ASSISTANT", "content": "Thật tuyệt vời! Bác có muốn chia sẻ những kỷ niệm đẹp thời trẻ không ạ? Tôi rất thích nghe những câu chuyện của bác."},
                    {"role": "USER", "content": "Ngày xưa tôi làm giáo viên, dạy học ở vùng quê"},
                    {"role": "ASSISTANT", "content": "Nghề giáo viên thật cao quý! Chắc bác có nhiều kỷ niệm đẹp với học trò. Bác có nhớ học sinh nào đặc biệt không ạ?"},
                    {"role": "USER", "content": "Có một em học sinh rất chăm chỉ, sau này thành bác sĩ"},
                    {"role": "ASSISTANT", "content": "Thật tự hào! Bác đã góp phần nuôi dưỡng một bác sĩ tương lai. Những kỷ niệm như vậy thật quý giá và đáng trân trọng."}
                ]
            },
            {
                "title": "Hỏi về chế độ ăn uống",
                "started_at": datetime.now() - timedelta(days=3),
                "ended_at": datetime.now() - timedelta(days=3, hours=-1),
                "summary": "Tư vấn về chế độ ăn uống phù hợp cho người cao tuổi",
                "topics": ["dinh dưỡng", "chế độ ăn", "sức khỏe"],
                "messages": [
                    {"role": "USER", "content": "Tôi muốn hỏi về chế độ ăn uống"},
                    {"role": "ASSISTANT", "content": "Dạ, tôi sẵn sàng tư vấn về dinh dưỡng cho bác. Bác có vấn đề gì về ăn uống cần quan tâm không ạ?"},
                    {"role": "USER", "content": "Tôi bị tiểu đường, nên ăn gì?"},
                    {"role": "ASSISTANT", "content": "Với tiểu đường, bác nên ăn nhiều rau xanh, hạn chế đường và tinh bột. Nên ăn ít nhiều bữa và kiểm soát lượng cơm. Bác có thể ăn cá, thịt nạc, trứng và các loại hạt."}
                ]
            },
            {
                "title": "Trò chuyện về thời tiết",
                "started_at": datetime.now() - timedelta(days=1),
                "ended_at": datetime.now() - timedelta(days=1, hours=-0.5),
                "summary": "Nói chuyện về thời tiết và ảnh hưởng đến sức khỏe",
                "topics": ["thời tiết", "sức khỏe", "chăm sóc"],
                "messages": [
                    {"role": "USER", "content": "Hôm nay trời lạnh quá"},
                    {"role": "ASSISTANT", "content": "Dạ, thời tiết lạnh bác cần giữ ấm cơ thể. Bác nhớ mặc đủ ấm và uống nước ấm nhé!"},
                    {"role": "USER", "content": "Tôi hay bị đau khớp khi trời lạnh"},
                    {"role": "ASSISTANT", "content": "Đau khớp khi trời lạnh là hiện tượng phổ biến ở người cao tuổi. Bác nên giữ ấm các khớp, có thể xoa bóp nhẹ nhàng và vận động nhẹ trong nhà."}
                ]
            }
        ]
        
        # Create conversations
        for conv_data in conversations_data:
            # Create conversation
            conv_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO conversations (id, user_id, title, started_at, ended_at, is_active, 
                                         total_messages, conversation_summary, topics_discussed)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                conv_id, user_id, conv_data["title"], conv_data["started_at"], 
                conv_data["ended_at"], False, len(conv_data["messages"]), 
                conv_data["summary"], conv_data["topics"]
            ))
            
            # Create messages
            for i, msg_data in enumerate(conv_data["messages"]):
                msg_id = str(uuid.uuid4())
                timestamp = conv_data["started_at"] + timedelta(minutes=i*5)
                cur.execute("""
                    INSERT INTO conversation_messages (id, conversation_id, role, content, 
                                                     timestamp, message_order, has_audio)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    msg_id, conv_id, msg_data["role"], msg_data["content"],
                    timestamp, i + 1, False
                ))
            
            print(f"Created conversation: {conv_data['title']} with {len(conv_data['messages'])} messages")
        
        conn.commit()
        print(f"\n✅ Successfully created test data for user: sondaitai27@gmail.com")
        print(f"Total conversations created: {len(conversations_data)}")
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_test_data() 