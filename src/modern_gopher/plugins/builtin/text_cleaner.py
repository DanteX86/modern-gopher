"""
Text cleaning content processor plugin.

This plugin cleans up text content by removing excessive whitespace,
fixing encoding issues, and standardizing line endings.
"""

import re
from typing import Any
from typing import Dict
from typing import Tuple

from ..base import ContentProcessor
from ..base import PluginMetadata


class TextCleaner(ContentProcessor):
    """Plugin that cleans up text content."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="text_cleaner",
            version="1.0.0",
            author="Modern Gopher Team",
            description=("Cleans up text content by removing excessive "
                         "whitespace and fixing formatting")
        )

    def should_process(self, content: str, metadata: Dict[str, Any]) -> bool:
        """Check if content should be cleaned."""
        # Only process text content
        content_type = metadata.get('content_type')
        if content_type and content_type != 'text':
            return False

        # Skip if already processed
        if metadata.get('text_cleaned'):
            return False

        # Always clean text unless disabled
        return self.get_config('enabled', True)

    def process(self, content: str,
                metadata: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Clean up text content."""
        original_length = len(content)
        cleaned_content = content
        changes_made = []

        # Remove carriage returns (normalize line endings)
        if '\r' in cleaned_content:
            cleaned_content = cleaned_content.replace(
                '\r\n', '\n').replace('\r', '\n')
            changes_made.append('normalized_line_endings')

        # Remove trailing whitespace from lines
        if self.get_config('remove_trailing_whitespace', True):
            lines = cleaned_content.split('\n')
            stripped_lines = [line.rstrip() for line in lines]
            if lines != stripped_lines:
                cleaned_content = '\n'.join(stripped_lines)
                changes_made.append('removed_trailing_whitespace')

        # Remove excessive blank lines (more than 2 consecutive)
        if self.get_config('limit_blank_lines', True):
            max_blank_lines = self.get_config('max_consecutive_blank_lines', 2)
            pattern = '\n' * (max_blank_lines + 2)  # 3+ consecutive newlines
            # Replace with max allowed
            replacement = '\n' * (max_blank_lines + 1)

            if pattern in cleaned_content:
                cleaned_content = re.sub(
                    r'\n{3,}', replacement, cleaned_content)
                changes_made.append('limited_blank_lines')

        # Remove leading/trailing whitespace from the entire content
        if self.get_config('strip_content', True):
            stripped_content = cleaned_content.strip()
            if stripped_content != cleaned_content:
                cleaned_content = stripped_content
                changes_made.append('stripped_content')

        # Fix common encoding issues
        if self.get_config('fix_encoding', True):
            # Replace common problematic characters
            replacements = {
                '\u2018': "'",  # Left single quotation mark
                '\u2019': "'",  # Right single quotation mark
                '\u201c': '"',  # Left double quotation mark
                '\u201d': '"',  # Right double quotation mark
                '\u2013': '-',  # En dash
                '\u2014': '--',  # Em dash
                '\u2026': '...',  # Ellipsis
            }

            for old, new in replacements.items():
                if old in cleaned_content:
                    cleaned_content = cleaned_content.replace(old, new)
                    changes_made.append('fixed_encoding')

        # Update metadata
        metadata = metadata.copy()
        metadata['text_cleaned'] = True
        metadata['original_text_length'] = original_length
        metadata['cleaned_text_length'] = len(cleaned_content)
        metadata['cleaning_changes'] = changes_made

        if changes_made:
            metadata['text_cleaning_applied'] = True
            saved_chars = original_length - len(cleaned_content)
            if saved_chars > 0:
                metadata['characters_removed'] = saved_chars

        return cleaned_content, metadata

    def get_processing_order(self) -> int:
        """Process text cleaning very early in the pipeline."""
        return 10
