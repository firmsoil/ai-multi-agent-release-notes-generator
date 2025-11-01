from abc import ABC, abstractmethod
from typing import List, Dict, Any
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import structlog

# FIXED: Absolute import instead of relative
from confluence_formatter import ConfluenceFormatter

logger = structlog.get_logger()

class LLMClient(ABC):
    def __init__(self, output_format: str = 'markdown'):
        self.output_format = output_format
    
    @abstractmethod
    async def generate_notes(self, commits: List[Dict[str, Any]]) -> str:
        """Generate release notes from a list of commits."""
        pass

    @staticmethod
    def create(
        provider: str, 
        openai_key: str | None, 
        anthropic_key: str | None, 
        gemini_key: str | None,
        output_format: str = 'markdown'
    ) -> 'LLMClient':
        """Factory method to create an LLM client based on provider."""
        if provider == 'openai':
            if not openai_key:
                raise ValueError("OPENAI_API_KEY is required for OpenAI provider")
            return OpenAIClient(openai_key, output_format)
        elif provider == 'anthropic':
            if not anthropic_key:
                raise ValueError("ANTHROPIC_API_KEY is required for Anthropic provider")
            return AnthropicClient(anthropic_key, output_format)
        elif provider == 'google':
            if not gemini_key:
                raise ValueError("GEMINI_API_KEY is required for Google Gemini provider")
            return GeminiClient(gemini_key, output_format)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

class OpenAIClient(LLMClient):
    def __init__(self, api_key: str, output_format: str = 'markdown'):
        super().__init__(output_format)
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate_notes(self, commits: List[Dict[str, Any]]) -> str:
        """Generate release notes using OpenAI's GPT model."""
        prompt = self._build_prompt(commits)
        system_message = self._get_system_message()
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("OpenAI API error", error=str(e))
            return self._fallback_notes(commits)

    def _get_system_message(self) -> str:
        if self.output_format == 'confluence':
            return """You are a helpful assistant that generates clear, concise, and categorized release notes in Confluence Storage Format (XHTML).

Format requirements:
- Use <h2> tags for section headers
- Wrap each section in <ac:structured-macro ac:name="panel"> with appropriate bgColor
- Use <ul> and <li> tags for lists
- Create hyperlinks with <a href="...">text</a>
- Use <strong> for emphasis
- Categories: 🚀 New Features (#E3FCEF), 🐛 Bug Fixes (#FFEBE6), 📄 Changes (#DEEBFF), 📝 Documentation (#F4F5F7), 💅 Style (#FFF0B3), 🧪 Tests (#EAE6FF)

Example panel structure:
<ac:structured-macro ac:name="panel" ac:schema-version="1">
  <ac:parameter ac:name="bgColor">#E3FCEF</ac:parameter>
  <ac:parameter ac:name="title">🚀 New Features</ac:parameter>
  <ac:rich-text-body>
    <ul>
      <li><strong>Feature description</strong> - <a href="url">PR #123</a>: Title</li>
    </ul>
  </ac:rich-text-body>
</ac:structured-macro>"""
        else:
            return """You are a helpful assistant that generates clear, concise, and categorized release notes from GitHub commits and PRs. Use markdown format with categories like 🚀 New Features, 🐛 Bug Fixes, 📄 Changes, 📝 Documentation, 💅 Style, 🧪 Tests."""

    def _build_prompt(self, commits: List[Dict[str, Any]]) -> str:
        if self.output_format == 'confluence':
            prompt = "Generate release notes in Confluence Storage Format (XHTML) based on the following commits and PRs:\n\n"
            for commit in commits:
                pr_info = f" (PR #{commit['pr_number']} - {commit['pr_title']} - {commit['pr_url']})" if commit.get('pr_number') else ""
                prompt += f"- {commit['message']}{pr_info}\n"
            prompt += "\nCategorize changes and format as Confluence panels with colored backgrounds. Use proper XHTML syntax."
        else:
            prompt = "Generate release notes in markdown format based on the following commits and PRs:\n\n"
            for commit in commits:
                pr_info = f" (PR #{commit['pr_number']} - [{commit['pr_title']}]({commit['pr_url']}))" if commit.get('pr_number') else ""
                prompt += f"- {commit['message']}{pr_info}\n"
            prompt += "\nCategorize the changes into sections like New Features, Bug Fixes, Changes, Documentation, Style, and Tests. Use emojis (🚀, 🐛, 📄, 📝, 💅, 🧪) for each section."
        
        return prompt

    def _fallback_notes(self, commits: List[Dict[str, Any]]) -> str:
        if self.output_format == 'confluence':
            return ConfluenceFormatter._generate_confluence_notes(commits, 'unknown', 'unknown')
        else:
            notes = "## Release Notes\n\n"
            for commit in commits:
                pr_info = f" (PR #{commit['pr_number']} - [{commit['pr_title']}]({commit['pr_url']}))" if commit.get('pr_number') else ""
                notes += f"- {commit['message']}{pr_info}\n"
            return notes

