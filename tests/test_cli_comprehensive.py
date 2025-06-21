#!/usr/bin/env python3
"""
Comprehensive tests for CLI module to improve coverage.
"""

import argparse
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from modern_gopher.cli import (
    setup_common_args,
    display_gopher_items,
    cmd_keybindings_list,
    cmd_keybindings_reset,
    cmd_session,
    cmd_config,
    cmd_browse,
    cmd_get,
    cmd_info,
    cmd_plugins,
    parse_args,
    main,
)
from modern_gopher.core.types import GopherItem, GopherItemType


class TestSetupCommonArgs:
    """Test the setup_common_args function."""

    def test_setup_common_args(self):
        """Test that common args are added correctly."""
        parser = argparse.ArgumentParser()
        setup_common_args(parser)
        
        # Parse with default values
        args = parser.parse_args([])
        assert args.timeout == 30
        assert args.ipv4 is False
        assert args.ipv6 is False
        assert args.ssl is False
        assert args.verbose is False

    def test_setup_common_args_with_values(self):
        """Test common args with specific values."""
        parser = argparse.ArgumentParser()
        setup_common_args(parser)
        
        # Parse with specific values
        args = parser.parse_args(['--timeout', '60', '--ipv4', '--ssl', '--verbose'])
        assert args.timeout == 60
        assert args.ipv4 is True
        assert args.ipv6 is False
        assert args.ssl is True
        assert args.verbose is True

    def test_setup_common_args_ipv6(self):
        """Test IPv6 flag."""
        parser = argparse.ArgumentParser()
        setup_common_args(parser)
        
        args = parser.parse_args(['--ipv6'])
        assert args.ipv4 is False
        assert args.ipv6 is True

    def test_setup_common_args_mutually_exclusive(self):
        """Test that IPv4 and IPv6 are mutually exclusive."""
        parser = argparse.ArgumentParser()
        setup_common_args(parser)
        
        with pytest.raises(SystemExit):
            parser.parse_args(['--ipv4', '--ipv6'])


class TestDisplayGopherItems:
    """Test the display_gopher_items function."""

    @patch('modern_gopher.cli.console')
    def test_display_empty_items(self, mock_console):
        """Test displaying empty item list."""
        display_gopher_items([])
        mock_console.print.assert_called()
        # Should print a panel with "No items found"

    @patch('modern_gopher.cli.console')
    def test_display_gopher_items(self, mock_console):
        """Test displaying gopher items."""
        items = [
            GopherItem(
                GopherItemType.TEXT_FILE,
                "Test File",
                "/test.txt",
                "example.com",
                70
            ),
            GopherItem(
                GopherItemType.DIRECTORY,
                "Test Directory", 
                "/dir",
                "example.com",
                70
            )
        ]
        
        display_gopher_items(items)
        mock_console.print.assert_called()
        # Should print a table with the items


