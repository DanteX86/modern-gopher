#!/usr/bin/env python3
"""
Tests for text cleaner plugin.
"""

import unittest
from unittest.mock import MagicMock

from modern_gopher.plugins.builtin.text_cleaner import TextCleaner


class TestTextCleaner(unittest.TestCase):
    """Test TextCleaner plugin."""

    def setUp(self):
        """Set up test fixtures."""
        self.cleaner = TextCleaner()

    def test_metadata_properties(self):
        """Test metadata properties."""
        metadata = self.cleaner.metadata
        
        self.assertEqual(metadata.name, "text_cleaner")
        self.assertEqual(metadata.version, "1.0.0")
        self.assertEqual(metadata.author, "Modern Gopher Team")
        self.assertIn("text content", metadata.description)
        self.assertIn("whitespace", metadata.description)

    def test_can_process_string_content(self):
        """Test can_process with string content."""
        content = "Some text content"
        metadata = {}
        
        self.assertTrue(self.cleaner.can_process(content, metadata))

    def test_can_process_non_string_content(self):
        """Test can_process with non-string content."""
        metadata = {}
        
        self.assertFalse(self.cleaner.can_process(b"binary content", metadata))
        self.assertFalse(self.cleaner.can_process(123, metadata))
        self.assertFalse(self.cleaner.can_process(None, metadata))

    def test_can_process_already_cleaned(self):
        """Test can_process with already cleaned content."""
        content = "Some text"
        metadata = {"text_cleaned": True}
        
        self.assertFalse(self.cleaner.can_process(content, metadata))

    def test_can_process_text_content_type(self):
        """Test can_process with explicit text content type."""
        content = "Some text"
        metadata = {"content_type": "text"}
        
        self.assertTrue(self.cleaner.can_process(content, metadata))

    def test_can_process_markdown_content_type(self):
        """Test can_process with markdown content type."""
        content = "Some text"
        metadata = {"content_type": "markdown"}
        
        self.assertTrue(self.cleaner.can_process(content, metadata))

    def test_can_process_invalid_content_type(self):
        """Test can_process with invalid content type."""
        content = "Some text"
        metadata = {"content_type": "binary"}
        
        self.assertFalse(self.cleaner.can_process(content, metadata))

    def test_can_process_disabled_config(self):
        """Test can_process when disabled in config."""
        content = "Some text"
        metadata = {}
        
        # Mock config to disable the cleaner
        self.cleaner.config = {"enabled": False}
        
        self.assertFalse(self.cleaner.can_process(content, metadata))

    def test_process_normalize_line_endings(self):
        """Test processing normalizes line endings."""
        content = "Line 1\r\nLine 2\rLine 3\n"
        metadata = {}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        self.assertEqual(result_content, "Line 1\nLine 2\nLine 3")
        self.assertIn("normalized_line_endings", result_metadata["cleaning_changes"])

    def test_process_remove_trailing_whitespace(self):
        """Test processing removes trailing whitespace."""
        content = "Line 1   \nLine 2\t\nLine 3\n"
        metadata = {}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        self.assertEqual(result_content, "Line 1\nLine 2\nLine 3")
        self.assertIn("removed_trailing_whitespace", result_metadata["cleaning_changes"])

    def test_process_remove_trailing_whitespace_disabled(self):
        """Test processing with trailing whitespace removal disabled."""
        self.cleaner.config = {"remove_trailing_whitespace": False}
        content = "Line 1   \nLine 2\t\n"
        metadata = {}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        # Should still strip overall content by default (strip_content=True), but preserve line-level trailing whitespace
        self.assertEqual(result_content, "Line 1   \nLine 2\t")
        self.assertNotIn("removed_trailing_whitespace", result_metadata["cleaning_changes"])

    def test_process_limit_blank_lines(self):
        """Test processing limits excessive blank lines."""
        content = "Line 1\n\n\n\n\nLine 2"
        metadata = {}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        self.assertEqual(result_content, "Line 1\n\n\nLine 2")
        self.assertIn("limited_blank_lines", result_metadata["cleaning_changes"])

    def test_process_limit_blank_lines_custom_max(self):
        """Test processing with custom max blank lines."""
        self.cleaner.config = {"limit_blank_lines": True, "max_consecutive_blank_lines": 1}
        content = "Line 1\n\n\n\nLine 2"
        metadata = {}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        self.assertEqual(result_content, "Line 1\n\nLine 2")
        self.assertIn("limited_blank_lines", result_metadata["cleaning_changes"])

    def test_process_limit_blank_lines_disabled(self):
        """Test processing with blank line limiting disabled."""
        self.cleaner.config = {"limit_blank_lines": False}
        content = "Line 1\n\n\n\n\nLine 2"
        metadata = {}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        self.assertEqual(result_content, "Line 1\n\n\n\n\nLine 2")
        self.assertNotIn("limited_blank_lines", result_metadata["cleaning_changes"])

    def test_process_strip_content(self):
        """Test processing strips leading/trailing whitespace."""
        content = "  \n  Content here  \n  "
        metadata = {}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        self.assertEqual(result_content, "Content here")
        self.assertIn("stripped_content", result_metadata["cleaning_changes"])

    def test_process_strip_content_disabled(self):
        """Test processing with content stripping disabled."""
        self.cleaner.config = {"strip_content": False}
        content = "  \n  Content here  \n  "
        metadata = {}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        # Should still remove trailing whitespace from lines by default, but not strip overall content
        self.assertEqual(result_content, "\n  Content here\n")
        self.assertNotIn("stripped_content", result_metadata["cleaning_changes"])

    def test_process_fix_encoding_quotes(self):
        """Test processing fixes encoding issues with quotes."""
        content = "He said \u201cHello\u201d and \u2018goodbye\u2019."
        metadata = {}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        self.assertEqual(result_content, 'He said "Hello" and \'goodbye\'.')
        self.assertIn("fixed_encoding", result_metadata["cleaning_changes"])

    def test_process_fix_encoding_dashes(self):
        """Test processing fixes encoding issues with dashes."""
        content = "This is an en-dash – and em-dash — example."
        metadata = {}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        self.assertEqual(result_content, "This is an en-dash - and em-dash -- example.")
        self.assertIn("fixed_encoding", result_metadata["cleaning_changes"])

    def test_process_fix_encoding_ellipsis(self):
        """Test processing fixes encoding issues with ellipsis."""
        content = "This continues…"
        metadata = {}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        self.assertEqual(result_content, "This continues...")
        self.assertIn("fixed_encoding", result_metadata["cleaning_changes"])

    def test_process_fix_encoding_disabled(self):
        """Test processing with encoding fixes disabled."""
        self.cleaner.config = {"fix_encoding": False}
        content = "He said \u201cHello\u201d and \u2018goodbye\u2019."
        metadata = {}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        self.assertEqual(result_content, "He said \u201cHello\u201d and \u2018goodbye\u2019.")
        self.assertNotIn("fixed_encoding", result_metadata["cleaning_changes"])

    def test_process_metadata_updates(self):
        """Test that processing updates metadata correctly."""
        content = "  Some content  "
        metadata = {"existing": "value"}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        # Check metadata updates
        self.assertTrue(result_metadata["text_cleaned"])
        self.assertEqual(result_metadata["original_text_length"], len(content))
        self.assertEqual(result_metadata["cleaned_text_length"], len(result_content))
        self.assertIn("cleaning_changes", result_metadata)
        self.assertIn("text_cleaning_applied", result_metadata)
        self.assertIn("characters_removed", result_metadata)
        
        # Original metadata should be preserved
        self.assertEqual(result_metadata["existing"], "value")
        
        # Should be a copy, not the same object
        self.assertIsNot(result_metadata, metadata)

    def test_process_no_changes_made(self):
        """Test processing when no changes are needed."""
        content = "Perfect content"
        metadata = {}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        self.assertEqual(result_content, content)
        self.assertTrue(result_metadata["text_cleaned"])
        self.assertEqual(result_metadata["cleaning_changes"], [])
        self.assertNotIn("text_cleaning_applied", result_metadata)
        self.assertNotIn("characters_removed", result_metadata)

    def test_process_comprehensive_cleaning(self):
        """Test comprehensive cleaning with multiple issues."""
        content = "  \r\n  He said \u201cHello\u201d…   \r\n\r\n\r\n\r\n\r\n  Goodbye.  \r\n  "
        metadata = {}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        expected = 'He said "Hello"...\n\n\nGoodbye.'
        self.assertEqual(result_content, expected)
        
        changes = result_metadata["cleaning_changes"]
        self.assertIn("normalized_line_endings", changes)
        self.assertIn("removed_trailing_whitespace", changes)
        self.assertIn("limited_blank_lines", changes)
        self.assertIn("stripped_content", changes)
        self.assertIn("fixed_encoding", changes)

    def test_get_processing_order(self):
        """Test processing order."""
        self.assertEqual(self.cleaner.get_processing_order(), 10)

    def test_config_defaults(self):
        """Test that config defaults work correctly."""
        # Default config should enable most features
        content = "  Text with   trailing   \r\n\r\n\r\nMore text  "
        metadata = {}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        # Should apply all default cleanings
        self.assertNotEqual(result_content, content)
        self.assertTrue(len(result_metadata["cleaning_changes"]) > 0)


