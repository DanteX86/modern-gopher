#!/usr/bin/env python3
"""
Comprehensive tests for config module.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import yaml

from modern_gopher.config import (
    DEFAULT_CONFIG,
    ModernGopherConfig,
    get_config,
)


class TestModernGopherConfigCreation(unittest.TestCase):
    """Test ModernGopherConfig creation and basic functionality."""

    def test_default_initialization(self):
        """Test default config initialization."""
        config = ModernGopherConfig()
        
        # Check default values
        self.assertEqual(config.default_server, "gopher://gopher.floodgap.com")
        self.assertEqual(config.default_port, 70)
        self.assertEqual(config.timeout, 30)
        self.assertFalse(config.use_ssl)
        self.assertIsNone(config.use_ipv6)
        
        # Check cache defaults
        self.assertTrue(config.cache_enabled)
        self.assertEqual(config.cache_max_size_mb, 100)
        self.assertEqual(config.cache_expiration_hours, 24)
        
        # Check browser defaults
        self.assertIsNone(config.initial_url)
        self.assertEqual(config.max_history_items, 1000)
        self.assertTrue(config.save_session)
        
        # Check session defaults
        self.assertTrue(config.session_enabled)
        self.assertTrue(config.session_auto_restore)
        self.assertTrue(config.session_backup_sessions)
        self.assertEqual(config.session_max_sessions, 10)
        
        # Check UI defaults
        self.assertTrue(config.show_icons)
        self.assertTrue(config.status_bar_help)
        self.assertTrue(config.mouse_support)
        self.assertEqual(config.color_scheme, "default")
        
        # Check logging defaults
        self.assertEqual(config.log_level, "INFO")
        self.assertIsNone(config.log_file)
        self.assertTrue(config.log_console)

    def test_custom_initialization(self):
        """Test config initialization with custom values."""
        config = ModernGopherConfig(
            default_server="gopher://example.com",
            default_port=7070,
            timeout=60,
            use_ssl=True,
            cache_enabled=False,
            log_level="DEBUG"
        )
        
        self.assertEqual(config.default_server, "gopher://example.com")
        self.assertEqual(config.default_port, 7070)
        self.assertEqual(config.timeout, 60)
        self.assertTrue(config.use_ssl)
        self.assertFalse(config.cache_enabled)
        self.assertEqual(config.log_level, "DEBUG")

    def test_post_init_path_expansion(self):
        """Test that paths are expanded during initialization."""
        config = ModernGopherConfig(
            cache_directory="~/test_cache",
            bookmarks_file="~/test_bookmarks.json",
            history_file="~/test_history.json",
            session_file="~/test_session.json",
            log_file="~/test.log"
        )
        
        # Paths should be expanded
        self.assertTrue(config.cache_directory.startswith("/"))
        self.assertTrue(config.bookmarks_file.startswith("/"))
        self.assertTrue(config.history_file.startswith("/"))
        self.assertTrue(config.session_file.startswith("/"))
        self.assertTrue(config.log_file.startswith("/"))
        
        # Should contain expanded home directory
        home = os.path.expanduser("~")
        self.assertIn(home, config.cache_directory)
        self.assertIn(home, config.bookmarks_file)

    def test_post_init_no_log_file(self):
        """Test post_init when log_file is None."""
        config = ModernGopherConfig(log_file=None)
        self.assertIsNone(config.log_file)

    def test_effective_initial_url_with_value(self):
        """Test effective_initial_url when initial_url is set."""
        config = ModernGopherConfig(initial_url="gopher://test.com")
        self.assertEqual(config.effective_initial_url, "gopher://test.com")

    def test_effective_initial_url_fallback(self):
        """Test effective_initial_url falls back to default_server."""
        config = ModernGopherConfig(
            initial_url=None,
            default_server="gopher://fallback.com"
        )
        self.assertEqual(config.effective_initial_url, "gopher://fallback.com")

    def test_config_dir_property(self):
        """Test config_dir property."""
        config = ModernGopherConfig(bookmarks_file="/test/config/bookmarks.json")
        self.assertEqual(config.config_dir, Path("/test/config"))

    def test_ensure_directories_success(self):
        """Test ensure_directories creates directories successfully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = os.path.join(temp_dir, "cache")
            config_dir = os.path.join(temp_dir, "config")
            
            config = ModernGopherConfig(
                cache_directory=cache_dir,
                bookmarks_file=os.path.join(config_dir, "bookmarks.json")
            )
            
            config.ensure_directories()
            
            self.assertTrue(os.path.exists(cache_dir))
            self.assertTrue(os.path.exists(config_dir))

    @patch('modern_gopher.config.logger')
    def test_ensure_directories_error(self, mock_logger):
        """Test ensure_directories handles errors."""
        # Use an invalid path that will cause OSError
        config = ModernGopherConfig(
            cache_directory="/root/cannot_create",
            bookmarks_file="/root/cannot_create/bookmarks.json"
        )
        
        # Should not raise exception
        config.ensure_directories()
        
        # Should log warnings
        mock_logger.warning.assert_called()


