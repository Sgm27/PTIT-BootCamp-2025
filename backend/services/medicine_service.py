"""
Medicine scanning service using OpenAI's vision model
"""
import base64
import logging
from typing import Dict, Any
from openai import AsyncOpenAI
from config.settings import settings

# Set up logging
logger = logging.getLogger(__name__)


class MedicineService:
    """A service for scanning and identifying medicines from images using OpenAI's vision model."""
    
    SYSTEM_PROMPT = """
    Bạn là một chuyên gia dược sĩ có kinh nghiệm. Hãy phân tích hình ảnh thuốc này và cung cấp thông tin chi tiết về:
    
    1. Tên thuốc (tên gốc và tên thương mại)
    2. Thành phần hoạt chất chính
    3. Công dụng và chỉ định
    4. Liều lượng và cách sử dụng
    5. Tác dụng phụ thường gặp
    6. Lưu ý khi sử dụng
    7. Tương tác thuốc (nếu có)
    8. Đối tượng cần thận trọng
    
    QUAN TRỌNG: Bạn PHẢI LUÔN LUÔN trả lời bằng tiếng Việt, không được sử dụng tiếng Anh hoặc ngôn ngữ khác. 
    Hãy trả lời rõ ràng, dễ hiểu và phù hợp cho người cao tuổi Việt Nam.
    Nếu có thuật ngữ y tế, hãy giải thích bằng tiếng Việt đơn giản.
    """
    
    def __init__(self, client: AsyncOpenAI = None, model: str = None, temperature: float = 0.2):
        """Initialize medicine service.
        
        Args:
            client: OpenAI client instance. Creates new if None.
            model: Model to use for vision. Uses default from settings if None.
            temperature: Model temperature for responses.
        """
        self.client = client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = model or settings.OPENAI_VISION_MODEL
        self.temperature = temperature
    
    @staticmethod
    def encode_image(image_path: str) -> str:
        """Encodes an image file to a base64 string.
        
        Args:
            image_path: Path to the image file.
            
        Returns:
            Base64 encoded string of the image.
            
        Raises:
            FileNotFoundError: If image file doesn't exist.
            IOError: If error reading image file.
        """
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_string
        except FileNotFoundError:
            raise FileNotFoundError(f"Image file not found: {image_path}")
        except Exception as e:
            raise IOError(f"Error reading image file: {e}")
    
    async def _create_completion(self, content_list: list) -> Dict[str, Any]:
        """Create a completion request to OpenAI.
        
        Args:
            content_list: List of content items for the API request.
            
        Returns:
            Dictionary containing result, success status, and optional error.
        """
        try:
            logger.info(f"Calling OpenAI Vision API with model: {self.model}")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": content_list}
                ],
                temperature=self.temperature,
            )
            
            result = response.choices[0].message.content.strip()
            logger.info(f"OpenAI Vision API response received, length: {len(result)}")
            
            return {
                "result": result,
                "success": True
            }
        except Exception as e:
            logger.error(f"Error calling OpenAI Vision API: {e}")
            return {
                "result": f"Lỗi khi gọi API: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    async def scan_from_url(self, image_url: str) -> Dict[str, Any]:
        """Scan medicine from an image URL.
        
        Args:
            image_url: URL of the image to scan.
            
        Returns:
            Dictionary containing scan results.
        """
        if not image_url:
            return {
                "result": "URL hình ảnh không được cung cấp.",
                "success": False,
                "error": "Missing image URL"
            }
        
        content_list = [
            {
                "type": "image_url",
                "image_url": {"url": image_url}
            }
        ]
        
        return await self._create_completion(content_list)
    
    async def scan_from_base64(self, base64_string: str) -> Dict[str, Any]:
        """Scan medicine from a base64 encoded image string.
        
        Args:
            base64_string: Base64 encoded image data.
            
        Returns:
            Dictionary containing scan results.
        """
        if not base64_string:
            return {
                "result": "Chuỗi base64 không được cung cấp.",
                "success": False,
                "error": "Missing base64 string"
            }
        
        try:
            logger.info(f"Processing base64 image, length: {len(base64_string)}")
            
            # Clean the base64 string (remove data:image/jpeg;base64, prefix if present)
            if base64_string.startswith("data:image"):
                base64_string = base64_string.split(",")[1]
                logger.info("Removed data:image prefix from base64 string")
            
            # Validate base64 string
            try:
                decoded_data = base64.b64decode(base64_string)
                logger.info(f"Base64 validation successful, decoded size: {len(decoded_data)} bytes")
            except Exception as decode_error:
                logger.error(f"Base64 validation failed: {decode_error}")
                return {
                    "result": f"Chuỗi base64 không hợp lệ: {str(decode_error)}",
                    "success": False,
                    "error": f"Invalid base64: {str(decode_error)}"
                }
            
            content_list = [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_string}"
                    }
                }
            ]
            
            logger.info("Calling OpenAI Vision API for medicine analysis")
            return await self._create_completion(content_list)
        except Exception as e:
            return {
                "result": f"Lỗi xử lý chuỗi base64: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    async def scan_from_file_content(self, file_content: bytes) -> Dict[str, Any]:
        """Scan medicine from uploaded file content.
        
        Args:
            file_content: Raw file content bytes.
            
        Returns:
            Dictionary containing scan results.
        """
        try:
            # Encode to base64
            base64_string = base64.b64encode(file_content).decode("utf-8")
            return await self.scan_from_base64(base64_string)
        except Exception as e:
            return {
                "result": f"Lỗi xử lý file: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    async def scan_medicine(self, input_data: str) -> Dict[str, Any]:
        """Get medicine information from an image URL or base64 string.
        
        Args:
            input_data: Either image URL or base64 string.
            
        Returns:
            Dictionary containing scan results.
            
        Raises:
            ValueError: If input_data is empty.
        """
        if not input_data:
            raise ValueError("Input must be provided.")
        
        if input_data.startswith("http"):
            return await self.scan_from_url(input_data)
        else:
            return await self.scan_from_base64(input_data)