class TestTextCleanerEdgeCases(unittest.TestCase):
    """Test edge cases for TextCleaner."""

    def setUp(self):
        """Set up test fixtures."""
        self.cleaner = TextCleaner()

    def test_process_empty_string(self):
        """Test processing empty string."""
        content = ""
        metadata = {}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        self.assertEqual(result_content, "")
        self.assertTrue(result_metadata["text_cleaned"])

    def test_process_whitespace_only(self):
        """Test processing whitespace-only content."""
        content = "   \n\n\t  \r\n  "
        metadata = {}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        self.assertEqual(result_content, "")
        self.assertIn("stripped_content", result_metadata["cleaning_changes"])

    def test_process_single_character_replacements(self):
        """Test processing with single character encoding issues."""
        content = "\u2018"  # Single problematic character (left single quote)
        metadata = {}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        self.assertEqual(result_content, "'")
        self.assertIn("fixed_encoding", result_metadata["cleaning_changes"])

    def test_process_no_carriage_returns(self):
        """Test processing content without carriage returns."""
        content = "Line 1\nLine 2\nLine 3"
        metadata = {}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        self.assertNotIn("normalized_line_endings", result_metadata["cleaning_changes"])

    def test_process_no_trailing_whitespace(self):
        """Test processing content without trailing whitespace."""
        content = "Line 1\nLine 2\nLine 3"
        metadata = {}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        self.assertNotIn("removed_trailing_whitespace", result_metadata["cleaning_changes"])

    def test_process_no_excessive_blank_lines(self):
        """Test processing content without excessive blank lines."""
        content = "Line 1\n\nLine 2"
        metadata = {}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        self.assertNotIn("limited_blank_lines", result_metadata["cleaning_changes"])

    def test_process_no_leading_trailing_space(self):
        """Test processing content without leading/trailing space."""
        content = "Perfect content"
        metadata = {}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        self.assertNotIn("stripped_content", result_metadata["cleaning_changes"])

    def test_process_no_encoding_issues(self):
        """Test processing content without encoding issues."""
        content = "Normal text with 'quotes' and - dashes..."
        metadata = {}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        self.assertNotIn("fixed_encoding", result_metadata["cleaning_changes"])

    def test_config_get_with_defaults(self):
        """Test config.get behavior with defaults."""
        # Test that config.get works with defaults when config is empty
        self.cleaner.config = {}
        
        content = "  Text  "
        metadata = {}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        # Should still work with default values
        self.assertEqual(result_content, "Text")


