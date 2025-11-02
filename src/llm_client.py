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
        self.model = "gpt-3.5-turbo"

    async def generate_notes(self, commits: List[Dict[str, Any]]) -> str:
        """Generate release notes using OpenAI's GPT model."""
        prompt = self._build_prompt(commits)
        system_message = self._get_system_message()
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("OpenAI API error", error=str(e), model=self.model)
            return self._fallback_notes(commits)

    def _get_system_message(self) -> str:
        """Get system message based on output format."""
        if self.output_format == 'confluence':
            return """You are a helpful assistant that generates clear, concise, and categorized release notes in Confluence Storage Format (XHTML).

Format requirements:
- Use <h2> tags for section headers
- Wrap each section in <ac:structured-macro ac:name="panel"> with appropriate bgColor
- Use <ul> and <li> tags for lists
- ALWAYS include PR numbers prominently: <a href="url">PR #123</a>
- Format: <strong>Description</strong> (<a href="url">PR #123</a>) - PR Title
- Use <strong> for emphasis
- Categories: 🚀 New Features (#E3FCEF), 🐛 Bug Fixes (#FFEBE6), 🔄 Changes (#DEEBFF), 📝 Documentation (#F4F5F7), 💅 Style (#FFF0B3), 🧪 Tests (#EAE6FF)

Example item format:
<li><strong>Add user authentication</strong> (<a href="https://github.com/org/repo/pull/123">PR #123</a>) - Implement OAuth2 login system</li>"""
        else:
            return """You are a helpful assistant that generates clear, concise, and categorized release notes from GitHub commits and PRs. 

IMPORTANT: Always include PR numbers prominently in this format:
- **Description** ([PR #123](url)) - PR Title

Use markdown format with categories like 🚀 New Features, 🐛 Bug Fixes, 🔄 Changes, 📝 Documentation, 💅 Style, 🧪 Tests."""

    def _build_prompt(self, commits: List[Dict[str, Any]]) -> str:
        """Build the prompt based on output format."""
        if self.output_format == 'confluence':
            prompt = "Generate release notes in Confluence Storage Format (XHTML) based on the following commits and PRs. ALWAYS include PR numbers:\n\n"
            for commit in commits:
                if commit.get('pr_number'):
                    pr_info = f" [PR #{commit['pr_number']} - {commit['pr_title']} - {commit['pr_url']}]"
                else:
                    pr_info = " [No PR]"
                prompt += f"- {commit['message']}{pr_info}\n"
            prompt += "\nCategorize changes and format as Confluence panels. For each item, show: <strong>description</strong> (<a href='url'>PR #number</a>) - PR title"
        else:
            prompt = "Generate release notes in markdown format based on the following commits and PRs. ALWAYS include PR numbers:\n\n"
            for commit in commits:
                if commit.get('pr_number'):
                    pr_info = f" [PR #{commit['pr_number']} - {commit['pr_title']} - {commit['pr_url']}]"
                else:
                    pr_info = " [No PR]"
                prompt += f"- {commit['message']}{pr_info}\n"
            prompt += "\nCategorize the changes. For each item use format: **description** ([PR #123](url)) - PR title"
        
        return prompt

    def _fallback_notes(self, commits: List[Dict[str, Any]]) -> str:
        """Generate fallback release notes without LLM."""
        if self.output_format == 'confluence':
            return ConfluenceFormatter._generate_confluence_notes(commits, 'unknown', 'unknown')
        else:
            notes = "## Release Notes\n\n"
            for commit in commits:
                if commit.get('pr_number'):
                    pr_link = f"[PR #{commit['pr_number']}]({commit['pr_url']})"
                    notes += f"- **{commit['message']}** ({pr_link}) - {commit['pr_title']}\n"
                else:
                    notes += f"- **{commit['message']}**\n"
            return notes


