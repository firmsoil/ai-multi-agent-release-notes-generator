from openai import AsyncOpenAI
from typing import List
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential
from openai import OpenAIError

logger = structlog.get_logger()

class LLMClient:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_notes(self, commits: List[dict]) -> str:
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant that generates release notes from commits and their associated pull requests. Categorize with emojis: 🚀 New Features, 🐛 Bug Fixes, 🔄 Changes, 📝 Docs. Include PR number and title (linked to PR URL) where available."},
                {"role": "user", "content": "Generate categorized release notes from these commits:\n" + "\n".join(
                    [f"- {c['message']} (PR #{c['pr_number']} - [{c['pr_title']}]({c['pr_url']}))" if c.get("pr_number") else f"- {c['message']}" for c in commits]
                )}
            ]
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=1000
            )
            notes = response.choices[0].message.content
            logger.info("Generated notes", length=len(notes))
            return notes
        except OpenAIError as e:
            if "insufficient_quota" in str(e):
                logger.error("OpenAI quota exceeded", error=str(e))
                return "\n".join([
                    "## Fallback Release Notes (Quota Exceeded)",
                    "🚀 **New Features**",
                    *[f"- {c['message']} (PR #{c['pr_number']} - [{c['pr_title']}]({c['pr_url']}))" if c.get("pr_number") else f"- {c['message']}" for c in commits[:5]],
                    "🐛 **Bug Fixes**",
                    "- Contact OpenAI to resolve quota issue."
                ])
            logger.error("Error generating notes", error=str(e))
            raise
        except Exception as e:
            logger.error("Unexpected error generating notes", error=str(e))
            raise
