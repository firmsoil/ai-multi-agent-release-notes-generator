from .llm_client import LLMClient
from .github_client import GitHubClient

async def generate_release_notes(repo: str, from_tag: str, to_tag: str, github_token: str, llm_provider: str, openai_key: str | None, anthropic_key: str | None) -> str:
    """
    Generate release notes from commits between two tags for a given repository.

    Args:
        repo: GitHub repository in the format 'owner/repo'
        from_tag: Starting tag
        to_tag: Ending tag
        github_token: GitHub personal access token
        llm_provider: LLM provider ('openai' or 'anthropic')
        openai_key: OpenAI API key
        anthropic_key: Anthropic API key

    Returns:
        Formatted release notes as a string
    """
    gh_client = GitHubClient(github_token)
    llm_client = LLMClient.create(provider=llm_provider, openai_key=openai_key, anthropic_key=anthropic_key)
    
    # Fetch commits
    async with aiohttp.ClientSession() as session:
        commits = await gh_client.get_commits_between_tags(repo, from_tag, to_tag, session)
    
    # Generate notes using LLM
    notes = await llm_client.generate_notes(commits)
    return notes
