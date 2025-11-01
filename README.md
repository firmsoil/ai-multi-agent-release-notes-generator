# Multi-Agent Release Notes Generator

A Python tool that generates professional release notes from GitHub commits and PRs using LLM providers (OpenAI or Anthropic). Supports both **Markdown** and **Confluence Storage Format** output.

## Features

- 🚀 **Dual Format Support**: Generate release notes in Markdown or Confluence format
- 🤖 **Multi-LLM Support**: Choose between OpenAI (GPT) or Anthropic (Claude)
- 📊 **Smart Categorization**: Automatically categorizes commits into New Features, Bug Fixes, Changes, etc.
- 🔗 **PR Integration**: Links commits to their associated GitHub Pull Requests
- 🎨 **Confluence Styling**: Color-coded panels and status badges for Confluence pages
- 📝 **Local Mode**: Test with sample data without GitHub API calls
- ⚡ **Async Operations**: Fast and efficient with async/await

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd multi-agent-release-notes

# Install dependencies
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"

# Optional: Install Confluence API support
pip install -e ".[confluence]"
```

## Setup

Create a `.env` file in the project root:

```bash
# Required
GITHUB_TOKEN=ghp_your_github_token_here

# Choose one LLM provider
OPENAI_API_KEY=sk-your_openai_key_here
# OR
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here
```

### Getting API Keys

- **GitHub Token**: [Create a Personal Access Token](https://github.com/settings/tokens) with `repo` scope
- **OpenAI Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Anthropic Key**: Get from [Anthropic Console](https://console.anthropic.com/)

## Usage

### Basic Command (Markdown Output)

```bash
generate-release-notes \
  --repo owner/repo \
  --from-tag v1.0.0 \
  --to-tag v1.1.0 \
  --llm-provider openai
```

### Confluence Format Output

```bash
generate-release-notes \
  --repo owner/repo \
  --from-tag v1.0.0 \
  --to-tag v1.1.0 \
  --llm-provider anthropic \
  --format confluence \
  --output release_notes_confluence.html
```

### Local Testing Mode

```bash
# Test with sample data (no API calls)
generate-release-notes \
  --repo local \
  --from-tag v1.0.0 \
  --to-tag v1.1.0 \
  --llm-provider openai \
  --format confluence
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--repo` | GitHub repo (owner/repo) or "local" for samples | Required |
| `--from-tag` | Starting tag/version | Required |
| `--to-tag` | Ending tag/version | Required |
| `--llm-provider` | LLM provider: `openai` or `anthropic` | `openai` |
| `--format` | Output format: `markdown` or `confluence` | `markdown` |
| `--output` | Output file name | `release_notes.txt` |

## Output Formats

### Markdown Format

Standard GitHub-flavored markdown with emoji sections:

```markdown
## Release Notes

🚀 **New Features**
- Add user authentication (PR #123 - [Auth System](https://...))
- Implement dark mode (PR #124 - [Dark Mode UI](https://...))

🐛 **Bug Fixes**
- Fix login redirect issue (PR #125 - [Login Fix](https://...))
```

### Confluence Format

Confluence Storage Format (XHTML) with colored panels and status badges:

```html
<h1>Release Notes: v1.1.0</h1>

<ac:structured-macro ac:name="info">
  <ac:rich-text-body>
    <p><strong>Release Date:</strong> 2025-11-01</p>
    <p><strong>Total Commits:</strong> 15</p>
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

## Using Confluence Output

### Method 1: Insert Markup (Recommended)

1. Open your Confluence page in edit mode
2. Click the **`</>`** (Insert markup) button in the toolbar
3. Copy the contents of your output file
4. Paste into the markup editor
5. Click **Insert**

### Method 2: Source Editor

1. Edit your Confluence page
2. Click **···** (More) → **View source**
3. Paste the Confluence-formatted content
4. Save the page

## Project Structure

```
multi-agent-release-notes/
├── generate_release_notes.sh
├── pyproject.toml.backup
├── README.md
├── release_confluence.html
├── release_notes.txt
├── requirements.txt
├── samples
│   ├── commits.txt
│   └── pr.txt
├── setup.py
└── src
    ├── __init__.py
    ├── confluence_formatter.py
    ├── generator.py
    ├── github_client.py
    ├── llm_client.py
    └── main.py
```

## Confluence Styling Reference

The tool uses these color schemes for Confluence panels:

| Category | Emoji | Color | Hex Code |
|----------|-------|-------|----------|
| New Features | 🚀 | Green | #E3FCEF |
| Bug Fixes | 🐛 | Red | #FFEBE6 |
| Changes | 📄 | Blue | #DEEBFF |
| Documentation | 📝 | Grey | #F4F5F7 |
| Style | 💅 | Yellow | #FFF0B3 |
| Tests | 🧪 | Purple | #EAE6FF |

## Examples

### Example 1: Generate Markdown Notes

```bash
generate-release-notes \
  --repo facebook/react \
  --from-tag v18.0.0 \
  --to-tag v18.1.0 \
  --llm-provider openai
```

Output: `release_notes.txt` (Markdown)

### Example 2: Generate Confluence Notes with Claude

```bash
generate-release-notes \
  --repo kubernetes/kubernetes \
  --from-tag v1.28.0 \
  --to-tag v1.29.0 \
  --llm-provider anthropic \
  --format confluence \
  --output k8s_release_v1.29.html
```

Output: `k8s_release_v1.29.html` (Confluence XHTML)

### Example 3: Test Locally

```bash
# First, create sample files
mkdir -p samples
echo "Fix authentication bug
Add user profile page
Update documentation" > samples/commits.txt

echo "123|Auth Bug Fix|https://github.com/org/repo/pull/123
124|User Profile|https://github.com/org/repo/pull/124" > samples/pr.txt

# Generate notes
generate-release-notes \
  --repo local \
  --from-tag v1.0.0 \
  --to-tag v1.1.0 \
  --format confluence
```

## Troubleshooting

### "Error: Set GITHUB_TOKEN in .env"
- Ensure your `.env` file exists and contains a valid GitHub token
- Check token permissions (needs `repo` scope)

### "OpenAI API error" or "Anthropic API error"
- Verify your API key is correct
- Check your API quota/credits
- The tool will fallback to basic formatting if LLM fails

### Confluence Format Not Rendering
- Ensure you're using the "Insert markup" method
- Check for any HTML validation errors
- Try the source editor method instead

### Rate Limiting
- GitHub API: 5,000 requests/hour (authenticated)
- Add delays between requests if processing many tags
- Use local mode for testing to avoid API calls

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=multi_agent_release_notes
```

### Adding New Features

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or contributions, please open an issue on GitHub.
