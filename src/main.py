import asyncio
import click
import os
from dotenv import load_dotenv
import structlog
import aiohttp

# FIXED: Use absolute imports instead of relative imports
from generator import generate_release_notes
from github_client import GitHubClient, Commit
from confluence_formatter import ConfluenceFormatter

load_dotenv()

logger = structlog.get_logger()

@click.command()
@click.option('--repo', required=True, help='GitHub repo (owner/repo) or "local" for sample data')
@click.option('--from-tag', required=True, help='From tag')
@click.option('--to-tag', required=True, help='To tag')
@click.option('--llm-provider', default='openai', type=click.Choice(['openai', 'anthropic', 'google']), help='LLM provider')
@click.option('--format', 'output_format', default='markdown', type=click.Choice(['markdown', 'confluence']), help='Output format')
@click.option('--output', default='release_notes.txt', help='Output file name')
def cli(repo: str, from_tag: str, to_tag: str, llm_provider: str, output_format: str, output: str):
    """Generate release notes from GitHub commits and PRs."""
    # Run the async function using asyncio.run()
    asyncio.run(async_main(repo, from_tag, to_tag, llm_provider, output_format, output))

async def async_main(repo: str, from_tag: str, to_tag: str, llm_provider: str, output_format: str, output: str):
    """Async implementation of the main logic."""
    github_token = os.getenv('GITHUB_TOKEN')
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    if not github_token:
        click.echo("❌ Error: Set GITHUB_TOKEN in .env")
        return

    if llm_provider == 'openai' and not openai_key:
        click.echo("❌ Error: Set OPENAI_API_KEY in .env for OpenAI provider")
        return
    if llm_provider == 'anthropic' and not anthropic_key:
        click.echo("❌ Error: Set ANTHROPIC_API_KEY in .env for Anthropic provider")
        return
    if llm_provider == 'google' and not gemini_key:
        click.echo("❌ Error: Set GEMINI_API_KEY in .env for Google Gemini provider")
        return

    try:
        if repo == "local":
            # Local mode - read sample files
            try:
                with open("samples/commits.txt", "r") as f:
                    commit_messages = [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                click.echo("❌ Error: samples/commits.txt not found. Create sample files first.")
                return
            
            # Read sample PRs (optional)
            pr_data = []
            try:
                with open("samples/pr.txt", "r") as f:
                    for line in f:
                        if line.strip():
                            parts = line.strip().split("|")
                            if len(parts) == 3:
                                number, title, url = parts
                                pr_data.append({"number": number, "title": title, "url": url})
            except FileNotFoundError:
                logger.warning("samples/pr.txt not found, using commits without PRs")

            # Map PRs to commits
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
                    "sha": "local123"
                })

            logger.info("Loaded local commits", count=len(commits), format=output_format)

            from llm_client import LLMClient
            llm_client = LLMClient.create(
                provider=llm_provider,
                openai_key=openai_key,
                anthropic_key=anthropic_key,
                gemini_key=gemini_key,
                output_format=output_format
            )
            notes = await llm_client.generate_notes(commits)
            
            # Post-process for Confluence if needed
            if output_format == 'confluence' and not notes.strip().startswith('<'):
                notes = ConfluenceFormatter.format_release_notes(
                    commits, from_tag, to_tag, repo=None, notes_content=notes
                )
        else:
            # GitHub mode
            notes = await generate_release_notes(
                repo=repo,
                from_tag=from_tag,
                to_tag=to_tag,
                github_token=github_token,
                llm_provider=llm_provider,
                openai_key=openai_key,
                anthropic_key=anthropic_key,
                gemini_key=gemini_key,
                output_format=output_format
            )

        # Save release notes
        with open(output, 'w', encoding='utf-8') as f:
            f.write(notes)
        
        file_type = "Confluence Storage Format" if output_format == 'confluence' else "Markdown"
        click.echo(f"✅ Release notes saved to {output} ({file_type})")
        
        if output_format == 'confluence':
            click.echo("\n📋 To use in Confluence:")
            click.echo("   1. Open Confluence page editor")
            click.echo("   2. Click '</>' (Insert markup)")
            click.echo("   3. Paste the contents of the output file")
            click.echo("   4. Click 'Insert'")
            
    except Exception as e:
        logger.error("Failed to generate notes", error=str(e))
        click.echo(f"❌ Error: {e}")
        raise

def main():
    """Entry point for the CLI command."""
    cli()

if __name__ == '__main__':
    main()
