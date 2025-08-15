import base64
import asyncio
from typing import Optional, Dict, Any
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os


class MedicineScanner:
    """
    A class for scanning and identifying medicines from images using OpenAI's vision model.
    """
    
    DEFAULT_MODEL = "gpt-4.1"
    DEFAULT_TEMPERATURE = 0.2
    
    SYSTEM_PROMPT = """
    Bạn là một chuyên gia trong việc nhận diện và cung cấp thông tin về thuốc.
    Bạn sẽ nhận được một hình ảnh hoặc URL của một hình ảnh thuốc và trả về tên thuốc đó
    Không cần trả lời thêm bất kỳ thông tin nào khác ngoài tên thuốc.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL, temperature: float = DEFAULT_TEMPERATURE):
        """
        Initialize the MedicineScanner.
        
        Args:
            api_key: OpenAI API key. If None, will load from environment.
            model: OpenAI model to use for image analysis.
            temperature: Temperature setting for the model.
        """
        load_dotenv(override=True)
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.model = model
        self.temperature = temperature
        self.client = AsyncOpenAI(api_key=self.api_key)
    
    @staticmethod
    def encode_image(image_path: str) -> str:
        """
        Encodes an image file to a base64 string.
        
        Args:
            image_path: Path to the image file.
            
        Returns:
            Base64 encoded string of the image.
            
        Raises:
            FileNotFoundError: If the image file doesn't exist.
            IOError: If there's an error reading the file.
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
        """
        Create a completion request to OpenAI.
        
        Args:
            content_list: List of content items for the user message.
            
        Returns:
            Dictionary containing the result from OpenAI.
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {
                        "role": "user", 
                        "content": content_list
                    }
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
        """
        Scan medicine from an image URL.
        
        Args:
            image_url: URL of the image to scan.
            
        Returns:
            Dictionary containing the scan result.
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
                "image_url": {
                    "url": image_url
                }
            }
        ]
        
        return await self._create_completion(content_list)
    
    async def scan_from_file(self, image_path: str) -> Dict[str, Any]:
        """
        Scan medicine from a local image file.
        
        Args:
            image_path: Path to the local image file.
            
        Returns:
            Dictionary containing the scan result.
        """
        if not image_path:
            return {
                "result": "Đường dẫn hình ảnh không được cung cấp.",
                "success": False,
                "error": "Missing image path"
            }
        
        try:
            encoded_image = self.encode_image(image_path)
            content_list = [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encoded_image}"
                    }
                }
            ]
            
            return await self._create_completion(content_list)
        except (FileNotFoundError, IOError) as e:
            return {
                "result": f"Lỗi đọc file hình ảnh: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    async def scan_medicine(self, input: str) -> Dict[str, Any]:
        """
        Get medicine information from an image URL or base64 string.
        
        Args:
            input: Base64 string or URL to scan.
            
        Returns:
            Dictionary containing the scan result.
            
        Raises:
            ValueError: If input is not provided.
        """
        if not input:
            raise ValueError("Input must be provided.")
        
        # Tự động phát hiện loại input
        if input.startswith("http"):
            return await self.scan_from_url(input)
        else:
            # Treat as base64 string
            return await self.scan_from_base64(input)
    
    async def scan_from_base64(self, base64_string: str) -> Dict[str, Any]:
        """
        Scan medicine from a base64 encoded image string.
        
        Args:
            base64_string: Base64 encoded image string.
            
        Returns:
            Dictionary containing the scan result.
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


if __name__ == "__main__":
    # Example usage
    async def main():
        # Using the class directly
        scanner = MedicineScanner()
        
        # Input có thể là URL hoặc base64 string
        # input_value = "https://cdn.youmed.vn/tin-tuc/wp-content/uploads/2020/06/thuoc-panadol-extra-2-1024x569.jpg"
        
        # Để test với base64, cần encode file local trước
        image_path = "./12972.webp"
        try:
            base64_string = scanner.encode_image(image_path)
            input_value = base64_string
        except (FileNotFoundError, IOError) as e:
            print(f"Lỗi đọc file: {e}")
            return
        
        # Gọi hàm với input duy nhất (base64 string)
        result = await scanner.scan_medicine(input=input_value)
            
        print("Result:", result)
    
    asyncio.run(main())