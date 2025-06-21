#!/usr/bin/env python3
"""
Enhanced tests for CLI commands to improve coverage.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from modern_gopher.cli import (
    cmd_keybindings_list,
    cmd_keybindings_reset,
    cmd_session,
    cmd_config,
    setup_common_args,
)
from modern_gopher.core.protocol import GopherProtocolError


class TestKeybindingsCommands:
    """Test keybindings management commands."""

    @patch("modern_gopher.cli.KeyBindingManager")
    @patch("modern_gopher.cli.console")
    def test_cmd_keybindings_list_success(self, mock_console, mock_key_manager_class):
        """Test successful keybindings list command."""
        # Setup mock keybinding manager
        mock_manager = Mock()
        mock_manager.get_all_categories.return_value = ["navigation", "editing"]
        
        # Mock bindings
        mock_binding = Mock()
        mock_binding.keys = ["Ctrl+C", "q"]
        mock_binding.description = "Quit application"
        mock_binding.context.value = "global"
        mock_binding.enabled = True
        
        mock_manager.get_bindings_by_category.return_value = {
            "quit": mock_binding
        }
        
        # Mock config path
        mock_config_path = Mock()
        mock_config_path.exists.return_value = True
        mock_manager.get_default_config_path.return_value = mock_config_path
        
        mock_key_manager_class.return_value = mock_manager
        
        # Create arguments
        args = Mock()
        args.verbose = False
        
        # Call command
        result = cmd_keybindings_list(args)
        
        assert result == 0
        mock_manager.get_all_categories.assert_called_once()
        mock_console.print.assert_called()

    @patch("modern_gopher.cli.KeyBindingManager")
    @patch("modern_gopher.cli.console")
    def test_cmd_keybindings_list_exception(self, mock_console, mock_key_manager_class):
        """Test keybindings list command with exception."""
        # Setup mock to raise exception
        mock_key_manager_class.side_effect = Exception("Keybinding error")
        
        # Create arguments
        args = Mock()
        args.verbose = False
        
        # Call command
        result = cmd_keybindings_list(args)
        
        assert result == 1
        mock_console.print.assert_called()

    @patch("modern_gopher.cli.KeyBindingManager")
    @patch("modern_gopher.cli.console")
    def test_cmd_keybindings_list_exception_verbose(self, mock_console, mock_key_manager_class):
        """Test keybindings list command with exception in verbose mode."""
        # Setup mock to raise exception
        mock_key_manager_class.side_effect = Exception("Keybinding error")
        
        # Create arguments
        args = Mock()
        args.verbose = True
        
        # Call command
        result = cmd_keybindings_list(args)
        
        assert result == 1
        mock_console.print.assert_called()
        mock_console.print_exception.assert_called_once()

    @patch("modern_gopher.cli.KeyBindingManager")
    @patch("modern_gopher.cli.console")
    def test_cmd_keybindings_reset_success(self, mock_console, mock_key_manager_class):
        """Test successful keybindings reset command."""
        # Setup mock keybinding manager
        mock_manager = Mock()
        mock_manager.backup_keybindings.return_value = "/tmp/backup.json"
        mock_manager.save_to_file.return_value = True
        mock_manager.config_file = "/home/user/.config/modern-gopher/keybindings.json"
        mock_manager.bindings = {"key1": Mock(enabled=True), "key2": Mock(enabled=False)}
        
        mock_key_manager_class.return_value = mock_manager
        
        # Create arguments
        args = Mock()
        args.verbose = False
        
        # Call command
        result = cmd_keybindings_reset(args)
        
        assert result == 0
        mock_manager.backup_keybindings.assert_called_once()
        mock_manager.reset_to_defaults.assert_called_once()
        mock_manager.save_to_file.assert_called_once()
        mock_console.print.assert_called()

    @patch("modern_gopher.cli.KeyBindingManager")
    @patch("modern_gopher.cli.console")
    def test_cmd_keybindings_reset_save_failure(self, mock_console, mock_key_manager_class):
        """Test keybindings reset command with save failure."""
        # Setup mock keybinding manager
        mock_manager = Mock()
        mock_manager.backup_keybindings.return_value = None
        mock_manager.save_to_file.return_value = False
        
        mock_key_manager_class.return_value = mock_manager
        
        # Create arguments
        args = Mock()
        args.verbose = False
        
        # Call command
        result = cmd_keybindings_reset(args)
        
        assert result == 1
        mock_console.print.assert_called()


class TestSessionCommands:
    """Test session management commands."""

    @patch("modern_gopher.cli.SessionManager")
    @patch("modern_gopher.cli.get_config")
    @patch("modern_gopher.cli.console")
    def test_cmd_session_list_success(self, mock_console, mock_get_config, mock_session_manager_class):
        """Test successful session list command."""
        # Setup mock config
        mock_config = Mock()
        mock_config.session_file = "/tmp/sessions.json"
        mock_get_config.return_value = mock_config
        
        # Setup mock session manager
        mock_session_manager = Mock()
        mock_session = Mock()
        mock_session.session_id = "abc123def456"
        mock_session.name = "Test Session"
        mock_session.current_url = "gopher://example.com"
        mock_session.created_datetime.strftime.return_value = "2024-01-01 12:00"
        mock_session.last_used_datetime.strftime.return_value = "2024-01-02 13:00"
        
        mock_session_manager.list_sessions.return_value = [mock_session]
        mock_session_manager_class.return_value = mock_session_manager
        
        # Create arguments
        args = Mock()
        args.session_action = "list"
        args.config_file = None
        
        # Call command
        result = cmd_session(args)
        
        assert result == 0
        mock_session_manager.list_sessions.assert_called_once()
        mock_console.print.assert_called()

    @patch("modern_gopher.cli.SessionManager")
    @patch("modern_gopher.cli.get_config")
    @patch("modern_gopher.cli.console")
    def test_cmd_session_list_empty(self, mock_console, mock_get_config, mock_session_manager_class):
        """Test session list command with no sessions."""
        # Setup mock config
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        # Setup mock session manager
        mock_session_manager = Mock()
        mock_session_manager.list_sessions.return_value = []
        mock_session_manager_class.return_value = mock_session_manager
        
        # Create arguments
        args = Mock()
        args.session_action = "list"
        
        # Call command
        result = cmd_session(args)
        
        assert result == 0
        mock_console.print.assert_called_with("No saved sessions found", style="yellow")

    @patch("modern_gopher.cli.SessionManager")
    @patch("modern_gopher.cli.get_config")
    @patch("modern_gopher.cli.console")
    def test_cmd_session_show_success(self, mock_console, mock_get_config, mock_session_manager_class):
        """Test successful session show command."""
        # Setup mock config
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        # Setup mock session manager
        mock_session_manager = Mock()
        mock_session_info = {
            'id': 'abc123',
            'name': 'Test Session',
            'description': 'Test description',
            'current_url': 'gopher://example.com',
            'created_at': '2024-01-01',
            'last_used': '2024-01-02',
            'history_count': 5,
            'tags': ['test', 'demo'],
            'is_searching': True,
            'search_query': 'test query'
        }
        mock_session_manager.get_session_info.return_value = mock_session_info
        mock_session_manager_class.return_value = mock_session_manager
        
        # Create arguments
        args = Mock()
        args.session_action = "show"
        args.session_id = "abc123"
        
        # Call command
        result = cmd_session(args)
        
        assert result == 0
        mock_session_manager.get_session_info.assert_called_once_with("abc123")
        mock_console.print.assert_called()

    @patch("modern_gopher.cli.SessionManager")
    @patch("modern_gopher.cli.get_config")
    @patch("modern_gopher.cli.console")
    def test_cmd_session_show_not_found(self, mock_console, mock_get_config, mock_session_manager_class):
        """Test session show command with session not found."""
        # Setup mock config
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        # Setup mock session manager
        mock_session_manager = Mock()
        mock_session_manager.get_session_info.return_value = None
        mock_session_manager_class.return_value = mock_session_manager
        
        # Create arguments
        args = Mock()
        args.session_action = "show"
        args.session_id = "nonexistent"
        
        # Call command
        result = cmd_session(args)
        
        assert result == 1
        mock_console.print.assert_called()

    @patch("modern_gopher.cli.SessionManager")
    @patch("modern_gopher.cli.get_config")
    @patch("modern_gopher.cli.console")
    def test_cmd_session_delete_success(self, mock_console, mock_get_config, mock_session_manager_class):
        """Test successful session delete command."""
        # Setup mock config
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        # Setup mock session manager
        mock_session_manager = Mock()
        mock_session_manager.delete_session.return_value = True
        mock_session_manager_class.return_value = mock_session_manager
        
        # Create arguments
        args = Mock()
        args.session_action = "delete"
        args.session_id = "abc123"
        
        # Call command
        result = cmd_session(args)
        
        assert result == 0
        mock_session_manager.delete_session.assert_called_once_with("abc123")
        mock_console.print.assert_called()

    @patch("modern_gopher.cli.SessionManager")
    @patch("modern_gopher.cli.get_config")
    @patch("modern_gopher.cli.console")
    def test_cmd_session_load(self, mock_console, mock_get_config, mock_session_manager_class):
        """Test session load command."""
        # Setup mock config
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        # Setup mock session manager
        mock_session_manager = Mock()
        mock_session_manager_class.return_value = mock_session_manager
        
        # Create arguments
        args = Mock()
        args.session_action = "load"
        
        # Call command
        result = cmd_session(args)
        
        assert result == 0
        mock_console.print.assert_called_with(
            "Use 'modern-gopher browse' with session loading to load a session", 
            style="yellow"
        )


class TestConfigCommands:
    """Test configuration management commands."""

    @patch("modern_gopher.cli.get_config")
    @patch("modern_gopher.cli.console")
    def test_cmd_config_show_success(self, mock_console, mock_get_config):
        """Test successful config show command."""
        # Setup mock config
        mock_config = Mock()
        mock_config.to_dict.return_value = {
            "network": {
                "timeout": 30,
                "use_ssl": False
            },
            "interface": {
                "theme": "default"
            }
        }
        mock_config.get_default_config_path.return_value = "/home/user/.config/modern-gopher/config.toml"
        mock_get_config.return_value = mock_config
        
        # Create arguments
        args = Mock()
        args.config_action = "show"
        args.config_file = None
        
        # Call command
        result = cmd_config(args)
        
        assert result == 0
        mock_config.to_dict.assert_called_once()
        mock_console.print.assert_called()

    @patch("modern_gopher.cli.get_config")
    @patch("modern_gopher.cli.console")
    def test_cmd_config_get_success(self, mock_console, mock_get_config):
        """Test successful config get command."""
        # Setup mock config
        mock_config = Mock()
        mock_config.get_value.return_value = "test_value"
        mock_get_config.return_value = mock_config
        
        # Create arguments
        args = Mock()
        args.config_action = "get"
        args.key = "network.timeout"
        
        # Call command
        result = cmd_config(args)
        
        assert result == 0
        mock_config.get_value.assert_called_once_with("network.timeout")
        mock_console.print.assert_called()

    @patch("modern_gopher.cli.get_config")
    @patch("modern_gopher.cli.console")
    def test_cmd_config_get_missing_key(self, mock_console, mock_get_config):
        """Test config get command with missing key."""
        # Setup mock config
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        # Create arguments without key
        args = Mock()
        args.config_action = "get"
        args.key = None
        
        # Call command
        result = cmd_config(args)
        
        assert result == 1
        mock_console.print.assert_called_with("Error: key required for get command", style="red")

    @patch("modern_gopher.cli.get_config")
    @patch("modern_gopher.cli.console")
    def test_cmd_config_path(self, mock_console, mock_get_config):
        """Test config path command."""
        # Setup mock config
        mock_config = Mock()
        mock_config_path = Mock()
        mock_config_path.exists.return_value = True
        mock_config.get_default_config_path.return_value = mock_config_path
        mock_get_config.return_value = mock_config
        
        # Create arguments
        args = Mock()
        args.config_action = "path"
        
        # Call command
        result = cmd_config(args)
        
        assert result == 0
        mock_console.print.assert_called()


class TestUtilityFunctions:
    """Test utility functions."""

    def test_setup_common_args(self):
        """Test setup_common_args function."""
        import argparse
        
        parser = argparse.ArgumentParser()
        setup_common_args(parser)
        
        # Test that arguments are added
        args = parser.parse_args(['--timeout', '60', '--ipv4', '--ssl', '--verbose'])
        
        assert args.timeout == 60
        assert args.ipv4 is True
        assert args.ipv6 is False
        assert args.ssl is True
        assert args.verbose is True

    def test_setup_common_args_defaults(self):
        """Test setup_common_args function with defaults."""
        import argparse
        
        parser = argparse.ArgumentParser()
        setup_common_args(parser)
        
        # Test default values
        args = parser.parse_args([])
        
        assert args.timeout == 30
        assert args.ipv4 is False
        assert args.ipv6 is False
        assert args.ssl is False
        assert args.verbose is False


if __name__ == "__main__":
    pytest.main([__file__])

