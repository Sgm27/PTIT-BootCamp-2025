from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

load_dotenv(override=True)

SYSTEM_PROMPT = """
Bạn là chuyên gia trong việc trích xuất thông tin từ văn bản. 
Nhiệm vụ của bạn là phân tích văn bản và trích xuất các thông tin quan trọng,
bao gồm các sự kiện, nhân vật, địa điểm và các chi tiết liên quan khác.
Hãy đảm bảo rằng thông tin được trích xuất rõ ràng và có cấu trúc
để dễ dàng sử dụng trong việc viết hồi ký.

Bạn được cung cấp một đoạn hội thoại với người dùng và AI
để trích xuất thông tin từ văn bản.
Hãy trả lời bằng cách cung cấp các thông tin đã được trích xuất.
Chỉ trả lời văn ban trích xuất, không cần giải thích hay bình luận thêm.
"""

async def extract_info_for_memoir(text: str) -> str:
    """
    Extracts information from the provided text for memoir purposes.
    
    Args:
        text (str): The input text from which to extract information.
    
    Returns:
        str: The extracted information.
    """
    openai = AsyncOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    response = await openai.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        temperature=0.7,
        seed=42,
    )
    
    return response.choices[0].message.content.strip() if response.choices else ""

if __name__ == "__main__":
    import asyncio
    sample_text = """
    User: Tôi nhớ như in ngày 30 tháng 4 năm 1975, khi nghe tin Sài Gòn được giải phóng, cả làng chúng tôi ở Hà Nam đều vui mừng khôn xiết.
    AI: Ông có thể kể thêm về cảm xúc và hoạt động của mọi người trong làng lúc đó không?
    User: Mọi người đều chạy ra đường, vỗ tay hò reo. Bà con mang cờ đỏ sao vàng ra vẫy, có người đánh trống, người khác thổi kèn. Ông Ba tôi, một cựu chiến binh, đã khóc nức nở vì xúc động.
    AI: Thật là cảm động! Ông có nhớ những chi tiết cụ thể nào khác về ngày lịch sử đó không?
    User: Tôi nhớ chiều hôm đó, cả làng tổ chức liên hoan ngay trên sân đình. Bà con mang thức ăn ra chia sẻ với nhau. Ông Ba kể lại những năm tháng kháng chiến gian khổ, từ ngày đánh Pháp đến chống Mỹ.
    AI: Ông Ba có kể gì về thời kỳ kháng chiến chống Mỹ không?
    User: Ông kể về những đêm oanh tạc ở Hà Nội, khi máy bay B-52 thả bom. Ông phải trú ẩn trong hầm, nhưng tinh thần luôn kiên cường. Ông nói rằng dù khó khăn đến mấy, nhân dân ta cũng quyết tâm chiến thắng giặc Mỹ xâm lược.
    """
    extracted_info = asyncio.run(extract_info_for_memoir(sample_text))
    print(extracted_info)