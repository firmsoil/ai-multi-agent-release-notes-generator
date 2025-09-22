import asyncio
import click
import os
from dotenv import load_dotenv
from .generator import generate_release_notes
import structlog
from .github_client import GitHubClient, Commit
import aiohttp

load_dotenv()

logger = structlog.get_logger()

@click.command()
@click.option('--repo', required=True, help='GitHub repo (owner/repo) or "local" for sample data')
@click.option('--from-tag', required=True, help='From tag')
@click.option('--to-tag', required=True, help='To tag')
async def cli(repo: str, from_tag: str, to_tag: str):
    github_token = os.getenv('GITHUB_TOKEN')
    openai_key = os.getenv('OPENAI_API_KEY')
    if not github_token or not openai_key:
        click.echo("Error: Set GITHUB_TOKEN and OPENAI_API_KEY in .env")
        return

    try:
        if repo == "local":
            # Read sample commits
            with open("samples/commits.txt", "r") as f:
                commit_messages = [line.strip() for line in f if line.strip()]
            
            # Read sample PRs
            pr_data = []
            try:
                with open("samples/pr.txt", "r") as f:
                    for line in f:
                        if line.strip():
                            number, title, url = line.strip().split("|")
                            pr_data.append({"number": number, "title": title, "url": url})
            except FileNotFoundError:
                logger.warning("samples/pr.txt not found, using commits without PRs")
                pr_data = []

            # Map PRs to commits (simple match by message content)
            commits = []
            for msg in commit_messages:
                pr_match = None
                for pr in pr_data:
                    if any(word.lower() in msg.lower() for word in pr["title"].lower().split()):
                        pr_match = pr
                        break
                commits.append({
                    "message": msg,
                    "pr_number": pr_match["number"] if pr_match else None,
                    "pr_title": pr_match["title"] if pr_match else None,
                    "pr_url": pr_match["url"] if pr_match else None,
                    "sha": "mocksha"  # Dummy SHA for local mode
                })

            logger.info("Loaded local commits", count=len(commits))
            for commit in commits:
                pr_info = (
                    f"PR #{commit['pr_number']} - {commit['pr_title']} ({commit['pr_url']})"
                    if commit["pr_number"]
                    else "No PR associated"
                )
                logger.info(
                    "Commit details",
                    sha=commit["sha"][:7],
                    message=commit["message"],
                    pr_info=pr_info
                )

            from .llm_client import LLMClient
            llm_client = LLMClient(openai_key)
            notes = await llm_client.generate_notes(commits)
        else:
            # Existing GitHub logic
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
                        sha=commit.sha[:7],
                        message=commit.message,
                        pr_info=pr_info
                    )

                notes = await generate_release_notes(repo, from_tag, to_tag, github_token, openai_key)

        # Save release notes
        with open('release_notes.txt', 'w') as f:
            f.write(notes)
        click.echo("Release notes saved to release_notes.txt")
    except Exception as e:
        logger.error("Failed to generate notes", error=str(e))
        click.echo(f"Error: {e}")

if __name__ == '__main__':
    asyncio.run(cli())
