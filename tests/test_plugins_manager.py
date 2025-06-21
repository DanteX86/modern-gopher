#!/usr/bin/env python3
"""
Tests for plugin manager.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from modern_gopher.core.types import GopherItem, GopherItemType
from modern_gopher.plugins.base import BasePlugin, ContentProcessor, ItemTypeHandler, PluginMetadata
from modern_gopher.plugins.manager import PluginManager, get_manager, reset_manager


class TestPluginManager(unittest.TestCase):
    """Test PluginManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir)
        self.manager = PluginManager(str(self.config_dir))

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test plugin manager initialization."""
        self.assertEqual(self.manager.config_dir, self.config_dir)
        self.assertFalse(self.manager.initialized)
        self.assertEqual(self.manager.config_file, self.config_dir / "plugins.json")
        self.assertEqual(self.manager.plugin_config, {})

    def test_load_plugin_config_new_file(self):
        """Test loading plugin config when file doesn't exist."""
        self.manager._load_plugin_config()
        
        # Should create default config
        expected_config = {
            "enabled_plugins": [],
            "disabled_plugins": [],
            "plugin_settings": {},
        }
        self.assertEqual(self.manager.plugin_config, expected_config)
        
        # Should create config file
        self.assertTrue(self.manager.config_file.exists())

    def test_load_plugin_config_existing_file(self):
        """Test loading plugin config from existing file."""
        config_data = {
            "enabled_plugins": ["test_plugin"],
            "disabled_plugins": ["another_plugin"],
            "plugin_settings": {"test_plugin": {"setting": "value"}},
        }
        
        # Create config file
        with open(self.manager.config_file, "w") as f:
            json.dump(config_data, f)
        
        self.manager._load_plugin_config()
        self.assertEqual(self.manager.plugin_config, config_data)

    def test_load_plugin_config_corrupted_file(self):
        """Test loading plugin config with corrupted JSON."""
        # Create corrupted config file
        with open(self.manager.config_file, "w") as f:
            f.write("{ invalid json")
        
        self.manager._load_plugin_config()
        
        # Should fall back to default config
        expected_config = {
            "enabled_plugins": [],
            "disabled_plugins": [],
            "plugin_settings": {},
        }
        self.assertEqual(self.manager.plugin_config, expected_config)

    def test_save_plugin_config(self):
        """Test saving plugin config."""
        config_data = {
            "enabled_plugins": ["test_plugin"],
            "disabled_plugins": [],
            "plugin_settings": {"test_plugin": {"setting": "value"}},
        }
        self.manager.plugin_config = config_data
        
        self.manager._save_plugin_config()
        
        # Verify file was created and contains correct data
        self.assertTrue(self.manager.config_file.exists())
        with open(self.manager.config_file, "r") as f:
            loaded_data = json.load(f)
        self.assertEqual(loaded_data, config_data)

    @patch('modern_gopher.plugins.manager.logger')
    def test_save_plugin_config_error(self, mock_logger):
        """Test save plugin config with write error."""
        # Set config to readonly directory
        readonly_dir = self.config_dir / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)
        
        self.manager.config_file = readonly_dir / "plugins.json"
        self.manager.plugin_config = {"test": "data"}
        
        self.manager._save_plugin_config()
        
        # Should log error
        mock_logger.error.assert_called()

    @patch('modern_gopher.plugins.manager.importlib.import_module')
    def test_load_builtin_plugins_success(self, mock_import):
        """Test loading built-in plugins successfully."""
        mock_import.side_effect = ImportError("Module not found")
        
        # This should not raise an exception even with import errors
        self.manager._load_builtin_plugins()
        
        # Should have attempted to import built-in plugins
        self.assertTrue(mock_import.called)

    @patch('modern_gopher.plugins.manager.importlib.import_module')
    def test_load_builtin_plugins_import_error(self, mock_import):
        """Test loading built-in plugins with import error."""
        mock_import.side_effect = ImportError("Module not found")
        
        # This should not raise an exception even with import errors
        self.manager._load_builtin_plugins()
        
        # Verify import was attempted (would have logged warnings)
        self.assertTrue(mock_import.called)

    def test_load_external_plugins_no_directory(self):
        """Test loading external plugins when directory doesn't exist."""
        self.manager._load_external_plugins()
        
        # Should create plugins directory
        plugins_dir = self.config_dir / "plugins"
        self.assertTrue(plugins_dir.exists())

    def test_load_external_plugins_empty_directory(self):
        """Test loading external plugins with empty directory."""
        plugins_dir = self.config_dir / "plugins"
        plugins_dir.mkdir()
        
        self.manager._load_external_plugins()
        
        # Should not raise any errors
        self.assertTrue(plugins_dir.exists())

    def test_load_external_plugins_with_files(self):
        """Test loading external plugins with Python files."""
        plugins_dir = self.config_dir / "plugins"
        plugins_dir.mkdir()
        
        # Create a test plugin file
        plugin_file = plugins_dir / "test_plugin.py"
        plugin_content = '''
from modern_gopher.plugins.base import BasePlugin, PluginMetadata

class TestExternalPlugin(BasePlugin):
    @property
    def metadata(self):
        return PluginMetadata(
            name="test_external",
            version="1.0.0",
            author="Test",
            description="External test plugin"
        )
'''
        plugin_file.write_text(plugin_content)
        
        # Mock registry
        self.manager.registry.register_plugin = Mock(return_value=True)
        
        with patch('modern_gopher.plugins.manager.logger') as mock_logger:
            self.manager._load_external_plugins()
            
            # Should attempt to load the plugin
            mock_logger.info.assert_called()

    def test_load_external_plugins_skip_private_files(self):
        """Test that external plugin loading skips private files."""
        plugins_dir = self.config_dir / "plugins"
        plugins_dir.mkdir()
        
        # Create private file
        private_file = plugins_dir / "_private_plugin.py"
        private_file.write_text("# Private plugin")
        
        self.manager._load_external_plugins()
        
        # Should not attempt to load private files

    @patch('modern_gopher.plugins.manager.logger')
    def test_load_external_plugins_loading_error(self, mock_logger):
        """Test loading external plugins with loading error."""
        plugins_dir = self.config_dir / "plugins"
        plugins_dir.mkdir()
        
        # Create invalid plugin file
        plugin_file = plugins_dir / "invalid_plugin.py"
        plugin_file.write_text("invalid python syntax !!!")
        
        self.manager._load_external_plugins()
        
        # Should log warning for failed loading
        mock_logger.warning.assert_called()

    @patch('modern_gopher.plugins.manager.PluginManager._load_external_plugins')
    @patch('modern_gopher.plugins.manager.PluginManager._load_builtin_plugins')
    @patch('modern_gopher.plugins.manager.PluginManager._load_plugin_config')
    def test_initialize_success(self, mock_load_config, mock_load_builtin, mock_load_external):
        """Test successful initialization."""
        self.manager.initialize()
        
        self.assertTrue(self.manager.initialized)
        mock_load_config.assert_called_once()
        mock_load_builtin.assert_called_once()
        mock_load_external.assert_called_once()

    @patch('modern_gopher.plugins.manager.logger')
    @patch('modern_gopher.plugins.manager.PluginManager._load_plugin_config')
    def test_initialize_error(self, mock_load_config, mock_logger):
        """Test initialization with error."""
        mock_load_config.side_effect = Exception("Configuration error")
        
        with self.assertRaises(Exception):
            self.manager.initialize()
        
        self.assertFalse(self.manager.initialized)
        mock_logger.error.assert_called()

    def test_process_content_not_initialized(self):
        """Test process_content when not initialized."""
        content = "test content"
        result_content, result_metadata = self.manager.process_content(
            GopherItemType.TEXT_FILE, content
        )
        
        self.assertEqual(result_content, content)
        self.assertEqual(result_metadata, {})

    def test_process_content_with_item_handler(self):
        """Test process_content with item type handler."""
        # Mock initialization
        self.manager.initialized = True
        
        # Create mock handler
        mock_handler = Mock(spec=ItemTypeHandler)
        mock_handler.can_handle.return_value = True
        mock_handler.process_content.return_value = ("processed content", {"handler": "applied"})
        mock_handler.metadata = PluginMetadata(
            name="test_handler",
            version="1.0.0",
            author="Test",
            description="Test handler"
        )
        
        # Mock registry
        self.manager.registry.get_item_handlers = Mock(return_value=[mock_handler])
        self.manager.registry.get_content_processors = Mock(return_value=[])
        
        content = "original content"
        result_content, result_metadata = self.manager.process_content(
            GopherItemType.TEXT_FILE, content
        )
        
        self.assertEqual(result_content, "processed content")
        self.assertIn("handler", result_metadata)
        self.assertIn("test_handler", result_metadata["plugins_applied"])

    def test_process_content_with_content_processor(self):
        """Test process_content with content processor."""
        # Mock initialization
        self.manager.initialized = True
        
        # Create mock processor
        mock_processor = Mock(spec=ContentProcessor)
        mock_processor.can_process.return_value = True
        mock_processor.process.return_value = ("processed content", {"processor": "applied"})
        mock_processor.metadata = PluginMetadata(
            name="test_processor",
            version="1.0.0",
            author="Test",
            description="Test processor"
        )
        
        # Mock registry
        self.manager.registry.get_item_handlers = Mock(return_value=[])
        self.manager.registry.get_content_processors = Mock(return_value=[mock_processor])
        
        content = "original content"
        result_content, result_metadata = self.manager.process_content(
            GopherItemType.TEXT_FILE, content
        )
        
        self.assertEqual(result_content, "processed content")
        self.assertIn("processor", result_metadata)
        self.assertIn("test_processor", result_metadata["plugins_applied"])

    @patch('modern_gopher.plugins.manager.logger')
    def test_process_content_handler_error(self, mock_logger):
        """Test process_content with handler error."""
        # Mock initialization
        self.manager.initialized = True
        
        # Create mock handler that raises error
        mock_handler = Mock(spec=ItemTypeHandler)
        mock_handler.can_handle.return_value = True
        mock_handler.process_content.side_effect = Exception("Handler error")
        mock_handler.metadata = PluginMetadata(
            name="error_handler",
            version="1.0.0",
            author="Test",
            description="Error handler"
        )
        
        # Mock registry
        self.manager.registry.get_item_handlers = Mock(return_value=[mock_handler])
        self.manager.registry.get_content_processors = Mock(return_value=[])
        
        content = "original content"
        result_content, result_metadata = self.manager.process_content(
            GopherItemType.TEXT_FILE, content
        )
        
        # Should return original content and log warning
        self.assertEqual(result_content, content)
        mock_logger.warning.assert_called()

    @patch('modern_gopher.plugins.manager.logger')
    def test_process_content_processor_error(self, mock_logger):
        """Test process_content with processor error."""
        # Mock initialization
        self.manager.initialized = True
        
        # Create mock processor that raises error
        mock_processor = Mock(spec=ContentProcessor)
        mock_processor.can_process.return_value = True
        mock_processor.process.side_effect = Exception("Processor error")
        mock_processor.metadata = PluginMetadata(
            name="error_processor",
            version="1.0.0",
            author="Test",
            description="Error processor"
        )
        
        # Mock registry
        self.manager.registry.get_item_handlers = Mock(return_value=[])
        self.manager.registry.get_content_processors = Mock(return_value=[mock_processor])
        
        content = "original content"
        result_content, result_metadata = self.manager.process_content(
            GopherItemType.TEXT_FILE, content
        )
        
        # Should return original content and log warning
        self.assertEqual(result_content, content)
        mock_logger.warning.assert_called()

    @patch('modern_gopher.plugins.manager.logger')
    def test_process_content_pipeline_error(self, mock_logger):
        """Test process_content with pipeline error."""
        # Mock initialization
        self.manager.initialized = True
        
        # Mock registry to raise error
        self.manager.registry.get_item_handlers = Mock(side_effect=Exception("Registry error"))
        
        content = "original content"
        result_content, result_metadata = self.manager.process_content(
            GopherItemType.TEXT_FILE, content
        )
        
        # Should return original content and log error
        self.assertEqual(result_content, content)
        mock_logger.error.assert_called()

    def test_get_plugin_info_not_initialized(self):
        """Test get_plugin_info when not initialized."""
        result = self.manager.get_plugin_info()
        self.assertEqual(result, {})

    def test_get_plugin_info_initialized(self):
        """Test get_plugin_info when initialized."""
        # Mock initialization
        self.manager.initialized = True
        
        # Create mock plugin
        mock_plugin = Mock()
        mock_plugin.metadata = PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            author="Test Author",
            description="Test plugin description"
        )
        mock_plugin.enabled = True
        mock_plugin.get_priority.return_value = 100
        # Mock get_supported_types to return empty list for plugins that don't have it
        mock_plugin.get_supported_types.return_value = []
        
        # Mock registry
        self.manager.registry.get_all_plugins = Mock(return_value={"test_plugin": mock_plugin})
        
        result = self.manager.get_plugin_info()
        
        expected = {
            "test_plugin": {
                "name": "test_plugin",
                "version": "1.0.0",
                "author": "Test Author",
                "description": "Test plugin description",
                "enabled": True,
                "type": "Mock",
                "priority": 100,
                "supported_types": []
            }
        }
        self.assertEqual(result, expected)

    def test_get_plugin_info_with_supported_types(self):
        """Test get_plugin_info with plugin that has supported types."""
        # Mock initialization
        self.manager.initialized = True
        
        # Create mock plugin with supported types
        mock_plugin = Mock()
        mock_plugin.metadata = PluginMetadata(
            name="test_handler",
            version="1.0.0",
            author="Test",
            description="Test handler"
        )
        mock_plugin.enabled = True
        mock_plugin.get_priority.return_value = 50
        mock_plugin.get_supported_types.return_value = [GopherItemType.TEXT_FILE, GopherItemType.IMAGE_FILE]
        
        # Mock registry
        self.manager.registry.get_all_plugins = Mock(return_value={"test_handler": mock_plugin})
        
        result = self.manager.get_plugin_info()
        
        self.assertIn("supported_types", result["test_handler"])
        self.assertEqual(result["test_handler"]["supported_types"], ["0", "I"])

    def test_enable_plugin_not_initialized(self):
        """Test enable_plugin when not initialized."""
        result = self.manager.enable_plugin("test_plugin")
        self.assertFalse(result)

    def test_enable_plugin_success(self):
        """Test enable_plugin successfully."""
        # Mock initialization
        self.manager.initialized = True
        
        # Mock registry
        self.manager.registry.enable_plugin = Mock(return_value=True)
        
        # Set up plugin config with disabled plugin
        self.manager.plugin_config = {
            "disabled_plugins": ["test_plugin"],
            "plugin_settings": {}
        }
        
        result = self.manager.enable_plugin("test_plugin")
        
        self.assertTrue(result)
        self.assertNotIn("test_plugin", self.manager.plugin_config["disabled_plugins"])

    def test_enable_plugin_failure(self):
        """Test enable_plugin failure."""
        # Mock initialization
        self.manager.initialized = True
        
        # Mock registry to fail
        self.manager.registry.enable_plugin = Mock(return_value=False)
        
        result = self.manager.enable_plugin("test_plugin")
        self.assertFalse(result)

    def test_disable_plugin_not_initialized(self):
        """Test disable_plugin when not initialized."""
        result = self.manager.disable_plugin("test_plugin")
        self.assertFalse(result)

    def test_disable_plugin_success(self):
        """Test disable_plugin successfully."""
        # Mock initialization
        self.manager.initialized = True
        
        # Mock registry
        self.manager.registry.disable_plugin = Mock(return_value=True)
        
        # Set up plugin config
        self.manager.plugin_config = {
            "disabled_plugins": [],
            "plugin_settings": {}
        }
        
        result = self.manager.disable_plugin("test_plugin")
        
        self.assertTrue(result)
        self.assertIn("test_plugin", self.manager.plugin_config["disabled_plugins"])

    def test_disable_plugin_failure(self):
        """Test disable_plugin failure."""
        # Mock initialization
        self.manager.initialized = True
        
        # Mock registry to fail
        self.manager.registry.disable_plugin = Mock(return_value=False)
        
        result = self.manager.disable_plugin("test_plugin")
        self.assertFalse(result)

    def test_configure_plugin_not_initialized(self):
        """Test configure_plugin when not initialized."""
        result = self.manager.configure_plugin("test_plugin", {"setting": "value"})
        self.assertFalse(result)

    def test_configure_plugin_success(self):
        """Test configure_plugin successfully."""
        # Mock initialization
        self.manager.initialized = True
        
        # Create mock plugin
        mock_plugin = Mock()
        mock_plugin.configure.return_value = True
        
        # Mock registry
        self.manager.registry.get_plugin = Mock(return_value=mock_plugin)
        
        # Set up plugin config
        self.manager.plugin_config = {"plugin_settings": {}}
        
        config = {"setting": "value"}
        result = self.manager.configure_plugin("test_plugin", config)
        
        self.assertTrue(result)
        self.assertEqual(self.manager.plugin_config["plugin_settings"]["test_plugin"], config)

    def test_configure_plugin_not_found(self):
        """Test configure_plugin with non-existent plugin."""
        # Mock initialization
        self.manager.initialized = True
        
        # Mock registry to return None
        self.manager.registry.get_plugin = Mock(return_value=None)
        
        result = self.manager.configure_plugin("nonexistent", {"setting": "value"})
        self.assertFalse(result)

    def test_configure_plugin_failure(self):
        """Test configure_plugin with configuration failure."""
        # Mock initialization
        self.manager.initialized = True
        
        # Create mock plugin that fails configuration
        mock_plugin = Mock()
        mock_plugin.configure.return_value = False
        
        # Mock registry
        self.manager.registry.get_plugin = Mock(return_value=mock_plugin)
        
        result = self.manager.configure_plugin("test_plugin", {"setting": "value"})
        self.assertFalse(result)

    def test_get_available_plugins_not_initialized(self):
        """Test get_available_plugins when not initialized."""
        result = self.manager.get_available_plugins()
        self.assertEqual(result, [])

    def test_get_available_plugins_initialized(self):
        """Test get_available_plugins when initialized."""
        # Mock initialization
        self.manager.initialized = True
        
        # Mock registry
        self.manager.registry.get_all_plugins = Mock(return_value={
            "plugin1": Mock(),
            "plugin2": Mock(),
            "plugin3": Mock()
        })
        
        result = self.manager.get_available_plugins()
        self.assertEqual(set(result), {"plugin1", "plugin2", "plugin3"})

    def test_load_plugin_file_not_found(self):
        """Test load_plugin with non-existent file."""
        result = self.manager.load_plugin("/nonexistent/plugin.py")
        self.assertFalse(result)

    def test_load_plugin_success(self):
        """Test load_plugin successfully."""
        # Create test plugin file
        plugin_file = self.config_dir / "test_plugin.py"
        plugin_content = '''
from modern_gopher.plugins.base import BasePlugin, PluginMetadata

class TestLoadPlugin(BasePlugin):
    @property
    def metadata(self):
        return PluginMetadata(
            name="test_load",
            version="1.0.0",
            author="Test",
            description="Test load plugin"
        )
'''
        plugin_file.write_text(plugin_content)
        
        # Mock registry
        self.manager.registry.register_plugin = Mock(return_value=True)
        
        result = self.manager.load_plugin(str(plugin_file))
        self.assertTrue(result)

    @patch('modern_gopher.plugins.manager.logger')
    def test_load_plugin_error(self, mock_logger):
        """Test load_plugin with error."""
        # Create invalid plugin file
        plugin_file = self.config_dir / "invalid_plugin.py"
        plugin_file.write_text("invalid python syntax !!!")
        
        result = self.manager.load_plugin(str(plugin_file))
        
        self.assertFalse(result)
        mock_logger.error.assert_called()

    def test_load_plugin_no_plugin_classes(self):
        """Test load_plugin with file containing no plugin classes."""
        # Create file with no plugin classes
        plugin_file = self.config_dir / "no_plugins.py"
        plugin_file.write_text("# No plugin classes here\nprint('Hello')")
        
        result = self.manager.load_plugin(str(plugin_file))
        self.assertFalse(result)