class AnthropicClient(LLMClient):
    def __init__(self, api_key: str, output_format: str = 'markdown'):
        super().__init__(output_format)
        self.client = AsyncAnthropic(api_key=api_key)
        # FIXED: Use Claude 3 Haiku - fastest and most accessible model
        self.model = "claude-3-haiku-20240307"

    async def generate_notes(self, commits: List[Dict[str, Any]]) -> str:
        """Generate release notes using Anthropic's Claude model."""
        prompt = self._build_prompt(commits)
        system_message = self._get_system_message()
        
        # Try multiple models in order of preference, starting with Haiku
        models_to_try = [
            "claude-3-haiku-20240307",      # Fastest, most accessible (PRIMARY)
            "claude-3-5-sonnet-20241022",   # Latest Sonnet (Oct 2024)
            "claude-3-5-sonnet-latest",     # Auto-updated latest
            "claude-3-opus-20240229",       # Most capable Claude 3
            "claude-3-sonnet-20240229",     # Balanced Claude 3
        ]
        
        for model in models_to_try:
            try:
                logger.info("Attempting Anthropic model", model=model)
                response = await self.client.messages.create(
                    model=model,
                    max_tokens=1500,
                    temperature=0.7,
                    system=system_message,
                    messages=[{"role": "user", "content": prompt}]
                )
                logger.info("Successfully used Anthropic model", model=model)
                return response.content[0].text
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Model {model} failed", error=error_msg)
                
                # If it's a 404, try next model
                if "404" in error_msg or "not_found" in error_msg:
                    continue
                else:
                    # For other errors (rate limit, auth, etc), stop trying
                    logger.error("Anthropic API error (non-404)", error=error_msg, model=model)
                    break
        
        # All models failed, use fallback
        logger.error("All Anthropic models failed, using fallback")
        return self._fallback_notes(commits)
            
    def _get_system_message(self) -> str:
        """Get system message based on output format."""
        if self.output_format == 'confluence':
            return """You are a helpful assistant that generates clear, concise, and categorized release notes in Confluence Storage Format (XHTML).

Format requirements:
- Use <h2> tags for section headers
- Wrap each section in <ac:structured-macro ac:name="panel"> with appropriate bgColor
- Use <ul> and <li> tags for lists
- ALWAYS include PR numbers prominently: <a href="url">PR #123</a>
- Format: <strong>Description</strong> (<a href="url">PR #123</a>) - PR Title
- Use <strong> for emphasis
- Categories: 🚀 New Features (#E3FCEF), 🐛 Bug Fixes (#FFEBE6), 🔄 Changes (#DEEBFF), 📝 Documentation (#F4F5F7), 💅 Style (#FFF0B3), 🧪 Tests (#EAE6FF)

Example item format:
<li><strong>Add user authentication</strong> (<a href="https://github.com/org/repo/pull/123">PR #123</a>) - Implement OAuth2 login system</li>"""
        else:
            return """You are a helpful assistant that generates clear, concise, and categorized release notes from GitHub commits and PRs. 

IMPORTANT: Always include PR numbers prominently in this format:
- **Description** ([PR #123](url)) - PR Title

Use markdown format with categories like 🚀 New Features, 🐛 Bug Fixes, 🔄 Changes, 📝 Documentation, 💅 Style, 🧪 Tests."""

    def _build_prompt(self, commits: List[Dict[str, Any]]) -> str:
        """Build the prompt based on output format."""
        if self.output_format == 'confluence':
            prompt = "Generate release notes in Confluence Storage Format (XHTML) based on the following commits and PRs. ALWAYS include PR numbers:\n\n"
            for commit in commits:
                if commit.get('pr_number'):
                    pr_info = f" [PR #{commit['pr_number']} - {commit['pr_title']} - {commit['pr_url']}]"
                else:
                    pr_info = " [No PR]"
                prompt += f"- {commit['message']}{pr_info}\n"
            prompt += "\nCategorize changes and format as Confluence panels. For each item, show: <strong>description</strong> (<a href='url'>PR #number</a>) - PR title"
        else:
            prompt = "Generate release notes in markdown format based on the following commits and PRs. ALWAYS include PR numbers:\n\n"
            for commit in commits:
                if commit.get('pr_number'):
                    pr_info = f" [PR #{commit['pr_number']} - {commit['pr_title']} - {commit['pr_url']}]"
                else:
                    pr_info = " [No PR]"
                prompt += f"- {commit['message']}{pr_info}\n"
            prompt += "\nCategorize the changes. For each item use format: **description** ([PR #123](url)) - PR title"
        
        return prompt

    def _fallback_notes(self, commits: List[Dict[str, Any]]) -> str:
        """Generate fallback release notes without LLM."""
        if self.output_format == 'confluence':
            return ConfluenceFormatter._generate_confluence_notes(commits, 'unknown', 'unknown')
        else:
            notes = "## Release Notes\n\n"
            for commit in commits:
                if commit.get('pr_number'):
                    pr_link = f"[PR #{commit['pr_number']}]({commit['pr_url']})"
                    notes += f"- **{commit['message']}** ({pr_link}) - {commit['pr_title']}\n"
                else:
                    notes += f"- **{commit['message']}**\n"
            return notes


