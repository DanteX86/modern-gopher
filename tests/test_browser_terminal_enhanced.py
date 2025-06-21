#!/usr/bin/env python3
"""
Enhanced tests for browser terminal module to improve coverage.
Tests GopherBrowser and HistoryManager classes comprehensively.
"""

import logging
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, PropertyMock

import pytest

# Mock prompt_toolkit to avoid import issues in test environment
with patch.dict('sys.modules', {
    'prompt_toolkit': MagicMock(),
    'prompt_toolkit.application': MagicMock(),
    'prompt_toolkit.key_binding': MagicMock(),
    'prompt_toolkit.layout': MagicMock(),
    'prompt_toolkit.mouse_events': MagicMock(),
    'prompt_toolkit.shortcuts': MagicMock(),
    'prompt_toolkit.styles': MagicMock(),
    'prompt_toolkit.validation': MagicMock(),
    'prompt_toolkit.widgets': MagicMock(),
}):
    from modern_gopher.browser.terminal import HistoryManager, GopherBrowser, DEFAULT_URL
    from modern_gopher.core.types import GopherItem, GopherItemType
    from modern_gopher.keybindings import KeyContext


class TestHistoryManager:
    """Test the HistoryManager class."""

    def test_history_manager_initialization(self):
        """Test history manager initialization."""
        history = HistoryManager()
        assert history.max_size == 100
        assert history.history == []
        assert history.position == -1

    def test_history_manager_custom_max_size(self):
        """Test history manager with custom max size."""
        history = HistoryManager(max_size=50)
        assert history.max_size == 50

    def test_add_first_url(self):
        """Test adding the first URL to history."""
        history = HistoryManager()
        history.add("gopher://example.com")
        
        assert len(history.history) == 1
        assert history.history[0] == "gopher://example.com"
        assert history.position == 0

    def test_add_multiple_urls(self):
        """Test adding multiple URLs to history."""
        history = HistoryManager()
        urls = ["gopher://example.com", "gopher://test.com", "gopher://demo.com"]
        
        for url in urls:
            history.add(url)
        
        assert len(history.history) == 3
        assert history.history == urls
        assert history.position == 2

    def test_add_duplicate_url_consecutive(self):
        """Test adding duplicate consecutive URL doesn't create duplicate."""
        history = HistoryManager()
        history.add("gopher://example.com")
        history.add("gopher://example.com")
        
        assert len(history.history) == 1
        assert history.position == 0

    def test_add_duplicate_url_non_consecutive(self):
        """Test adding duplicate non-consecutive URL creates new entry."""
        history = HistoryManager()
        history.add("gopher://example.com")
        history.add("gopher://test.com")
        history.add("gopher://example.com")
        
        assert len(history.history) == 3
        assert history.history[2] == "gopher://example.com"
        assert history.position == 2

    def test_max_size_limit(self):
        """Test that history respects max size limit."""
        history = HistoryManager(max_size=3)
        
        urls = ["gopher://1.com", "gopher://2.com", "gopher://3.com", "gopher://4.com"]
        for url in urls:
            history.add(url)
        
        assert len(history.history) == 3
        assert history.history == ["gopher://2.com", "gopher://3.com", "gopher://4.com"]
        assert history.position == 2

    def test_back_navigation_success(self):
        """Test successful back navigation."""
        history = HistoryManager()
        history.add("gopher://example.com")
        history.add("gopher://test.com")
        
        back_url = history.back()
        assert back_url == "gopher://example.com"
        assert history.position == 0

    def test_back_navigation_at_beginning(self):
        """Test back navigation when at beginning of history."""
        history = HistoryManager()
        history.add("gopher://example.com")
        
        # Already at position 0, can't go back
        back_url = history.back()
        assert back_url is None
        assert history.position == 0

    def test_back_navigation_empty_history(self):
        """Test back navigation with empty history."""
        history = HistoryManager()
        back_url = history.back()
        assert back_url is None
        assert history.position == -1

    def test_forward_navigation_success(self):
        """Test successful forward navigation."""
        history = HistoryManager()
        history.add("gopher://example.com")
        history.add("gopher://test.com")
        history.back()  # Go back to position 0
        
        forward_url = history.forward()
        assert forward_url == "gopher://test.com"
        assert history.position == 1

    def test_forward_navigation_at_end(self):
        """Test forward navigation when at end of history."""
        history = HistoryManager()
        history.add("gopher://example.com")
        
        # Already at end, can't go forward
        forward_url = history.forward()
        assert forward_url is None
        assert history.position == 0

    def test_forward_navigation_empty_history(self):
        """Test forward navigation with empty history."""
        history = HistoryManager()
        forward_url = history.forward()
        assert forward_url is None
        assert history.position == -1

    def test_current_url_valid_position(self):
        """Test getting current URL with valid position."""
        history = HistoryManager()
        history.add("gopher://example.com")
        history.add("gopher://test.com")
        
        current = history.current()
        assert current == "gopher://test.com"

    def test_current_url_invalid_position(self):
        """Test getting current URL with invalid position."""
        history = HistoryManager()
        current = history.current()
        assert current is None

    def test_truncate_forward_history_on_add(self):
        """Test that adding a new URL truncates forward history."""
        history = HistoryManager()
        history.add("gopher://1.com")
        history.add("gopher://2.com")
        history.add("gopher://3.com")
        
        # Go back two steps
        history.back()  # position 1
        history.back()  # position 0
        
        # Add new URL - should truncate forward history
        history.add("gopher://new.com")
        
        assert len(history.history) == 2
        assert history.history == ["gopher://1.com", "gopher://new.com"]
        assert history.position == 1