class TestKeybindingsCommands:
    """Test keybinding command functions."""

    @patch('modern_gopher.cli.KeyBindingManager')
    @patch('modern_gopher.cli.console')
    def test_cmd_keybindings_list_success(self, mock_console, mock_kb_manager_class):
        """Test successful keybindings list command."""
        # Setup mock manager
        mock_manager = Mock()
        mock_manager.get_all_categories.return_value = ['navigation', 'global']
        
        # Mock binding object
        mock_binding = Mock()
        mock_binding.keys = ['h', 'f1']
        mock_binding.description = 'Show help'
        mock_binding.context.value = 'global'
        mock_binding.enabled = True
        
        mock_manager.get_bindings_by_category.return_value = {
            'help': mock_binding
        }
        mock_manager.get_default_config_path.return_value = Path('/test/path')
        
        mock_kb_manager_class.return_value = mock_manager
        
        args = argparse.Namespace()
        result = cmd_keybindings_list(args)
        
        assert result == 0
        mock_console.print.assert_called()

    @patch('modern_gopher.cli.KeyBindingManager')
    @patch('modern_gopher.cli.console')
    def test_cmd_keybindings_list_exception(self, mock_console, mock_kb_manager_class):
        """Test keybindings list command with exception."""
        mock_kb_manager_class.side_effect = Exception("Test error")
        
        args = argparse.Namespace()
        result = cmd_keybindings_list(args)
        
        assert result == 1
        mock_console.print.assert_called()

    @patch('modern_gopher.cli.KeyBindingManager')
    @patch('modern_gopher.cli.console')
    def test_cmd_keybindings_reset_success(self, mock_console, mock_kb_manager_class):
        """Test successful keybindings reset command."""
        mock_manager = Mock()
        mock_manager.backup_keybindings.return_value = Path('/backup/path')
        mock_manager.reset_to_defaults.return_value = None
        mock_manager.save_to_file.return_value = True
        mock_manager.config_file = Path('/config/path')
        mock_manager.bindings = {'action1': Mock(enabled=True), 'action2': Mock(enabled=False)}
        
        mock_kb_manager_class.return_value = mock_manager
        
        args = argparse.Namespace()
        result = cmd_keybindings_reset(args)
        
        assert result == 0
        mock_console.print.assert_called()

    @patch('modern_gopher.cli.KeyBindingManager')
    @patch('modern_gopher.cli.console')
    def test_cmd_keybindings_reset_save_failure(self, mock_console, mock_kb_manager_class):
        """Test keybindings reset with save failure."""
        mock_manager = Mock()
        mock_manager.backup_keybindings.return_value = None
        mock_manager.reset_to_defaults.return_value = None
        mock_manager.save_to_file.return_value = False
        
        mock_kb_manager_class.return_value = mock_manager
        
        args = argparse.Namespace()
        result = cmd_keybindings_reset(args)
        
        assert result == 1


class TestSessionCommands:
    """Test session command functions."""

    @patch('modern_gopher.cli.get_config')
    @patch('modern_gopher.cli.SessionManager')
    @patch('modern_gopher.cli.console')
    def test_cmd_session_list_success(self, mock_console, mock_session_manager_class, mock_get_config):
        """Test successful session list command."""
        # Setup mocks
        mock_config = Mock()
        mock_config.session_file = '/sessions.json'
        mock_get_config.return_value = mock_config
        
        mock_session = Mock()
        mock_session.session_id = 'test-session-id'
        mock_session.name = 'Test Session'
        mock_session.current_url = 'gopher://example.com'
        mock_session.created_datetime.strftime.return_value = '2023-01-01 12:00'
        mock_session.last_used_datetime.strftime.return_value = '2023-01-01 13:00'
        
        mock_manager = Mock()
        mock_manager.list_sessions.return_value = [mock_session]
        mock_session_manager_class.return_value = mock_manager
        
        args = argparse.Namespace()
        args.session_action = 'list'
        
        result = cmd_session(args)
        assert result == 0

    @patch('modern_gopher.cli.get_config')
    @patch('modern_gopher.cli.SessionManager')
    @patch('modern_gopher.cli.console')
    def test_cmd_session_list_empty(self, mock_console, mock_session_manager_class, mock_get_config):
        """Test session list with no sessions."""
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_manager = Mock()
        mock_manager.list_sessions.return_value = []
        mock_session_manager_class.return_value = mock_manager
        
        args = argparse.Namespace()
        args.session_action = 'list'
        
        result = cmd_session(args)
        assert result == 0

    @patch('modern_gopher.cli.get_config')
    @patch('modern_gopher.cli.SessionManager')
    @patch('modern_gopher.cli.console')
    def test_cmd_session_show_success(self, mock_console, mock_session_manager_class, mock_get_config):
        """Test successful session show command."""
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_manager = Mock()
        mock_manager.get_session_info.return_value = {
            'id': 'test-id',
            'name': 'Test Session',
            'description': 'Test Description',
            'current_url': 'gopher://example.com',
            'created_at': '2023-01-01',
            'last_used': '2023-01-01',
            'history_count': 5,
            'tags': ['test'],
            'is_searching': True,
            'search_query': 'test query'
        }
        mock_session_manager_class.return_value = mock_manager
        
        args = argparse.Namespace()
        args.session_action = 'show'
        args.session_id = 'test-id'
        
        result = cmd_session(args)
        assert result == 0

    @patch('modern_gopher.cli.get_config')
    @patch('modern_gopher.cli.SessionManager')
    @patch('modern_gopher.cli.console')
    def test_cmd_session_show_not_found(self, mock_console, mock_session_manager_class, mock_get_config):
        """Test session show with session not found."""
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_manager = Mock()
        mock_manager.get_session_info.return_value = None
        mock_session_manager_class.return_value = mock_manager
        
        args = argparse.Namespace()
        args.session_action = 'show'
        args.session_id = 'nonexistent'
        
        result = cmd_session(args)
        assert result == 1

    @patch('modern_gopher.cli.get_config')
    @patch('modern_gopher.cli.SessionManager')
    @patch('modern_gopher.cli.console')
    def test_cmd_session_delete_success(self, mock_console, mock_session_manager_class, mock_get_config):
        """Test successful session delete command."""
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_manager = Mock()
        mock_manager.delete_session.return_value = True
        mock_session_manager_class.return_value = mock_manager
        
        args = argparse.Namespace()
        args.session_action = 'delete'
        args.session_id = 'test-id'
        
        result = cmd_session(args)
        assert result == 0

    @patch('modern_gopher.cli.get_config')
    @patch('modern_gopher.cli.SessionManager')
    @patch('modern_gopher.cli.console')
    def test_cmd_session_load(self, mock_console, mock_session_manager_class, mock_get_config):
        """Test session load command."""
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        mock_manager = Mock()
        mock_session_manager_class.return_value = mock_manager
        
        args = argparse.Namespace()
        args.session_action = 'load'
        
        result = cmd_session(args)
        assert result == 0


