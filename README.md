# ai-multi-agent-release-notes-generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful, async-powered tool to generate polished release notes from GitHub commits and pull requests using AI.

## Table of Contents
- [About the Project](#about-the-project)
  - [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Command-Line Usage](#command-line-usage)
  - [Automation Script](#automation-script)
  - [GitHub Actions Workflow](#github-actions-workflow)
  - [Local Testing with Samples](#local-testing-with-samples)
  - [Tests](#tests)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Acknowledgments](#acknowledgments)

## About the Project

The Multi-Agent Release Notes Generator automates the creation of high-quality release notes for a GitHub project by analyzing GitHub commits and pull requests (PRs) with a multi-agent AI system. Built with modern Python, it uses async I/O, robust error handling, and supports multiple LLM providers (OpenAI's `gpt-3.5-turbo` or Anthropic's Claude) to generate insightful, categorized release notes (e.g., 🚀 New Features, 🐛 Bug Fixes) with PR context.

**Why Use This Tool?**
- Saves time by automating release note generation.
- Enhances notes with PR details (number, title, URL) for traceability.
- Leverages AI to produce engaging, user-friendly summaries.
- Modular and extensible for any GitHub repository.

This tool is pre-configured out of the box for [firmsoil/slsa](https://github.com/firmsoil/slsa) repository but is adaptable to any GitHub project with proper token setup.

([back to top](#multi-agent-release-notes-generator))

### Built With
- [Python](https://www.python.org/)
- [OpenAI](https://platform.openai.com/)
- [Anthropic](https://www.anthropic.com/)
- [aiohttp](https://docs.aiohttp.org/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [Click](https://click.palletsprojects.com/)

([back to top](#multi-agent-release-notes-generator))

## Getting Started

Follow these steps to set up the project locally and generate release notes.

### Prerequisites
- **Python 3.10+**: Ensure you have Python 3.10 or higher installed.
  ```bash
  python3 --version

---

## Features

  - Async fetching of commit and pull request data with automatic retries
  - Detailed pull request lookup via GitHub GraphQL API (PR number, title, URL)
  - OpenAI GPT-powered release notes generation with contextual awareness
  - Structured, categorized notes with sections for new features, bug fixes, changes, and documentation
  - Extensive logging and error handling for robust automated workflows
  - Modern packaging for easy installation and extension
  - Pytest-based test suite ensuring code quality and reliability
  - Shell script for out-of-the-box use with spinnaker/spinnaker example

---

## Demo

Run the generator to produce release notes from official Spinnaker releases:

    generate-release-notes --repo spinnaker/spinnaker --from-tag release-1.30.0 --to-tag release-1.31.0

  Sample output excerpt (`release_notes.txt`):
        
    Spinnaker Release 1.31.0 (from 1.30.0)
    
    🚀 New Features
    Enhanced canary analysis for multi-cloud pipelines (PR #123 - Add Canary Support)
    
    🐛 Bug Fixes
    Fixed ECR image tagging issues (PR #124 - Fix ECR Tagging)
    
    🔄 Changes
    Updated Kork building blocks
    
    📝 Documentation
    Expanded CI/CD guides

---

## Installation

  1. Clone the repository:
  
          git clone https://github.com/firmsoil/ai-multi-agent-release-notes-generator.git 
          cd ai-multi-agent-release-notes-generator 
          pip install .
  
  2. Create a virtual environment:
  
          python3 -m venv venv
          source venv/bin/activate
  
  3. Install dependencies:
     
         pip install -r requirements.txt
         pip install .

  4. Set up environment variables:

    cp .env.example .env
    nano .env

  5. Add (include at least one API key based on your LLM provider):
     
          GITHUB_TOKEN=ghp_YourTokenWithRepoScope  
          OPENAI_API_KEY=sk-YourOpenAIKey
          ANTHROPIC_API_KEY=sk-ant-YourAnthropicKey
     
---

## Usage

Generate release notes for any GitHub repository with commits and PRs. The tool fetches data asynchronously, retrieves PR details via GraphQL, and uses the specified LLM provider (OpenAI or Anthropic) to produce categorized notes.

### Command-Line Usage

Generate notes using OpenAI (default):

    generate-release-notes --repo firmsoil/slsa --from-tag v0.1.0 --to-tag v1.0.0

Generate notes using Anthropic:

    bashgenerate-release-notes --repo firmsoil/slsa --from-tag v0.1.0 --to-tag v1.0.0 --llm-provider anthropic

Outputs release_notes.txt and logs commits/PRs to console (e.g., sha=92afd8b message=Add SLSA verification pr_info=PR #123).

### Automation Script

Run the default script for firmsoil/slsa (uses OpenAI by default):

    ./generate_release_notes.sh

Configured for firmsoil/slsa with tags v0.1.0 to v1.0.0.

To use Anthropic, set environment variable:

    LLM_PROVIDER=anthropic ./generate_release_notes.sh

    Sample console output:
    text2025-09-22 01:XX:XX [info] Fetched commits count=97 repo=firmsoil/slsa total_raw=97
    2025-09-22 01:XX:XX [info] Commit and PR Summary repo=firmsoil/slsa
    2025-09-22 01:XX:XX [info] Commit details sha=92afd8b message=Add SLSA verification pr_info=PR #123 - Add Verification Workflow<a     
    href="https://github.com/firmsoil/slsa/pull/123" target="_blank" rel="noopener noreferrer nofollow"></a>
    2025-09-22 01:XX:XX [info] Commit details sha=abc1234 message=Fix signing bug pr_info=PR #124 - Fix Signing<a   
    href="https://github.com/firmsoil/slsa/pull/124" target="_blank" rel="noopener noreferrer nofollow"></a>
    ...

4. The release notes will be saved as `release_notes.txt` with categorized sections.

---

## Configuration

- **GITHUB_TOKEN**: GitHub Personal Access Token with repository scope to fetch data.
- **OPENAI_API_KEY**: API key for OpenAI to enable AI-powered summarization.
- Tags for releases can be customized based on target repository.

---

## GitHub Actions Workflow

Automate release note generation when pushing tags (e.g., v1.0.0):

Trigger: Runs on tag pushes matching v* (semantic versioning).
Process: Fetches the previous tag, generates notes using generate-release-notes, and commits release_notes.txt to the repository.
Setup:

Ensure the repository is hosted on GitHub.
Add OPENAI_API_KEY as a repository secret in Settings > Secrets and variables > Actions.
Push a tag:

      git tag v1.0.0
      git push origin v1.0.0

Output: Check the Actions tab for logs. The generated release_notes.txt is committed to the repository.

Example Output (release_notes.txt)

    SLSA Release v1.0.0 (from v0.1.0)

    🚀 **New Features**
    - Added supply-chain artifact verification (PR #123 - [Add Verification Workflow](https://github.com/firmsoil/slsa/pull/123))
    
    🐛 **Bug Fixes**
    - Fixed signing bug in GitHub Actions (PR #124 - [Fix Signing](https://github.com/firmsoil/slsa/pull/124))
    
    🔄 **Changes**
    - Updated Shell scripts for SLSA compliance
    
    📝 **Documentation**
    - Improved README for artifact provenance

---

Local Testing with Samples
Test the tool offline using sample data in samples/commits.txt and samples/pr.txt:

    generate-release-notes --repo local --from-tag v0.1 --to-tag v0.2

Reads commits from samples/commits.txt and PRs from samples/pr.txt.

Associates PRs with commits based on message similarity.
Outputs release_notes.txt with categorized notes, including PR details where applicable.

Example Output (release_notes.txt)
    
    SLSA Release v1.0.0 (from v0.1.0)
    
    🚀 **New Features**
    - Added supply-chain artifact verification (PR #123 - [Add Verification Workflow](https://github.com/firmsoil/slsa/pull/123))
    
    🐛 **Bug Fixes**
    - Fixed signing bug in GitHub Actions (PR #124 - [Fix Signing](https://github.com/firmsoil/slsa/pull/124))
    
    🔄 **Changes**
    - Updated Shell scripts for SLSA compliance
    
    📝 **Documentation**
    - Improved README for artifact provenance (PR #125 - [Update README for SLSA](https://github.com/firmsoil/slsa/pull/125))

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

Please ensure tests pass and code is linted before submitting.

---

## Tests

Run the test suite with:

    pytest

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

---

## Contact

Project Link: [https://github.com/firmsoil/ai-multi-agent-release-notes-generator](https://github.com/firmsoil/ai-multi-agent-release-notes-generator)

---

## Acknowledgments

    othneildrew/Best-README-Template
    OpenAI
    GitHub API
    Pydantic
    Structlog

---
