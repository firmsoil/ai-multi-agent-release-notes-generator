from .github_client import GitHubClient
from .llm_client import LLMClient
import asyncio
import aiohttp
from typing import List
import structlog

logger = structlog.get_logger()

async def generate_release_notes(repo: str, from_tag: str, to_tag: str, github_token: str, openai_key: str) -> str:
    async with aiohttp.ClientSession() as session:
        gh_client = GitHubClient(github_token)
        commits = await gh_client.get_commits_between_tags(repo, from_tag, to_tag, session)
        
        llm_client = LLMClient(openai_key)
        notes = await llm_client.generate_notes([
            {
                "message": c.message,
                "pr_number": c.pr_number,
                "pr_title": c.pr_title,
                "pr_url": c.pr_url
            } for c in commits
        ])
        
        logger.info("Release notes generation complete", repo=repo)
        return notes