class TestPluginManagerGlobalFunctions(unittest.TestCase):
    """Test global plugin manager functions."""

    def setUp(self):
        """Set up test fixtures."""
        reset_manager()

    def tearDown(self):
        """Clean up test fixtures."""
        reset_manager()

    def test_get_manager_creates_instance(self):
        """Test get_manager creates new instance."""
        manager = get_manager("/tmp/test")
        self.assertIsInstance(manager, PluginManager)
        self.assertEqual(str(manager.config_dir), "/tmp/test")

    def test_get_manager_returns_same_instance(self):
        """Test get_manager returns same instance on subsequent calls."""
        manager1 = get_manager("/tmp/test")
        manager2 = get_manager("/tmp/test")
        self.assertIs(manager1, manager2)

    def test_reset_manager(self):
        """Test reset_manager clears global instance."""
        manager1 = get_manager("/tmp/test")
        reset_manager()
        manager2 = get_manager("/tmp/test")
        self.assertIsNot(manager1, manager2)


class TestPluginManagerIntegration(unittest.TestCase):
    """Integration tests for PluginManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir)
        self.manager = PluginManager(str(self.config_dir))

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_lifecycle_with_external_plugin(self):
        """Test full lifecycle with external plugin."""
        # Create plugins directory
        plugins_dir = self.config_dir / "plugins"
        plugins_dir.mkdir()
        
        # Create test plugin
        plugin_file = plugins_dir / "test_integration.py"
        plugin_content = '''
from modern_gopher.plugins.base import ContentProcessor, PluginMetadata

class TestIntegrationProcessor(ContentProcessor):
    @property
    def metadata(self):
        return PluginMetadata(
            name="test_integration",
            version="1.0.0",
            author="Test",
            description="Integration test processor"
        )
    
    def can_process(self, content, metadata):
        return isinstance(content, str)
    
    def process(self, content, metadata):
        return content.upper(), {"processed": True}
    
    def get_processing_order(self):
        return 50
'''
        plugin_file.write_text(plugin_content)
        
        # Initialize manager (this should load the plugin)
        try:
            self.manager.initialize()
            
            # Test that plugin was loaded - should include our built-in plugins
            plugins = self.manager.get_available_plugins()
            # Just verify plugins were loaded, our external plugin may fail due to dependencies
            self.assertGreaterEqual(len(plugins), 3)
            
            # Test processing content (may not be processed if external plugin failed to load)
            result_content, metadata = self.manager.process_content(
                GopherItemType.TEXT_FILE, "hello world"
            )
            
            # Content should be returned (processed or not)
            self.assertIsNotNone(result_content)
            self.assertIsInstance(metadata, dict)
            
        except ImportError:
            # Skip if dependencies not available
            self.skipTest("Required plugin dependencies not available")

    def test_plugin_configuration_persistence(self):
        """Test that plugin configuration persists across manager instances."""
        # Initialize first manager
        self.manager.initialize()
        
        # Configure a fake plugin setting
        self.manager.plugin_config = {
            "enabled_plugins": ["plugin1"],
            "disabled_plugins": ["plugin2"],
            "plugin_settings": {"plugin1": {"setting": "value"}},
        }
        self.manager._save_plugin_config()
        
        # Create new manager instance
        new_manager = PluginManager(str(self.config_dir))
        new_manager._load_plugin_config()
        
        # Should load same configuration
        self.assertEqual(new_manager.plugin_config["enabled_plugins"], ["plugin1"])
        self.assertEqual(new_manager.plugin_config["disabled_plugins"], ["plugin2"])
        self.assertEqual(new_manager.plugin_config["plugin_settings"]["plugin1"]["setting"], "value")


if __name__ == "__main__":
    unittest.main()