class TestModernGopherConfigSerialization(unittest.TestCase):
    """Test config serialization and deserialization."""

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = ModernGopherConfig(
            default_server="gopher://test.com",
            cache_enabled=False,
            log_level="DEBUG"
        )
        
        result = config.to_dict()
        
        # Check structure
        self.assertIn("gopher", result)
        self.assertIn("cache", result)
        self.assertIn("browser", result)
        self.assertIn("session", result)
        self.assertIn("ui", result)
        self.assertIn("logging", result)
        
        # Check values
        self.assertEqual(result["gopher"]["default_server"], "gopher://test.com")
        self.assertFalse(result["cache"]["enabled"])
        self.assertEqual(result["logging"]["level"], "DEBUG")

    def test_from_dict_complete(self):
        """Test creating config from complete dictionary."""
        config_dict = {
            "gopher": {
                "default_server": "gopher://example.com",
                "default_port": 7070,
                "timeout": 60,
                "use_ssl": True,
                "use_ipv6": True,
            },
            "cache": {
                "enabled": False,
                "directory": "/tmp/cache",
                "max_size_mb": 200,
                "expiration_hours": 48,
            },
            "browser": {
                "initial_url": "gopher://start.com",
                "bookmarks_file": "/tmp/bookmarks.json",
                "history_file": "/tmp/history.json",
                "max_history_items": 500,
                "save_session": False,
            },
            "session": {
                "enabled": False,
                "auto_restore": False,
                "session_file": "/tmp/session.json",
                "backup_sessions": False,
                "max_sessions": 5,
            },
            "ui": {
                "show_icons": False,
                "status_bar_help": False,
                "mouse_support": False,
                "color_scheme": "dark",
            },
            "logging": {
                "level": "ERROR",
                "file": "/tmp/log.txt",
                "console": False,
            },
        }
        
        config = ModernGopherConfig.from_dict(config_dict)
        
        # Check gopher settings
        self.assertEqual(config.default_server, "gopher://example.com")
        self.assertEqual(config.default_port, 7070)
        self.assertEqual(config.timeout, 60)
        self.assertTrue(config.use_ssl)
        self.assertTrue(config.use_ipv6)
        
        # Check cache settings
        self.assertFalse(config.cache_enabled)
        self.assertEqual(config.cache_directory, "/tmp/cache")
        self.assertEqual(config.cache_max_size_mb, 200)
        self.assertEqual(config.cache_expiration_hours, 48)
        
        # Check browser settings
        self.assertEqual(config.initial_url, "gopher://start.com")
        self.assertEqual(config.bookmarks_file, "/tmp/bookmarks.json")
        self.assertEqual(config.history_file, "/tmp/history.json")
        self.assertEqual(config.max_history_items, 500)
        self.assertFalse(config.save_session)
        
        # Check session settings
        self.assertFalse(config.session_enabled)
        self.assertFalse(config.session_auto_restore)
        self.assertEqual(config.session_file, "/tmp/session.json")
        self.assertFalse(config.session_backup_sessions)
        self.assertEqual(config.session_max_sessions, 5)
        
        # Check UI settings
        self.assertFalse(config.show_icons)
        self.assertFalse(config.status_bar_help)
        self.assertFalse(config.mouse_support)
        self.assertEqual(config.color_scheme, "dark")
        
        # Check logging settings
        self.assertEqual(config.log_level, "ERROR")
        self.assertEqual(config.log_file, "/tmp/log.txt")
        self.assertFalse(config.log_console)

    def test_from_dict_partial(self):
        """Test creating config from partial dictionary."""
        config_dict = {
            "gopher": {
                "default_server": "gopher://partial.com",
                "timeout": 45,
            },
            "ui": {
                "color_scheme": "light",
            }
        }
        
        config = ModernGopherConfig.from_dict(config_dict)
        
        # Should use provided values
        self.assertEqual(config.default_server, "gopher://partial.com")
        self.assertEqual(config.timeout, 45)
        self.assertEqual(config.color_scheme, "light")
        
        # Should use defaults for missing values
        self.assertEqual(config.default_port, 70)
        self.assertFalse(config.use_ssl)
        self.assertTrue(config.show_icons)

    def test_from_dict_empty_sections(self):
        """Test creating config from dictionary with empty sections."""
        config_dict = {
            "gopher": {},
            "cache": {},
            "browser": {},
            "session": {},
            "ui": {},
            "logging": {},
        }
        
        config = ModernGopherConfig.from_dict(config_dict)
        
        # Should all be defaults
        self.assertEqual(config.default_server, "gopher://gopher.floodgap.com")
        self.assertTrue(config.cache_enabled)
        self.assertEqual(config.log_level, "INFO")

    def test_from_dict_missing_sections(self):
        """Test creating config from dictionary with missing sections."""
        config_dict = {
            "gopher": {
                "default_server": "gopher://only.com",
            }
            # All other sections missing
        }
        
        config = ModernGopherConfig.from_dict(config_dict)
        
        # Should use provided value
        self.assertEqual(config.default_server, "gopher://only.com")
        
        # Should use defaults for missing sections
        self.assertTrue(config.cache_enabled)
        self.assertEqual(config.log_level, "INFO")
        self.assertTrue(config.show_icons)