class GeminiClient(LLMClient):
    def __init__(self, api_key: str, output_format: str = 'markdown'):
        super().__init__(output_format)
        
        # FIXED: Simplified Gemini client initialization
        try:
            # Import here to avoid issues if google-generativeai not installed
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
            # Gemini doesn't have native async in google-generativeai, use sync in thread
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
        """Get system message based on output format."""
        if self.output_format == 'confluence':
            return """You are a helpful assistant that generates clear, concise, and categorized release notes in Confluence Storage Format (XHTML).

Format requirements:
- Use <h2> tags for section headers
- Wrap each section in <ac:structured-macro ac:name="panel"> with appropriate bgColor
- Use <ul> and <li> tags for lists
- ALWAYS include PR numbers prominently: <a href="url">PR #123</a>
- Format: <strong>Description</strong> (<a href="url">PR #123</a>) - PR Title
- Use <strong> for emphasis
- Categories: 🚀 New Features (#E3FCEF), 🐛 Bug Fixes (#FFEBE6), 🔄 Changes (#DEEBFF), 📝 Documentation (#F4F5F7), 💅 Style (#FFF0B3), 🧪 Tests (#EAE6FF)"""
        else:
            return """You are a helpful assistant that generates clear, concise, and categorized release notes from GitHub commits and PRs. 

IMPORTANT: Always include PR numbers prominently in this format:
- **Description** ([PR #123](url)) - PR Title

Use markdown format with categories like 🚀 New Features, 🐛 Bug Fixes, 🔄 Changes, 📝 Documentation, 💅 Style, 🧪 Tests."""

    def _build_prompt(self, commits: List[Dict[str, Any]]) -> str:
        """Build the prompt based on output format."""
        if self.output_format == 'confluence':
            prompt = "Generate release notes in Confluence Storage Format (XHTML) based on the following commits and PRs. ALWAYS include PR numbers:\n\n"
            for commit in commits:
                if commit.get('pr_number'):
                    pr_info = f" [PR #{commit['pr_number']} - {commit['pr_title']} - {commit['pr_url']}]"
                else:
                    pr_info = " [No PR]"
                prompt += f"- {commit['message']}{pr_info}\n"
            prompt += "\nCategorize changes and format as Confluence panels. For each item, show: <strong>description</strong> (<a href='url'>PR #number</a>) - PR title"
        else:
            prompt = "Generate release notes in markdown format based on the following commits and PRs. ALWAYS include PR numbers:\n\n"
            for commit in commits:
                if commit.get('pr_number'):
                    pr_info = f" [PR #{commit['pr_number']} - {commit['pr_title']} - {commit['pr_url']}]"
                else:
                    pr_info = " [No PR]"
                prompt += f"- {commit['message']}{pr_info}\n"
            prompt += "\nCategorize the changes. For each item use format: **description** ([PR #123](url)) - PR title"
        
        return prompt

    def _fallback_notes(self, commits: List[Dict[str, Any]]) -> str:
        """Generate fallback release notes without LLM."""
        if self.output_format == 'confluence':
            return ConfluenceFormatter._generate_confluence_notes(commits, 'unknown', 'unknown')
        else:
            notes = "## Release Notes\n\n"
            for commit in commits:
                if commit.get('pr_number'):
                    pr_link = f"[PR #{commit['pr_number']}]({commit['pr_url']})"
                    notes += f"- **{commit['message']}** ({pr_link}) - {commit['pr_title']}\n"
                else:
                    notes += f"- **{commit['message']}**\n"
            return notes
