"""
Advanced browser terminal tests targeting uncovered functionality.

This module contains comprehensive tests for the GopherBrowser terminal
interface that were missing test coverage, focusing on content processing,
session management, plugin integration, and error handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
import logging

# Import the browser terminal classes to test
from modern_gopher.browser.terminal import GopherBrowser, launch_browser
from modern_gopher.core.types import GopherItem, GopherItemType
from modern_gopher.core.protocol import GopherProtocolError


class TestGopherBrowserAdvancedFunctionality:
    """Test advanced GopherBrowser functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        # Mock configuration
        self.mock_config = Mock()
        self.mock_config.gopher_host = "test.example.com"
        self.mock_config.gopher_port = 70
        self.mock_config.gopher_timeout = 30
        self.mock_config.session_auto_restore = False
        self.mock_config.save_session = False
        self.mock_config.sessions_enabled = True
        self.mock_config.session_enabled = False  # Note: different from sessions_enabled
        self.mock_config.ui_color_scheme = "default"
        self.mock_config.ui_show_status_bar = True
        self.mock_config.ui_show_help = True
        self.mock_config.effective_initial_url = "gopher://test.example.com/"
        self.mock_config.initial_url = None
        self.mock_config.cache_enabled = False
        self.mock_config.cache_directory = None
        self.mock_config.max_history_items = 100
        self.mock_config.bookmarks_file = "/tmp/bookmarks.json"
        self.mock_config.session_file = "/tmp/sessions.json"
        self.mock_config.config_dir = "/tmp/config"
        
        # Mock gopher item
        self.mock_item = Mock(spec=GopherItem)
        self.mock_item.host = "test.example.com"
        self.mock_item.port = 70
        self.mock_item.selector = "/test"
        self.mock_item.item_type = GopherItemType.TEXT_FILE
        self.mock_item.display_string = "Test Item"

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    def test_init_with_plugin_manager_error(self, mock_keybinding_manager, mock_bookmark_manager, mock_session_manager, mock_get_manager, mock_client, mock_get_config):
        """Test browser initialization when plugin manager initialization fails."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        mock_get_manager.side_effect = Exception("Plugin manager error")
        
        # This should not raise an exception, plugin manager should be None
        browser = GopherBrowser()
        
        # Verify plugin manager is None due to error
        assert browser.plugin_manager is None

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    def test_init_with_session_manager_error(self, mock_keybinding_manager, mock_bookmark_manager, mock_session_manager, mock_get_manager, mock_client, mock_get_config):
        """Test browser initialization when session manager initialization fails."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        mock_session_manager.side_effect = Exception("Session manager error")
        
        # This should not raise an exception, session manager should be None
        browser = GopherBrowser()
        
        # Verify session manager is None due to error
        assert browser.session_manager is None

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    def test_navigate_to_with_plugin_processing(self, mock_app, mock_setup_keybindings, mock_setup_ui, mock_keybinding_manager, mock_bookmark_manager, mock_session_manager, mock_get_manager, mock_client, mock_get_config):
        """Test navigate_to with plugin processing of content."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        # Mock plugin manager
        mock_plugin_manager = Mock()
        mock_get_manager.return_value = mock_plugin_manager
        
        # Create browser instance
        browser = GopherBrowser()
        browser.update_display = Mock()
        browser._update_context = Mock()
        
        # Mock the client response for text content
        test_content = "Test text content"
        mock_client_instance.get_resource.return_value = test_content
        
        # Mock plugin processing
        processed_content = "Processed test content"
        metadata = {"processing_steps": ["test_processor"]}
        mock_plugin_manager.process_content.return_value = (processed_content, metadata)
        
        # Execute navigation
        browser.navigate_to("gopher://test.example.com/0/test")
        
        # Verify plugin processing was called
        mock_plugin_manager.process_content.assert_called_once()
        
        # Verify content was processed
        assert browser.content_view.text == processed_content

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    def test_navigate_to_with_plugin_processing_error(self, mock_session_manager, mock_get_manager, mock_client, mock_get_config):
        """Test navigate_to when plugin processing fails."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        # Mock plugin manager that throws an error
        mock_plugin_manager = Mock()
        mock_get_manager.return_value = mock_plugin_manager
        mock_plugin_manager.process_content.side_effect = Exception("Plugin error")
        
        # Create browser instance
        browser = GopherBrowser()
        browser.update_display = Mock()
        browser._update_context = Mock()
        
        # Mock the client response
        test_content = "Test text content"
        mock_client_instance.get_resource.return_value = test_content
        
        # Execute navigation
        with patch('modern_gopher.browser.terminal.logger') as mock_logger:
            browser.navigate_to("gopher://test.example.com/0/test")
            
            # Verify error was logged
            mock_logger.error.assert_called()
            
            # Verify fallback to original content
            assert browser.content_view.text == test_content

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    @patch('modern_gopher.browser.terminal.render_html_to_text')
    def test_navigate_to_html_content(self, mock_render_html, mock_session_manager, mock_get_manager, mock_client, mock_get_config):
        """Test navigate_to with HTML content rendering."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        # Create browser instance
        browser = GopherBrowser()
        browser.update_display = Mock()
        browser._update_context = Mock()
        
        # Mock HTML content
        html_content = "<html><body><h1>Test</h1><a href='link'>Link</a></body></html>"
        mock_client_instance.get_resource.return_value = html_content
        
        # Mock HTML rendering
        rendered_text = "Test\nLink"
        extracted_links = [{"text": "Link", "url": "link"}]
        mock_render_html.return_value = (rendered_text, extracted_links)
        
        # Execute navigation
        browser.navigate_to("gopher://test.example.com/h/test.html")
        
        # Verify HTML rendering was called
        mock_render_html.assert_called_once_with(html_content)
        
        # Verify rendered content and links
        assert browser.content_view.text == rendered_text
        assert browser.extracted_html_links == extracted_links

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    @patch('modern_gopher.browser.terminal.render_html_to_text')
    def test_navigate_to_html_rendering_error(self, mock_render_html, mock_session_manager, mock_get_manager, mock_client, mock_get_config):
        """Test navigate_to when HTML rendering fails."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        # Create browser instance
        browser = GopherBrowser()
        browser.update_display = Mock()
        browser._update_context = Mock()
        
        # Mock HTML content
        html_content = "<html><body>Invalid HTML</body>"
        mock_client_instance.get_resource.return_value = html_content
        
        # Mock HTML rendering failure
        mock_render_html.side_effect = Exception("HTML parsing error")
        
        # Execute navigation
        with patch('modern_gopher.browser.terminal.logger') as mock_logger:
            browser.navigate_to("gopher://test.example.com/h/test.html")
            
            # Verify error was logged
            mock_logger.warning.assert_called()
            
            # Verify fallback to raw content
            assert browser.content_view.text == html_content

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    def test_navigate_to_binary_content(self, mock_session_manager, mock_get_manager, mock_client, mock_get_config):
        """Test navigate_to with binary content processing."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        # Mock plugin manager
        mock_plugin_manager = Mock()
        mock_get_manager.return_value = mock_plugin_manager
        
        # Create browser instance
        browser = GopherBrowser()
        browser.update_display = Mock()
        browser._update_context = Mock()
        
        # Mock binary content
        binary_content = b"Binary data content"
        mock_client_instance.get_resource.return_value = binary_content
        
        # Mock plugin processing
        processed_content = "Image: test.png (1024x768)"
        metadata = {"processing_steps": ["image_handler"]}
        mock_plugin_manager.process_content.return_value = (processed_content, metadata)
        
        # Execute navigation
        browser.navigate_to("gopher://test.example.com/I/test.png")
        
        # Verify plugin processing was called
        mock_plugin_manager.process_content.assert_called_once()
        
        # Verify content was processed
        assert browser.content_view.text == processed_content

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    def test_navigate_to_binary_content_no_plugins(self, mock_session_manager, mock_get_manager, mock_client, mock_get_config):
        """Test navigate_to with binary content when no plugins available."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        # Create browser instance without plugin manager
        browser = GopherBrowser()
        browser.plugin_manager = None
        browser.update_display = Mock()
        browser._update_context = Mock()
        
        # Mock binary content
        binary_content = b"Binary data content"
        mock_client_instance.get_resource.return_value = binary_content
        
        # Execute navigation
        browser.navigate_to("gopher://test.example.com/I/test.png")
        
        # Verify default binary content message
        assert "Binary content (19 bytes)" in browser.content_view.text

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    def test_navigate_to_protocol_error(self, mock_session_manager, mock_get_manager, mock_client, mock_get_config):
        """Test navigate_to when protocol error occurs."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        # Create browser instance
        browser = GopherBrowser()
        browser.update_display = Mock()
        browser.update_status_bar = Mock()
        
        # Mock protocol error
        mock_client_instance.get_resource.side_effect = GopherProtocolError("Server not found")
        
        # Execute navigation
        with patch('modern_gopher.browser.terminal.logger') as mock_logger:
            browser.navigate_to("gopher://invalid.example.com/")
            
            # Verify error handling
            assert "Error: Server not found" in browser.content_view.text
            assert browser.is_loading is False
            mock_logger.error.assert_called()

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    def test_open_selected_item(self, mock_session_manager, mock_get_manager, mock_client, mock_get_config):
        """Test opening a selected item."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        
        # Create browser instance
        browser = GopherBrowser()
        browser.navigate_to = Mock()
        
        # Set up current items
        browser.current_items = [self.mock_item]
        browser.selected_index = 0
        browser.use_ssl = False
        
        # Execute opening selected item
        browser.open_selected_item()
        
        # Verify navigation was called with correct URL
        expected_url = f"gopher://{self.mock_item.host}:{self.mock_item.port}/{self.mock_item.item_type.value}{self.mock_item.selector}"
        browser.navigate_to.assert_called_once_with(expected_url)

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    def test_open_selected_item_no_items(self, mock_session_manager, mock_get_manager, mock_client, mock_get_config):
        """Test opening selected item when no items available."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        
        # Create browser instance
        browser = GopherBrowser()
        browser.navigate_to = Mock()
        
        # Set up empty items
        browser.current_items = []
        browser.selected_index = 0
        
        # Execute opening selected item
        browser.open_selected_item()
        
        # Verify navigation was not called
        browser.navigate_to.assert_not_called()

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    def test_go_back(self, mock_session_manager, mock_get_manager, mock_client, mock_get_config):
        """Test going back in history."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        
        # Create browser instance
        browser = GopherBrowser()
        browser.navigate_to = Mock()
        browser.history = Mock()
        browser.history.back.return_value = "gopher://previous.example.com/"
        
        # Execute go back
        browser.go_back()
        
        # Verify navigation was called
        browser.navigate_to.assert_called_once_with("gopher://previous.example.com/")

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    def test_go_back_no_history(self, mock_session_manager, mock_get_manager, mock_client, mock_get_config):
        """Test going back when no history available."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        
        # Create browser instance
        browser = GopherBrowser()
        browser.navigate_to = Mock()
        browser.history = Mock()
        browser.history.back.return_value = None
        
        # Execute go back
        browser.go_back()
        
        # Verify navigation was not called
        browser.navigate_to.assert_not_called()

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    def test_go_forward(self, mock_session_manager, mock_get_manager, mock_client, mock_get_config):
        """Test going forward in history."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        
        # Create browser instance
        browser = GopherBrowser()
        browser.navigate_to = Mock()
        browser.history = Mock()
        browser.history.forward.return_value = "gopher://forward.example.com/"
        
        # Execute go forward
        browser.go_forward()
        
        # Verify navigation was called
        browser.navigate_to.assert_called_once_with("gopher://forward.example.com/")

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    def test_refresh(self, mock_session_manager, mock_get_manager, mock_client, mock_get_config):
        """Test refreshing the current page."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        # Create browser instance
        browser = GopherBrowser()
        browser.navigate_to = Mock()
        browser.current_url = "gopher://test.example.com/"
        
        # Mock cache with entry
        cache_key = "test_cache_key"
        mock_client_instance._cache_key.return_value = cache_key
        mock_client_instance.memory_cache = {cache_key: "cached_data"}
        
        # Execute refresh
        browser.refresh()
        
        # Verify cache was cleared and navigation called
        assert cache_key not in mock_client_instance.memory_cache
        browser.navigate_to.assert_called_once_with("gopher://test.example.com/")

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    def test_get_browser_state(self, mock_session_manager, mock_get_manager, mock_client, mock_get_config):
        """Test getting browser state for session saving."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        
        # Create browser instance
        browser = GopherBrowser()
        browser.current_url = "gopher://test.example.com/"
        browser.selected_index = 2
        browser.is_searching = True
        browser.search_query = "test search"
        
        # Mock history
        browser.history = Mock()
        browser.history.history = ["url1", "url2", "url3"]
        browser.history.position = 1
        
        # Get browser state
        state = browser.get_browser_state()
        
        # Verify state
        assert state["current_url"] == "gopher://test.example.com/"
        assert state["selected_index"] == 2
        assert state["is_searching"] is True
        assert state["search_query"] == "test search"
        assert state["history"] == ["url1", "url2", "url3"]
        assert state["history_position"] == 1

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    def test_restore_browser_state(self, mock_session_manager, mock_get_manager, mock_client, mock_get_config):
        """Test restoring browser state from session data."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        
        # Create browser instance
        browser = GopherBrowser()
        browser.navigate_to = Mock()
        browser.history = Mock()
        
        # Session state to restore
        state = {
            "current_url": "gopher://restored.example.com/",
            "history": ["url1", "url2"],
            "history_position": 1,
            "selected_index": 3,
            "is_searching": True,
            "search_query": "restored search"
        }
        
        # Execute restore
        with patch('modern_gopher.browser.terminal.logger') as mock_logger:
            browser.restore_browser_state(state)
            
            # Verify state was restored
            assert browser.current_url == "gopher://restored.example.com/"
            assert browser.selected_index == 3
            assert browser.is_searching is True
            assert browser.search_query == "restored search"
            
            # Verify history was restored
            browser.history.history = ["url1", "url2"]
            browser.history.position = 1
            
            # Verify navigation was called
            browser.navigate_to.assert_called_once_with("gopher://restored.example.com/")
            mock_logger.info.assert_called()

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    def test_restore_browser_state_error(self, mock_session_manager, mock_get_manager, mock_client, mock_get_config):
        """Test restoring browser state when error occurs."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        
        # Create browser instance
        browser = GopherBrowser()
        browser.navigate_to = Mock()
        browser.navigate_to.side_effect = Exception("Navigation error")
        
        # Session state to restore
        state = {"current_url": "gopher://restored.example.com/"}
        
        # Execute restore
        with patch('modern_gopher.browser.terminal.logger') as mock_logger:
            browser.restore_browser_state(state)
            
            # Verify error was logged
            mock_logger.error.assert_called()

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    def test_auto_restore_session_disabled(self, mock_session_manager, mock_get_manager, mock_client, mock_get_config):
        """Test auto restore session when disabled."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        self.mock_config.session_auto_restore = False
        
        # Create browser instance
        browser = GopherBrowser()
        
        # Execute auto restore
        result = browser.auto_restore_session()
        
        # Verify it returns False when disabled
        assert result is False

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    def test_auto_restore_session_success(self, mock_session_manager_class, mock_get_manager, mock_client, mock_get_config):
        """Test successful auto restore session."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        self.mock_config.session_auto_restore = True
        
        mock_session_manager = Mock()
        mock_session_manager_class.return_value = mock_session_manager
        
        # Create browser instance
        browser = GopherBrowser()
        browser.restore_browser_state = Mock()
        
        # Mock session data
        session_data = {"current_url": "gopher://restored.example.com/"}
        mock_session_manager.get_default_session.return_value = session_data
        
        # Execute auto restore
        with patch('modern_gopher.browser.terminal.logger') as mock_logger:
            result = browser.auto_restore_session()
            
            # Verify success
            assert result is True
            browser.restore_browser_state.assert_called_once_with(session_data)
            mock_logger.info.assert_called()

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    def test_auto_restore_session_no_session(self, mock_session_manager_class, mock_get_manager, mock_client, mock_get_config):
        """Test auto restore session when no session available."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        self.mock_config.session_auto_restore = True
        
        mock_session_manager = Mock()
        mock_session_manager_class.return_value = mock_session_manager
        
        # Create browser instance
        browser = GopherBrowser()
        
        # Mock no session data
        mock_session_manager.get_default_session.return_value = None
        
        # Execute auto restore
        with patch('modern_gopher.browser.terminal.logger') as mock_logger:
            result = browser.auto_restore_session()
            
            # Verify no session case
            assert result is False
            mock_logger.info.assert_called()

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    def test_show_session_dialog_no_sessions(self, mock_session_manager_class, mock_get_manager, mock_client, mock_get_config):
        """Test session dialog when no sessions available."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        
        mock_session_manager = Mock()
        mock_session_manager_class.return_value = mock_session_manager
        
        # Create browser instance
        browser = GopherBrowser()
        
        # Mock no sessions
        mock_session_manager.list_sessions.return_value = []
        
        # Execute show session dialog
        browser.show_session_dialog()
        
        # Verify status message
        assert browser.status_bar.text == "No saved sessions"

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    def test_show_session_dialog_with_sessions(self, mock_session_manager_class, mock_get_manager, mock_client, mock_get_config):
        """Test session dialog with available sessions."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        
        mock_session_manager = Mock()
        mock_session_manager_class.return_value = mock_session_manager
        
        # Create browser instance
        browser = GopherBrowser()
        
        # Mock session data
        mock_session = Mock()
        mock_session.name = "Test Session"
        mock_session.current_url = "gopher://test.example.com/"
        mock_session.created_datetime = datetime(2024, 1, 1, 12, 0)
        mock_session.last_used_datetime = datetime(2024, 1, 2, 12, 0)
        mock_session.description = "Test description"
        mock_session.tags = ["test", "demo"]
        
        mock_session_manager.list_sessions.return_value = [mock_session]
        
        # Execute show session dialog
        browser.show_session_dialog()
        
        # Verify content was updated
        assert "Test Session" in browser.content_view.text
        assert "gopher://test.example.com/" in browser.content_view.text
        assert "Showing 1 saved sessions" in browser.status_bar.text

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    def test_auto_save_session_on_exit(self, mock_session_manager_class, mock_get_manager, mock_client, mock_get_config):
        """Test auto save session on exit."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        self.mock_config.save_session = True
        
        mock_session_manager = Mock()
        mock_session_manager_class.return_value = mock_session_manager
        
        # Create browser instance
        browser = GopherBrowser()
        browser.get_browser_state = Mock()
        browser.get_browser_state.return_value = {"current_url": "gopher://test.example.com/"}
        
        # Mock successful save
        mock_session_manager.save_session.return_value = "session_id_123"
        
        # Execute auto save
        with patch('modern_gopher.browser.terminal.logger') as mock_logger:
            with patch('modern_gopher.browser.terminal.datetime') as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = "2024-01-01 12:00"
                browser.auto_save_session_on_exit()
                
                # Verify save was called
                mock_session_manager.save_session.assert_called_once()
                mock_logger.info.assert_called()

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    def test_run_with_session_restore(self, mock_session_manager, mock_get_manager, mock_client, mock_get_config):
        """Test browser run with session restore."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        self.mock_config.session_auto_restore = True
        
        # Create browser instance
        browser = GopherBrowser()
        browser.auto_restore_session = Mock(return_value=True)
        browser.auto_save_session_on_exit = Mock()
        browser._update_context = Mock()
        browser.update_status_bar = Mock()
        
        # Mock the app
        browser.app = Mock()
        
        # Execute run
        result = browser.run()
        
        # Verify session restore was attempted
        browser.auto_restore_session.assert_called_once()
        
        # Verify app was run
        browser.app.run.assert_called_once()
        
        # Verify exit code
        assert result == 0

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    def test_run_keyboard_interrupt(self, mock_session_manager, mock_get_manager, mock_client, mock_get_config):
        """Test browser run with keyboard interrupt."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        
        # Create browser instance
        browser = GopherBrowser()
        browser.auto_restore_session = Mock(return_value=False)
        browser.auto_save_session_on_exit = Mock()
        browser.navigate_to = Mock()
        browser._update_context = Mock()
        browser.update_status_bar = Mock()
        
        # Mock the app to raise KeyboardInterrupt
        browser.app = Mock()
        browser.app.run.side_effect = KeyboardInterrupt()
        
        # Execute run
        result = browser.run()
        
        # Verify exit code for keyboard interrupt
        assert result == 130
        
        # Verify auto save was called
        browser.auto_save_session_on_exit.assert_called()

    @patch('modern_gopher.browser.terminal.get_config')
    @patch('modern_gopher.browser.terminal.GopherClient')
    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.browser.terminal.BookmarkManager')
    @patch('modern_gopher.browser.terminal.KeyBindingManager')
    @patch.object(GopherBrowser, 'setup_ui', return_value=None)
    @patch.object(GopherBrowser, 'setup_keybindings', return_value=None)
    @patch('modern_gopher.browser.terminal.Application')
    @patch('modern_gopher.browser.terminal.SessionManager')
    def test_run_unexpected_error(self, mock_session_manager, mock_get_manager, mock_client, mock_get_config):
        """Test browser run with unexpected error."""
        # Setup mocks
        mock_get_config.return_value = self.mock_config
        
        # Create browser instance
        browser = GopherBrowser()
        browser.auto_restore_session = Mock(return_value=False)
        browser.navigate_to = Mock()
        browser._update_context = Mock()
        browser.update_status_bar = Mock()
        
        # Mock the app to raise unexpected error
        browser.app = Mock()
        browser.app.run.side_effect = Exception("Unexpected error")
        
        # Execute run
        with patch('modern_gopher.browser.terminal.logger') as mock_logger:
            result = browser.run()
            
            # Verify exit code for error
            assert result == 1
            
            # Verify error was logged
            mock_logger.exception.assert_called()


