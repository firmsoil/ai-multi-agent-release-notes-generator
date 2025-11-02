# Multi-Agent Release Notes Generator

A Python CLI tool that generates professional release notes from GitHub commits and PRs using AI (OpenAI GPT, Anthropic Claude, or Google Gemini). Supports both **Markdown** and **Confluence Storage Format** output.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## ✨ Features

- 🤖 **Multi-LLM Support**: Choose between OpenAI (GPT), Anthropic (Claude), or Google (Gemini)
- 📊 **Dual Format Output**: Generate in Markdown or Confluence Storage Format (XHTML)
- 🔗 **Smart PR Integration**: Automatically links commits to their GitHub Pull Requests
- 🎨 **Confluence Styling**: Color-coded panels and status badges for Confluence pages
- 📝 **Local Testing Mode**: Test without API calls using sample data
- ⚡ **Async Operations**: Fast and efficient with async/await
- 🏷️ **Smart Categorization**: Auto-categorizes into Features, Bug Fixes, Documentation, etc.
- 🔄 **Automatic Fallbacks**: Falls back gracefully if LLM APIs fail

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- Git
- GitHub Personal Access Token
- API key for at least one LLM provider (OpenAI, Anthropic, or Google)

### Quick Install

```bash
# Clone the repository
git clone <your-repo-url>
cd multi-agent-release-notes

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows

# Install the package
pip install -e .

# Verify installation
generate-release-notes --help
```

## 🔑 Setup

### 1. Create `.env` File

Create a `.env` file in the project root:

```bash
# Required
GITHUB_TOKEN=ghp_your_github_personal_access_token_here

# At least ONE of these LLM providers is required:
OPENAI_API_KEY=sk-your_openai_api_key_here
ANTHROPIC_API_KEY=sk-ant-your_anthropic_api_key_here
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### 2. Get API Keys

**GitHub Token:**
- Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
- Click "Generate new token (classic)"
- Select scopes: `repo` (for private repos) or `public_repo` (for public repos only)
- Copy the token to your `.env` file

**OpenAI API Key:**
- Visit [OpenAI Platform](https://platform.openai.com/api-keys)
- Create new secret key
- Copy to `.env` file

**Anthropic API Key:**
- Visit [Anthropic Console](https://console.anthropic.com/)
- Generate API key
- Copy to `.env` file

**Google Gemini API Key:**
- Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
- Create API key
- Copy to `.env` file

## 🚀 Usage

### Basic Command (Markdown Output)

```bash
generate-release-notes \
  --repo owner/repository \
  --from-tag v1.0.0 \
  --to-tag v1.1.0 \
  --llm-provider openai
```

### Confluence Format Output

```bash
generate-release-notes \
  --repo owner/repository \
  --from-tag v1.0.0 \
  --to-tag v1.1.0 \
  --llm-provider anthropic \
  --format confluence \
  --output release_notes_confluence.html
```

### Local Testing Mode (No GitHub API Calls)

```bash
# Create sample files first
mkdir -p samples

cat > samples/commits.txt << 'EOF'
feat: add user authentication system
fix: resolve memory leak in data processor
docs: update API documentation
test: add unit tests for auth module
EOF

cat > samples/pr.txt << 'EOF'
123|Add Authentication|https://github.com/org/repo/pull/123
124|Fix Memory Leak|https://github.com/org/repo/pull/124
EOF

# Generate release notes from samples
generate-release-notes \
  --repo local \
  --from-tag v1.0.0 \
  --to-tag v2.0.0 \
  --llm-provider openai
```

### Using the Shell Script

```bash
# Make it executable
chmod +x generate_release_notes.sh

