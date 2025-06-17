#!/usr/bin/env python3
"""
Tests for the browser search functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from modern_gopher.browser.terminal import GopherBrowser
from modern_gopher.core.types import GopherItem, GopherItemType
from modern_gopher.config import ModernGopherConfig


class TestBrowserSearchFunctionality:
    """Test the directory search functionality in the browser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create a mock config
        self.mock_config = Mock(spec=ModernGopherConfig)
        self.mock_config.initial_url = None
        self.mock_config.cache_enabled = False
        self.mock_config.cache_directory = '/tmp/test'
        self.mock_config.max_history_items = 100
        self.mock_config.bookmarks_file = '/tmp/bookmarks.json'
        
        # Create test items
        self.test_items = [
            GopherItem(GopherItemType.TEXT_FILE, "README.txt", "/readme.txt", "example.com", 70),
            GopherItem(GopherItemType.TEXT_FILE, "documentation.txt", "/docs.txt", "example.com", 70),
            GopherItem(GopherItemType.DIRECTORY, "source code", "/src", "example.com", 70),
            GopherItem(GopherItemType.TEXT_FILE, "LICENSE", "/license", "example.com", 70),
            GopherItem(GopherItemType.BINARY_FILE, "program.exe", "/bin/program.exe", "example.com", 70),
        ]
    
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.GopherClient')
    def test_perform_search_basic(self, mock_client_class, mock_bookmark_class):
        """Test basic search functionality."""
        # Create browser instance
        browser = GopherBrowser(config=self.mock_config)
        browser.current_items = self.test_items.copy()
        
        # Perform search for "doc"
        browser.perform_search("doc")
        
        # Should find items containing "doc"
        assert browser.is_searching
        assert browser.search_query == "doc"
        assert len(browser.current_items) == 1  # Only documentation.txt contains "doc"
        assert browser.current_items[0].display_string == "documentation.txt"
    
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.GopherClient')
    def test_perform_search_case_insensitive(self, mock_client_class, mock_bookmark_class):
        """Test that search is case-insensitive."""
        browser = GopherBrowser(config=self.mock_config)
        browser.current_items = self.test_items.copy()
        
        # Perform search for "LICENSE" in lowercase
        browser.perform_search("license")
        
        # Should find the LICENSE file
        assert browser.is_searching
        assert len(browser.current_items) == 1
        assert browser.current_items[0].display_string == "LICENSE"
    
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.GopherClient')
    def test_perform_search_no_results(self, mock_client_class, mock_bookmark_class):
        """Test search with no matching results."""
        browser = GopherBrowser(config=self.mock_config)
        browser.current_items = self.test_items.copy()
        
        # Perform search for non-existent term
        browser.perform_search("nonexistent")
        
        # Should have no results but still be in search mode
        assert browser.is_searching
        assert browser.search_query == "nonexistent"
        assert len(browser.current_items) == 0
    
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.GopherClient')
    def test_clear_search(self, mock_client_class, mock_bookmark_class):
        """Test clearing search and restoring original items."""
        browser = GopherBrowser(config=self.mock_config)
        browser.current_items = self.test_items.copy()
        
        # Perform search
        browser.perform_search("doc")
        assert browser.is_searching
        assert len(browser.current_items) == 1
        
        # Clear search
        browser.clear_search()
        
        # Should restore original items
        assert not browser.is_searching
        assert browser.search_query == ""
        assert len(browser.current_items) == 5  # All original items
        assert browser.selected_index == 0
    
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.GopherClient')
    def test_perform_search_empty_query(self, mock_client_class, mock_bookmark_class):
        """Test search with empty query clears search."""
        browser = GopherBrowser(config=self.mock_config)
        browser.current_items = self.test_items.copy()
        
        # First perform a search
        browser.perform_search("doc")
        assert browser.is_searching
        
        # Then search with empty query
        browser.perform_search("")
        
        # Should clear search
        assert not browser.is_searching
        assert len(browser.current_items) == 5  # All original items restored
    
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.GopherClient')
    def test_perform_search_whitespace_query(self, mock_client_class, mock_bookmark_class):
        """Test search with whitespace-only query clears search."""
        browser = GopherBrowser(config=self.mock_config)
        browser.current_items = self.test_items.copy()
        
        # First perform a search
        browser.perform_search("doc")
        assert browser.is_searching
        
        # Then search with whitespace query
        browser.perform_search("   ")
        
        # Should clear search
        assert not browser.is_searching
        assert len(browser.current_items) == 5  # All original items restored
    
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.GopherClient')
    def test_show_search_dialog_no_items(self, mock_client_class, mock_bookmark_class):
        """Test search dialog with no current items."""
        browser = GopherBrowser(config=self.mock_config)
        browser.current_items = []  # No items
        
        # Mock the status bar
        browser.status_bar = Mock()
        
        # Try to show search dialog
        browser.show_search_dialog()
        
        # Should set appropriate status message
        browser.status_bar.text = "No directory to search"
    
    @patch('modern_gopher.browser.terminal.input_dialog')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.GopherClient')
    def test_show_search_dialog_with_input(self, mock_client_class, mock_bookmark_class, mock_input_dialog):
        """Test search dialog with user input."""
        browser = GopherBrowser(config=self.mock_config)
        browser.current_items = self.test_items.copy()
        
        # Mock input dialog to return search query
        mock_input_dialog.return_value = "test"
        
        # Mock perform_search method
        browser.perform_search = Mock()
        
        # Show search dialog
        browser.show_search_dialog()
        
        # Should call input_dialog and perform_search
        mock_input_dialog.assert_called_once_with(
            title="Search Directory",
            text="Enter search term (case-insensitive):",
            validator=None
        )
        browser.perform_search.assert_called_once_with("test")
    
    @patch('modern_gopher.browser.terminal.input_dialog')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.GopherClient')
    def test_show_search_dialog_cancelled(self, mock_client_class, mock_bookmark_class, mock_input_dialog):
        """Test search dialog when user cancels."""
        browser = GopherBrowser(config=self.mock_config)
        browser.current_items = self.test_items.copy()
        
        # Mock input dialog to return None (cancelled)
        mock_input_dialog.return_value = None
        
        # Mock perform_search method
        browser.perform_search = Mock()
        
        # Show search dialog
        browser.show_search_dialog()
        
        # Should call input_dialog but not perform_search
        mock_input_dialog.assert_called_once()
        browser.perform_search.assert_not_called()
    
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.GopherClient')
    def test_search_in_selector_field(self, mock_client_class, mock_bookmark_class):
        """Test that search looks in both display_string and selector."""
        browser = GopherBrowser(config=self.mock_config)
        browser.current_items = self.test_items.copy()
        
        # Search for "src" which appears in selector but not display_string
        browser.perform_search("src")
        
        # Should find the "source code" directory
        assert browser.is_searching
        assert len(browser.current_items) == 1
        assert browser.current_items[0].display_string == "source code"
        assert "/src" in browser.current_items[0].selector


if __name__ == "__main__":
    pytest.main([__file__])

