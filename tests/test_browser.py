#!/usr/bin/env python3
"""
Comprehensive tests for the browser module.

This test suite covers the GopherBrowser class and HistoryManager
to improve test coverage from 16% to 60%+.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from modern_gopher.browser.terminal import GopherBrowser, HistoryManager
from modern_gopher.core.types import GopherItem, GopherItemType
from modern_gopher.config import ModernGopherConfig


class TestHistoryManager:
    """Test the HistoryManager class."""
    
    def test_history_initialization(self):
        """Test HistoryManager initialization."""
        history = HistoryManager(max_size=50)
        
        assert history.history == []
        assert history.position == -1
        assert history.max_size == 50
    
    def test_history_default_max_size(self):
        """Test default max size."""
        history = HistoryManager()
        assert history.max_size == 100
    
    def test_add_first_url(self):
        """Test adding the first URL to history."""
        history = HistoryManager()
        
        history.add("gopher://example.com")
        
        assert len(history.history) == 1
        assert history.history[0] == "gopher://example.com"
        assert history.position == 0
    
    def test_add_multiple_urls(self):
        """Test adding multiple URLs."""
        history = HistoryManager()
        
        history.add("gopher://example.com")
        history.add("gopher://test.com")
        history.add("gopher://another.com")
        
        assert len(history.history) == 3
        assert history.position == 2
        assert history.current() == "gopher://another.com"
    
    def test_add_duplicate_url(self):
        """Test adding the same URL twice."""
        history = HistoryManager()
        
        history.add("gopher://example.com")
        history.add("gopher://example.com")
        
        assert len(history.history) == 1
        assert history.position == 0
    
    def test_history_max_size_limit(self):
        """Test that history respects max size limit."""
        history = HistoryManager(max_size=3)
        
        history.add("gopher://url1.com")
        history.add("gopher://url2.com")
        history.add("gopher://url3.com")
        history.add("gopher://url4.com")  # Should remove first URL
        
        assert len(history.history) == 3
        assert "gopher://url1.com" not in history.history
        assert history.history[0] == "gopher://url2.com"
        assert history.current() == "gopher://url4.com"
    
    def test_back_navigation(self):
        """Test going back in history."""
        history = HistoryManager()
        
        history.add("gopher://url1.com")
        history.add("gopher://url2.com")
        history.add("gopher://url3.com")
        
        # Go back
        back_url = history.back()
        assert back_url == "gopher://url2.com"
        assert history.position == 1
        
        # Go back again
        back_url = history.back()
        assert back_url == "gopher://url1.com"
        assert history.position == 0
        
        # Can't go back further
        back_url = history.back()
        assert back_url is None
        assert history.position == 0
    
    def test_forward_navigation(self):
        """Test going forward in history."""
        history = HistoryManager()
        
        history.add("gopher://url1.com")
        history.add("gopher://url2.com")
        history.add("gopher://url3.com")
        
        # Go back twice
        history.back()
        history.back()
        assert history.position == 0
        
        # Go forward
        forward_url = history.forward()
        assert forward_url == "gopher://url2.com"
        assert history.position == 1
        
        # Go forward again
        forward_url = history.forward()
        assert forward_url == "gopher://url3.com"
        assert history.position == 2
        
        # Can't go forward further
        forward_url = history.forward()
        assert forward_url is None
        assert history.position == 2
    
    def test_current_url(self):
        """Test getting current URL."""
        history = HistoryManager()
        
        # No URLs yet
        assert history.current() is None
        
        # Add URL
        history.add("gopher://example.com")
        assert history.current() == "gopher://example.com"
        
        # Add another and go back
        history.add("gopher://test.com")
        history.back()
        assert history.current() == "gopher://example.com"
    
    def test_add_url_truncates_forward_history(self):
        """Test that adding a new URL truncates forward history."""
        history = HistoryManager()
        
        history.add("gopher://url1.com")
        history.add("gopher://url2.com")
        history.add("gopher://url3.com")
        
        # Go back
        history.back()
        assert history.position == 1
        assert len(history.history) == 3
        
        # Add new URL - should truncate forward history
        history.add("gopher://new-url.com")
        assert len(history.history) == 3  # url1, url2, new-url
        assert history.history[2] == "gopher://new-url.com"
        assert history.position == 2
        assert "gopher://url3.com" not in history.history


class TestGopherBrowser:
    """Test the GopherBrowser class."""
    
    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    def test_browser_initialization_defaults(self, mock_bookmarks, mock_client, mock_get_config):
        """Test browser initialization with default values."""
        # Mock config
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = True
        mock_config.cache_directory = "/tmp/cache"
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/tmp/bookmarks.json"
        mock_get_config.return_value = mock_config
        
        browser = GopherBrowser()
        
        assert browser.current_url == "gopher://gopher.floodgap.com"
        assert browser.current_items == []
        assert browser.selected_index == 0
        assert browser.config == mock_config
        assert isinstance(browser.history, HistoryManager)
        mock_client.assert_called_once()
    
    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    def test_browser_initialization_custom_values(self, mock_bookmarks, mock_client, mock_get_config):
        """Test browser initialization with custom values."""
        # Mock config
        mock_config = Mock()
        mock_config.initial_url = "gopher://config.url.com"
        mock_config.cache_enabled = False
        mock_config.max_history_items = 50
        mock_config.bookmarks_file = "/custom/bookmarks.json"
        mock_get_config.return_value = mock_config
        
        browser = GopherBrowser(
            initial_url="gopher://custom.com",
            timeout=60,
            use_ssl=True,
            cache_dir="/custom/cache"
        )
        
        assert browser.current_url == "gopher://custom.com"
        assert browser.use_ssl is True
        mock_client.assert_called_with(
            timeout=60,
            cache_dir="/custom/cache",
            use_ipv6=None
        )
    
    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    def test_browser_uses_config_initial_url(self, mock_bookmarks, mock_client, mock_get_config):
        """Test that browser uses config initial URL when default is provided."""
        mock_config = Mock()
        mock_config.initial_url = "gopher://config-default.com"
        mock_config.cache_enabled = True
        mock_config.cache_directory = "/tmp/cache"
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/tmp/bookmarks.json"
        mock_get_config.return_value = mock_config
        
        browser = GopherBrowser()  # Uses DEFAULT_URL
        
        assert browser.current_url == "gopher://config-default.com"
    
    def test_get_item_icon(self):
        """Test getting icons for different item types."""
        with patch('modern_gopher.browser.terminal.get_config'), \
             patch('modern_gopher.browser.terminal.GopherClient'), \
             patch('modern_gopher.browser.terminal.BookmarkManager'):
            
            browser = GopherBrowser()
            
            # Test various item types
            assert browser.get_item_icon(GopherItemType.TEXT_FILE) in ["📄", "[TXT]"]
            assert browser.get_item_icon(GopherItemType.DIRECTORY) in ["📁", "[DIR]"]
            assert browser.get_item_icon(GopherItemType.BINARY_FILE) in ["📎", "[BIN]"]
            assert browser.get_item_icon(GopherItemType.GIF_IMAGE) in ["🖼️", "[IMG]"]
            assert browser.get_item_icon(GopherItemType.HTML) in ["🌐", "[HTM]"]
    
    def test_format_display_string(self):
        """Test formatting display strings."""
        with patch('modern_gopher.browser.terminal.get_config'), \
             patch('modern_gopher.browser.terminal.GopherClient'), \
             patch('modern_gopher.browser.terminal.BookmarkManager'):
            
            browser = GopherBrowser()
            
            # Test normal text
            assert browser.format_display_string("Hello World") == "Hello World"
            
            # Test long text truncation
            long_text = "A" * 200
            formatted = browser.format_display_string(long_text, max_length=50)
            assert len(formatted) <= 53  # 50 + "..."
            assert formatted.endswith("...")
    
    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    def test_update_status(self, mock_bookmarks, mock_client, mock_get_config):
        """Test status bar updates."""
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = True
        mock_config.cache_directory = "/tmp/cache"
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/tmp/bookmarks.json"
        mock_get_config.return_value = mock_config
        
        browser = GopherBrowser()
        
        # Test setting status
        browser.update_status("Test message")
        assert browser.status_bar.text == "Test message"
        
        # Test status with items count
        browser.current_items = [Mock(), Mock(), Mock()]
        browser.selected_index = 1
        browser.update_status("Browsing")
        # Status should include position info
        assert "2/3" in browser.status_bar.text or "Browsing" in browser.status_bar.text
    
    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    def test_bookmark_toggle_add(self, mock_bookmarks, mock_client, mock_get_config):
        """Test adding a bookmark."""
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = True
        mock_config.cache_directory = "/tmp/cache"
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/tmp/bookmarks.json"
        mock_get_config.return_value = mock_config
        
        mock_bm = Mock()
        mock_bm.is_bookmarked.return_value = False
        mock_bookmarks.return_value = mock_bm
        
        browser = GopherBrowser()
        browser.current_url = "gopher://example.com"
        browser.toggle_bookmark()
        
        mock_bm.is_bookmarked.assert_called_with("gopher://example.com")
        mock_bm.add.assert_called_once()
        assert "Bookmark added" in browser.status_bar.text
    
    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    def test_bookmark_toggle_remove(self, mock_bookmarks, mock_client, mock_get_config):
        """Test removing a bookmark."""
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = True
        mock_config.cache_directory = "/tmp/cache"
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/tmp/bookmarks.json"
        mock_get_config.return_value = mock_config
        
        mock_bm = Mock()
        mock_bm.is_bookmarked.return_value = True
        mock_bookmarks.return_value = mock_bm
        
        browser = GopherBrowser()
        browser.current_url = "gopher://example.com"
        browser.toggle_bookmark()
        
        mock_bm.is_bookmarked.assert_called_with("gopher://example.com")
        mock_bm.remove.assert_called_with("gopher://example.com")
        assert "Bookmark removed" in browser.status_bar.text
    
    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    def test_show_history_empty(self, mock_bookmarks, mock_client, mock_get_config):
        """Test showing empty history."""
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = True
        mock_config.cache_directory = "/tmp/cache"
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/tmp/bookmarks.json"
        mock_get_config.return_value = mock_config
        
        browser = GopherBrowser()
        browser.show_history()
        
        assert "No browsing history" in browser.status_bar.text
    
    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    def test_show_history_with_items(self, mock_bookmarks, mock_client, mock_get_config):
        """Test showing history with items."""
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = True
        mock_config.cache_directory = "/tmp/cache"
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/tmp/bookmarks.json"
        mock_get_config.return_value = mock_config
        
        browser = GopherBrowser()
        browser.history.add("gopher://example.com")
        browser.history.add("gopher://test.com")
        browser.show_history()
        
        content = browser.content_view.text
        assert "Browsing History" in content
        assert "gopher://example.com" in content
        assert "gopher://test.com" in content
        assert "(current)" in content
    
    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    def test_show_bookmarks_empty(self, mock_bookmarks, mock_client, mock_get_config):
        """Test showing empty bookmarks."""
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = True
        mock_config.cache_directory = "/tmp/cache"
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/tmp/bookmarks.json"
        mock_get_config.return_value = mock_config
        
        mock_bm = Mock()
        mock_bm.get_all.return_value = []
        mock_bookmarks.return_value = mock_bm
        
        browser = GopherBrowser()
        browser.show_bookmarks()
        
        assert "No bookmarks saved" in browser.status_bar.text
    
    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    def test_show_bookmarks_with_items(self, mock_bookmarks, mock_client, mock_get_config):
        """Test showing bookmarks with items."""
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = True
        mock_config.cache_directory = "/tmp/cache"
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/tmp/bookmarks.json"
        mock_get_config.return_value = mock_config
        
        # Create mock bookmark
        mock_bookmark = Mock()
        mock_bookmark.title = "Test Site"
        mock_bookmark.url = "gopher://test.com"
        mock_bookmark.description = "A test site"
        mock_bookmark.tags = ["test", "example"]
        
        mock_bm = Mock()
        mock_bm.get_all.return_value = [mock_bookmark]
        mock_bookmarks.return_value = mock_bm
        
        browser = GopherBrowser()
        browser.show_bookmarks()
        
        content = browser.content_view.text
        assert "Bookmarks:" in content
        assert "Test Site" in content
        assert "gopher://test.com" in content
        assert "A test site" in content
        assert "test, example" in content
    
    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    def test_url_validator_creation(self, mock_bookmarks, mock_client, mock_get_config):
        """Test URL validator creation."""
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = True
        mock_config.cache_directory = "/tmp/cache"
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/tmp/bookmarks.json"
        mock_get_config.return_value = mock_config
        
        browser = GopherBrowser()
        validator = browser._url_validator()
        
        assert validator is not None
        assert hasattr(validator, 'validate')
    
    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    def test_get_menu_text_empty(self, mock_bookmarks, mock_client, mock_get_config):
        """Test getting menu text with no items."""
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = True
        mock_config.cache_directory = "/tmp/cache"
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/tmp/bookmarks.json"
        mock_get_config.return_value = mock_config
        
        browser = GopherBrowser()
        browser.current_items = []
        
        menu_text = browser.get_menu_text()
        assert menu_text == []
    
    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    def test_get_menu_text_with_items(self, mock_bookmarks, mock_client, mock_get_config):
        """Test getting menu text with items."""
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = True
        mock_config.cache_directory = "/tmp/cache"
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/tmp/bookmarks.json"
        mock_get_config.return_value = mock_config
        
        # Create mock items
        item1 = GopherItem(GopherItemType.TEXT_FILE, "Test File", "/test.txt", "example.com", 70)
        item2 = GopherItem(GopherItemType.DIRECTORY, "Test Dir", "/test", "example.com", 70)
        
        browser = GopherBrowser()
        browser.current_items = [item1, item2]
        browser.selected_index = 0
        
        menu_text = browser.get_menu_text()
        
        assert len(menu_text) == 2
        # First item should be selected
        assert menu_text[0][0] == 'class:menu.selection'
        assert "Test File" in menu_text[0][1]
        # Second item should not be selected
        assert menu_text[1][0] == ''
        assert "Test Dir" in menu_text[1][1]
    
    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    def test_search_functionality_basic(self, mock_bookmarks, mock_client, mock_get_config):
        """Test basic search functionality."""
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = True
        mock_config.cache_directory = "/tmp/cache"
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/tmp/bookmarks.json"
        mock_get_config.return_value = mock_config
        
        browser = GopherBrowser()
        
        # Set up test items
        items = [
            GopherItem(
                item_type=GopherItemType.DIRECTORY,
                display_string="Documentation",
                selector="/docs",
                host="example.com",
                port=70
            ),
            GopherItem(
                item_type=GopherItemType.TEXT_FILE,
                display_string="README.txt",
                selector="/readme.txt",
                host="example.com",
                port=70
            ),
            GopherItem(
                item_type=GopherItemType.TEXT_FILE,
                display_string="License File",
                selector="/license",
                host="example.com",
                port=70
            )
        ]
        
        browser.current_items = items
        browser.is_searching = False
        
        # Perform search for "doc"
        browser.perform_search("doc")
        
        # Should find one item
        assert len(browser.current_items) == 1
        assert browser.current_items[0].display_string == "Documentation"
        assert browser.is_searching is True
        assert browser.search_query == "doc"
        assert len(browser.filtered_items) == 3  # Original items preserved
    
    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    def test_search_functionality_case_insensitive(self, mock_bookmarks, mock_client, mock_get_config):
        """Test that search is case insensitive."""
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = True
        mock_config.cache_directory = "/tmp/cache"
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/tmp/bookmarks.json"
        mock_get_config.return_value = mock_config
        
        browser = GopherBrowser()
        
        items = [
            GopherItem(
                item_type=GopherItemType.TEXT_FILE,
                display_string="README.TXT",
                selector="/readme.txt",
                host="example.com",
                port=70
            ),
            GopherItem(
                item_type=GopherItemType.TEXT_FILE,
                display_string="license file",
                selector="/license",
                host="example.com",
                port=70
            )
        ]
        
        browser.current_items = items
        browser.is_searching = False
        
        # Search for "readme" (lowercase) should find "README.TXT"
        browser.perform_search("readme")
        
        assert len(browser.current_items) == 1
        assert browser.current_items[0].display_string == "README.TXT"
    
    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    def test_search_functionality_selector_matching(self, mock_bookmarks, mock_client, mock_get_config):
        """Test that search matches both display string and selector."""
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = True
        mock_config.cache_directory = "/tmp/cache"
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/tmp/bookmarks.json"
        mock_get_config.return_value = mock_config
        
        browser = GopherBrowser()
        
        items = [
            GopherItem(
                item_type=GopherItemType.TEXT_FILE,
                display_string="Important Document",
                selector="/hidden/secret.txt",
                host="example.com",
                port=70
            ),
            GopherItem(
                item_type=GopherItemType.TEXT_FILE,
                display_string="Public File",
                selector="/public.txt",
                host="example.com",
                port=70
            )
        ]
        
        browser.current_items = items
        browser.is_searching = False
        
        # Search for "secret" should find the first item via selector
        browser.perform_search("secret")
        
        assert len(browser.current_items) == 1
        assert browser.current_items[0].display_string == "Important Document"
    
    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    def test_search_functionality_no_results(self, mock_bookmarks, mock_client, mock_get_config):
        """Test search with no matching results."""
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = True
        mock_config.cache_directory = "/tmp/cache"
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/tmp/bookmarks.json"
        mock_get_config.return_value = mock_config
        
        browser = GopherBrowser()
        
        items = [
            GopherItem(
                item_type=GopherItemType.TEXT_FILE,
                display_string="README.txt",
                selector="/readme.txt",
                host="example.com",
                port=70
            )
        ]
        
        browser.current_items = items
        browser.is_searching = False
        
        # Search for something that doesn't exist
        browser.perform_search("nonexistent")
        
        assert len(browser.current_items) == 0
        assert browser.is_searching is True
        assert len(browser.filtered_items) == 1  # Original items preserved
    
    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    def test_search_functionality_empty_query(self, mock_bookmarks, mock_client, mock_get_config):
        """Test search with empty query clears search."""
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = True
        mock_config.cache_directory = "/tmp/cache"
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/tmp/bookmarks.json"
        mock_get_config.return_value = mock_config
        
        browser = GopherBrowser()
        
        items = [
            GopherItem(
                item_type=GopherItemType.TEXT_FILE,
                display_string="README.txt",
                selector="/readme.txt",
                host="example.com",
                port=70
            )
        ]
        
        browser.current_items = items
        browser.is_searching = True
        browser.filtered_items = items.copy()
        browser.search_query = "previous search"
        
        # Empty search should clear search
        browser.perform_search("")
        
        assert browser.is_searching is False
        assert browser.search_query == ""
        assert len(browser.filtered_items) == 0
    
    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    def test_clear_search_functionality(self, mock_bookmarks, mock_client, mock_get_config):
        """Test clearing search restores original items."""
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = True
        mock_config.cache_directory = "/tmp/cache"
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/tmp/bookmarks.json"
        mock_get_config.return_value = mock_config
        
        browser = GopherBrowser()
        
        original_items = [
            GopherItem(
                item_type=GopherItemType.TEXT_FILE,
                display_string="README.txt",
                selector="/readme.txt",
                host="example.com",
                port=70
            ),
            GopherItem(
                item_type=GopherItemType.TEXT_FILE,
                display_string="License",
                selector="/license",
                host="example.com",
                port=70
            )
        ]
        
        # Set up search state
        browser.current_items = [original_items[0]]  # Filtered results
        browser.filtered_items = original_items.copy()  # Original items
        browser.is_searching = True
        browser.search_query = "readme"
        browser.selected_index = 0
        
        # Clear search
        browser.clear_search()
        
        # Should restore original state
        assert len(browser.current_items) == 2
        assert browser.current_items == original_items
        assert browser.is_searching is False
        assert browser.search_query == ""
        assert len(browser.filtered_items) == 0
        assert browser.selected_index == 0
    
    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    def test_clear_search_when_not_searching(self, mock_bookmarks, mock_client, mock_get_config):
        """Test clearing search when not currently searching."""
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = True
        mock_config.cache_directory = "/tmp/cache"
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/tmp/bookmarks.json"
        mock_get_config.return_value = mock_config
        
        browser = GopherBrowser()
        
        items = [
            GopherItem(
                item_type=GopherItemType.TEXT_FILE,
                display_string="README.txt",
                selector="/readme.txt",
                host="example.com",
                port=70
            )
        ]
        
        browser.current_items = items
        browser.is_searching = False
        
        # Clear search when not searching should do nothing
        browser.clear_search()
        
        assert len(browser.current_items) == 1
        assert browser.is_searching is False
    
    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    def test_consecutive_searches(self, mock_bookmarks, mock_client, mock_get_config):
        """Test performing multiple consecutive searches."""
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = True
        mock_config.cache_directory = "/tmp/cache"
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/tmp/bookmarks.json"
        mock_get_config.return_value = mock_config
        
        browser = GopherBrowser()
        
        items = [
            GopherItem(
                item_type=GopherItemType.DIRECTORY,
                display_string="Documents",
                selector="/docs",
                host="example.com",
                port=70
            ),
            GopherItem(
                item_type=GopherItemType.TEXT_FILE,
                display_string="Document 1",
                selector="/doc1.txt",
                host="example.com",
                port=70
            ),
            GopherItem(
                item_type=GopherItemType.TEXT_FILE,
                display_string="File Archive",
                selector="/archive.zip",
                host="example.com",
                port=70
            )
        ]
        
        browser.current_items = items
        browser.is_searching = False
        
        # First search for "doc"
        browser.perform_search("doc")
        assert len(browser.current_items) == 2  # Documents + Document 1
        assert browser.is_searching is True
        
        # Second search for "archive" (should search from original items)
        browser.perform_search("archive")
        assert len(browser.current_items) == 1  # File Archive
        assert browser.current_items[0].display_string == "File Archive"
        assert len(browser.filtered_items) == 3  # Original items still preserved


if __name__ == "__main__":
    pytest.main([__file__])

