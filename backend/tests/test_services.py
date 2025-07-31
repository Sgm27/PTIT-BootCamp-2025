"""
Test examples for the restructured services
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, Mock
from openai import AsyncOpenAI

# Test for Medicine Service
async def test_medicine_service():
    """Example test for medicine service."""
    from services.medicine_service import MedicineService
    
    # Mock OpenAI client
    mock_client = AsyncMock(spec=AsyncOpenAI)
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Panadol"
    
    mock_client.chat.completions.create.return_value = mock_response
    
    # Create service with mock client
    service = MedicineService(client=mock_client)
    
    # Test URL scanning
    result = await service.scan_from_url("https://example.com/medicine.jpg")
    
    assert result["success"] == True
    assert "Panadol" in result["result"]
    
    print("✅ Medicine service test passed")


# Test for Text Extraction Service
async def test_text_extraction_service():
    """Example test for text extraction service."""
    from services.text_extraction_service import TextExtractionService
    
    # Mock OpenAI client
    mock_client = AsyncMock(spec=AsyncOpenAI)
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Extracted information about health consultation"
    
    mock_client.chat.completions.create.return_value = mock_response
    
    # Create service with mock client
    service = TextExtractionService(client=mock_client)
    
    # Test text extraction
    test_text = "User talked about taking medicine and feeling better"
    result = await service.extract_info_for_memoir(test_text)
    
    assert "health consultation" in result
    
    print("✅ Text extraction service test passed")


# Test for Session Service
def test_session_service():
    """Example test for session service."""
    from services.session_service import SessionService
    import tempfile
    import os
    
    # Create temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        # Create service with temporary file
        service = SessionService(session_file=temp_file)
        
        # Test saving session
        test_handle = "test_session_123"
        service.save_previous_session_handle(test_handle)
        
        # Test loading session (should be valid since just created)
        loaded_handle = service.load_previous_session_handle()
        
        assert loaded_handle == test_handle
        
        print("✅ Session service test passed")
        
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.unlink(temp_file)


if __name__ == "__main__":
    # Run tests
    print("Running service tests...")
    
    # Test session service (synchronous)
    test_session_service()
    
    # Test async services
    async def run_async_tests():
        await test_medicine_service()
        await test_text_extraction_service()
    
    asyncio.run(run_async_tests())
    
    print("🎉 All tests completed!")
