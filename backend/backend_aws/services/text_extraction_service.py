"""
Text extraction service for memoir information
"""
from openai import AsyncOpenAI
from fastapi import HTTPException
from config.settings import settings


class TextExtractionService:
    """A service for extracting information from text for memoir purposes."""
    
    SYSTEM_PROMPT = """
    Bạn là chuyên gia trong việc trích xuất thông tin từ văn bản. 
    Nhiệm vụ của bạn là phân tích văn bản và trích xuất các thông tin quan trọng,
    bao gồm các sự kiện, nhân vật, địa điểm và các chi tiết liên quan khác.
    Hãy đảm bảo rằng thông tin được trích xuất rõ ràng và có cấu trúc
    để dễ dàng sử dụng trong việc viết hồi ký.

    Bạn được cung cấp một đoạn hội thoại với người dùng và AI
    để trích xuất thông tin từ văn bản.
    Hãy trả lời bằng cách cung cấp các thông tin đã được trích xuất.
    Chỉ trả lời văn bản trích xuất, không cần giải thích hay bình luận thêm.
    """
    
    def __init__(self, client: AsyncOpenAI = None, model: str = None, temperature: float = 0.7):
        """Initialize text extraction service.
        
        Args:
            client: OpenAI client instance. Creates new if None.
            model: Model to use for text processing. Uses default from settings if None.
            temperature: Model temperature for responses.
        """
        self.client = client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = model or settings.OPENAI_TEXT_MODEL
        self.temperature = temperature
    
    async def extract_info_for_memoir(self, text: str) -> str:
        """Extracts information from the provided text for memoir purposes.
        
        Args:
            text: Text to extract information from.
            
        Returns:
            Extracted information as a string.
            
        Raises:
            HTTPException: If API call fails.
        """
        if not text:
            raise ValueError("Text must be provided for extraction.")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": text}
                ],
                temperature=self.temperature,
                seed=42,
            )
            
            return response.choices[0].message.content.strip() if response.choices else ""
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error extracting text: {str(e)}")
    
    async def extract_structured_info(self, text: str, extraction_type: str = "memoir") -> dict:
        """Extract structured information from text.
        
        Args:
            text: Text to extract information from.
            extraction_type: Type of extraction to perform.
            
        Returns:
            Dictionary containing structured extracted information.
        """
        if not text:
            return {"error": "No text provided", "extracted_info": ""}
        
        try:
            extracted_text = await self.extract_info_for_memoir(text)
            return {
                "success": True,
                "extraction_type": extraction_type,
                "original_text_length": len(text),
                "extracted_info": extracted_text,
                "timestamp": None  # Could add timestamp if needed
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "extracted_info": ""
            }
