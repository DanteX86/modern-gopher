#!/usr/bin/env python3
"""
Complete tests for plugin base classes to achieve high coverage.
Tests all classes: PluginMetadata, BasePlugin, ItemTypeHandler, ContentProcessor, ProtocolExtension, PluginRegistry.
"""

from unittest.mock import Mock, patch, MagicMock, PropertyMock
from typing import Dict, Any, List, Optional, Tuple
import pytest

from modern_gopher.plugins.base import (
    BasePlugin,
    ItemTypeHandler,
    ContentProcessor,
    ProtocolExtension,
    PluginRegistry,
    PluginMetadata,
)
from modern_gopher.core.types import GopherItem, GopherItemType


class TestPluginMetadata:
    """Test the PluginMetadata dataclass."""

    def test_basic_creation(self):
        """Test basic metadata creation."""
        metadata = PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            author="Test Author",
            description="A test plugin"
        )
        
        assert metadata.name == "test_plugin"
        assert metadata.version == "1.0.0"
        assert metadata.author == "Test Author"
        assert metadata.description == "A test plugin"
        assert metadata.supported_item_types is None
        assert metadata.dependencies is None
        assert metadata.enabled is True

    def test_full_creation(self):
        """Test metadata creation with all fields."""
        metadata = PluginMetadata(
            name="full_plugin",
            version="2.1.0",
            author="Full Author",
            description="A full plugin",
            supported_item_types=["text", "image"],
            dependencies=["requests", "beautifulsoup4"],
            enabled=False
        )
        
        assert metadata.name == "full_plugin"
        assert metadata.version == "2.1.0"
        assert metadata.author == "Full Author"
        assert metadata.description == "A full plugin"
        assert metadata.supported_item_types == ["text", "image"]
        assert metadata.dependencies == ["requests", "beautifulsoup4"]
        assert metadata.enabled is False


class TestBasePlugin:
    """Test the BasePlugin abstract base class."""

    def create_test_plugin(self, config=None):
        """Create a test plugin implementation."""
        class TestPlugin(BasePlugin):
            @property
            def metadata(self):
                return PluginMetadata(
                    name="test_plugin",
                    version="1.0.0",
                    author="Test Author",
                    description="A test plugin"
                )
                
            def initialize(self):
                """Override to test error handling."""
                try:
                    result = super().initialize()
                    return result
                except Exception:
                    return False
                    
            def shutdown(self):
                """Override to test error handling."""
                try:
                    result = super().shutdown()
                    return result
                except Exception:
                    return False
                    
            def configure(self, config):
                """Override to test error handling."""
                try:
                    result = super().configure(config)
                    return result
                except Exception:
                    return False
        
        return TestPlugin(config)

    def test_init_default(self):
        """Test plugin initialization with defaults."""
        plugin = self.create_test_plugin()
        
        assert plugin.config == {}
        assert plugin._enabled is True
        assert plugin._initialized is False
        assert plugin.enabled is False  # Not initialized yet

    def test_init_with_config(self):
        """Test plugin initialization with config."""
        config = {"key1": "value1", "key2": "value2"}
        plugin = self.create_test_plugin(config)
        
        assert plugin.config == config
        assert plugin._enabled is True
        assert plugin._initialized is False

    def test_initialize_success(self):
        """Test successful plugin initialization."""
        plugin = self.create_test_plugin()
        
        result = plugin.initialize()
        
        assert result is True
        assert plugin._initialized is True
        assert plugin.enabled is True

    def test_initialize_with_logger_debug(self):
        """Test that initialization triggers debug logging."""
        with patch('modern_gopher.plugins.base.logger') as mock_logger:
            plugin = self.create_test_plugin()
            result = plugin.initialize()
            
            assert result is True
            assert plugin._initialized is True
            mock_logger.debug.assert_called()

    def test_shutdown_success(self):
        """Test successful plugin shutdown."""
        plugin = self.create_test_plugin()
        plugin.initialize()
        
        result = plugin.shutdown()
        
        assert result is True
        assert plugin._initialized is False
        assert plugin.enabled is False

    def test_shutdown_with_logger_debug(self):
        """Test that shutdown triggers debug logging."""
        with patch('modern_gopher.plugins.base.logger') as mock_logger:
            plugin = self.create_test_plugin()
            plugin.initialize()
            result = plugin.shutdown()
            
            assert result is True
            assert plugin._initialized is False
            mock_logger.debug.assert_called()

    def test_configure_success(self):
        """Test successful plugin configuration."""
        plugin = self.create_test_plugin({"initial": "value"})
        
        new_config = {"new_key": "new_value", "initial": "updated_value"}
        result = plugin.configure(new_config)
        
        assert result is True
        assert plugin.config["new_key"] == "new_value"
        assert plugin.config["initial"] == "updated_value"

    def test_configure_with_logger_debug(self):
        """Test that configuration triggers debug logging."""
        with patch('modern_gopher.plugins.base.logger') as mock_logger:
            plugin = self.create_test_plugin({"initial": "value"})
            result = plugin.configure({"new_key": "new_value"})
            
            assert result is True
            mock_logger.debug.assert_called()

    def test_enabled_property(self):
        """Test the enabled property logic."""
        plugin = self.create_test_plugin()
        
        # Not initialized, should be False
        assert plugin.enabled is False
        
        # Initialize
        plugin.initialize()
        assert plugin.enabled is True
        
        # Disable
        plugin.enabled = False
        assert plugin._enabled is False
        assert plugin.enabled is False
        
        # Re-enable
        plugin.enabled = True
        assert plugin._enabled is True
        assert plugin.enabled is True
        
        # Shutdown
        plugin.shutdown()
        assert plugin.enabled is False

    def test_get_priority_default(self):
        """Test default priority value."""
        plugin = self.create_test_plugin()
        assert plugin.get_priority() == 50

    def test_get_priority_custom(self):
        """Test custom priority value."""
        class CustomPriorityPlugin(BasePlugin):
            @property
            def metadata(self):
                return PluginMetadata(
                    name="custom_priority_plugin",
                    version="1.0.0",
                    author="Test Author",
                    description="A plugin with custom priority"
                )
                
            def get_priority(self):
                return 75
        
        plugin = CustomPriorityPlugin()
        assert plugin.get_priority() == 75



