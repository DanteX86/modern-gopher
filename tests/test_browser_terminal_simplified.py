"""
Simplified browser terminal tests targeting uncovered functionality.

This module contains focused tests for the GopherBrowser terminal
interface to improve coverage in uncovered areas.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import the browser terminal classes to test
from modern_gopher.browser.terminal import GopherBrowser, launch_browser
from modern_gopher.core.types import GopherItem, GopherItemType
from modern_gopher.core.protocol import GopherProtocolError


class TestGopherBrowserSimplified:
    """Test GopherBrowser functionality with simplified setup."""

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
        self.mock_config.session_enabled = False
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

    def create_mock_browser(self):
        """Create a browser instance with all UI dependencies mocked."""
        with patch('modern_gopher.browser.terminal.get_config', return_value=self.mock_config), \
             patch('modern_gopher.browser.terminal.GopherClient') as mock_client, \
             patch('modern_gopher.plugins.manager.get_manager') as mock_get_manager, \
             patch('modern_gopher.browser.terminal.BookmarkManager'), \
             patch('modern_gopher.browser.terminal.KeyBindingManager'), \
             patch.object(GopherBrowser, 'setup_ui', return_value=None), \
             patch.object(GopherBrowser, 'setup_keybindings', return_value=None), \
             patch('modern_gopher.browser.terminal.Application') as mock_app, \
             patch('modern_gopher.browser.terminal.SessionManager'):
            
            browser = GopherBrowser()
            
            # Mock client instance
            mock_client_instance = Mock()
            mock_client.return_value = mock_client_instance
            browser.client = mock_client_instance
            
            # Mock plugin manager
            mock_plugin_manager = Mock()
            mock_get_manager.return_value = mock_plugin_manager
            browser.plugin_manager = mock_plugin_manager
            
            # Mock UI components that tests expect
            browser.content_view = Mock()
            browser.content_view.text = ""
            browser.status_bar = Mock()
            browser.status_bar.text = ""
            browser.update_display = Mock()
            browser._update_context = Mock()
            browser.update_status_bar = Mock()
            
            return browser

    def test_init_with_plugin_manager_error(self):
        """Test browser initialization when plugin manager initialization fails."""
        with patch('modern_gopher.browser.terminal.get_config', return_value=self.mock_config), \
             patch('modern_gopher.browser.terminal.GopherClient'), \
             patch('modern_gopher.plugins.manager.get_manager', side_effect=Exception("Plugin manager error")), \
             patch('modern_gopher.browser.terminal.BookmarkManager'), \
             patch('modern_gopher.browser.terminal.KeyBindingManager'), \
             patch.object(GopherBrowser, 'setup_ui', return_value=None), \
             patch.object(GopherBrowser, 'setup_keybindings', return_value=None), \
             patch('modern_gopher.browser.terminal.Application'), \
             patch('modern_gopher.browser.terminal.SessionManager'):
            
            browser = GopherBrowser()
            assert browser.plugin_manager is None

    def test_navigate_to_with_plugin_processing(self):
        """Test navigate_to with plugin processing of content."""
        browser = self.create_mock_browser()
        
        # Mock the client response for text content
        test_content = "Test text content"
        browser.client.get_resource.return_value = test_content
        
        # Mock plugin processing
        processed_content = "Processed test content"
        metadata = {"processing_steps": ["test_processor"]}
        browser.plugin_manager.process_content.return_value = (processed_content, metadata)
        
        # Execute navigation
        browser.navigate_to("gopher://test.example.com/0/test")
        
        # Verify plugin processing was called
        browser.plugin_manager.process_content.assert_called_once()
        
        # Verify content was processed
        assert browser.content_view.text == processed_content

    def test_navigate_to_with_plugin_processing_error(self):
        """Test navigate_to when plugin processing fails."""
        browser = self.create_mock_browser()
        
        # Mock plugin manager that throws an error
        browser.plugin_manager.process_content.side_effect = Exception("Plugin error")
        
        # Mock the client response
        test_content = "Test text content"
        browser.client.get_resource.return_value = test_content
        
        # Execute navigation
        with patch('modern_gopher.browser.terminal.logger') as mock_logger:
            browser.navigate_to("gopher://test.example.com/0/test")
            
            # Verify error was logged
            mock_logger.error.assert_called()
            
            # Verify fallback to original content
            assert browser.content_view.text == test_content

    def test_navigate_to_html_content(self):
        """Test navigate_to with HTML content rendering."""
        browser = self.create_mock_browser()
        
        # Mock HTML content
        html_content = "<html><body><h1>Test</h1><a href='link'>Link</a></body></html>"
        browser.client.get_resource.return_value = html_content
        
        # Mock HTML rendering
        rendered_text = "Test\nLink"
        extracted_links = [{"text": "Link", "url": "link"}]
        
        with patch('modern_gopher.browser.terminal.render_html_to_text', return_value=(rendered_text, extracted_links)):
            # Execute navigation
            browser.navigate_to("gopher://test.example.com/h/test.html")
            
            # Verify rendered content and links
            assert browser.content_view.text == rendered_text
            assert browser.extracted_html_links == extracted_links

    def test_navigate_to_binary_content(self):
        """Test navigate_to with binary content processing."""
        browser = self.create_mock_browser()
        
        # Mock binary content
        binary_content = b"Binary data content"
        browser.client.get_resource.return_value = binary_content
        
        # Mock plugin processing
        processed_content = "Image: test.png (1024x768)"
        metadata = {"processing_steps": ["image_handler"]}
        browser.plugin_manager.process_content.return_value = (processed_content, metadata)
        
        # Execute navigation
        browser.navigate_to("gopher://test.example.com/I/test.png")
        
        # Verify plugin processing was called
        browser.plugin_manager.process_content.assert_called_once()
        
        # Verify content was processed
        assert browser.content_view.text == processed_content

    def test_navigate_to_binary_content_no_plugins(self):
        """Test navigate_to with binary content when no plugins available."""
        browser = self.create_mock_browser()
        browser.plugin_manager = None
        
        # Mock binary content
        binary_content = b"Binary data content"
        browser.client.get_resource.return_value = binary_content
        
        # Execute navigation
        browser.navigate_to("gopher://test.example.com/I/test.png")
        
        # Verify default binary content message
        assert "Binary content (19 bytes)" in browser.content_view.text

    def test_navigate_to_protocol_error(self):
        """Test navigate_to when protocol error occurs."""
        browser = self.create_mock_browser()
        
        # Mock protocol error
        browser.client.get_resource.side_effect = GopherProtocolError("Server not found")
        
        # Execute navigation
        with patch('modern_gopher.browser.terminal.logger') as mock_logger:
            browser.navigate_to("gopher://invalid.example.com/")
            
            # Verify error handling
            assert "Error: Server not found" in browser.content_view.text
            assert browser.is_loading is False
            mock_logger.error.assert_called()

    def test_open_selected_item(self):
        """Test opening a selected item."""
        browser = self.create_mock_browser()
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

    def test_open_selected_item_no_items(self):
        """Test opening selected item when no items available."""
        browser = self.create_mock_browser()
        browser.navigate_to = Mock()
        
        # Set up empty items
        browser.current_items = []
        browser.selected_index = 0
        
        # Execute opening selected item
        browser.open_selected_item()
        
        # Verify navigation was not called
        browser.navigate_to.assert_not_called()

    def test_go_back(self):
        """Test going back in history."""
        browser = self.create_mock_browser()
        browser.navigate_to = Mock()
        browser.history = Mock()
        browser.history.back.return_value = "gopher://previous.example.com/"
        
        # Execute go back
        browser.go_back()
        
        # Verify navigation was called
        browser.navigate_to.assert_called_once_with("gopher://previous.example.com/")

    def test_go_back_no_history(self):
        """Test going back when no history available."""
        browser = self.create_mock_browser()
        browser.navigate_to = Mock()
        browser.history = Mock()
        browser.history.back.return_value = None
        
        # Execute go back
        browser.go_back()
        
        # Verify navigation was not called
        browser.navigate_to.assert_not_called()

    def test_go_forward(self):
        """Test going forward in history."""
        browser = self.create_mock_browser()
        browser.navigate_to = Mock()
        browser.history = Mock()
        browser.history.forward.return_value = "gopher://forward.example.com/"
        
        # Execute go forward
        browser.go_forward()
        
        # Verify navigation was called
        browser.navigate_to.assert_called_once_with("gopher://forward.example.com/")

    def test_refresh(self):
        """Test refreshing the current page."""
        browser = self.create_mock_browser()
        browser.navigate_to = Mock()
        browser.current_url = "gopher://test.example.com/"
        
        # Mock cache with entry
        cache_key = "test_cache_key"
        browser.client._cache_key.return_value = cache_key
        browser.client.memory_cache = {cache_key: "cached_data"}
        
        # Execute refresh
        browser.refresh()
        
        # Verify cache was cleared and navigation called
        assert cache_key not in browser.client.memory_cache
        browser.navigate_to.assert_called_once_with("gopher://test.example.com/")

    def test_get_browser_state(self):
        """Test getting browser state for session saving."""
        browser = self.create_mock_browser()
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

    def test_restore_browser_state(self):
        """Test restoring browser state from session data."""
        browser = self.create_mock_browser()
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
            
            # Verify navigation was called
            browser.navigate_to.assert_called_once_with("gopher://restored.example.com/")
            mock_logger.info.assert_called()

    def test_auto_restore_session_disabled(self):
        """Test auto restore session when disabled."""
        browser = self.create_mock_browser()
        self.mock_config.session_auto_restore = False
        
        # Execute auto restore
        result = browser.auto_restore_session()
        
        # Verify it returns False when disabled
        assert result is False

    def test_run_keyboard_interrupt(self):
        """Test browser run with keyboard interrupt."""
        browser = self.create_mock_browser()
        browser.auto_restore_session = Mock(return_value=False)
        browser.auto_save_session_on_exit = Mock()
        browser.navigate_to = Mock()
        
        # Mock the app to raise KeyboardInterrupt
        browser.app = Mock()
        browser.app.run.side_effect = KeyboardInterrupt()
        
        # Execute run
        result = browser.run()
        
        # Verify exit code for keyboard interrupt
        assert result == 130
        
        # Verify auto save was called
        browser.auto_save_session_on_exit.assert_called()

    def test_run_unexpected_error(self):
        """Test browser run with unexpected error."""
        browser = self.create_mock_browser()
        browser.auto_restore_session = Mock(return_value=False)
        browser.navigate_to = Mock()
        
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

