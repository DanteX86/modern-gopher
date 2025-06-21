"""
Markdown content processor plugin.

This plugin processes markdown content and renders it with syntax highlighting.
"""

from typing import Dict, Any, Tuple
from ..base import ContentProcessor, PluginMetadata


class MarkdownProcessor(ContentProcessor):
    """Plugin that processes Markdown content."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="markdown_processor",
            version="1.0.0",
            author="Modern Gopher Team",
            description="Processes Markdown content with syntax highlighting",
            dependencies=["rich"]
        )
    
    def should_process(self, content: str, metadata: Dict[str, Any]) -> bool:
        """Check if content should be processed as Markdown."""
        # Check if explicitly marked as markdown
        if metadata.get('content_type') == 'markdown':
            return True
        
        # Check file extension from selector
        selector = metadata.get('selector', '')
        if selector.endswith(('.md', '.markdown')):
            return True
        
        # Check for markdown-like patterns in content
        lines = content.split('\n')[:10]  # Check first 10 lines
        markdown_indicators = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Headers
            if line.startswith('#'):
                markdown_indicators += 2
            # Links
            elif '[' in line and '](' in line:
                markdown_indicators += 1
            # Bold/italic
            elif '**' in line or '__' in line or '*' in line or '_' in line:
                markdown_indicators += 1
            # Code blocks
            elif line.startswith('```') or line.startswith('    '):
                markdown_indicators += 1
            # Lists
            elif line.startswith(('- ', '* ', '+ ')) or (len(line) > 2 and line[0].isdigit() and line[1:3] == '. '):
                markdown_indicators += 1
        
        # Consider it markdown if we found multiple indicators
        return markdown_indicators >= 2
    
    def process(self, content: str, metadata: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Process markdown content."""
        try:
            from rich.markdown import Markdown
            from rich.console import Console
            from io import StringIO
            
            # Create a markdown object
            markdown = Markdown(content)
            
            # Render to string using Rich console
            console = Console(file=StringIO(), width=80, force_terminal=True)
            console.print(markdown)
            rendered_content = console.file.getvalue()
            
            # Update metadata
            metadata = metadata.copy()
            metadata['processed_as'] = 'markdown'
            metadata['processor'] = self.metadata.name
            metadata['original_length'] = len(content)
            metadata['processed_length'] = len(rendered_content)
            
            return rendered_content, metadata
            
        except ImportError:
            # Rich not available, return content as-is
            metadata = metadata.copy()
            metadata['processing_error'] = 'Rich library not available for markdown rendering'
            return content, metadata
        except Exception as e:
            # Fallback on error
            metadata = metadata.copy()
            metadata['processing_error'] = f'Markdown processing failed: {str(e)}'
            return content, metadata
    
    def get_processing_order(self) -> int:
        """Process markdown early in the pipeline."""
        return 50