class TestItemTypeHandler:
    """Test the ItemTypeHandler abstract base class."""

    def create_test_handler(self, config=None):
        """Create a test item type handler implementation."""
        class TestHandler(ItemTypeHandler):
            @property
            def metadata(self):
                return PluginMetadata(
                    name="test_handler",
                    version="1.0.0",
                    author="Test Author",
                    description="A test handler"
                )
            
            def get_supported_types(self):
                return [GopherItemType.TEXT_FILE, GopherItemType.HTML]
            
            def can_handle(self, item_type, content):
                return item_type in self.get_supported_types()
            
            def process_content(self, item_type, content, item=None):
                processed = f"Processed: {content}"
                metadata = {"processed": True, "original_type": item_type}
                return processed, metadata
        
        return TestHandler(config)

    def test_handler_inheritance(self):
        """Test that handler inherits from BasePlugin."""
        handler = self.create_test_handler()
        assert isinstance(handler, BasePlugin)
        assert isinstance(handler, ItemTypeHandler)

    def test_get_supported_types(self):
        """Test getting supported types."""
        handler = self.create_test_handler()
        types = handler.get_supported_types()
        
        assert GopherItemType.TEXT_FILE in types
        assert GopherItemType.HTML in types

    def test_can_handle(self):
        """Test can_handle method."""
        handler = self.create_test_handler()
        
        assert handler.can_handle(GopherItemType.TEXT_FILE, "test content") is True
        assert handler.can_handle(GopherItemType.HTML, "test content") is True
        assert handler.can_handle(GopherItemType.DIRECTORY, "test content") is False

    def test_process_content_with_item(self):
        """Test processing content with item context."""
        handler = self.create_test_handler()
        item = GopherItem(
            GopherItemType.TEXT_FILE,
            "Test File",
            "/test.txt",
            "example.com",
            70
        )
        
        processed, metadata = handler.process_content(
            GopherItemType.TEXT_FILE,
            "test content",
            item
        )
        
        assert processed == "Processed: test content"
        assert metadata["processed"] is True
        assert metadata["original_type"] == GopherItemType.TEXT_FILE

    def test_process_content_without_item(self):
        """Test processing content without item context."""
        handler = self.create_test_handler()
        
        processed, metadata = handler.process_content(
            GopherItemType.HTML,
            "html content"
        )
        
        assert processed == "Processed: html content"
        assert metadata["processed"] is True
        assert metadata["original_type"] == GopherItemType.HTML


