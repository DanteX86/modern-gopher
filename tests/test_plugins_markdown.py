#!/usr/bin/env python3
"""
Tests for markdown processor plugin.
"""

import unittest
from unittest.mock import MagicMock, patch

from modern_gopher.plugins.builtin.markdown_processor import MarkdownProcessor


class TestMarkdownProcessor(unittest.TestCase):
    """Test MarkdownProcessor plugin."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = MarkdownProcessor()

    def test_metadata_properties(self):
        """Test metadata properties."""
        metadata = self.processor.metadata
        
        self.assertEqual(metadata.name, "markdown_processor")
        self.assertEqual(metadata.version, "1.0.0")
        self.assertEqual(metadata.author, "Modern Gopher Team")
        self.assertIn("Markdown", metadata.description)
        self.assertIn("rich", metadata.dependencies)

    def test_can_process_explicit_markdown_content_type(self):
        """Test can_process with explicit markdown content type."""
        content = "# Hello World"
        metadata = {"content_type": "markdown"}
        
        self.assertTrue(self.processor.can_process(content, metadata))

    def test_can_process_markdown_file_extensions(self):
        """Test can_process with markdown file extensions."""
        content = "Some content"
        
        # Test .md extension
        metadata = {"selector": "document.md"}
        self.assertTrue(self.processor.can_process(content, metadata))
        
        # Test .markdown extension
        metadata = {"selector": "readme.markdown"}
        self.assertTrue(self.processor.can_process(content, metadata))

    def test_can_process_non_string_content(self):
        """Test can_process with non-string content."""
        metadata = {}
        
        self.assertFalse(self.processor.can_process(b"binary content", metadata))
        self.assertFalse(self.processor.can_process(123, metadata))
        self.assertFalse(self.processor.can_process(None, metadata))

    def test_can_process_markdown_headers(self):
        """Test can_process with markdown headers."""
        content = """
# Main Header
Some text here
## Sub Header
More content
"""
        metadata = {}
        
        # Should detect headers and return True
        self.assertTrue(self.processor.can_process(content, metadata))

    def test_can_process_markdown_links(self):
        """Test can_process with markdown links."""
        content = """
