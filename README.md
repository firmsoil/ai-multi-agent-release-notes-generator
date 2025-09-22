# ai-multi-agent-release-notes-generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Multi-Agent Release Notes Generator — An advanced, modular, and async Python tool for automating the generation of structured release notes by aggregating GitHub repository commit data, pull request information, and OpenAI-powered summarization.

---

## Table of Contents

- [About](#about)
- [Features](#features)
- [Demo](#demo)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [Tests](#tests)
- [License](#license)
- [Contact](#contact)

---

## About

Release notes are a critical part of software delivery, offering clear communication of changes, new features, and bug fixes between versions. This project refactors and enhances release notes generation into a scalable, async, error-resilient Python package.

It supports integration with the GitHub GraphQL API to fetch detailed pull request context for each commit, and leverages OpenAI's language models to generate insightful, categorized release notes automatically.

This tool is pre-configured out of the box for [spinnaker/spinnaker](https://github.com/spinnaker/spinnaker) repository but is adaptable to any GitHub project with proper token setup.

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

Clone the repository:

    git clone https://github.com/firmsoil/ai-multi-agent-release-notes-generator.git 
    cd ai-multi-agent-release-notes-generator 
    pip install .

---

## Usage

1. Copy `.env.example` to `.env` and add your API keys:
    
        GITHUB_TOKEN=ghp_YourTokenWithRepoScope  
        OPENAI_API_KEY=sk-YourOpenAIKey

2. Run the release notes generator:

        generate-release-notes --repo spinnaker/spinnaker --from-tag release-1.30.0 --to-tag release-1.31.0

3. The release notes will be saved as `release_notes.txt` with categorized sections.

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
Author: Firmsoil