class TestModernGopherConfigValidation(unittest.TestCase):
    """Test config validation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = ModernGopherConfig()

    def test_validate_setting_gopher_timeout_valid(self):
        """Test validating valid gopher timeout."""
        is_valid, error = self.config.validate_setting("gopher.timeout", 30)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_validate_setting_gopher_timeout_invalid(self):
        """Test validating invalid gopher timeout."""
        is_valid, error = self.config.validate_setting("gopher.timeout", 0)
        self.assertFalse(is_valid)
        self.assertIn("must be positive", error)

        is_valid, error = self.config.validate_setting("gopher.timeout", -10)
        self.assertFalse(is_valid)
        self.assertIn("must be positive", error)

    def test_validate_setting_gopher_port_valid(self):
        """Test validating valid gopher port."""
        is_valid, error = self.config.validate_setting("gopher.default_port", 70)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

        is_valid, error = self.config.validate_setting("gopher.default_port", 65535)
        self.assertTrue(is_valid)

    def test_validate_setting_gopher_port_invalid(self):
        """Test validating invalid gopher port."""
        is_valid, error = self.config.validate_setting("gopher.default_port", 0)
        self.assertFalse(is_valid)
        self.assertIn("between 1 and 65535", error)

        is_valid, error = self.config.validate_setting("gopher.default_port", 70000)
        self.assertFalse(is_valid)
        self.assertIn("between 1 and 65535", error)

    def test_validate_setting_cache_size_valid(self):
        """Test validating valid cache size."""
        is_valid, error = self.config.validate_setting("cache.max_size_mb", 100)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_validate_setting_cache_size_invalid(self):
        """Test validating invalid cache size."""
        is_valid, error = self.config.validate_setting("cache.max_size_mb", 0)
        self.assertFalse(is_valid)
        self.assertIn("must be positive", error)

    def test_validate_setting_log_level_valid(self):
        """Test validating valid log levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in valid_levels:
            is_valid, error = self.config.validate_setting("logging.level", level)
            self.assertTrue(is_valid, f"Level {level} should be valid")
            self.assertEqual(error, "")

    def test_validate_setting_log_level_invalid(self):
        """Test validating invalid log level."""
        is_valid, error = self.config.validate_setting("logging.level", "INVALID")
        self.assertFalse(is_valid)
        self.assertIn("must be one of", error)

    def test_validate_setting_color_scheme_valid(self):
        """Test validating valid color schemes."""
        valid_schemes = ["default", "dark", "light", "monochrome"]
        
        for scheme in valid_schemes:
            is_valid, error = self.config.validate_setting("ui.color_scheme", scheme)
            self.assertTrue(is_valid, f"Scheme {scheme} should be valid")
            self.assertEqual(error, "")

    def test_validate_setting_color_scheme_invalid(self):
        """Test validating invalid color scheme."""
        is_valid, error = self.config.validate_setting("ui.color_scheme", "rainbow")
        self.assertFalse(is_valid)
        self.assertIn("must be one of", error)

    def test_validate_setting_boolean_valid(self):
        """Test validating boolean values."""
        # Test actual booleans
        is_valid, error = self.config.validate_setting("cache.enabled", True)
        self.assertTrue(is_valid)
        
        is_valid, error = self.config.validate_setting("cache.enabled", False)
        self.assertTrue(is_valid)

    def test_validate_setting_boolean_string_valid(self):
        """Test validating boolean string values."""
        valid_true = ["true", "1", "yes", "on"]
        valid_false = ["false", "0", "no", "off"]
        
        for value in valid_true + valid_false:
            is_valid, error = self.config.validate_setting("cache.enabled", value)
            self.assertTrue(is_valid, f"String '{value}' should be valid boolean")

    def test_validate_setting_boolean_invalid(self):
        """Test validating invalid boolean values."""
        is_valid, error = self.config.validate_setting("cache.enabled", "maybe")
        self.assertFalse(is_valid)
        self.assertIn("Boolean value expected", error)

    def test_validate_setting_numeric_invalid(self):
        """Test validating invalid numeric values."""
        is_valid, error = self.config.validate_setting("gopher.timeout", "not_a_number")
        self.assertFalse(is_valid)
        self.assertIn("Numeric value expected", error)

    def test_validate_setting_unknown_key(self):
        """Test validating unknown key path."""
        is_valid, error = self.config.validate_setting("unknown.key", "value")
        self.assertFalse(is_valid)
        self.assertIn("Unknown key path", error)

    def test_validate_setting_exception_handling(self):
        """Test validation with exception handling."""
        # Mock the DEFAULT_CONFIG to cause an error
        with patch('modern_gopher.config.DEFAULT_CONFIG', {}):
            is_valid, error = self.config.validate_setting("gopher.timeout", 30)
            self.assertFalse(is_valid)
            self.assertIn("Validation error", error)