class TestContentProcessor:
    """Test the ContentProcessor abstract base class."""

    def create_test_processor(self, config=None):
        """Create a test content processor implementation."""
        class TestProcessor(ContentProcessor):
            @property
            def metadata(self):
                return PluginMetadata(
                    name="test_processor",
                    version="1.0.0",
                    author="Test Author",
                    description="A test processor"
                )
            
            def can_process(self, content, metadata):
                return isinstance(content, str) and "processable" in content
            
            def process(self, content, metadata):
                processed = content.replace("processable", "processed")
                updated_metadata = metadata.copy()
                updated_metadata["processed_by"] = "test_processor"
                return processed, updated_metadata
        
        return TestProcessor(config)

    def test_processor_inheritance(self):
        """Test that processor inherits from BasePlugin."""
        processor = self.create_test_processor()
        assert isinstance(processor, BasePlugin)
        assert isinstance(processor, ContentProcessor)

    def test_can_process_true(self):
        """Test can_process returning True."""
        processor = self.create_test_processor()
        
        result = processor.can_process(
            "This is processable content",
            {"type": "text"}
        )
        
        assert result is True

    def test_can_process_false(self):
        """Test can_process returning False."""
        processor = self.create_test_processor()
        
        # Not a string
        result = processor.can_process(
            b"binary content",
            {"type": "binary"}
        )
        assert result is False
        
        # String but doesn't contain "processable"
        result = processor.can_process(
            "normal content",
            {"type": "text"}
        )
        assert result is False

    def test_process_content(self):
        """Test processing content."""
        processor = self.create_test_processor()
        
        content = "This content is processable and ready"
        metadata = {"type": "text", "size": len(content)}
        
        processed, updated_metadata = processor.process(content, metadata)
        
        assert processed == "This content is processed and ready"
        assert updated_metadata["type"] == "text"
        assert updated_metadata["size"] == len(content)  # Original metadata preserved
        assert updated_metadata["processed_by"] == "test_processor"

    def test_process_metadata_immutability(self):
        """Test that original metadata is not modified."""
        processor = self.create_test_processor()
        
        content = "processable content"
        original_metadata = {"type": "text"}
        
        processed, updated_metadata = processor.process(content, original_metadata)
        
        # Original metadata should be unchanged
        assert "processed_by" not in original_metadata
        assert "processed_by" in updated_metadata


class TestProtocolExtension:
    """Test the ProtocolExtension abstract base class."""

    def create_test_extension(self, config=None):
        """Create a test protocol extension implementation."""
        class TestExtension(ProtocolExtension):
            @property
            def metadata(self):
                return PluginMetadata(
                    name="test_extension",
                    version="1.0.0",
                    author="Test Author",
                    description="A test protocol extension"
                )
            
            def get_protocol_schemes(self):
                return ["gopher", "gophers"]
            
            def can_handle_url(self, url):
                return url.startswith(("gopher://", "gophers://"))
            
            def process_request(self, url, headers=None):
                response_data = f"Response for {url}".encode()
                response_metadata = {
                    "url": url,
                    "headers": headers or {},
                    "status": "success"
                }
                return response_data, response_metadata
        
        return TestExtension(config)

    def test_extension_inheritance(self):
        """Test that extension inherits from BasePlugin."""
        extension = self.create_test_extension()
        assert isinstance(extension, BasePlugin)
        assert isinstance(extension, ProtocolExtension)

    def test_get_protocol_schemes(self):
        """Test getting supported protocol schemes."""
        extension = self.create_test_extension()
        schemes = extension.get_protocol_schemes()
        
        assert "gopher" in schemes
        assert "gophers" in schemes

    def test_can_handle_url_true(self):
        """Test can_handle_url returning True."""
        extension = self.create_test_extension()
        
        assert extension.can_handle_url("gopher://example.com/1test") is True
        assert extension.can_handle_url("gophers://secure.example.com/0menu") is True

    def test_can_handle_url_false(self):
        """Test can_handle_url returning False."""
        extension = self.create_test_extension()
        
        assert extension.can_handle_url("http://example.com") is False
        assert extension.can_handle_url("ftp://example.com") is False

    def test_process_request_without_headers(self):
        """Test processing a request without headers."""
        extension = self.create_test_extension()
        
        url = "gopher://example.com/1test"
        response_data, response_metadata = extension.process_request(url)
        
        assert response_data == b"Response for gopher://example.com/1test"
        assert response_metadata["url"] == url
        assert response_metadata["headers"] == {}
        assert response_metadata["status"] == "success"

    def test_process_request_with_headers(self):
        """Test processing a request with headers."""
        extension = self.create_test_extension()
        
        url = "gophers://secure.example.com/0menu"
        headers = {"User-Agent": "modern-gopher/1.0", "Accept": "*/*"}
        response_data, response_metadata = extension.process_request(url, headers)
        
        assert response_data == b"Response for gophers://secure.example.com/0menu"
        assert response_metadata["url"] == url
        assert response_metadata["headers"] == headers
        assert response_metadata["status"] == "success"