# Use with environment variables
REPO=owner/repo \
FROM_TAG=v1.0.0 \
TO_TAG=v2.0.0 \
LLM_PROVIDER=anthropic \
FORMAT=confluence \
./generate_release_notes.sh
```

## 📋 Command Line Options

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `--repo` | GitHub repository (owner/repo) or "local" | - | ✅ Yes |
| `--from-tag` | Starting git tag | - | ✅ Yes |
| `--to-tag` | Ending git tag | - | ✅ Yes |
| `--llm-provider` | AI provider: `openai`, `anthropic`, or `google` | `openai` | No |
| `--format` | Output format: `markdown` or `confluence` | `markdown` | No |
| `--output` | Output file name | `release_notes.txt` | No |

## 📝 Output Formats

### Markdown Format

Standard GitHub-flavored markdown with emoji sections:

```markdown
## Release Notes

🚀 **New Features**
- Add user authentication system (PR #123 - [Add Authentication](https://...))
- Implement dark mode (PR #124 - [Dark Mode UI](https://...))

🐛 **Bug Fixes**
- Fix login redirect issue (PR #125 - [Login Fix](https://...))

📝 **Documentation**
- Update API documentation (PR #126 - [API Docs](https://...))
```

### Confluence Format

Confluence Storage Format (XHTML) with colored panels:

```html
<h1>Release Notes: v1.1.0</h1>

<ac:structured-macro ac:name="info">
  <ac:rich-text-body>
    <p><strong>Release Date:</strong> 2024-11-02</p>
    <p><strong>Total Commits:</strong> 25</p>
  </ac:rich-text-body>
</ac:structured-macro>

<ac:structured-macro ac:name="panel">
  <ac:parameter ac:name="bgColor">#E3FCEF</ac:parameter>
  <ac:parameter ac:name="title">🚀 New Features</ac:parameter>
  <ac:rich-text-body>
    <ul>
      <li><strong>Add authentication</strong> - <a href="...">PR #123</a>: Auth System</li>
    </ul>
  </ac:rich-text-body>
</ac:structured-macro>
```

## 📤 Using Confluence Output

### Method 1: Insert Markup (Recommended)

1. Open your Confluence page in edit mode
2. Click the **`</>`** (Insert markup) button in the toolbar
3. Copy the entire contents of your output file
4. Paste into the markup editor
5. Click **Insert**

### Method 2: Source Editor

1. Edit your Confluence page
2. Click **···** (More) → **View source**
3. Paste the Confluence-formatted content
4. Save the page

## 🎨 Confluence Color Scheme

| Category | Emoji | Panel Color | Hex Code |
|----------|-------|-------------|----------|
| New Features | 🚀 | Light Green | #E3FCEF |
| Bug Fixes | 🐛 | Light Red | #FFEBE6 |
| Changes | 📄 | Light Blue | #DEEBFF |
| Documentation | 📝 | Light Grey | #F4F5F7 |
| Style | 💅 | Light Yellow | #FFF0B3 |
| Tests | 🧪 | Light Purple | #EAE6FF |

## 🛠️ Project Structure

```
multi-agent-release-notes/
├── src/
│   ├── main.py                    # CLI entry point
│   ├── generator.py               # Main orchestration logic
│   ├── github_client.py           # GitHub API client with GraphQL
│   ├── llm_client.py              # Multi-LLM provider abstraction
│   └── confluence_formatter.py    # Confluence XHTML formatter
├── samples/
│   ├── commits.txt                # Sample commit data
│   └── pr.txt                     # Sample PR data
├── setup.py                       # Package configuration
├── .env                           # API keys (create this)
├── generate_release_notes.sh     # Convenience script
└── README.md
```

## 🔧 Advanced Usage

### Environment Variables

```bash
# Set these in your shell or .env file
export GITHUB_TOKEN=ghp_...
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export GEMINI_API_KEY=...

# Override defaults
export REPO=owner/repo
export FROM_TAG=v1.0.0
export TO_TAG=v2.0.0
export LLM_PROVIDER=anthropic
export FORMAT=confluence

# Run with environment variables
./generate_release_notes.sh
```

### Testing Different LLM Providers

```bash
# OpenAI GPT-3.5 Turbo (fast, cost-effective)
generate-release-notes ... --llm-provider openai

# Anthropic Claude 3 Haiku (fast, high quality)
generate-release-notes ... --llm-provider anthropic

# Google Gemini Pro (free tier available)
generate-release-notes ... --llm-provider google
```

### Batch Processing Multiple Releases

```bash
#!/bin/bash
# batch_generate.sh

RELEASES=(
  "v1.0.0:v1.1.0"
  "v1.1.0:v1.2.0"
  "v1.2.0:v2.0.0"
)

for release in "${RELEASES[@]}"; do
  IFS=':' read -r from to <<< "$release"
  generate-release-notes \
    --repo owner/repo \
    --from-tag "$from" \
    --to-tag "$to" \
    --output "release_${to}.md"
done
```

## 🐛 Troubleshooting

### Common Issues

**Issue: "GITHUB_TOKEN not found"**
```bash
# Solution: Create .env file with your token
echo "GITHUB_TOKEN=ghp_your_token_here" > .env
```

**Issue: "Repository not found (404)"**
```bash
# Solution: Check repository name and access
# Run diagnostic:
python check_github_access.py

# Verify repo name format: owner/repository
# Check if repo is private (requires token with repo scope)
```

**Issue: "Tags not found (404)"**
```bash
# Solution: List available tags
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/repos/owner/repo/tags

# Use exact tag names (case-sensitive)
```

**Issue: "Anthropic API error (404)"**
```bash
# Solution: Model not available with your API key
# Run diagnostic:
python check_anthropic_models.py

# Or use a different provider:
generate-release-notes ... --llm-provider openai
```

**Issue: "No module named 'main'"**
```bash
# Solution: Reinstall the package
pip uninstall multi-agent-release-notes -y
pip install -e .
```

### Debug Mode

```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG

# Check what's happening
generate-release-notes ... 2>&1 | tee debug.log
```

### Rate Limiting

GitHub API has rate limits:
- **Authenticated**: 5,000 requests/hour
- **Unauthenticated**: 60 requests/hour

Always use `GITHUB_TOKEN` for authenticated requests.

## 🧪 Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# With coverage
pytest --cov=src tests/
```

### Code Quality

```bash
# Format code
black src/

# Sort imports
isort src/

# Type checking
mypy src/

# Linting
flake8 src/
```

## 📊 Examples

### Example 1: Open Source Project

```bash
generate-release-notes \
  --repo kubernetes/kubernetes \
  --from-tag v1.28.0 \
  --to-tag v1.29.0 \
  --llm-provider anthropic \
  --format markdown
```

### Example 2: Internal Project with Confluence

```bash
generate-release-notes \
  --repo myorg/internal-api \
  --from-tag v2.1.0 \
  --to-tag v2.2.0 \
  --llm-provider openai \
  --format confluence \
  --output confluence_v2.2.0.html
```

### Example 3: Testing Locally

```bash
# No API calls needed!
generate-release-notes \
  --repo local \
  --from-tag v1.0.0 \
  --to-tag v2.0.0 \
  --llm-provider openai
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [OpenAI](https://openai.com/), [Anthropic](https://www.anthropic.com/), and [Google AI](https://ai.google/)
- GitHub API for commit and PR data
- Inspired by the need for automated, high-quality release documentation

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourorg/multi-agent-release-notes/issues)
- **Documentation**: This README
- **Discussions**: [GitHub Discussions](https://github.com/yourorg/multi-agent-release-notes/discussions)

## 🗺️ Roadmap

- [ ] Custom templates for output formatting
- [ ] Direct Confluence API integration for auto-publishing
- [ ] Slack/Teams webhook notifications
- [ ] PDF export support
- [ ] Web UI for non-technical users
- [ ] Docker container for easy deployment
- [ ] GitHub Action for automated release notes

---

**Made with ❤️ by the AI Team**

*Generate professional release notes in seconds, not hours!*
