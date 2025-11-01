from setuptools import setup

setup(
    name="multi-agent-release-notes",
    version="0.3.0",
    description="Multi-agent release notes generator with async, retries, logging, and Confluence support",
    author="AI Team",
    author_email="ai-team@example.com",
    package_dir={"": "src"},
    py_modules=[
        "main",
        "generator",
        "github_client",
        "llm_client",
        "confluence_formatter",
    ],
    install_requires=[
        "aiohttp>=3.9.0",
        "openai>=1.0.0",
        "anthropic>=0.28.0",
        "google-generativeai>=0.3.0",
        "pydantic>=2.0.0",
        "tenacity>=8.0.0",
        "structlog>=23.0.0",
        "python-dotenv>=1.0.0",
        "click>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.0.0",
        ],
        "confluence": [
            "atlassian-python-api>=3.41.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "generate-release-notes=main:main",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