class TestPluginRegistry:
    """Test the PluginRegistry class."""

    def create_test_item_handler(self, name="test_handler", priority=50):
        """Create a test item handler for registry testing."""
        class TestHandler(ItemTypeHandler):
            @property
            def metadata(self):
                return PluginMetadata(
                    name=name,
                    version="1.0.0",
                    author="Test Author",
                    description="A test handler"
                )
            
            def get_supported_types(self):
                return [GopherItemType.TEXT_FILE]
            
            def can_handle(self, item_type, content):
                return item_type in self.get_supported_types()
            
            def process_content(self, item_type, content, item=None):
                return content, {}
                
            def get_priority(self):
                return priority
        
        handler = TestHandler()
        handler.initialize()
        return handler

    def create_test_content_processor(self, name="test_processor", priority=50):
        """Create a test content processor for registry testing."""
        class TestProcessor(ContentProcessor):
            @property
            def metadata(self):
                return PluginMetadata(
                    name=name,
                    version="1.0.0",
                    author="Test Author",
                    description="A test processor"
                )
            
            def can_process(self, content, metadata):
                return True
            
            def process(self, content, metadata):
                return content, metadata
                
            def get_priority(self):
                return priority
        
        processor = TestProcessor()
        processor.initialize()
        return processor

    def create_test_protocol_extension(self, name="test_extension", priority=50):
        """Create a test protocol extension for registry testing."""
        class TestExtension(ProtocolExtension):
            @property
            def metadata(self):
                return PluginMetadata(
                    name=name,
                    version="1.0.0",
                    author="Test Author",
                    description="A test extension"
                )
            
            def get_protocol_schemes(self):
                return ["test"]
            
            def can_handle_url(self, url):
                return url.startswith("test://")
            
            def process_request(self, url, headers=None):
                return b"test response", {}
                
            def get_priority(self):
                return priority
        
        extension = TestExtension()
        extension.initialize()
        return extension

    def test_registry_initialization(self):
        """Test registry initialization."""
        registry = PluginRegistry()
        
        assert len(registry._item_handlers) == 0
        assert len(registry._content_processors) == 0
        assert len(registry._protocol_extensions) == 0
        assert len(registry._all_plugins) == 0

    def test_register_item_handler_success(self):
        """Test successful item handler registration."""
        registry = PluginRegistry()
        handler = self.create_test_item_handler()
        
        result = registry.register_plugin(handler)
        
        assert result is True
        assert len(registry._item_handlers) == 1
        assert handler in registry._item_handlers
        assert "test_handler" in registry._all_plugins

    def test_register_content_processor_success(self):
        """Test successful content processor registration."""
        registry = PluginRegistry()
        processor = self.create_test_content_processor()
        
        result = registry.register_plugin(processor)
        
        assert result is True
        assert len(registry._content_processors) == 1
        assert processor in registry._content_processors
        assert "test_processor" in registry._all_plugins

    def test_register_protocol_extension_success(self):
        """Test successful protocol extension registration."""
        registry = PluginRegistry()
        extension = self.create_test_protocol_extension()
        
        result = registry.register_plugin(extension)
        
        assert result is True
        assert len(registry._protocol_extensions) == 1
        assert extension in registry._protocol_extensions
        assert "test_extension" in registry._all_plugins

    def test_register_plugin_duplicate(self):
        """Test registering duplicate plugin."""
        registry = PluginRegistry()
        handler1 = self.create_test_item_handler("duplicate_handler")
        handler2 = self.create_test_item_handler("duplicate_handler")
        
        result1 = registry.register_plugin(handler1)
        result2 = registry.register_plugin(handler2)
        
        assert result1 is True
        assert result2 is False
        assert len(registry._item_handlers) == 1
        assert len(registry._all_plugins) == 1

    @patch('modern_gopher.plugins.base.logger')
    def test_register_plugin_exception(self, mock_logger):
        """Test plugin registration with exception."""
        registry = PluginRegistry()
        
        # Create a mock plugin that raises an exception when accessing metadata.name
        mock_plugin = Mock()
        # Make metadata.name raise an exception as a property access
        type(mock_plugin.metadata).name = PropertyMock(side_effect=Exception("Test exception"))
        
        result = registry.register_plugin(mock_plugin)
        
        assert result is False
        mock_logger.error.assert_called()

    def test_register_priority_sorting(self):
        """Test that plugins are sorted by priority."""
        registry = PluginRegistry()
        
        handler_low = self.create_test_item_handler("handler_low", priority=25)
        handler_high = self.create_test_item_handler("handler_high", priority=75)
        handler_medium = self.create_test_item_handler("handler_medium", priority=50)
        
        registry.register_plugin(handler_low)
        registry.register_plugin(handler_high)
        registry.register_plugin(handler_medium)
        
        # Should be sorted high to low priority
        assert registry._item_handlers[0] == handler_high
        assert registry._item_handlers[1] == handler_medium
        assert registry._item_handlers[2] == handler_low

    def test_unregister_plugin_success(self):
        """Test successful plugin unregistration."""
        registry = PluginRegistry()
        handler = self.create_test_item_handler()
        
        registry.register_plugin(handler)
        result = registry.unregister_plugin("test_handler")
        
        assert result is True
        assert len(registry._item_handlers) == 0
        assert "test_handler" not in registry._all_plugins

    def test_unregister_plugin_not_found(self):
        """Test unregistering non-existent plugin."""
        registry = PluginRegistry()
        
        result = registry.unregister_plugin("nonexistent_plugin")
        
        assert result is False

    @patch('modern_gopher.plugins.base.logger')
    def test_unregister_plugin_exception(self, mock_logger):
        """Test plugin unregistration with exception."""
        registry = PluginRegistry()
        
        # Create a mock plugin that raises an exception during shutdown
        mock_plugin = Mock()
        mock_plugin.shutdown.side_effect = Exception("Shutdown failed")
        registry._all_plugins["failing_plugin"] = mock_plugin
        
        result = registry.unregister_plugin("failing_plugin")
        
        assert result is False
        mock_logger.error.assert_called()

    def test_get_item_handlers(self):
        """Test getting item handlers by type."""
        registry = PluginRegistry()
        handler = self.create_test_item_handler()
        
        registry.register_plugin(handler)
        handlers = registry.get_item_handlers(GopherItemType.TEXT_FILE)
        
        assert len(handlers) == 1
        assert handler in handlers

    def test_get_item_handlers_disabled(self):
        """Test that disabled handlers are not returned."""
        registry = PluginRegistry()
        handler = self.create_test_item_handler()
        handler.enabled = False
        
        registry.register_plugin(handler)
        handlers = registry.get_item_handlers(GopherItemType.TEXT_FILE)
        
        assert len(handlers) == 0

    def test_get_content_processors(self):
        """Test getting enabled content processors."""
        registry = PluginRegistry()
        processor = self.create_test_content_processor()
        
        registry.register_plugin(processor)
        processors = registry.get_content_processors()
        
        assert len(processors) == 1
        assert processor in processors

    def test_get_content_processors_disabled(self):
        """Test that disabled processors are not returned."""
        registry = PluginRegistry()
        processor = self.create_test_content_processor()
        processor.enabled = False
        
        registry.register_plugin(processor)
        processors = registry.get_content_processors()
        
        assert len(processors) == 0

    def test_get_protocol_extensions(self):
        """Test getting protocol extensions by scheme."""
        registry = PluginRegistry()
        extension = self.create_test_protocol_extension()
        
        registry.register_plugin(extension)
        extensions = registry.get_protocol_extensions("test")
        
        assert len(extensions) == 1
        assert extension in extensions

    def test_get_protocol_extensions_disabled(self):
        """Test that disabled extensions are not returned."""
        registry = PluginRegistry()
        extension = self.create_test_protocol_extension()
        extension.enabled = False
        
        registry.register_plugin(extension)
        extensions = registry.get_protocol_extensions("test")
        
        assert len(extensions) == 0

    def test_get_plugin(self):
        """Test getting plugin by name."""
        registry = PluginRegistry()
        handler = self.create_test_item_handler()
        
        registry.register_plugin(handler)
        retrieved = registry.get_plugin("test_handler")
        
        assert retrieved == handler

    def test_get_plugin_not_found(self):
        """Test getting non-existent plugin."""
        registry = PluginRegistry()
        
        retrieved = registry.get_plugin("nonexistent")
        
        assert retrieved is None

    def test_get_all_plugins(self):
        """Test getting all plugins."""
        registry = PluginRegistry()
        handler = self.create_test_item_handler()
        processor = self.create_test_content_processor()
        
        registry.register_plugin(handler)
        registry.register_plugin(processor)
        
        all_plugins = registry.get_all_plugins()
        
        assert len(all_plugins) == 2
        assert "test_handler" in all_plugins
        assert "test_processor" in all_plugins
        assert all_plugins["test_handler"] == handler
        assert all_plugins["test_processor"] == processor

    def test_get_all_plugins_is_copy(self):
        """Test that get_all_plugins returns a copy."""
        registry = PluginRegistry()
        handler = self.create_test_item_handler()
        
        registry.register_plugin(handler)
        all_plugins = registry.get_all_plugins()
        
        # Modify the returned dict
        all_plugins["new_plugin"] = Mock()
        
        # Original registry should be unchanged
        assert "new_plugin" not in registry._all_plugins

    def test_enable_plugin_success(self):
        """Test enabling a plugin."""
        registry = PluginRegistry()
        handler = self.create_test_item_handler()
        handler.enabled = False
        
        registry.register_plugin(handler)
        result = registry.enable_plugin("test_handler")
        
        assert result is True
        assert handler.enabled is True

    def test_enable_plugin_not_found(self):
        """Test enabling non-existent plugin."""
        registry = PluginRegistry()
        
        result = registry.enable_plugin("nonexistent")
        
        assert result is False

    def test_disable_plugin_success(self):
        """Test disabling a plugin."""
        registry = PluginRegistry()
        handler = self.create_test_item_handler()
        
        registry.register_plugin(handler)
        result = registry.disable_plugin("test_handler")
        
        assert result is True
        assert handler.enabled is False

    def test_disable_plugin_not_found(self):
        """Test disabling non-existent plugin."""
        registry = PluginRegistry()
        
        result = registry.disable_plugin("nonexistent")
        
        assert result is False

    def test_unregister_content_processor(self):
        """Test unregistering a content processor."""
        registry = PluginRegistry()
        processor = self.create_test_content_processor()
        
        registry.register_plugin(processor)
        assert len(registry._content_processors) == 1
        
        result = registry.unregister_plugin("test_processor")
        
        assert result is True
        assert len(registry._content_processors) == 0
        assert "test_processor" not in registry._all_plugins

    def test_unregister_protocol_extension(self):
        """Test unregistering a protocol extension."""
        registry = PluginRegistry()
        extension = self.create_test_protocol_extension()
        
        registry.register_plugin(extension)
        assert len(registry._protocol_extensions) == 1
        
        result = registry.unregister_plugin("test_extension")
        
        assert result is True
        assert len(registry._protocol_extensions) == 0
        assert "test_extension" not in registry._all_plugins


if __name__ == "__main__":
    pytest.main([__file__])