class TestModernGopherConfigSetValue(unittest.TestCase):
    """Test config set_value functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = ModernGopherConfig()

    def test_set_value_gopher_section(self):
        """Test setting values in gopher section."""
        # Test all gopher keys
        self.assertTrue(self.config.set_value("gopher.default_server", "gopher://new.com"))
        self.assertEqual(self.config.default_server, "gopher://new.com")
        
        self.assertTrue(self.config.set_value("gopher.default_port", "80"))
        self.assertEqual(self.config.default_port, 80)
        
        self.assertTrue(self.config.set_value("gopher.timeout", "60"))
        self.assertEqual(self.config.timeout, 60)
        
        self.assertTrue(self.config.set_value("gopher.use_ssl", "true"))
        self.assertTrue(self.config.use_ssl)
        
        self.assertTrue(self.config.set_value("gopher.use_ipv6", "false"))
        self.assertFalse(self.config.use_ipv6)

    def test_set_value_cache_section(self):
        """Test setting values in cache section."""
        self.assertTrue(self.config.set_value("cache.enabled", "false"))
        self.assertFalse(self.config.cache_enabled)
        
        self.assertTrue(self.config.set_value("cache.directory", "~/new_cache"))
        self.assertIn("new_cache", self.config.cache_directory)
        
        self.assertTrue(self.config.set_value("cache.max_size_mb", "200"))
        self.assertEqual(self.config.cache_max_size_mb, 200)
        
        self.assertTrue(self.config.set_value("cache.expiration_hours", "48"))
        self.assertEqual(self.config.cache_expiration_hours, 48)

    def test_set_value_browser_section(self):
        """Test setting values in browser section."""
        self.assertTrue(self.config.set_value("browser.initial_url", "gopher://start.com"))
        self.assertEqual(self.config.initial_url, "gopher://start.com")
        
        self.assertTrue(self.config.set_value("browser.bookmarks_file", "~/new_bookmarks.json"))
        self.assertIn("new_bookmarks.json", self.config.bookmarks_file)
        
        self.assertTrue(self.config.set_value("browser.history_file", "~/new_history.json"))
        self.assertIn("new_history.json", self.config.history_file)
        
        self.assertTrue(self.config.set_value("browser.max_history_items", "500"))
        self.assertEqual(self.config.max_history_items, 500)
        
        self.assertTrue(self.config.set_value("browser.save_session", "false"))
        self.assertFalse(self.config.save_session)

    def test_set_value_session_section(self):
        """Test setting values in session section."""
        self.assertTrue(self.config.set_value("session.enabled", "false"))
        self.assertFalse(self.config.session_enabled)
        
        self.assertTrue(self.config.set_value("session.auto_restore", "false"))
        self.assertFalse(self.config.session_auto_restore)
        
        self.assertTrue(self.config.set_value("session.session_file", "~/new_session.json"))
        self.assertIn("new_session.json", self.config.session_file)
        
        self.assertTrue(self.config.set_value("session.backup_sessions", "false"))
        self.assertFalse(self.config.session_backup_sessions)
        
        self.assertTrue(self.config.set_value("session.max_sessions", "5"))
        self.assertEqual(self.config.session_max_sessions, 5)

    def test_set_value_ui_section(self):
        """Test setting values in UI section."""
        self.assertTrue(self.config.set_value("ui.show_icons", "false"))
        self.assertFalse(self.config.show_icons)
        
        self.assertTrue(self.config.set_value("ui.status_bar_help", "false"))
        self.assertFalse(self.config.status_bar_help)
        
        self.assertTrue(self.config.set_value("ui.mouse_support", "false"))
        self.assertFalse(self.config.mouse_support)
        
        self.assertTrue(self.config.set_value("ui.color_scheme", "dark"))
        self.assertEqual(self.config.color_scheme, "dark")

    def test_set_value_logging_section(self):
        """Test setting values in logging section."""
        self.assertTrue(self.config.set_value("logging.level", "DEBUG"))
        self.assertEqual(self.config.log_level, "DEBUG")
        
        self.assertTrue(self.config.set_value("logging.file", "/tmp/test.log"))
        self.assertEqual(self.config.log_file, "/tmp/test.log")
        
        self.assertTrue(self.config.set_value("logging.console", "false"))
        self.assertFalse(self.config.log_console)

    def test_set_value_invalid_key_path(self):
        """Test setting value with invalid key path."""
        # Too many parts
        self.assertFalse(self.config.set_value("gopher.section.timeout", "30"))
        
        # Too few parts
        self.assertFalse(self.config.set_value("timeout", "30"))
        
        # Empty
        self.assertFalse(self.config.set_value("", "30"))

    def test_set_value_unknown_section(self):
        """Test setting value in unknown section."""
        self.assertFalse(self.config.set_value("unknown.key", "value"))

    def test_set_value_unknown_key(self):
        """Test setting unknown key in valid section."""
        self.assertFalse(self.config.set_value("gopher.unknown_key", "value"))

    def test_set_value_type_conversion_error(self):
        """Test setting value with type conversion error."""
        # Try to set invalid integer
        self.assertFalse(self.config.set_value("gopher.timeout", "not_a_number"))

    def test_set_value_validation_error(self):
        """Test setting value that fails validation."""
        # Try to set invalid timeout
        self.assertFalse(self.config.set_value("gopher.timeout", "0"))

    def test_set_value_boolean_conversion(self):
        """Test boolean conversion from strings."""
        # Test various boolean string values
        true_values = ["true", "1", "yes", "on", "TRUE", "Yes", "ON"]
        false_values = ["false", "0", "no", "off", "FALSE", "No", "OFF"]
        
        for value in true_values:
            self.config.set_value("cache.enabled", value)
            self.assertTrue(self.config.cache_enabled, f"'{value}' should convert to True")
        
        for value in false_values:
            self.config.set_value("cache.enabled", value)
            self.assertFalse(self.config.cache_enabled, f"'{value}' should convert to False")


class TestConfigGlobalFunctions(unittest.TestCase):
    """Test global config functions."""

    def test_get_default_config_path(self):
        """Test get_default_config_path function."""
        path = ModernGopherConfig.get_default_config_path()
        
        self.assertIsInstance(path, Path)
        self.assertTrue(str(path).endswith("config.yaml"))
        self.assertIn(".config", str(path))
        self.assertIn("modern-gopher", str(path))

    @patch('modern_gopher.config.ModernGopherConfig.ensure_directories')
    def test_get_config_default_path(self, mock_ensure):
        """Test get_config with default path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.yaml"
            
            # Create a valid config file
            config_data = {
                "gopher": {"default_server": "gopher://test.com"},
                "ui": {"color_scheme": "dark"}
            }
            with open(config_file, "w") as f:
                yaml.dump(config_data, f)
            
            with patch('modern_gopher.config.ModernGopherConfig.get_default_config_path', return_value=config_file):
                config = get_config()
                
                self.assertEqual(config.default_server, "gopher://test.com")
                self.assertEqual(config.color_scheme, "dark")
                mock_ensure.assert_called_once()

    def test_get_config_custom_path(self):
        """Test get_config with custom path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "custom_config.yaml"
            
            # Create a valid config file
            config_data = {
                "gopher": {"timeout": 60},
                "cache": {"enabled": False}
            }
            with open(config_file, "w") as f:
                yaml.dump(config_data, f)
            
            config = get_config(config_file)
            
            self.assertEqual(config.timeout, 60)
            self.assertFalse(config.cache_enabled)

    def test_get_config_nonexistent_file(self):
        """Test get_config with non-existent file."""
        nonexistent_file = Path("/nonexistent/config.yaml")
        
        config = get_config(nonexistent_file)
        
        # Should return default config
        self.assertEqual(config.default_server, "gopher://gopher.floodgap.com")
        self.assertTrue(config.cache_enabled)

    def test_get_config_invalid_yaml(self):
        """Test get_config with invalid YAML file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "invalid_config.yaml"
            
            # Create invalid YAML
            with open(config_file, "w") as f:
                f.write("{ invalid yaml content")
            
            config = get_config(config_file)
            
            # Should return default config
            self.assertEqual(config.default_server, "gopher://gopher.floodgap.com")

    @patch('modern_gopher.config.logger')
    def test_get_config_file_error(self, mock_logger):
        """Test get_config with file read error."""
        # Try to read a directory as a file
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir)  # This is a directory, not a file
            
            config = get_config(config_path)
            
            # Should return default config and log error
            self.assertEqual(config.default_server, "gopher://gopher.floodgap.com")
            mock_logger.error.assert_called()


