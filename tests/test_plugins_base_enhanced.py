#!/usr/bin/env python3
"""
Enhanced tests for plugin base classes to improve coverage.
"""

from unittest.mock import Mock, patch

import pytest

from modern_gopher.plugins.base import (
    BasePlugin,
    ItemTypeHandler,
    ContentProcessor,
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


    def test_shutdown_success(self):
        """Test successful plugin shutdown."""
        plugin = self.create_test_plugin()
        plugin.initialize()
        
        result = plugin.shutdown()
        
        assert result is True
        assert plugin._initialized is False
        assert plugin.enabled is False


    def test_configure_success(self):
        """Test successful plugin configuration."""
        plugin = self.create_test_plugin({"initial": "value"})
        
        new_config = {"new_key": "new_value", "initial": "updated_value"}
        result = plugin.configure(new_config)
        
        assert result is True
        assert plugin.config["new_key"] == "new_value"
        assert plugin.config["initial"] == "updated_value"


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

    def test_abstract_methods_enforcement(self):
        """Test that abstract methods must be implemented."""
        with pytest.raises(TypeError):
            # This should fail because abstract methods aren't implemented
            class IncompleteHandler(ItemTypeHandler):
                @property
                def metadata(self):
                    return PluginMetadata(
                        name="incomplete",
                        version="1.0.0",
                        author="Test",
                        description="Incomplete"
                    )
            
            IncompleteHandler()


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

    def test_abstract_methods_enforcement(self):
        """Test that abstract methods must be implemented."""
        with pytest.raises(TypeError):
            # This should fail because abstract methods aren't implemented
            class IncompleteProcessor(ContentProcessor):
                @property
                def metadata(self):
                    return PluginMetadata(
                        name="incomplete",
                        version="1.0.0",
                        author="Test",
                        description="Incomplete"
                    )
            
            IncompleteProcessor()


if __name__ == "__main__":
    pytest.main([__file__])