class TestConfigCommands:
    """Test config command functions."""

    @patch('modern_gopher.cli.get_config')
    @patch('modern_gopher.cli.console')
    def test_cmd_config_show_success(self, mock_console, mock_get_config):
        """Test successful config show command."""
        mock_config = Mock()
        mock_config.to_dict.return_value = {
            'gopher': {'timeout': 30, 'port': 70},
            'cache': {'enabled': True}
        }
        mock_config.get_default_config_path.return_value = Path('/config/path')
        mock_get_config.return_value = mock_config
        
        args = argparse.Namespace()
        args.config_action = 'show'
        
        result = cmd_config(args)
        assert result == 0

    @patch('modern_gopher.cli.get_config')
    @patch('modern_gopher.cli.console')
    def test_cmd_config_get_success(self, mock_console, mock_get_config):
        """Test successful config get command."""
        mock_config = Mock()
        mock_config.get_value.return_value = 30
        mock_get_config.return_value = mock_config
        
        args = argparse.Namespace()
        args.config_action = 'get'
        args.key = 'gopher.timeout'
        
        result = cmd_config(args)
        assert result == 0

    @patch('modern_gopher.cli.get_config')
    @patch('modern_gopher.cli.console')
    def test_cmd_config_get_missing_key(self, mock_console, mock_get_config):
        """Test config get with missing key."""
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        args = argparse.Namespace()
        args.config_action = 'get'
        # Missing key attribute
        
        result = cmd_config(args)
        assert result == 1

    @patch('modern_gopher.cli.get_config')
    @patch('modern_gopher.cli.console')
    def test_cmd_config_path(self, mock_console, mock_get_config):
        """Test config path command."""
        mock_config = Mock()
        mock_config.get_default_config_path.return_value = Path('/config/path')
        mock_get_config.return_value = mock_config
        
        args = argparse.Namespace()
        args.config_action = 'path'
        
        result = cmd_config(args)
        assert result == 0