class AnthropicClient(LLMClient):
    def __init__(self, api_key: str, output_format: str = 'markdown'):
        super().__init__(output_format)
        self.client = AsyncAnthropic(api_key=api_key)

    async def generate_notes(self, commits: List[Dict[str, Any]]) -> str:
        """Generate release notes using Anthropic's Claude model."""
        prompt = self._build_prompt(commits)
        system_message = self._get_system_message()
        
        try:
            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                system=system_message,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error("Anthropic API error", error=str(e))
            return self._fallback_notes(commits)
            
    def _get_system_message(self) -> str:
        if self.output_format == 'confluence':
            return """You are a helpful assistant that generates clear, concise, and categorized release notes in Confluence Storage Format (XHTML).

Format requirements:
- Use <h2> tags for section headers
- Wrap each section in <ac:structured-macro ac:name="panel"> with appropriate bgColor
- Use <ul> and <li> tags for lists
- Create hyperlinks with <a href="...">text</a>
- Use <strong> for emphasis
- Categories: 🚀 New Features (#E3FCEF), 🐛 Bug Fixes (#FFEBE6), 📄 Changes (#DEEBFF), 📝 Documentation (#F4F5F7), 💅 Style (#FFF0B3), 🧪 Tests (#EAE6FF)

Example panel structure:
<ac:structured-macro ac:name="panel" ac:schema-version="1">
  <ac:parameter ac:name="bgColor">#E3FCEF</ac:parameter>
  <ac:parameter ac:name="title">🚀 New Features</ac:parameter>
  <ac:rich-text-body>
    <ul>
      <li><strong>Feature description</strong> - <a href="url">PR #123</a>: Title</li>
    </ul>
  </ac:rich-text-body>
</ac:structured-macro>"""
        else:
            return """You are a helpful assistant that generates clear, concise, and categorized release notes from GitHub commits and PRs. Use markdown format with categories like 🚀 New Features, 🐛 Bug Fixes, 📄 Changes, 📝 Documentation, 💅 Style, 🧪 Tests."""

    def _build_prompt(self, commits: List[Dict[str, Any]]) -> str:
        if self.output_format == 'confluence':
            prompt = "Generate release notes in Confluence Storage Format (XHTML) based on the following commits and PRs:\n\n"
            for commit in commits:
                pr_info = f" (PR #{commit['pr_number']} - {commit['pr_title']} - {commit['pr_url']})" if commit.get('pr_number') else ""
                prompt += f"- {commit['message']}{pr_info}\n"
            prompt += "\nCategorize changes and format as Confluence panels with colored backgrounds. Use proper XHTML syntax."
        else:
            prompt = "Generate release notes in markdown format based on the following commits and PRs:\n\n"
            for commit in commits:
                pr_info = f" (PR #{commit['pr_number']} - [{commit['pr_title']}]({commit['pr_url']}))" if commit.get('pr_number') else ""
                prompt += f"- {commit['message']}{pr_info}\n"
            prompt += "\nCategorize the changes into sections like New Features, Bug Fixes, Changes, Documentation, Style, and Tests. Use emojis (🚀, 🐛, 📄, 📝, 💅, 🧪) for each section."
        
        return prompt

    def _fallback_notes(self, commits: List[Dict[str, Any]]) -> str:
        if self.output_format == 'confluence':
            return ConfluenceFormatter._generate_confluence_notes(commits, 'unknown', 'unknown')
        else:
            notes = "## Release Notes\n\n"
            for commit in commits:
                pr_info = f" (PR #{commit['pr_number']} - [{commit['pr_title']}]({commit['pr_url']}))" if commit.get('pr_number') else ""
                notes += f"- {commit['message']}{pr_info}\n"
            return notes

