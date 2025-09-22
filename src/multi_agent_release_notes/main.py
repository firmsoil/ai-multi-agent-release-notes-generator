import asyncio
import click
import os
from dotenv import load_dotenv
from .generator import generate_release_notes
import structlog
from .github_client import GitHubClient, Commit  # Import Commit for type hint

load_dotenv()

logger = structlog.get_logger()

@click.command()
@click.option('--repo', required=True, help='GitHub repo (owner/repo)')
@click.option('--from-tag', required=True, help='From tag')
@click.option('--to-tag', required=True, help='To tag')
async def cli(repo: str, from_tag: str, to_tag: str):
    github_token = os.getenv('GITHUB_TOKEN')
    openai_key = os.getenv('OPENAI_API_KEY')
    if not github_token or not openai_key:
        click.echo("Error: Set GITHUB_TOKEN and OPENAI_API_KEY in .env")
        return

    try:
        # Fetch commits to log PR details
        async with aiohttp.ClientSession() as session:
            gh_client = GitHubClient(github_token)
            commits = await gh_client.get_commits_between_tags(repo, from_tag, to_tag, session)
            
            # Log commit and PR details
            logger.info("Commit and PR Summary", repo=repo)
            for commit in commits:
                pr_info = (
                    f"PR #{commit.pr_number} - {commit.pr_title} ({commit.pr_url})"
                    if commit.pr_number
                    else "No PR associated"
                )
                logger.info(
                    "Commit details",
                    sha=commit.sha[:7],  # Short SHA for readability
                    message=commit.message,
                    pr_info=pr_info
                )

        # Generate and save release notes
        notes = await generate_release_notes(repo, from_tag, to_tag, github_token, openai_key)
        with open('release_notes.txt', 'w') as f:
            f.write(notes)
        click.echo("Release notes saved to release_notes.txt")
    except Exception as e:
        logger.error("Failed to generate notes", error=str(e))
        click.echo(f"Error: {e}")

if __name__ == '__main__':
    asyncio.run(cli())
