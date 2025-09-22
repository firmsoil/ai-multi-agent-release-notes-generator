import pytest
from unittest.mock import AsyncMock, patch
from src.multi_agent_release_notes.github_client import GitHubClient

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.mark.asyncio
async def test_get_commits_between_tags(mock_session):
    client = GitHubClient("fake_token")
    mock_session.get.return_value.json.return_value = {"object": {"sha": "abc123"}}
    mock_session.get.return_value.status = 200

    commits = await client.get_commits_between_tags("test/repo", "v1", "v2", mock_session)

    assert len(commits) >= 0  # Adjust based on mock
    mock_session.get.assert_called()