class GeminiClient(LLMClient):
    def __init__(self, api_key: str, output_format: str = 'markdown'):
        super().__init__(output_format)
        
        # FIXED: Simplified Gemini client initialization
        try:
            # Import here to avoid issues if google-genai not installed
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        except ImportError:
            raise ValueError("google-generativeai package not installed. Run: pip install google-generativeai")
        except Exception as e:
            logger.error("Gemini Client initialization failed", error=str(e))
            raise ValueError(f"Failed to initialize Gemini Client: {e}")

    async def generate_notes(self, commits: List[Dict[str, Any]]) -> str:
        """Generate release notes using Google's Gemini model."""
        prompt = self._build_prompt(commits)
        system_message = self._get_system_message()
        
        # Combine system message and prompt
        full_prompt = f"{system_message}\n\n{prompt}"
        
        try:
            # Gemini doesn't have native async in google-generativeai, use sync
            import asyncio
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt
            )
            return response.text
        except Exception as e:
            logger.error("Gemini API error", error=str(e))
            return self._fallback_notes(commits)

    def _get_system_message(self) -> str:
        if self.output_format == 'confluence':
            return """You are a helpful assistant that generates clear, concise, and categorized release notes in Confluence Storage Format (XHTML).

Format requirements:
- Use <h2> tags for section headers
- Wrap each section in <ac:structured-macro ac:name="panel"> with appropriate bgColor
- Use <ul> and <li> tags for lists
- Create hyperlinks with <a href="...">text</a>
- Use <strong> for emphasis
- Categories: 🚀 New Features (#E3FCEF), 🐛 Bug Fixes (#FFEBE6), 📄 Changes (#DEEBFF), 📝 Documentation (#F4F5F7), 💅 Style (#FFF0B3), 🧪 Tests (#EAE6FF)"""
        else:
            return """You are a helpful assistant that generates clear, concise, and categorized release notes from GitHub commits and PRs. Use markdown format with categories like 🚀 New Features, 🐛 Bug Fixes, 📄 Changes, 📝 Documentation, 💅 Style, 🧪 Tests."""

    def _build_prompt(self, commits: List[Dict[str, Any]]) -> str:
        if self.output_format == 'confluence':
            prompt = "Generate release notes in Confluence Storage Format (XHTML) based on the following commits and PRs:\n\n"
            for commit in commits:
                pr_info = f" (PR #{commit['pr_number']} - {commit['pr_title']} - {commit['pr_url']})" if commit.get('pr_number') else ""
                prompt += f"- {commit['message']}{pr_info}\n"
            prompt += "\nCategorize changes and format as Confluence panels with colored backgrounds. Use proper XHTML syntax."
        else:
            prompt = "Generate release notes in markdown format based on the following commits and PRs:\n\n"
            for commit in commits:
                pr_info = f" (PR #{commit['pr_number']} - [{commit['pr_title']}]({commit['pr_url']}))" if commit.get('pr_number') else ""
                prompt += f"- {commit['message']}{pr_info}\n"
            prompt += "\nCategorize the changes into sections like New Features, Bug Fixes, Changes, Documentation, Style, and Tests. Use emojis (🚀, 🐛, 📄, 📝, 💅, 🧪) for each section."
        
        return prompt

    def _fallback_notes(self, commits: List[Dict[str, Any]]) -> str:
        if self.output_format == 'confluence':
            return ConfluenceFormatter._generate_confluence_notes(commits, 'unknown', 'unknown')
        else:
            notes = "## Release Notes\n\n"
            for commit in commits:
                pr_info = f" (PR #{commit['pr_number']} - [{commit['pr_title']}]({commit['pr_url']}))" if commit.get('pr_number') else ""
                notes += f"- {commit['message']}{pr_info}\n"
            return notes
