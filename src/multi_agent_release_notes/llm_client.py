from abc import ABC, abstractmethod
from typing import List, Dict, Any
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import structlog

logger = structlog.get_logger()

class LLMClient(ABC):
    @abstractmethod
    async def generate_notes(self, commits: List[Dict[str, Any]]) -> str:
        """Generate release notes from a list of commits."""
        pass

    @staticmethod
    def create(provider: str, openai_key: str | None, anthropic_key: str | None) -> 'LLMClient':
        """Factory method to create an LLM client based on provider."""
        if provider == 'openai':
            if not openai_key:
                raise ValueError("OPENAI_API_KEY is required for OpenAI provider")
            return OpenAIClient(openai_key)
        elif provider == 'anthropic':
            if not anthropic_key:
                raise ValueError("ANTHROPIC_API_KEY is required for Anthropic provider")
            return AnthropicClient(anthropic_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

class OpenAIClient(LLMClient):
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate_notes(self, commits: List[Dict[str, Any]]) -> str:
        """Generate release notes using OpenAI's GPT model."""
        prompt = self._build_prompt(commits)
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates clear, concise, and categorized release notes from GitHub commits and PRs. Use markdown format with categories like 🚀 New Features, 🐛 Bug Fixes, 🔄 Changes, 📝 Documentation, 💅 Style, 🧪 Tests."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("OpenAI API error", error=str(e))
            return self._fallback_notes(commits)

    def _build_prompt(self, commits: List[Dict[str, Any]]) -> str:
        """Build the prompt for OpenAI from commit data."""
        prompt = "Generate release notes in markdown format based on the following commits and PRs:\n\n"
        for commit in commits:
            pr_info = f" (PR #{commit['pr_number']} - [{commit['pr_title']}]({commit['pr_url']}))" if commit['pr_number'] else ""
            prompt += f"- {commit['message']}{pr_info}\n"
        prompt += "\nCategorize the changes into sections like New Features, Bug Fixes, Changes, Documentation, Style, and Tests. Use emojis (🚀, 🐛, 🔄, 📝, 💅, 🧪) for each section."
        return prompt

    def _fallback_notes(self, commits: List[Dict[str, Any]]) -> str:
        """Generate fallback release notes without LLM."""
        notes = "## Release Notes\n\n"
        for commit in commits:
            pr_info = f" (PR #{commit['pr_number']} - [{commit['pr_title']}]({commit['pr_url']}))" if commit['pr_number'] else ""
            notes += f"- {commit['message']}{pr_info}\n"
        return notes

class AnthropicClient(LLMClient):
    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)

    async def generate_notes(self, commits: List[Dict[str, Any]]) -> str:
        """Generate release notes using Anthropic's Claude model."""
        prompt = self._build_prompt(commits)
        try:
            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                system="You are a helpful assistant that generates clear, concise, and categorized release notes from GitHub commits and PRs. Use markdown format with categories like 🚀 New Features, 🐛 Bug Fixes, 🔄 Changes, 📝 Documentation, 💅 Style, 🧪 Tests.",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error("Anthropic API error", error=str(e))
            return self._fallback_notes(commits)

    def _build_prompt(self, commits: List[Dict[str, Any]]) -> str:
        """Build the prompt for Anthropic from commit data."""
        prompt = "Generate release notes in markdown format based on the following commits and PRs:\n\n"
        for commit in commits:
            pr_info = f" (PR #{commit['pr_number']} - [{commit['pr_title']}]({commit['pr_url']}))" if commit['pr_number'] else ""
            prompt += f"- {commit['message']}{pr_info}\n"
        prompt += "\nCategorize the changes into sections like New Features, Bug Fixes, Changes, Documentation, Style, and Tests. Use emojis (🚀, 🐛, 🔄, 📝, 💅, 🧪) for each section."
        return prompt

    def _fallback_notes(self, commits: List[Dict[str, Any]]) -> str:
        """Generate fallback release notes without LLM."""
        notes = "## Release Notes\n\n"
        for commit in commits:
            pr_info = f" (PR #{commit['pr_number']} - [{commit['pr_title']}]({commit['pr_url']}))" if commit['pr_number'] else ""
            notes += f"- {commit['message']}{pr_info}\n"
        return notes
