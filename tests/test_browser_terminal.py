#!/usr/bin/env python3
"""
Tests for the terminal browser functionality.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from modern_gopher.browser.terminal import HistoryManager, GopherBrowser
from modern_gopher.core.types import GopherItem, GopherItemType


class TestHistoryManager:
    """Test the history management functionality."""

    def test_init(self):
        """Test history manager initialization."""
        history = HistoryManager(max_size=50)
        assert history.max_size == 50
        assert history.history == []
        assert history.position == -1

    def test_add_url(self):
        """Test adding URLs to history."""
        history = HistoryManager(max_size=3)
        
        history.add("gopher://example.com/1")
        assert len(history.history) == 1
        assert history.position == 0
        assert history.current() == "gopher://example.com/1"
        
        history.add("gopher://example.com/2")
        assert len(history.history) == 2
        assert history.position == 1
        assert history.current() == "gopher://example.com/2"

    def test_add_duplicate_url(self):
        """Test adding duplicate URLs doesn't create duplicates."""
        history = HistoryManager()
        
        history.add("gopher://example.com")
        history.add("gopher://example.com")
        
        assert len(history.history) == 1
        assert history.position == 0

    def test_max_size_limit(self):
        """Test that history respects max size limit."""
        history = HistoryManager(max_size=2)
        
        history.add("gopher://example.com/1")
        history.add("gopher://example.com/2")
        history.add("gopher://example.com/3")
        
        assert len(history.history) == 2
        assert history.history == ["gopher://example.com/2", "gopher://example.com/3"]
        assert history.position == 1

    def test_back_navigation(self):
        """Test going back in history."""
        history = HistoryManager()
        
        history.add("gopher://example.com/1")
        history.add("gopher://example.com/2")
        history.add("gopher://example.com/3")
        
        # Go back
        url = history.back()
        assert url == "gopher://example.com/2"
        assert history.position == 1
        
        # Go back again
        url = history.back()
        assert url == "gopher://example.com/1"
        assert history.position == 0
        
        # Can't go back further
        url = history.back()
        assert url is None
        assert history.position == 0

    def test_forward_navigation(self):
        """Test going forward in history."""
        history = HistoryManager()
        
        history.add("gopher://example.com/1")
        history.add("gopher://example.com/2")
        history.add("gopher://example.com/3")
        
        # Go back twice
        history.back()
        history.back()
        assert history.position == 0
        
        # Go forward
        url = history.forward()
        assert url == "gopher://example.com/2"
        assert history.position == 1
        
        # Go forward again
        url = history.forward()
        assert url == "gopher://example.com/3"
        assert history.position == 2
        
        # Can't go forward further
        url = history.forward()
        assert url is None
        assert history.position == 2

    def test_truncate_on_new_url_after_back(self):
        """Test that adding new URL after going back truncates future history."""
        history = HistoryManager()
        
        history.add("gopher://example.com/1")
        history.add("gopher://example.com/2")
        history.add("gopher://example.com/3")
        
        # Go back
        history.back()
        assert history.position == 1
        
        # Add new URL
        history.add("gopher://example.com/new")
        
        assert len(history.history) == 3
        assert history.history == [
            "gopher://example.com/1", 
            "gopher://example.com/2", 
            "gopher://example.com/new"
        ]
        assert history.position == 2

    def test_current_empty_history(self):
        """Test current() with empty history."""
        history = HistoryManager()
        assert history.current() is None

    def test_current_invalid_position(self):
        """Test current() with invalid position."""
        history = HistoryManager()
        history.history = ["test"]
        history.position = -1
        assert history.current() is None
        
        history.position = 1
        assert history.current() is None


