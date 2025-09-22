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

3. Run the release notes generator:
generate-release-notes --repo spinnaker/spinnaker --from-tag release-1.30.0 --to-tag release-1.31.0

4. The release notes will be saved as `release_notes.txt` with categorized sections.

---

## Configuration

- **GITHUB_TOKEN**: GitHub Personal Access Token with repository scope to fetch data.
- **OPENAI_API_KEY**: API key for OpenAI to enable AI-powered summarization.
- Tags for releases can be customized based on target repository.

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
