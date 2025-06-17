#!/usr/bin/env python3
"""
Tests for the CLI interface.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

from modern_gopher.cli import (
    parse_args, cmd_get, cmd_info, cmd_browse, main,
    setup_common_args, display_gopher_items
)
from modern_gopher.core.types import GopherItem, GopherItemType
from modern_gopher.core.protocol import GopherProtocolError


class TestArgumentParsing:
    """Test command line argument parsing."""
    
    def test_parse_args_get_command(self):
        """Test parsing get command arguments."""
        args = parse_args(['get', 'gopher://example.com/test.txt'])
        
        assert args.command == 'get'
        assert args.url == 'gopher://example.com/test.txt'
        assert args.timeout == 30
        assert not args.ipv4
        assert not args.ipv6
        assert not args.ssl
        assert not args.verbose
        assert args.output is None
        assert not args.markdown
    
    def test_parse_args_get_command_with_options(self):
        """Test parsing get command with all options."""
        args = parse_args([
            'get', 'gopher://example.com/test.txt',
            '--output', '/tmp/test.txt',
            '--markdown',
            '--timeout', '60',
            '--ipv4',
            '--ssl',
            '--verbose'
        ])
        
        assert args.command == 'get'
        assert args.url == 'gopher://example.com/test.txt'
        assert args.output == '/tmp/test.txt'
        assert args.markdown
        assert args.timeout == 60
        assert args.ipv4
        assert not args.ipv6
        assert args.ssl
        assert args.verbose
    
    def test_parse_args_browse_command(self):
        """Test parsing browse command arguments."""
        args = parse_args(['browse', 'gopher://example.com'])
        
        assert args.command == 'browse'
        assert args.url == 'gopher://example.com'
        assert args.timeout == 30
        assert not args.ipv4
        assert not args.ipv6
        assert not args.ssl
        assert not args.verbose
    
    def test_parse_args_info_command(self):
        """Test parsing info command arguments."""
        args = parse_args(['info', 'gopher://example.com/test.txt'])
        
        assert args.command == 'info'
        assert args.url == 'gopher://example.com/test.txt'
        assert not args.verbose
    
    def test_parse_args_ipv6_option(self):
        """Test IPv6 option parsing."""
        args = parse_args(['get', 'gopher://example.com', '--ipv6'])
        
        assert not args.ipv4
        assert args.ipv6
    
    def test_parse_args_mutually_exclusive_ip_options(self):
        """Test that IPv4 and IPv6 options are mutually exclusive."""
        with pytest.raises(SystemExit):
            parse_args(['get', 'gopher://example.com', '--ipv4', '--ipv6'])
    
    def test_parse_args_version(self):
        """Test version option."""
        with pytest.raises(SystemExit):
            parse_args(['--version'])
    
    def test_parse_args_help(self):
        """Test help option."""
        with pytest.raises(SystemExit):
            parse_args(['--help'])
    
    def test_parse_args_no_command(self):
        """Test that command is required."""
        with pytest.raises(SystemExit):
            parse_args([])


class TestDisplayFunction:
    """Test the display_gopher_items function."""
    
    @patch('modern_gopher.cli.console')
    def test_display_gopher_items_empty(self, mock_console):
        """Test displaying empty item list."""
        display_gopher_items([])
        
        # Should print a panel indicating no items
        mock_console.print.assert_called_once()
        call_args = mock_console.print.call_args[0][0]
        # Check that the panel's content contains "No items found"
        assert hasattr(call_args, 'renderable') or "No items found" in str(call_args) or "Empty Directory" in str(call_args)
    
    @patch('modern_gopher.cli.console')
    def test_display_gopher_items_with_items(self, mock_console):
        """Test displaying item list with items."""
        items = [
            GopherItem(GopherItemType.TEXT_FILE, "Test File", "/test.txt", "example.com", 70),
            GopherItem(GopherItemType.DIRECTORY, "Test Dir", "/test", "example.com", 70)
        ]
        
        display_gopher_items(items)
        
        # Should print a table
        mock_console.print.assert_called_once()
        call_args = mock_console.print.call_args[0][0]
        # The table should contain the item information
        assert hasattr(call_args, 'title')


class TestGetCommand:
    """Test the get command functionality."""
    
    @patch('modern_gopher.cli.GopherClient')
    @patch('modern_gopher.cli.parse_gopher_url')
    @patch('modern_gopher.cli.console')
    def test_cmd_get_text_display(self, mock_console, mock_parse_url, mock_client_class):
        """Test get command displaying text content."""
        # Setup mocks
        mock_url = Mock()
        mock_url.use_ssl = False
        mock_parse_url.return_value = mock_url
        
        mock_client = Mock()
        mock_client.get_resource.return_value = "Hello, World!"
        mock_client_class.return_value = mock_client
        
        # Create arguments
        args = Mock()
        args.url = "gopher://example.com/test.txt"
        args.output = None
        args.markdown = False
        args.ssl = False
        args.verbose = False
        args.timeout = 30
        args.ipv4 = False
        args.ipv6 = False
        
        # Call command
        result = cmd_get(args)
        
        assert result == 0
        mock_client.get_resource.assert_called_once_with(mock_url)
        mock_console.print.assert_called()
    
    @patch('modern_gopher.cli.GopherClient')
    @patch('modern_gopher.cli.parse_gopher_url')
    @patch('modern_gopher.cli.console')
    def test_cmd_get_directory_display(self, mock_console, mock_parse_url, mock_client_class):
        """Test get command displaying directory content."""
        # Setup mocks
        mock_url = Mock()
        mock_url.use_ssl = False
        mock_parse_url.return_value = mock_url
        
        mock_items = [
            GopherItem(GopherItemType.TEXT_FILE, "Test", "/test", "example.com", 70)
        ]
        mock_client = Mock()
        mock_client.get_resource.return_value = mock_items
        mock_client_class.return_value = mock_client
        
        # Create arguments
        args = Mock()
        args.url = "gopher://example.com/"
        args.output = None
        args.markdown = False
        args.ssl = False
        args.verbose = False
        args.timeout = 30
        args.ipv4 = False
        args.ipv6 = False
        
        # Call command
        result = cmd_get(args)
        
        assert result == 0
        mock_client.get_resource.assert_called_once_with(mock_url)
    
    @patch('modern_gopher.cli.GopherClient')
    @patch('modern_gopher.cli.parse_gopher_url')
    @patch('modern_gopher.cli.console')
    def test_cmd_get_save_to_file(self, mock_console, mock_parse_url, mock_client_class):
        """Test get command saving to file."""
        # Setup mocks
        mock_url = Mock()
        mock_url.use_ssl = False
        mock_parse_url.return_value = mock_url
        
        mock_client = Mock()
        mock_client.get_resource.return_value = 1024  # bytes written
        mock_client_class.return_value = mock_client
        
        with tempfile.NamedTemporaryFile() as temp_file:
            # Create arguments
            args = Mock()
            args.url = "gopher://example.com/test.bin"
            args.output = temp_file.name
            args.ssl = False
            args.verbose = False
            args.timeout = 30
            args.ipv4 = False
            args.ipv6 = False
            
            # Call command
            result = cmd_get(args)
            
            assert result == 0
            mock_client.get_resource.assert_called_once_with(mock_url, file_path=temp_file.name)
            mock_console.print.assert_called()
    
    @patch('modern_gopher.cli.GopherClient')
    @patch('modern_gopher.cli.parse_gopher_url')
    @patch('modern_gopher.cli.console')
    def test_cmd_get_binary_display(self, mock_console, mock_parse_url, mock_client_class):
        """Test get command displaying binary content."""
        # Setup mocks
        mock_url = Mock()
        mock_url.use_ssl = False
        mock_parse_url.return_value = mock_url
        
        mock_client = Mock()
        mock_client.get_resource.return_value = b"\x00\x01\x02"
        mock_client_class.return_value = mock_client
        
        # Create arguments
        args = Mock()
        args.url = "gopher://example.com/test.bin"
        args.output = None
        args.ssl = False
        args.verbose = False
        args.timeout = 30
        args.ipv4 = False
        args.ipv6 = False
        
        # Call command
        result = cmd_get(args)
        
        assert result == 0
        mock_console.print.assert_called()
    
    @patch('modern_gopher.cli.GopherClient')
    @patch('modern_gopher.cli.parse_gopher_url')
    @patch('modern_gopher.cli.console')
    def test_cmd_get_markdown_rendering(self, mock_console, mock_parse_url, mock_client_class):
        """Test get command with markdown rendering."""
        # Setup mocks
        mock_url = Mock()
        mock_url.use_ssl = False
        mock_parse_url.return_value = mock_url
        
        mock_client = Mock()
        mock_client.get_resource.return_value = "# Hello\n\nThis is **markdown**."
        mock_client_class.return_value = mock_client
        
        # Create arguments
        args = Mock()
        args.url = "gopher://example.com/test.md"
        args.output = None
        args.markdown = True
        args.ssl = False
        args.verbose = False
        args.timeout = 30
        args.ipv4 = False
        args.ipv6 = False
        
        # Call command
        result = cmd_get(args)
        
        assert result == 0
        mock_console.print.assert_called()
    
    @patch('modern_gopher.cli.GopherClient')
    @patch('modern_gopher.cli.parse_gopher_url')
    @patch('modern_gopher.cli.console')
    def test_cmd_get_protocol_error(self, mock_console, mock_parse_url, mock_client_class):
        """Test get command handling protocol errors."""
        # Setup mocks
        mock_url = Mock()
        mock_parse_url.return_value = mock_url
        
        mock_client = Mock()
        mock_client.get_resource.side_effect = GopherProtocolError("Connection failed")
        mock_client_class.return_value = mock_client
        
        # Create arguments
        args = Mock()
        args.url = "gopher://example.com/test.txt"
        args.output = None
        args.ssl = False
        args.verbose = False
        args.timeout = 30
        args.ipv4 = False
        args.ipv6 = False
        
        # Call command
        result = cmd_get(args)
        
        assert result == 1
        mock_console.print.assert_called()


class TestInfoCommand:
    """Test the info command functionality."""
    
    @patch('modern_gopher.cli.parse_gopher_url')
    @patch('modern_gopher.cli.console')
    def test_cmd_info_basic(self, mock_console, mock_parse_url):
        """Test info command basic functionality."""
        # Setup mocks
        mock_url = Mock()
        mock_url.host = "example.com"
        mock_url.port = 70
        mock_url.selector = "/test.txt"
        mock_url.item_type = GopherItemType.TEXT_FILE
        mock_url.use_ssl = False
        mock_url.query = None
        mock_parse_url.return_value = mock_url
        
        # Create arguments
        args = Mock()
        args.url = "gopher://example.com/0/test.txt"
        args.verbose = False
        
        # Call command
        result = cmd_info(args)
        
        assert result == 0
        mock_parse_url.assert_called_once_with("gopher://example.com/0/test.txt")
        mock_console.print.assert_called()
    
    @patch('modern_gopher.cli.parse_gopher_url')
    @patch('modern_gopher.cli.console')
    def test_cmd_info_with_ssl_and_query(self, mock_console, mock_parse_url):
        """Test info command with SSL and query."""
        # Setup mocks
        mock_url = Mock()
        mock_url.host = "secure.example.com"
        mock_url.port = 70
        mock_url.selector = "/search"
        mock_url.item_type = GopherItemType.SEARCH_SERVER
        mock_url.use_ssl = True
        mock_url.query = "test query"
        mock_parse_url.return_value = mock_url
        
        # Create arguments
        args = Mock()
        args.url = "gophers://secure.example.com/7/search?test query"
        args.verbose = False
        
        # Call command
        result = cmd_info(args)
        
        assert result == 0
        mock_console.print.assert_called()
    
    @patch('modern_gopher.cli.parse_gopher_url')
    @patch('modern_gopher.cli.console')
    def test_cmd_info_error(self, mock_console, mock_parse_url):
        """Test info command error handling."""
        # Setup mocks
        mock_parse_url.side_effect = ValueError("Invalid URL")
        
        # Create arguments
        args = Mock()
        args.url = "invalid-url"
        args.verbose = False
        
        # Call command
        result = cmd_info(args)
        
        assert result == 1
        mock_console.print.assert_called()


class TestBrowseCommand:
    """Test the browse command functionality."""
    
    @patch('modern_gopher.cli.launch_browser')
    @patch('modern_gopher.cli.console')
    @patch('modern_gopher.cli.get_config')
    def test_cmd_browse_basic(self, mock_get_config, mock_console, mock_launch_browser):
        """Test browse command basic functionality."""
        # Mock config
        mock_config = Mock()
        mock_config.effective_initial_url = "gopher://gopher.floodgap.com"
        mock_config.timeout = 30
        mock_config.use_ssl = False
        mock_config.use_ipv6 = None
        mock_config.cache_enabled = True
        mock_config.cache_directory = "/tmp/test_cache"
        mock_get_config.return_value = mock_config
        
        mock_launch_browser.return_value = 0
        
        # Create arguments
        args = Mock()
        args.url = "gopher://example.com"
        args.timeout = 30
        args.ssl = False
        args.ipv4 = False
        args.ipv6 = False
        args.verbose = False
        
        # Call command
        result = cmd_browse(args)
        
        assert result == 0
        mock_launch_browser.assert_called_once()
        mock_console.print.assert_called()  # Startup message
    
    @patch('modern_gopher.cli.launch_browser')
    @patch('modern_gopher.cli.console')
    @patch('modern_gopher.cli.get_config')
    def test_cmd_browse_with_options(self, mock_get_config, mock_console, mock_launch_browser):
        """Test browse command with all options."""
        # Mock config
        mock_config = Mock()
        mock_config.effective_initial_url = "gopher://gopher.floodgap.com"
        mock_config.timeout = 30
        mock_config.use_ssl = False
        mock_config.use_ipv6 = None
        mock_config.cache_enabled = True
        mock_config.cache_directory = "/tmp/test_cache"
        mock_get_config.return_value = mock_config
        
        mock_launch_browser.return_value = 0
        
        # Create arguments
        args = Mock()
        args.url = "gophers://secure.example.com"
        args.timeout = 60
        args.ssl = True
        args.ipv4 = False
        args.ipv6 = True
        args.verbose = True
        
        # Call command
        result = cmd_browse(args)
        
        assert result == 0
        
        # Check launch_browser was called with correct arguments
        call_args = mock_launch_browser.call_args
        assert call_args[1]['url'] == "gophers://secure.example.com"
        assert call_args[1]['timeout'] == 60
        assert call_args[1]['use_ssl'] is True
        assert call_args[1]['use_ipv6'] is True
    
    @patch('modern_gopher.cli.launch_browser')
    @patch('modern_gopher.cli.console')
    @patch('os.makedirs')
    def test_cmd_browse_error(self, mock_makedirs, mock_console, mock_launch_browser):
        """Test browse command error handling."""
        mock_launch_browser.side_effect = Exception("Browser failed")
        
        # Create arguments
        args = Mock()
        args.url = "gopher://example.com"
        args.timeout = 30
        args.ssl = False
        args.ipv4 = False
        args.ipv6 = False
        args.verbose = False
        
        # Call command
        result = cmd_browse(args)
        
        assert result == 1
        mock_console.print.assert_called()


class TestMainFunction:
    """Test the main function."""
    
    @patch('modern_gopher.cli.parse_args')
    def test_main_success(self, mock_parse_args):
        """Test main function success case."""
        # Setup mocks
        mock_args = Mock()
        mock_args.func.return_value = 0
        mock_parse_args.return_value = mock_args
        
        # Call main
        result = main()
        
        assert result == 0
        mock_args.func.assert_called_once_with(mock_args)
    
    @patch('modern_gopher.cli.parse_args')
    @patch('modern_gopher.cli.console')
    def test_main_keyboard_interrupt(self, mock_console, mock_parse_args):
        """Test main function handling keyboard interrupt."""
        # Setup mocks
        mock_args = Mock()
        mock_args.func.side_effect = KeyboardInterrupt()
        mock_parse_args.return_value = mock_args
        
        # Call main
        result = main()
        
        assert result == 130
        mock_console.print.assert_called()
    
    @patch('modern_gopher.cli.parse_args')
    @patch('modern_gopher.cli.console')
    def test_main_unexpected_error(self, mock_console, mock_parse_args):
        """Test main function handling unexpected errors."""
        # Setup mocks
        mock_args = Mock()
        mock_args.func.side_effect = RuntimeError("Unexpected error")
        mock_parse_args.return_value = mock_args
        
        # Call main
        result = main()
        
        assert result == 1
        mock_console.print.assert_called()
        mock_console.print_exception.assert_called()


if __name__ == "__main__":
    pytest.main([__file__])

