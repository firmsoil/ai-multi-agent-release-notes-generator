Multi-Agent Release Notes Generator
Refactored version with modular architecture, async I/O, error handling, testing, logging, and modern packaging. Configured for spinnaker/spinnaker by default, with PR lookup via GitHub GraphQL API.
Setup

pip install .
Copy .env.example to .env and add tokens:GITHUB_TOKEN=ghp_YourTokenWithRepoScope
OPENAI_API_KEY=sk-YourOpenAIKey


Run: generate-release-notes --repo spinnaker/spinnaker --from-tag release-1.30.0 --to-tag release-1.31.0

Features

Async GitHub API fetches with retries.
Pull request lookup for each commit (number, title, URL).
OpenAI-powered note generation with PR context.
Structured logging.
Pytest suite.

Automation
./generate_release_notes.sh (uses spinnaker/spinnaker with release-1.30.0 to release-1.31.0)
Example Output for Spinnaker
Running the command generates release_notes.txt with categorized notes like:
## Spinnaker Release 1.31.0 (from 1.30.0)

🚀 **New Features**
- Enhanced canary analysis for multi-cloud pipelines (PR #123 - [Add Canary Support](https://github.com/spinnaker/spinnaker/pull/123))

🐛 **Bug Fixes**
- Fixed ECR image tagging issues (PR #124 - [Fix ECR Tagging](https://github.com/spinnaker/spinnaker/pull/124))

🔄 **Changes**
- Updated Kork building blocks

📝 **Documentation**
- Expanded CI/CD guides

Available Tags in spinnaker/spinnaker
Common tags: release-1.30.0, release-1.31.0 (based on official Spinnaker releases).