This is a [link](http://example.com) in markdown.
Another [link here](http://test.com).
Regular text.
"""
        metadata = {}
        
        # Should detect links and return True
        self.assertTrue(self.processor.can_process(content, metadata))

    def test_can_process_markdown_formatting(self):
        """Test can_process with markdown formatting."""
        content = """
This has **bold text** and *italic text*.
Also __underline__ and _emphasis_.
Regular text without formatting.
"""
        metadata = {}
        
        # Should detect formatting and return True
        self.assertTrue(self.processor.can_process(content, metadata))

    def test_can_process_markdown_code_blocks(self):
        """Test can_process with markdown code blocks."""
        content = """
```python
def hello():
    print("Hello World")
```

    indented code block
    more code here
"""
        metadata = {}
        
        # Should detect code blocks and return True
        self.assertTrue(self.processor.can_process(content, metadata))

    def test_can_process_markdown_lists(self):
        """Test can_process with markdown lists."""
        content = """
- Item one
- Item two
* Another item
+ Plus item
1. Numbered item
2. Another number
"""
        metadata = {}
        
        # Should detect lists and return True
        self.assertTrue(self.processor.can_process(content, metadata))

    def test_can_process_insufficient_markdown_indicators(self):
        """Test can_process with insufficient markdown indicators."""
        content = """
Just plain text.
Nothing special here.
Regular paragraph.
"""
        metadata = {}
        
        # Should not detect as markdown
        self.assertFalse(self.processor.can_process(content, metadata))

    def test_can_process_single_markdown_indicator(self):
        """Test can_process with single markdown indicator."""
        content = """
Just some text with a *single* italic word.
Nothing else special.
"""
        metadata = {}
        
        # Should not detect as markdown (need >=2 indicators)
        self.assertFalse(self.processor.can_process(content, metadata))

    def test_can_process_empty_lines_ignored(self):
        """Test can_process ignores empty lines."""
        content = """

# Header


Some text with **bold**.

"""
        metadata = {}
        
        # Should detect as markdown despite empty lines
        self.assertTrue(self.processor.can_process(content, metadata))

    @patch('rich.markdown.Markdown')
    @patch('rich.console.Console')
    def test_process_successful_rendering(self, mock_console, mock_markdown):
        """Test successful markdown processing."""
        # Setup mocks
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance
        mock_console_instance.file.getvalue.return_value = "Rendered markdown content"
        
        content = "# Hello World"
        metadata = {"selector": "test.md"}
        
        result_content, result_metadata = self.processor.process(content, metadata)
        
        # Check result
        self.assertEqual(result_content, "Rendered markdown content")
        self.assertEqual(result_metadata["processed_as"], "markdown")
        self.assertEqual(result_metadata["processor"], "markdown_processor")
        self.assertEqual(result_metadata["original_length"], len(content))
        self.assertEqual(result_metadata["processed_length"], len("Rendered markdown content"))
        
        # Verify mocks were called
        mock_markdown.assert_called_once_with(content)
        mock_console.assert_called_once()
        mock_console_instance.print.assert_called_once()

    def test_process_import_error_fallback(self):
        """Test process with ImportError (Rich not available)."""
        content = "# Hello World"
        metadata = {"selector": "test.md"}
        
        with patch('rich.console.Console', side_effect=ImportError):
            result_content, result_metadata = self.processor.process(content, metadata)
        
        # Should return original content
        self.assertEqual(result_content, content)
        self.assertIn("processing_error", result_metadata)
        self.assertIn("Rich library not available", result_metadata["processing_error"])

    @patch('rich.markdown.Markdown')
    @patch('rich.console.Console')
    def test_process_exception_handling(self, mock_console, mock_markdown):
        """Test process with general exception."""
        # Setup mocks to raise exception
        mock_console.side_effect = Exception("Test error")
        
        content = "# Hello World"
        metadata = {"selector": "test.md"}
        
        result_content, result_metadata = self.processor.process(content, metadata)
        
        # Should return original content with error metadata
        self.assertEqual(result_content, content)
        self.assertIn("processing_error", result_metadata)
        self.assertIn("Markdown processing failed: Test error", result_metadata["processing_error"])

    def test_process_metadata_copy(self):
        """Test that process creates a copy of metadata."""
        content = "# Hello World"
        original_metadata = {"selector": "test.md", "existing": "value"}
        
        with patch('rich.console.Console', side_effect=ImportError):
            _, result_metadata = self.processor.process(content, original_metadata)
        
        # Original metadata should not be modified
        self.assertNotIn("processing_error", original_metadata)
        self.assertEqual(original_metadata["existing"], "value")
        
        # Result metadata should be different object
        self.assertIsNot(result_metadata, original_metadata)
        self.assertEqual(result_metadata["existing"], "value")
        self.assertIn("processing_error", result_metadata)

    def test_get_processing_order(self):
        """Test processing order."""
        self.assertEqual(self.processor.get_processing_order(), 50)


class TestMarkdownProcessorIntegration(unittest.TestCase):
    """Integration tests for MarkdownProcessor."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = MarkdownProcessor()

    def test_real_markdown_processing_if_rich_available(self):
        """Test real markdown processing if Rich is available."""
        try:
            from rich.console import Console
            from rich.markdown import Markdown
            
            # Rich is available, test real processing
            content = "# Hello World\n\nThis is **bold** text."
            metadata = {"selector": "test.md"}
            
            result_content, result_metadata = self.processor.process(content, metadata)
            
            # Should have processed content
            self.assertNotEqual(result_content, content)
            self.assertEqual(result_metadata["processed_as"], "markdown")
            self.assertEqual(result_metadata["processor"], "markdown_processor")
            self.assertIn("original_length", result_metadata)
            self.assertIn("processed_length", result_metadata)
            
        except ImportError:
            # Rich not available, skip this test
            self.skipTest("Rich library not available for integration test")

    def test_complex_markdown_detection(self):
        """Test complex markdown content detection."""
        complex_markdown = """
# Project Documentation

## Overview

This project implements a **gopher client** with the following features:

- Modern terminal interface
- Bookmark management
- Session support

### Installation

```bash
pip install modern-gopher
```

For more information, see [the documentation](http://example.com/docs).

1. Download the package
2. Install dependencies
3. Run the application
"""
        
        metadata = {}
        
        # Should definitely detect as markdown
        self.assertTrue(self.processor.can_process(complex_markdown, metadata))

    def test_borderline_markdown_detection(self):
        """Test borderline cases for markdown detection."""
        # Exactly 2 indicators (boundary case)
        content_with_two = """
# A Header
Some **bold** text.
Regular text here.
"""
        
        # Should detect as markdown (>=2 indicators)
        self.assertTrue(self.processor.can_process(content_with_two, {}))
        
        # Just one indicator
        content_with_one = """
Some text with just **bold** formatting.
Regular text here.
Nothing else special.
"""
        
        # Should not detect as markdown (<2 indicators)
        self.assertFalse(self.processor.can_process(content_with_one, {}))


if __name__ == "__main__":
    unittest.main()