class TestGopherBrowser:
    """Test the GopherBrowser class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create temporary config for testing
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config.yaml"

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    def test_browser_initialization_defaults(self, mock_kb_manager, mock_bookmark_manager, 
                                           mock_client_class, mock_get_config):
        """Test browser initialization with default parameters."""
        # Mock config
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = False
        mock_config.cache_directory = "/cache"
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/bookmarks.json"
        mock_config.config_dir = "/config"
        mock_get_config.return_value = mock_config
        
        # Mock client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock bookmark manager
        mock_bookmark_manager.return_value = Mock()
        
        # Mock keybinding manager
        mock_kb = Mock()
        mock_kb.get_bindings_by_context.return_value = {}
        mock_kb_manager.return_value = mock_kb
        
        browser = GopherBrowser()
        
        assert browser.current_url == DEFAULT_URL
        assert browser.current_items == []
        assert browser.selected_index == 0
        assert browser.is_searching is False
        assert browser.search_query == ""
        mock_client_class.assert_called_once()

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    def test_browser_initialization_with_custom_params(self, mock_kb_manager, mock_bookmark_manager,
                                                      mock_client_class, mock_get_config):
        """Test browser initialization with custom parameters."""
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = True
        mock_config.cache_directory = "/custom/cache"
        mock_config.max_history_items = 50
        mock_config.bookmarks_file = "/bookmarks.json"
        mock_config.config_dir = "/config"
        mock_get_config.return_value = mock_config
        
        mock_client_class.return_value = Mock()
        mock_bookmark_manager.return_value = Mock()
        
        mock_kb = Mock()
        mock_kb.get_bindings_by_context.return_value = {}
        mock_kb_manager.return_value = mock_kb
        
        browser = GopherBrowser(
            initial_url="gopher://test.com",
            timeout=60,
            use_ssl=True,
            use_ipv6=True,
            cache_dir="/custom/cache"
        )
        
        assert browser.current_url == "gopher://test.com"
        assert browser.use_ssl is True
        mock_client_class.assert_called_with(
            timeout=60,
            cache_dir="/custom/cache",
            use_ipv6=True
        )

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    def test_browser_with_config_initial_url(self, mock_kb_manager, mock_bookmark_manager,
                                            mock_client_class, mock_get_config):
        """Test browser uses config initial URL when default is provided."""
        mock_config = Mock()
        mock_config.initial_url = "gopher://config.com"
        mock_config.cache_enabled = False
        mock_config.cache_directory = "/cache"
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/bookmarks.json"
        mock_config.config_dir = "/config"
        mock_get_config.return_value = mock_config
        
        mock_client_class.return_value = Mock()
        mock_bookmark_manager.return_value = Mock()
        
        mock_kb = Mock()
        mock_kb.get_bindings_by_context.return_value = {}
        mock_kb_manager.return_value = mock_kb
        
        # Use default URL to trigger config override
        browser = GopherBrowser(initial_url=DEFAULT_URL)
        
        assert browser.current_url == "gopher://config.com"

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch('modern_gopher.browser.terminal.SessionManager')
    def test_browser_with_sessions_enabled(self, mock_session_manager_class, mock_kb_manager,
                                         mock_bookmark_manager, mock_client_class, mock_get_config):
        """Test browser initialization with sessions enabled."""
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = False
        mock_config.cache_directory = "/cache"
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/bookmarks.json"
        mock_config.config_dir = "/config"
        mock_config.session_enabled = True
        mock_config.session_file = "/sessions.json"
        mock_config.session_backup_sessions = 5
        mock_config.session_max_sessions = 10
        mock_get_config.return_value = mock_config
        
        mock_client_class.return_value = Mock()
        mock_bookmark_manager.return_value = Mock()
        
        mock_session_manager = Mock()
        mock_session_manager_class.return_value = mock_session_manager
        
        mock_kb = Mock()
        mock_kb.get_bindings_by_context.return_value = {}
        mock_kb_manager.return_value = mock_kb
        
        browser = GopherBrowser()
        
        assert browser.session_manager == mock_session_manager
        mock_session_manager_class.assert_called_once_with(
            session_file="/sessions.json",
            backup_sessions=5,
            max_sessions=10
        )

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    def test_browser_session_initialization_error(self, mock_kb_manager, mock_bookmark_manager,
                                                 mock_client_class, mock_get_config):
        """Test browser handles session initialization error gracefully."""
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = False
        mock_config.cache_directory = "/cache"
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/bookmarks.json"
        mock_config.config_dir = "/config"
        mock_config.session_enabled = True
        # Missing session_file attribute to trigger error
        del mock_config.session_file
        mock_get_config.return_value = mock_config
        
        mock_client_class.return_value = Mock()
        mock_bookmark_manager.return_value = Mock()
        
        mock_kb = Mock()
        mock_kb.get_bindings_by_context.return_value = {}
        mock_kb_manager.return_value = mock_kb
        
        browser = GopherBrowser()
        
        # Should handle error gracefully
        assert browser.session_manager is None

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch('modern_gopher.plugins.manager.get_manager')
    def test_browser_plugin_system_initialization(self, mock_get_manager, mock_kb_manager,
                                                 mock_bookmark_manager, mock_client_class, mock_get_config):
        """Test browser plugin system initialization."""
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = False
        mock_config.cache_directory = "/cache"
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/bookmarks.json"
        mock_config.config_dir = "/config"
        mock_get_config.return_value = mock_config
        
        mock_client_class.return_value = Mock()
        mock_bookmark_manager.return_value = Mock()
        
        mock_plugin_manager = Mock()
        mock_get_manager.return_value = mock_plugin_manager
        
        mock_kb = Mock()
        mock_kb.get_bindings_by_context.return_value = {}
        mock_kb_manager.return_value = mock_kb
        
        browser = GopherBrowser()
        
        assert browser.plugin_manager == mock_plugin_manager
        mock_get_manager.assert_called_once_with("/config")
        mock_plugin_manager.initialize.assert_called_once()

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch('modern_gopher.plugins.manager.get_manager')
    def test_browser_plugin_system_initialization_error(self, mock_get_manager, mock_kb_manager,
                                                       mock_bookmark_manager, mock_client_class, mock_get_config):
        """Test browser handles plugin system initialization error."""
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = False
        mock_config.cache_directory = "/cache"
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/bookmarks.json"
        mock_config.config_dir = "/config"
        mock_get_config.return_value = mock_config
        
        mock_client_class.return_value = Mock()
        mock_bookmark_manager.return_value = Mock()
        
        # Plugin manager raises exception
        mock_get_manager.side_effect = Exception("Plugin error")
        
        mock_kb = Mock()
        mock_kb.get_bindings_by_context.return_value = {}
        mock_kb_manager.return_value = mock_kb
        
        browser = GopherBrowser()
        
        # Should handle error gracefully
        assert browser.plugin_manager is None

    def create_test_browser(self):
        """Create a test browser instance with mocked dependencies."""
        with patch('modern_gopher.browser.terminal.get_config') as mock_get_config, \
             patch('modern_gopher.browser.terminal.GopherClient') as mock_client_class, \
             patch('modern_gopher.browser.terminal.BookmarkManager') as mock_bookmark_manager, \
             patch('modern_gopher.browser.terminal.KeyBindingManager') as mock_kb_manager:
            
            mock_config = Mock()
            mock_config.initial_url = None
            mock_config.cache_enabled = False
            mock_config.cache_directory = "/cache"
            mock_config.max_history_items = 100
            mock_config.bookmarks_file = "/bookmarks.json"
            mock_config.config_dir = "/config"
            mock_get_config.return_value = mock_config
            
            mock_client_class.return_value = Mock()
            mock_bookmark_manager.return_value = Mock()
            
            mock_kb = Mock()
            mock_kb.get_bindings_by_context.return_value = {}
            mock_kb_manager.return_value = mock_kb
            
            return GopherBrowser()

    def test_get_item_icon(self):
        """Test getting icons for different item types."""
        browser = self.create_test_browser()
        
        # Test various item types
        test_cases = [
            (GopherItemType.TEXT_FILE, "📄"),
            (GopherItemType.DIRECTORY, "📁"),
            (GopherItemType.HTML, "🌐"),
            (GopherItemType.BINARY_FILE, "📎"),  # Binary files use paperclip icon
            (GopherItemType.SEARCH_SERVER, "🔍"),
        ]
        
        for item_type, expected_icon in test_cases:
            icon = browser.get_item_icon(item_type)
            assert icon == expected_icon

    def test_format_display_string_short(self):
        """Test format_display_string with short text."""
        browser = self.create_test_browser()
        
        short_text = "Short text"
        result = browser.format_display_string(short_text)
        assert result == short_text

    def test_format_display_string_long(self):
        """Test format_display_string with long text."""
        browser = self.create_test_browser()
        
        long_text = "This is a very long text that exceeds the maximum length limit and should be truncated"
        result = browser.format_display_string(long_text, max_length=50)
        assert len(result) == 53  # 50 + "..."
        assert result.endswith("...")

    def test_handle_navigate_up(self):
        """Test navigating up in the item list."""
        browser = self.create_test_browser()
        
        # Create test items
        browser.current_items = [
            GopherItem(GopherItemType.TEXT_FILE, "Item 1", "/1", "example.com", 70),
            GopherItem(GopherItemType.TEXT_FILE, "Item 2", "/2", "example.com", 70),
            GopherItem(GopherItemType.TEXT_FILE, "Item 3", "/3", "example.com", 70),
        ]
        browser.selected_index = 2
        
        browser._handle_navigate_up()
        assert browser.selected_index == 1
        
        browser._handle_navigate_up()
        assert browser.selected_index == 0
        
        # Should not go below 0
        browser._handle_navigate_up()
        assert browser.selected_index == 0

    def test_handle_navigate_down(self):
        """Test navigating down in the item list."""
        browser = self.create_test_browser()
        
        # Create test items
        browser.current_items = [
            GopherItem(GopherItemType.TEXT_FILE, "Item 1", "/1", "example.com", 70),
            GopherItem(GopherItemType.TEXT_FILE, "Item 2", "/2", "example.com", 70),
            GopherItem(GopherItemType.TEXT_FILE, "Item 3", "/3", "example.com", 70),
        ]
        browser.selected_index = 0
        
        browser._handle_navigate_down()
        assert browser.selected_index == 1
        
        browser._handle_navigate_down()
        assert browser.selected_index == 2
        
        # Should not go beyond last item
        browser._handle_navigate_down()
        assert browser.selected_index == 2

    def test_context_determination_search(self):
        """Test context determination when searching."""
        browser = self.create_test_browser()
        browser.is_searching = True
        
        context = browser._determine_context()
        assert context == KeyContext.SEARCH

    def test_context_determination_content(self):
        """Test context determination for content view."""
        browser = self.create_test_browser()
        browser.is_searching = False
        browser.current_items = []
        browser.content_view.text = "This is a long piece of content that exceeds the 100 character threshold for content context determination and should trigger the content context."
        
        context = browser._determine_context()
        assert context == KeyContext.CONTENT

    def test_context_determination_directory(self):
        """Test context determination for directory view."""
        browser = self.create_test_browser()
        browser.is_searching = False
        browser.current_items = [
            GopherItem(GopherItemType.TEXT_FILE, "Item 1", "/1", "example.com", 70)
        ]
        
        context = browser._determine_context()
        assert context == KeyContext.DIRECTORY

    def test_context_determination_browser(self):
        """Test context determination defaults to browser."""
        browser = self.create_test_browser()
        browser.is_searching = False
        browser.current_items = []
        browser.content_view.text = "Short"
        
        context = browser._determine_context()
        assert context == KeyContext.BROWSER

    def test_update_context(self):
        """Test context update mechanism."""
        browser = self.create_test_browser()
        browser.current_context = KeyContext.BROWSER
        browser._last_keybinding_context = KeyContext.BROWSER
        
        # Set up for directory context
        browser.current_items = [
            GopherItem(GopherItemType.TEXT_FILE, "Item 1", "/1", "example.com", 70)
        ]
        
        browser._update_context()
        assert browser.current_context == KeyContext.DIRECTORY

    def test_convert_key_to_prompt_toolkit(self):
        """Test key conversion to prompt_toolkit format."""
        browser = self.create_test_browser()
        
        # Test simple keys
        assert browser._convert_key_to_prompt_toolkit("enter") == "enter"
        assert browser._convert_key_to_prompt_toolkit("space") == "space"
        
        # Test modifier keys
        assert browser._convert_key_to_prompt_toolkit("c-c") == "c-c"
        assert browser._convert_key_to_prompt_toolkit("a-f1") == "a-f1"
        
        # Test unsupported combinations
        assert browser._convert_key_to_prompt_toolkit("a-left") == "left"
        assert browser._convert_key_to_prompt_toolkit("s-tab") == "tab"

    def test_get_menu_text_empty(self):
        """Test get_menu_text with empty items."""
        browser = self.create_test_browser()
        browser.current_items = []
        
        result = browser.get_menu_text()
        assert result == []

    def test_get_menu_text_with_items(self):
        """Test get_menu_text with items."""
        browser = self.create_test_browser()
        browser.current_items = [
            GopherItem(GopherItemType.TEXT_FILE, "Item 1", "/1", "example.com", 70),
            GopherItem(GopherItemType.DIRECTORY, "Item 2", "/2", "example.com", 70),
        ]
        browser.selected_index = 0
        
        result = browser.get_menu_text()
        assert len(result) == 2
        
        # First item should be selected
        assert result[0][0] == "class:menu.selection"
        assert "📄 Item 1" in result[0][1]
        
        # Second item should not be selected
        assert result[1][0] == ""
        assert "📁 Item 2" in result[1][1]

    def test_handle_search_context_aware_directory(self):
        """Test search handling in directory context."""
        browser = self.create_test_browser()
        browser.current_context = KeyContext.DIRECTORY
        browser.current_items = [
            GopherItem(GopherItemType.TEXT_FILE, "Item 1", "/1", "example.com", 70)
        ]
        
        with patch.object(browser, 'show_search_dialog') as mock_search:
            event = Mock()
            browser._handle_search_context_aware(event)
            mock_search.assert_called_once()

    def test_handle_search_context_aware_content(self):
        """Test search handling in content context."""
        browser = self.create_test_browser()
        browser.current_context = KeyContext.CONTENT
        
        event = Mock()
        browser._handle_search_context_aware(event)
        assert "Search not available in content view" in browser.status_bar.text

    def test_handle_search_clear_context_aware_search(self):
        """Test search clear handling in search context."""
        browser = self.create_test_browser()
        browser.current_context = KeyContext.SEARCH
        browser.is_searching = True
        
        with patch.object(browser, 'clear_search') as mock_clear:
            event = Mock()
            browser._handle_search_clear_context_aware(event)
            mock_clear.assert_called_once()

    def test_handle_search_clear_context_aware_no_search(self):
        """Test search clear handling when not searching."""
        browser = self.create_test_browser()
        browser.current_context = KeyContext.BROWSER
        browser.is_searching = False
        
        event = Mock()
        browser._handle_search_clear_context_aware(event)
        assert "No active search to clear" in browser.status_bar.text

    def test_perform_search_empty_query(self):
        """Test perform search with empty query."""
        browser = self.create_test_browser()
        
        with patch.object(browser, 'clear_search') as mock_clear:
            browser.perform_search("")
            mock_clear.assert_called_once()

    def test_perform_search_with_results(self):
        """Test perform search with matching results."""
        browser = self.create_test_browser()
        browser.current_items = [
            GopherItem(GopherItemType.TEXT_FILE, "Test Item", "/test", "example.com", 70),
            GopherItem(GopherItemType.TEXT_FILE, "Another Item", "/other", "example.com", 70),
            GopherItem(GopherItemType.TEXT_FILE, "Test File", "/test2", "example.com", 70),
        ]
        browser.is_searching = False
        
        browser.perform_search("test")
        
        assert browser.is_searching is True
        assert browser.search_query == "test"
        assert len(browser.current_items) == 2  # Two items match "test"
        assert browser.selected_index == 0

    def test_perform_search_no_results(self):
        """Test perform search with no matching results."""
        browser = self.create_test_browser()
        browser.current_items = [
            GopherItem(GopherItemType.TEXT_FILE, "Item 1", "/1", "example.com", 70),
            GopherItem(GopherItemType.TEXT_FILE, "Item 2", "/2", "example.com", 70),
        ]
        browser.is_searching = False
        
        browser.perform_search("nonexistent")
        
        assert browser.is_searching is True
        assert browser.search_query == "nonexistent"
        assert len(browser.current_items) == 0
        assert "No results found" in browser.status_bar.text

    def test_clear_search(self):
        """Test clearing search results."""
        browser = self.create_test_browser()
        
        # Set up search state
        original_items = [
            GopherItem(GopherItemType.TEXT_FILE, "Item 1", "/1", "example.com", 70),
            GopherItem(GopherItemType.TEXT_FILE, "Item 2", "/2", "example.com", 70),
        ]
        browser.filtered_items = original_items.copy()
        browser.current_items = [original_items[0]]  # Filtered to one item
        browser.is_searching = True
        browser.search_query = "test"
        browser.selected_index = 0
        
        browser.clear_search()
        
        assert browser.is_searching is False
        assert browser.search_query == ""
        assert browser.current_items == original_items
        assert browser.filtered_items == []
        assert browser.selected_index == 0
        assert "Search cleared" in browser.status_bar.text

    def test_url_validator(self):
        """Test URL validator functionality."""
        browser = self.create_test_browser()
        validator = browser._url_validator()
        
        # Test valid URLs (should not raise)
        valid_document = Mock()
        valid_document.text = "gopher://example.com"
        
        # Should not raise ValidationError
        validator.validate(valid_document)
        
        # Test empty text (should not raise)
        empty_document = Mock()
        empty_document.text = ""
        validator.validate(empty_document)

    @patch('modern_gopher.browser.terminal.parse_gopher_url')
    def test_url_validator_invalid_url(self, mock_parse_url):
        """Test URL validator with invalid URL."""
        browser = self.create_test_browser()
        validator = browser._url_validator()
        
        # Make parse_gopher_url raise an exception
        mock_parse_url.side_effect = Exception("Invalid URL")
        
        invalid_document = Mock()
        invalid_document.text = "invalid://url"
        
        # Should raise ValidationError
        with pytest.raises(Exception):  # ValidationError from prompt_toolkit
            validator.validate(invalid_document)


if __name__ == "__main__":
    pytest.main([__file__])

