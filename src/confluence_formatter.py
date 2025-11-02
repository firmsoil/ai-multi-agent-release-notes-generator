"""
Confluence Storage Format (XHTML) formatter for release notes.
Generates tabular format with JIRA IDs extracted from PR titles.
"""
from typing import List, Dict, Any
from datetime import datetime
import html
import re
import os
from dotenv import load_dotenv

load_dotenv()

# Get JIRA base URL from environment or use default
JIRA_BASE_URL = os.getenv('JIRA_BASE_URL', 'https://jira.example.com')


class ConfluenceFormatter:
    """Formats release notes in Confluence Storage Format (XHTML) with tables."""
    
    # Common JIRA ID patterns
    JIRA_PATTERN = re.compile(r'\b([A-Z]{2,10}-\d+)\b')
    
    # Emoji to Confluence status macro mapping
    EMOJI_TO_STATUS = {
        '🚀': {'color': 'Green', 'title': 'NEW'},
        '🐛': {'color': 'Red', 'title': 'FIX'},
        '🔄': {'color': 'Blue', 'title': 'CHANGE'},
        '📝': {'color': 'Grey', 'title': 'DOCS'},
        '💅': {'color': 'Yellow', 'title': 'STYLE'},
        '🧪': {'color': 'Purple', 'title': 'TEST'},
    }
    
    # Section to panel color mapping
    SECTION_COLORS = {
        'new features': '#E3FCEF',
        'bug fixes': '#FFEBE6',
        'changes': '#DEEBFF',
        'documentation': '#F4F5F7',
        'style': '#FFF0B3',
        'tests': '#EAE6FF',
    }

    @staticmethod
    def format_release_notes(
        commits: List[Dict[str, Any]],
        from_tag: str,
        to_tag: str,
        repo: str = None,
        notes_content: str = None
    ) -> str:
        """
        Format release notes in Confluence Storage Format with tabular layout.
        
        Args:
            commits: List of commit dictionaries with PR info
            from_tag: Starting tag
            to_tag: Ending tag
            repo: Repository name (owner/repo)
            notes_content: Pre-generated markdown notes (ignored for table format)
            
        Returns:
            Confluence Storage Format XHTML string with tables
        """
        return ConfluenceFormatter._generate_table_format(
            commits, from_tag, to_tag, repo
        )

    @staticmethod
    def _extract_jira_ids(text: str) -> List[str]:
        """Extract JIRA IDs from text (PR title, commit message, etc.)."""
        if not text:
            return []
        matches = ConfluenceFormatter.JIRA_PATTERN.findall(text)
        # Return unique JIRA IDs in order of appearance
        seen = set()
        result = []
        for match in matches:
            if match not in seen:
                seen.add(match)
                result.append(match)
        return result

    @staticmethod
    def _generate_table_format(
        commits: List[Dict[str, Any]],
        from_tag: str,
        to_tag: str,
        repo: str = None
    ) -> str:
        """Generate Confluence-formatted release notes in table format."""
        output = []
        
        # Title
        output.append(f'<h1>Release Notes: {to_tag}</h1>')
        output.append('')
        
        # Metadata info box
        output.append(ConfluenceFormatter._create_metadata_box(
            from_tag, to_tag, len(commits), repo
        ))
        output.append('')
        
        # Categorize commits
        categorized = ConfluenceFormatter._categorize_commits(commits)
        
        # Generate a table for each category
        for category, category_commits in categorized.items():
            if category_commits:
                output.append(ConfluenceFormatter._create_category_table(
                    category, category_commits, repo
                ))
                output.append('')
        
        # Summary statistics
        output.append(ConfluenceFormatter._create_summary_section(commits))
        
        return '\n'.join(output)

    @staticmethod
    def _create_metadata_box(
        from_tag: str,
        to_tag: str,
        commit_count: int,
        repo: str = None
    ) -> str:
        """Create metadata information box."""
        release_date = datetime.now().strftime('%Y-%m-%d')
        
        info_content = f'<p><strong>Release Date:</strong> {release_date}</p>'
        info_content += f'<p><strong>Version:</strong> {to_tag}</p>'
        info_content += f'<p><strong>Previous Version:</strong> {from_tag}</p>'
        info_content += f'<p><strong>Total Commits:</strong> {commit_count}</p>'
        
        if repo:
            compare_url = f'https://github.com/{repo}/compare/{from_tag}...{to_tag}'
            info_content += f'<p><strong>Compare:</strong> <a href="{compare_url}">View Changes</a></p>'
        
        return f'''<ac:structured-macro ac:name="info" ac:schema-version="1">
  <ac:rich-text-body>
{info_content}
  </ac:rich-text-body>
</ac:structured-macro>'''

    @staticmethod
    def _create_category_table(
        category: str,
        commits: List[Dict[str, Any]],
        repo: str = None
    ) -> str:
        """Create a table for a specific category with colored header."""
        # Determine color for this category
        category_lower = category.lower()
        bg_color = '#F4F5F7'  # Default gray
        
        for key, color in ConfluenceFormatter.SECTION_COLORS.items():
            if key in category_lower:
                bg_color = color
                break
        
        # Extract emoji from category name
        emoji = ''
        section_name = category
        for emoji_char in ConfluenceFormatter.EMOJI_TO_STATUS.keys():
            if emoji_char in category:
                emoji = emoji_char
                section_name = category.replace(emoji_char, '').strip()
                break
        
        # Create title with status badge
        title_html = section_name
        if emoji and emoji in ConfluenceFormatter.EMOJI_TO_STATUS:
            status_info = ConfluenceFormatter.EMOJI_TO_STATUS[emoji]
            title_html = f'''<ac:structured-macro ac:name="status" ac:schema-version="1">
  <ac:parameter ac:name="colour">{status_info['color']}</ac:parameter>
  <ac:parameter ac:name="title">{status_info['title']}</ac:parameter>
</ac:structured-macro> {section_name}'''
        
        # Build table HTML
        table_html = f'''<h2>{title_html}</h2>
<table>
  <thead>
    <tr>
      <th style="background-color: {bg_color}; padding: 8px; border: 1px solid #ddd;"><strong>JIRA ID</strong></th>
      <th style="background-color: {bg_color}; padding: 8px; border: 1px solid #ddd;"><strong>Pull Request #</strong></th>
      <th style="background-color: {bg_color}; padding: 8px; border: 1px solid #ddd;"><strong>Commit Hash</strong></th>
      <th style="background-color: {bg_color}; padding: 8px; border: 1px solid #ddd;"><strong>Committer</strong></th>
      <th style="background-color: {bg_color}; padding: 8px; border: 1px solid #ddd;"><strong>Description</strong></th>
    </tr>
  </thead>
  <tbody>
'''
        
        # Add rows for each commit
        for commit in commits:
            table_html += ConfluenceFormatter._create_table_row(commit, repo)
        
        table_html += '''  </tbody>
</table>'''
        
        return table_html

    @staticmethod
    def _create_table_row(commit: Dict[str, Any], repo: str = None) -> str:
        """Create a single table row for a commit."""
        # Extract JIRA IDs from PR title and commit message
        pr_title = commit.get('pr_title', '')
        commit_message = commit.get('message', '')
        
        jira_ids = ConfluenceFormatter._extract_jira_ids(pr_title)
        if not jira_ids:
            jira_ids = ConfluenceFormatter._extract_jira_ids(commit_message)
        
        # Format JIRA IDs with links
        if jira_ids:
            jira_links = []
            for jira_id in jira_ids:
                jira_url = f'{JIRA_BASE_URL}/browse/{jira_id}'
                jira_links.append(f'<a href="{jira_url}">{jira_id}</a>')
            jira_cell = '<br/>'.join(jira_links)
        else:
            jira_cell = '<em>N/A</em>'
        
        # Format PR number with link
        if commit.get('pr_number'):
            pr_url = commit.get('pr_url', '#')
            pr_cell = f'<a href="{pr_url}">#{commit["pr_number"]}</a>'
        else:
            pr_cell = '<em>N/A</em>'
        
        # Format commit hash (short version with link)
        sha = commit.get('sha', 'unknown')
        short_sha = sha[:7]
        if repo:
            commit_url = f'https://github.com/{repo}/commit/{sha}'
            sha_cell = f'<code><a href="{commit_url}">{short_sha}</a></code>'
        else:
            sha_cell = f'<code>{short_sha}</code>'
        
        # Committer - use author_name from commit data
        author_name = commit.get('author_name', 'Unknown')
        committer_cell = html.escape(author_name)
        
        # Description - use PR title if available, otherwise commit message
        description = html.escape(pr_title if pr_title else commit_message)
        # Truncate if too long
        if len(description) > 100:
            description = description[:97] + '...'
        
        return f'''    <tr>
      <td style="padding: 8px; border: 1px solid #ddd;">{jira_cell}</td>
      <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{pr_cell}</td>
      <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{sha_cell}</td>
      <td style="padding: 8px; border: 1px solid #ddd;">{committer_cell}</td>
      <td style="padding: 8px; border: 1px solid #ddd;">{description}</td>
    </tr>
'''

    @staticmethod
    def _create_summary_section(commits: List[Dict[str, Any]]) -> str:
        """Create a summary statistics section."""
        total_commits = len(commits)
        commits_with_pr = sum(1 for c in commits if c.get('pr_number'))
        
        # Extract all unique JIRA IDs
        all_jira_ids = set()
        for commit in commits:
            pr_title = commit.get('pr_title', '')
            commit_message = commit.get('message', '')
            jira_ids = ConfluenceFormatter._extract_jira_ids(pr_title)
            if not jira_ids:
                jira_ids = ConfluenceFormatter._extract_jira_ids(commit_message)
            all_jira_ids.update(jira_ids)
        
        summary_html = '''<h2>📊 Summary</h2>
<table>
  <tbody>
    <tr>
      <td style="padding: 8px; border: 1px solid #ddd; background-color: #f9f9f9;"><strong>Total Commits</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">''' + str(total_commits) + '''</td>
    </tr>
    <tr>
      <td style="padding: 8px; border: 1px solid #ddd; background-color: #f9f9f9;"><strong>Commits with PRs</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">''' + str(commits_with_pr) + '''</td>
    </tr>
    <tr>
      <td style="padding: 8px; border: 1px solid #ddd; background-color: #f9f9f9;"><strong>Unique JIRA Issues</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">''' + str(len(all_jira_ids)) + '''</td>
    </tr>
  </tbody>
</table>'''
        
        if all_jira_ids:
            jira_list = ', '.join(sorted(all_jira_ids))
            summary_html += f'''
<p><strong>JIRA Issues in this release:</strong> {jira_list}</p>'''
        
        return summary_html

    @staticmethod
    def _categorize_commits(commits: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize commits by type based on keywords."""
        categories = {
            '🚀 New Features': [],
            '🐛 Bug Fixes': [],
            '🔄 Changes': [],
            '📝 Documentation': [],
            '💅 Style': [],
            '🧪 Tests': [],
        }
        
        for commit in commits:
            message = commit.get('message', '').lower()
            pr_title = (commit.get('pr_title') or '').lower()
            combined = f'{message} {pr_title}'
            
            categorized = False
            
            if any(word in combined for word in ['feat', 'feature', 'add', 'new', 'implement']):
                categories['🚀 New Features'].append(commit)
                categorized = True
            elif any(word in combined for word in ['fix', 'bug', 'issue', 'resolve', 'patch']):
                categories['🐛 Bug Fixes'].append(commit)
                categorized = True
            elif any(word in combined for word in ['doc', 'readme', 'comment', 'documentation']):
                categories['📝 Documentation'].append(commit)
                categorized = True
            elif any(word in combined for word in ['test', 'spec', 'testing']):
                categories['🧪 Tests'].append(commit)
                categorized = True
            elif any(word in combined for word in ['style', 'format', 'lint', 'refactor']):
                categories['💅 Style'].append(commit)
                categorized = True
            
            if not categorized:
                categories['🔄 Changes'].append(commit)
        
        return categories

    @staticmethod
    def _generate_confluence_notes(
        commits: List[Dict[str, Any]],
        from_tag: str,
        to_tag: str,
        repo: str = None
    ) -> str:
        """Generate Confluence-formatted notes (legacy method, now uses table format)."""
        return ConfluenceFormatter._generate_table_format(commits, from_tag, to_tag, repo)

    @staticmethod
    def _convert_markdown_to_confluence(
        markdown_notes: str,
        commits: List[Dict[str, Any]],
        from_tag: str,
        to_tag: str,
        repo: str = None
    ) -> str:
        """Convert markdown-style notes to Confluence format (uses table format)."""
        return ConfluenceFormatter._generate_table_format(commits, from_tag, to_tag, repo)

    @staticmethod
    def _format_commit_item(commit: Dict[str, Any]) -> str:
        """Format a single commit (legacy method for backward compatibility)."""
        message = html.escape(commit.get('message', ''))
        
        if commit.get('pr_number'):
            pr_number = commit['pr_number']
            pr_url = commit.get('pr_url', '#')
            pr_title = html.escape(commit.get('pr_title', ''))
            
            pr_link = f'<a href="{pr_url}">PR #{pr_number}</a>'
            return f'<strong>{message}</strong> ({pr_link}) - {pr_title}'
        else:
            return f'<strong>{message}</strong>'

    @staticmethod
    def _process_markdown_item(item: str) -> str:
        """Process markdown-style list item (legacy method)."""
        import re
        
        item = re.sub(
            r'\[PR #(\d+)\]\(([^)]+)\)',
            r'(<a href="\2">PR #\1</a>)',
            item
        )
        
        item = re.sub(
            r'\[([^\]]+)\]\(([^)]+)\)',
            r'<a href="\2">\1</a>',
            item
        )
        
        item = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', item)
        item = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', item)
        item = re.sub(r'`([^`]+)`', r'<code>\1</code>', item)
        
        return item