class TestTextCleanerConfiguration(unittest.TestCase):
    """Test TextCleaner with various configurations."""

    def setUp(self):
        """Set up test fixtures."""
        self.cleaner = TextCleaner()

    def test_all_features_disabled(self):
        """Test with all cleaning features disabled."""
        self.cleaner.config = {
            "remove_trailing_whitespace": False,
            "limit_blank_lines": False,
            "strip_content": False,
            "fix_encoding": False
        }
        
        content = "  Text with   spaces  \r\n\r\n\r\n\r\nMore \"text\"  "
        metadata = {}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        # Should only normalize line endings (always done)
        expected = "  Text with   spaces  \n\n\n\nMore \"text\"  "
        self.assertEqual(result_content, expected)
        
        changes = result_metadata["cleaning_changes"]
        self.assertEqual(changes, ["normalized_line_endings"])

    def test_custom_max_blank_lines_zero(self):
        """Test with max blank lines set to zero."""
        self.cleaner.config = {"max_consecutive_blank_lines": 0}
        
        content = "Line 1\n\n\nLine 2"  # Need at least 3 newlines to trigger the regex
        metadata = {}
        
        result_content, result_metadata = self.cleaner.process(content, metadata)
        
        self.assertEqual(result_content, "Line 1\nLine 2")
        self.assertIn("limited_blank_lines", result_metadata["cleaning_changes"])


if __name__ == "__main__":
    unittest.main()