class TestGopherBrowser:
    """Test the Gopher browser functionality."""

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    def test_browser_init_default(self, mock_keybinding_manager, mock_bookmark_manager, 
                                  mock_gopher_client, mock_get_config):
        """Test browser initialization with defaults."""
        # Setup mocks
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = False
        mock_config.cache_directory = None
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/tmp/bookmarks.json"
        mock_config.session_enabled = False
        mock_config.config_dir = Path("/tmp/config")
        mock_get_config.return_value = mock_config
        
        mock_client = Mock()
        mock_gopher_client.return_value = mock_client
        
        mock_bookmarks = Mock()
        mock_bookmark_manager.return_value = mock_bookmarks
        
        # Create mock KeyBinding objects
        mock_binding = Mock()
        mock_binding.enabled = True
        mock_binding.keys = ['h']
        
        mock_kb_manager = Mock()
        mock_kb_manager.get_bindings_by_context.return_value = {
            'navigate_up': mock_binding,
            'navigate_down': mock_binding, 
            'quit': mock_binding
        }
        mock_keybinding_manager.return_value = mock_kb_manager
        
        # Create browser - mock the import path
        with patch('modern_gopher.plugins.manager.get_manager') as mock_get_manager:
            mock_plugin_manager = Mock()
            mock_get_manager.return_value = mock_plugin_manager
            
            browser = GopherBrowser()
            
            assert browser.current_url == "gopher://gopher.floodgap.com"
            assert browser.current_items == []
            assert browser.filtered_items == []
            assert browser.search_query == ""
            assert browser.is_searching is False
            assert browser.selected_index == 0
            assert browser.use_ssl is False
            assert isinstance(browser.history, HistoryManager)

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    def test_browser_init_with_config_url(self, mock_keybinding_manager, mock_bookmark_manager, 
                                         mock_gopher_client, mock_get_config):
        """Test browser initialization with config URL."""
        # Setup mocks
        mock_config = Mock()
        mock_config.initial_url = "gopher://custom.example.com"
        mock_config.cache_enabled = True
        mock_config.cache_directory = "/tmp/cache"
        mock_config.max_history_items = 50
        mock_config.bookmarks_file = "/tmp/bookmarks.json"
        mock_config.session_enabled = False
        mock_config.config_dir = Path("/tmp/config")
        mock_get_config.return_value = mock_config
        
        mock_client = Mock()
        mock_gopher_client.return_value = mock_client
        
        mock_bookmarks = Mock()
        mock_bookmark_manager.return_value = mock_bookmarks
        
        # Create mock KeyBinding objects
        mock_binding = Mock()
        mock_binding.enabled = True
        mock_binding.keys = ['h']
        
        mock_kb_manager = Mock()
        mock_kb_manager.get_bindings_by_context.return_value = {
            'navigate_up': mock_binding,
            'navigate_down': mock_binding, 
            'quit': mock_binding
        }
        mock_keybinding_manager.return_value = mock_kb_manager
        
        # Create browser - mock the import path
        with patch('modern_gopher.plugins.manager.get_manager') as mock_get_manager:
            mock_plugin_manager = Mock()
            mock_get_manager.return_value = mock_plugin_manager
            
            browser = GopherBrowser()
            
            assert browser.current_url == "gopher://custom.example.com"
            mock_gopher_client.assert_called_with(
                timeout=30, 
                cache_dir="/tmp/cache", 
                use_ipv6=None
            )

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch('modern_gopher.browser.terminal.SessionManager')
    def test_browser_init_with_sessions(self, mock_session_manager, mock_keybinding_manager, 
                                       mock_bookmark_manager, mock_gopher_client, mock_get_config):
        """Test browser initialization with sessions enabled."""
        # Setup mocks
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = False
        mock_config.cache_directory = None
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/tmp/bookmarks.json"
        mock_config.session_enabled = True
        mock_config.session_file = "/tmp/sessions.json"
        mock_config.session_backup_sessions = 3
        mock_config.session_max_sessions = 5
        mock_config.config_dir = Path("/tmp/config")
        mock_get_config.return_value = mock_config
        
        mock_client = Mock()
        mock_gopher_client.return_value = mock_client
        
        mock_bookmarks = Mock()
        mock_bookmark_manager.return_value = mock_bookmarks
        
        # Create mock KeyBinding objects
        mock_binding = Mock()
        mock_binding.enabled = True
        mock_binding.keys = ['h']
        
        mock_kb_manager = Mock()
        mock_kb_manager.get_bindings_by_context.return_value = {
            'navigate_up': mock_binding,
            'navigate_down': mock_binding, 
            'quit': mock_binding
        }
        mock_keybinding_manager.return_value = mock_kb_manager
        
        mock_sessions = Mock()
        mock_session_manager.return_value = mock_sessions
        
        # Create browser - mock the import path
        with patch('modern_gopher.plugins.manager.get_manager') as mock_get_manager:
            mock_plugin_manager = Mock()
            mock_get_manager.return_value = mock_plugin_manager
            
            browser = GopherBrowser()
            
            assert browser.session_manager == mock_sessions
            mock_session_manager.assert_called_with(
                session_file="/tmp/sessions.json",
                backup_sessions=3,
                max_sessions=5
            )

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch('modern_gopher.browser.terminal.SessionManager')
    def test_browser_init_session_error(self, mock_session_manager, mock_keybinding_manager, 
                                       mock_bookmark_manager, mock_gopher_client, mock_get_config):
        """Test browser initialization when session manager fails."""
        # Setup mocks
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = False
        mock_config.cache_directory = None
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/tmp/bookmarks.json"
        mock_config.session_enabled = True
        mock_config.config_dir = Path("/tmp/config")
        mock_get_config.return_value = mock_config
        
        mock_client = Mock()
        mock_gopher_client.return_value = mock_client
        
        mock_bookmarks = Mock()
        mock_bookmark_manager.return_value = mock_bookmarks
        
        # Create mock KeyBinding objects
        mock_binding = Mock()
        mock_binding.enabled = True
        mock_binding.keys = ['h']
        
        mock_kb_manager = Mock()
        mock_kb_manager.get_bindings_by_context.return_value = {
            'navigate_up': mock_binding,
            'navigate_down': mock_binding, 
            'quit': mock_binding
        }
        mock_keybinding_manager.return_value = mock_kb_manager
        
        # Make session manager raise an exception
        mock_session_manager.side_effect = AttributeError("Mock config error")
        
        # Create browser - mock the import path
        with patch('modern_gopher.plugins.manager.get_manager') as mock_get_manager:
            mock_plugin_manager = Mock()
            mock_get_manager.return_value = mock_plugin_manager
            
            browser = GopherBrowser()
            
            assert browser.session_manager is None

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    def test_browser_init_plugin_manager_error(self, mock_keybinding_manager, mock_bookmark_manager, 
                                              mock_gopher_client, mock_get_config):
        """Test browser initialization when plugin manager fails."""
        # Setup mocks
        mock_config = Mock()
        mock_config.initial_url = None
        mock_config.cache_enabled = False
        mock_config.cache_directory = None
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/tmp/bookmarks.json"
        mock_config.session_enabled = False
        mock_config.config_dir = Path("/tmp/config")
        mock_get_config.return_value = mock_config
        
        mock_client = Mock()
        mock_gopher_client.return_value = mock_client
        
        mock_bookmarks = Mock()
        mock_bookmark_manager.return_value = mock_bookmarks
        
        # Create mock KeyBinding objects
        mock_binding = Mock()
        mock_binding.enabled = True
        mock_binding.keys = ['h']
        
        mock_kb_manager = Mock()
        mock_kb_manager.get_bindings_by_context.return_value = {
            'navigate_up': mock_binding,
            'navigate_down': mock_binding, 
            'quit': mock_binding
        }
        mock_keybinding_manager.return_value = mock_kb_manager
        
        # Create browser with plugin manager error
        with patch('modern_gopher.plugins.manager.get_manager') as mock_get_manager:
            mock_get_manager.side_effect = Exception("Plugin manager error")
            
            browser = GopherBrowser()
            
            assert browser.plugin_manager is None

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    def test_browser_with_custom_params(self, mock_keybinding_manager, mock_bookmark_manager, 
                                       mock_gopher_client, mock_get_config):
        """Test browser initialization with custom parameters."""
        # Setup mocks
        mock_config = Mock()
        mock_config.initial_url = "gopher://config.example.com"
        mock_config.cache_enabled = True
        mock_config.cache_directory = "/config/cache"
        mock_config.max_history_items = 200
        mock_config.bookmarks_file = "/tmp/bookmarks.json"
        mock_config.session_enabled = False
        mock_config.config_dir = Path("/tmp/config")
        mock_get_config.return_value = mock_config
        
        mock_client = Mock()
        mock_gopher_client.return_value = mock_client
        
        mock_bookmarks = Mock()
        mock_bookmark_manager.return_value = mock_bookmarks
        
        # Create mock KeyBinding objects
        mock_binding = Mock()
        mock_binding.enabled = True
        mock_binding.keys = ['h']
        
        mock_kb_manager = Mock()
        mock_kb_manager.get_bindings_by_context.return_value = {
            'navigate_up': mock_binding,
            'navigate_down': mock_binding, 
            'quit': mock_binding
        }
        mock_keybinding_manager.return_value = mock_kb_manager
        
        # Create browser with custom parameters
        with patch('modern_gopher.plugins.manager.get_manager') as mock_get_manager:
            mock_plugin_manager = Mock()
            mock_get_manager.return_value = mock_plugin_manager
            
            browser = GopherBrowser(
                initial_url="gopher://custom.example.com",
                timeout=60,
                use_ssl=True,
                use_ipv6=True,
                cache_dir="/custom/cache"
            )
            
            # Custom parameters should override config
            assert browser.current_url == "gopher://custom.example.com"
            assert browser.use_ssl is True
            mock_gopher_client.assert_called_with(
                timeout=60,
                cache_dir="/custom/cache",
                use_ipv6=True
            )


if __name__ == "__main__":
    pytest.main([__file__])

