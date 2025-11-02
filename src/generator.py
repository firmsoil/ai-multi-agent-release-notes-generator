import aiohttp

# FIXED: Absolute imports instead of relative
from llm_client import LLMClient
from github_client import GitHubClient
from confluence_formatter import ConfluenceFormatter


async def generate_release_notes(
    repo: str, 
    from_tag: str, 
    to_tag: str, 
    github_token: str, 
    llm_provider: str, 
    openai_key: str | None, 
    anthropic_key: str | None,
    gemini_key: str | None,
    output_format: str = 'markdown'
) -> str:
    """
    Generate release notes from commits between two tags for a given repository.

    Args:
        repo: GitHub repository in the format 'owner/repo'
        from_tag: Starting tag
        to_tag: Ending tag
        github_token: GitHub personal access token
        llm_provider: LLM provider ('openai', 'anthropic', or 'google')
        openai_key: OpenAI API key
        anthropic_key: Anthropic API key
        gemini_key: Google Gemini API key
        output_format: Output format ('markdown' or 'confluence')

    Returns:
        Formatted release notes as a string
    """
    gh_client = GitHubClient(github_token)
    llm_client = LLMClient.create(
        provider=llm_provider, 
        openai_key=openai_key, 
        anthropic_key=anthropic_key,
        gemini_key=gemini_key,
        output_format=output_format
    )
    
    # Fetch commits
    async with aiohttp.ClientSession() as session:
        commits = await gh_client.get_commits_between_tags(repo, from_tag, to_tag, session)
    
    # Convert Commit objects to dicts for LLM and formatter
    commit_dicts = [
        {
            'sha': c.sha,
            'message': c.message,
            'author_name': c.author_name,
            'author_email': c.author_email,
            'pr_number': c.pr_number,
            'pr_title': c.pr_title,
            'pr_url': c.pr_url
        }
        for c in commits
    ]
    
    # For Confluence format, use direct table generation
    if output_format == 'confluence':
        notes = ConfluenceFormatter.format_release_notes(
            commit_dicts, from_tag, to_tag, repo=repo, notes_content=None
        )
    else:
        # For Markdown, use LLM to generate notes
        notes = await llm_client.generate_notes(commit_dicts)
    
    return notes