class TestConfigConstants(unittest.TestCase):
    """Test config constants and defaults."""

    def test_default_config_structure(self):
        """Test DEFAULT_CONFIG has expected structure."""
        required_sections = ["gopher", "cache", "browser", "session", "ui", "keybindings", "logging"]
        
        for section in required_sections:
            self.assertIn(section, DEFAULT_CONFIG, f"Section '{section}' missing from DEFAULT_CONFIG")

    def test_default_config_gopher_section(self):
        """Test gopher section in DEFAULT_CONFIG."""
        gopher = DEFAULT_CONFIG["gopher"]
        
        self.assertIn("default_server", gopher)
        self.assertIn("default_port", gopher)
        self.assertIn("timeout", gopher)
        self.assertIn("use_ssl", gopher)
        self.assertIn("use_ipv6", gopher)
        
        # Check types
        self.assertIsInstance(gopher["default_server"], str)
        self.assertIsInstance(gopher["default_port"], int)
        self.assertIsInstance(gopher["timeout"], int)
        self.assertIsInstance(gopher["use_ssl"], bool)

    def test_default_config_values(self):
        """Test specific default config values."""
        self.assertEqual(DEFAULT_CONFIG["gopher"]["default_port"], 70)
        self.assertEqual(DEFAULT_CONFIG["gopher"]["timeout"], 30)
        self.assertFalse(DEFAULT_CONFIG["gopher"]["use_ssl"])
        
        self.assertTrue(DEFAULT_CONFIG["cache"]["enabled"])
        self.assertEqual(DEFAULT_CONFIG["cache"]["max_size_mb"], 100)
        
        self.assertEqual(DEFAULT_CONFIG["browser"]["max_history_items"], 1000)
        self.assertTrue(DEFAULT_CONFIG["ui"]["show_icons"])


if __name__ == "__main__":
    unittest.main()