class TestBrowseCommand:
    """Test browse command function."""

    @patch('modern_gopher.cli.get_config')
    @patch('modern_gopher.cli.launch_browser')
    @patch('modern_gopher.cli.console')
    @patch('modern_gopher.cli.logger')
    def test_cmd_browse_success(self, mock_logger, mock_console, mock_launch_browser, mock_get_config):
        """Test successful browse command."""
        mock_config = Mock()
        mock_config.effective_initial_url = 'gopher://example.com'
        mock_config.use_ipv6 = None
        mock_config.timeout = 30
        mock_config.use_ssl = False
        mock_config.cache_enabled = True
        mock_config.cache_directory = '/cache'
        mock_get_config.return_value = mock_config
        
        mock_launch_browser.return_value = 0
        
        args = argparse.Namespace()
        args.url = 'gopher://test.com'
        args.verbose = False
        args.ipv4 = False
        args.ipv6 = False
        
        result = cmd_browse(args)
        assert result == 0
        mock_launch_browser.assert_called_once()

    @patch('modern_gopher.cli.get_config')
    @patch('modern_gopher.cli.launch_browser')
    @patch('modern_gopher.cli.console')
    def test_cmd_browse_exception(self, mock_console, mock_launch_browser, mock_get_config):
        """Test browse command with exception."""
        mock_get_config.side_effect = Exception("Test error")
        
        args = argparse.Namespace()
        args.verbose = False
        
        result = cmd_browse(args)
        assert result == 1


class TestGetCommand:
    """Test get command function."""

    @patch('modern_gopher.cli.GopherClient')
    @patch('modern_gopher.cli.parse_gopher_url')
    @patch('modern_gopher.cli.console')
    @patch('modern_gopher.cli.logger')
    def test_cmd_get_text_success(self, mock_logger, mock_console, mock_parse_url, mock_client_class):
        """Test successful get command for text content."""
        mock_url = Mock()
        mock_url.use_ssl = False
        mock_parse_url.return_value = mock_url
        
        mock_client = Mock()
        mock_client.get_resource.return_value = "Test content"
        mock_client_class.return_value = mock_client
        
        args = argparse.Namespace()
        args.url = 'gopher://example.com/0/test.txt'
        args.verbose = False
        args.ipv4 = False
        args.ipv6 = False
        args.timeout = 30
        args.ssl = False
        args.output = None
        args.markdown = False
        
        result = cmd_get(args)
        assert result == 0

    @patch('modern_gopher.cli.GopherClient')
    @patch('modern_gopher.cli.parse_gopher_url')
    @patch('modern_gopher.cli.console')
    @patch('modern_gopher.cli.display_gopher_items')
    def test_cmd_get_directory_success(self, mock_display, mock_console, mock_parse_url, mock_client_class):
        """Test successful get command for directory listing."""
        mock_url = Mock()
        mock_url.use_ssl = False
        mock_parse_url.return_value = mock_url
        
        mock_client = Mock()
        mock_client.get_resource.return_value = [
            GopherItem(GopherItemType.TEXT_FILE, "Test", "/test", "example.com", 70)
        ]
        mock_client_class.return_value = mock_client
        
        args = argparse.Namespace()
        args.url = 'gopher://example.com/1/'
        args.verbose = False
        args.ipv4 = False
        args.ipv6 = False
        args.timeout = 30
        args.ssl = False
        args.output = None
        args.markdown = False
        
        result = cmd_get(args)
        assert result == 0
        mock_display.assert_called_once()