class TestLaunchBrowserFunction:
    """Test the launch_browser function."""

    @patch('modern_gopher.browser.terminal.GopherBrowser')
    def test_launch_browser_success(self, mock_browser_class):
        """Test successful browser launch."""
        # Setup mocks
        mock_browser = Mock()
        mock_browser_class.return_value = mock_browser
        mock_browser.run.return_value = 0
        
        # Execute launch
        result = launch_browser(
            url="gopher://test.example.com/",
            timeout=60,
            use_ssl=True,
            use_ipv6=True,
            cache_dir="/tmp/cache"
        )
        
        # Verify browser was created with correct parameters
        mock_browser_class.assert_called_once_with(
            initial_url="gopher://test.example.com/",
            timeout=60,
            use_ssl=True,
            use_ipv6=True,
            cache_dir="/tmp/cache"
        )
        
        # Verify result
        assert result == 0

    @patch('modern_gopher.browser.terminal.GopherBrowser')
    def test_launch_browser_error(self, mock_browser_class):
        """Test browser launch with error."""
        # Setup mocks
        mock_browser_class.side_effect = Exception("Browser initialization failed")
        
        # Execute launch
        with patch('modern_gopher.browser.terminal.logger') as mock_logger:
            result = launch_browser()
            
            # Verify error was logged
            mock_logger.exception.assert_called()
            
            # Verify error exit code
            assert result == 1


if __name__ == "__main__":
    pytest.main([__file__])

