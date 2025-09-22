import pytest
from unittest.mock import AsyncMock, patch
from src.multi_agent_release_notes.llm_client import LLMClient

@pytest.mark.asyncio
async def test_generate_notes():
    with patch('openai.AsyncOpenAI') as mock_openai:
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock(message=AsyncMock(content="Sample notes"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        client = LLMClient("fake_key")
        notes = await client.generate_notes([{"message": "Test commit"}])

        assert "notes" in notes
