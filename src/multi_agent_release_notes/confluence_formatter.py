"""
Confluence Storage Format (XHTML) formatter for release notes.
"""
from typing import List, Dict, Any
from datetime import datetime
import html


class ConfluenceFormatter:
    """Formats release notes in Confluence Storage Format (XHTML)."""
    
    # Emoji to Confluence status macro mapping
    EMOJI_TO_STATUS = {
        '🚀': {'color': 'Green', 'title': 'NEW'},
        '🐛': {'color': 'Red', 'title': 'FIX'},
        '📄': {'color': 'Blue', 'title': 'CHANGE'},
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
        Format release notes in Confluence Storage Format.
        
        Args:
            commits: List of commit dictionaries
            from_tag: Starting tag
            to_tag: Ending tag
            repo: Repository name (owner/repo)
            notes_content: Pre-generated markdown notes to convert
            
        Returns:
            Confluence Storage Format XHTML string
        """
        if notes_content:
            # Convert markdown-style notes to Confluence format
            return ConfluenceFormatter._convert_markdown_to_confluence(
                notes_content, commits, from_tag, to_tag, repo
            )
        else:
            # Generate from scratch
            return ConfluenceFormatter._generate_confluence_notes(
                commits, from_tag, to_tag, repo
            )

    @staticmethod
    def _generate_confluence_notes(
        commits: List[Dict[str, Any]],
        from_tag: str,
        to_tag: str,
        repo: str = None
    ) -> str:
        """Generate Confluence-formatted notes from scratch."""
        output = []
        
        # Title
        output.append(f'<h1>Release Notes: {to_tag}</h1>')
        output.append('')
        
        # Metadata info box
        output.append(ConfluenceFormatter._create_metadata_box(
            from_tag, to_tag, len(commits), repo
        ))
        output.append('')
        
        # Group commits by type (simple categorization)
        categorized = ConfluenceFormatter._categorize_commits(commits)
        
        # Generate sections
        for category, category_commits in categorized.items():
            if category_commits:
                output.append(ConfluenceFormatter._create_section_panel(
                    category, category_commits
                ))
                output.append('')
        
        return '\n'.join(output)

    @staticmethod
    def _convert_markdown_to_confluence(
        markdown_notes: str,
        commits: List[Dict[str, Any]],
        from_tag: str,
        to_tag: str,
        repo: str = None
    ) -> str:
        """Convert markdown-style notes to Confluence format."""
        output = []
        
        # Title
        output.append(f'<h1>Release Notes: {to_tag}</h1>')
        output.append('')
        
        # Metadata info box
        output.append(ConfluenceFormatter._create_metadata_box(
            from_tag, to_tag, len(commits), repo
        ))
        output.append('')
        
        # Parse markdown sections
        lines = markdown_notes.split('\n')
        current_section = None
        current_items = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and document title
            if not line or line.startswith('##'):
                if line.startswith('##'):
                    # Save previous section
                    if current_section and current_items:
                        output.append(ConfluenceFormatter._create_section_panel(
                            current_section, current_items, is_markdown=True
                        ))
                        output.append('')
                    
                    # Start new section
                    current_section = line.replace('##', '').strip()
                    current_items = []
                continue
            
            # Collect items
            if line.startswith('-') or line.startswith('*'):
                current_items.append(line[1:].strip())
        
        # Add last section
        if current_section and current_items:
            output.append(ConfluenceFormatter._create_section_panel(
                current_section, current_items, is_markdown=True
            ))
        
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
    def _create_section_panel(
        section_name: str,
        items: List[Any],
        is_markdown: bool = False
    ) -> str:
        """Create a colored panel for a section."""
        # Determine emoji and color
        emoji = ''
        section_lower = section_name.lower()
        
        for key, color in ConfluenceFormatter.SECTION_COLORS.items():
            if key in section_lower:
                bg_color = color
                break
        else:
            bg_color = '#F4F5F7'  # Default gray
        
        # Extract emoji from section name if present
        for emoji_char in ConfluenceFormatter.EMOJI_TO_STATUS.keys():
            if emoji_char in section_name:
                emoji = emoji_char
                section_name = section_name.replace(emoji_char, '').strip()
                break
        
        # Build items list
        items_html = '<ul>\n'
        for item in items:
            if is_markdown:
                # Process markdown-style item
                item_html = ConfluenceFormatter._process_markdown_item(item)
            else:
                # Process commit dict
                item_html = ConfluenceFormatter._format_commit_item(item)
            items_html += f'  <li>{item_html}</li>\n'
        items_html += '</ul>'
        
        # Create status badge if emoji present
        title_with_badge = section_name
        if emoji and emoji in ConfluenceFormatter.EMOJI_TO_STATUS:
            status_info = ConfluenceFormatter.EMOJI_TO_STATUS[emoji]
            title_with_badge = f'''<ac:structured-macro ac:name="status" ac:schema-version="1">
  <ac:parameter ac:name="colour">{status_info['color']}</ac:parameter>
  <ac:parameter ac:name="title">{status_info['title']}</ac:parameter>
</ac:structured-macro> {section_name}'''
        
        return f'''<ac:structured-macro ac:name="panel" ac:schema-version="1">
  <ac:parameter ac:name="bgColor">{bg_color}</ac:parameter>
  <ac:parameter ac:name="title">{title_with_badge}</ac:parameter>
  <ac:rich-text-body>
{items_html}
  </ac:rich-text-body>
</ac:structured-macro>'''

    @staticmethod
    def _format_commit_item(commit: Dict[str, Any]) -> str:
        """Format a single commit as Confluence HTML."""
        message = html.escape(commit.get('message', ''))
        
        if commit.get('pr_number'):
            pr_link = f'<a href="{commit["pr_url"]}">PR #{commit["pr_number"]}</a>'
            pr_title = html.escape(commit.get('pr_title', ''))
            return f'<strong>{message}</strong> - {pr_link}: {pr_title}'
        else:
            return f'<strong>{message}</strong>'

    @staticmethod
    def _process_markdown_item(item: str) -> str:
        """Process markdown-style list item to Confluence HTML."""
        # Convert markdown links [text](url) to HTML
        import re
        
        # Handle PR links
        item = re.sub(
            r'\[([^\]]+)\]\(([^)]+)\)',
            r'<a href="\2">\1</a>',
            item
        )
        
        # Handle bold **text**
        item = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', item)
        
        # Handle italic *text*
        item = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', item)
        
        # Handle code `code`
        item = re.sub(r'`([^`]+)`', r'<code>\1</code>', item)
        
        return item

    @staticmethod
    def _categorize_commits(commits: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize commits by type based on keywords."""
        categories = {
            '🚀 New Features': [],
            '🐛 Bug Fixes': [],
            '📄 Changes': [],
            '📝 Documentation': [],
            '💅 Style': [],
            '🧪 Tests': [],
        }
        
        for commit in commits:
            message = commit.get('message', '').lower()
            pr_title = (commit.get('pr_title') or '').lower()
            combined = f'{message} {pr_title}'
            
            categorized = False
            
            if any(word in combined for word in ['feat', 'feature', 'add', 'new']):
                categories['🚀 New Features'].append(commit)
                categorized = True
            elif any(word in combined for word in ['fix', 'bug', 'issue', 'resolve']):
                categories['🐛 Bug Fixes'].append(commit)
                categorized = True
            elif any(word in combined for word in ['doc', 'readme', 'comment']):
                categories['📝 Documentation'].append(commit)
                categorized = True
            elif any(word in combined for word in ['test', 'spec']):
                categories['🧪 Tests'].append(commit)
                categorized = True
            elif any(word in combined for word in ['style', 'format', 'lint']):
                categories['💅 Style'].append(commit)
                categorized = True
            
            if not categorized:
                categories['📄 Changes'].append(commit)
        
        return categories
