"""
Configuration file for release notes generator.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# JIRA Configuration
# Set your JIRA instance URL here, or use environment variable
JIRA_BASE_URL = os.getenv('JIRA_BASE_URL', 'https://jira.example.com')

# JIRA ID Pattern - customize if your JIRA uses different project keys
# Default pattern matches: ABC-123, PROJ-456, etc. (2-10 uppercase letters, dash, numbers)
JIRA_PATTERN = r'\b([A-Z]{2,10}-\d+)\b'

# GitHub Configuration (already in .env)
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