class TestInfoCommand:
    """Test info command function."""

    @patch('modern_gopher.cli.parse_gopher_url')
    @patch('modern_gopher.cli.console')
    @patch('modern_gopher.cli.logger')
    def test_cmd_info_success(self, mock_logger, mock_console, mock_parse_url):
        """Test successful info command."""
        mock_url = Mock()
        mock_url.host = 'example.com'
        mock_url.port = 70
        mock_url.selector = '/test.txt'
        mock_url.item_type = GopherItemType.TEXT_FILE
        mock_url.use_ssl = False
        mock_url.query = 'test query'
        mock_parse_url.return_value = mock_url
        
        args = argparse.Namespace()
        args.url = 'gopher://example.com/0/test.txt'
        args.verbose = False
        
        result = cmd_info(args)
        assert result == 0

    @patch('modern_gopher.cli.parse_gopher_url')
    @patch('modern_gopher.cli.console')
    def test_cmd_info_exception(self, mock_console, mock_parse_url):
        """Test info command with exception."""
        mock_parse_url.side_effect = Exception("Test error")
        
        args = argparse.Namespace()
        args.url = 'invalid://url'
        args.verbose = False
        
        result = cmd_info(args)
        assert result == 1


class TestPluginsCommand:
    """Test plugins command function."""

    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.cli.console')
    def test_cmd_plugins_list_success(self, mock_console, mock_get_manager):
        """Test successful plugins list command."""
        mock_manager = Mock()
        mock_manager.get_plugin_info.return_value = {
            'test_plugin': {
                'name': 'Test Plugin',
                'version': '1.0.0',
                'type': 'content_processor',
                'enabled': True,
                'description': 'A test plugin'
            }
        }
        mock_get_manager.return_value = mock_manager
        
        args = argparse.Namespace()
        args.plugin_action = 'list'
        args.enabled_only = False
        
        result = cmd_plugins(args)
        assert result == 0

    @patch('modern_gopher.plugins.manager.get_manager')
    @patch('modern_gopher.cli.console')
    def test_cmd_plugins_list_empty(self, mock_console, mock_get_manager):
        """Test plugins list with no plugins."""
        mock_manager = Mock()
        mock_manager.get_plugin_info.return_value = {}
        mock_get_manager.return_value = mock_manager
        
        args = argparse.Namespace()
        args.plugin_action = 'list'
        args.enabled_only = False
        
        result = cmd_plugins(args)
        assert result == 0


class TestParseArgs:
    """Test argument parsing."""

    def test_parse_args_browse(self):
        """Test parsing browse command."""
        args = parse_args(['browse', 'gopher://example.com'])
        assert args.command == 'browse'
        assert args.url == 'gopher://example.com'

    def test_parse_args_get(self):
        """Test parsing get command."""
        args = parse_args(['get', 'gopher://example.com/test.txt'])
        assert args.command == 'get'
        assert args.url == 'gopher://example.com/test.txt'

    def test_parse_args_config_show(self):
        """Test parsing config show command."""
        args = parse_args(['config', 'show'])
        assert args.command == 'config'
        assert args.config_action == 'show'

    def test_parse_args_session_list(self):
        """Test parsing session list command."""
        args = parse_args(['session', 'list'])
        assert args.command == 'session'
        assert args.session_action == 'list'


class TestMainFunction:
    """Test main function."""

    @patch('modern_gopher.cli.parse_args')
    @patch('modern_gopher.cli.console')
    def test_main_success(self, mock_console, mock_parse_args):
        """Test successful main execution."""
        mock_args = Mock()
        mock_args.func.return_value = 0
        mock_parse_args.return_value = mock_args
        
        result = main()
        assert result == 0

    @patch('modern_gopher.cli.parse_args')
    @patch('modern_gopher.cli.console')
    def test_main_keyboard_interrupt(self, mock_console, mock_parse_args):
        """Test main with keyboard interrupt."""
        mock_parse_args.side_effect = KeyboardInterrupt()
        
        result = main()
        assert result == 130

    @patch('modern_gopher.cli.parse_args')
    @patch('modern_gopher.cli.console')
    def test_main_exception(self, mock_console, mock_parse_args):
        """Test main with general exception."""
        mock_parse_args.side_effect = Exception("Test error")
        
        result = main()
        assert result == 1


if __name__ == "__main__":
    pytest.main([__file__])

