"""
Medicine scanning service using OpenAI's vision model
"""
import base64
from typing import Dict, Any
from openai import AsyncOpenAI
from config.settings import settings


class MedicineService:
    """A service for scanning and identifying medicines from images using OpenAI's vision model."""
    
    SYSTEM_PROMPT = """
    Bạn là một chuyên gia trong việc nhận diện và cung cấp thông tin về thuốc.
    Bạn sẽ nhận được một hình ảnh hoặc URL của một hình ảnh thuốc và trả về tên thuốc đó
    Không cần trả lời thêm bất kỳ thông tin nào khác ngoài tên thuốc.
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
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": content_list}
                ],
                temperature=self.temperature,
            )
            
            return {
                "result": response.choices[0].message.content.strip(),
                "success": True
            }
        except Exception as e:
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
            content_list = [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_string}"
                    }
                }
            ]
            
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
