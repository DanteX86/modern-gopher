#!/usr/bin/env python3
"""
Test the plugin system implementation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from modern_gopher.plugins.manager import get_manager
from modern_gopher.plugins.base import ItemTypeHandler, ContentProcessor, PluginMetadata
from modern_gopher.core.types import GopherItemType

# Test basic plugin functionality
class TestItemHandler(ItemTypeHandler):
    @property
    def metadata(self):
        return PluginMetadata(
            name="test_handler",
            version="1.0.0",
            author="Test",
            description="Test item handler"
        )
    
    def can_handle(self, item_type, content):
        return item_type == GopherItemType.TEXT_FILE
    
    def process_content(self, item_type, content, item=None):
        return f"PROCESSED: {content}", {"test": True}
    
    def get_supported_types(self):
        return [GopherItemType.TEXT_FILE]

class TestContentProcessor(ContentProcessor):
    @property
    def metadata(self):
        return PluginMetadata(
            name="test_processor",
            version="1.0.0", 
            author="Test",
            description="Test content processor"
        )
    
    def process(self, content, metadata):
        return content.upper(), metadata

def test_plugins():
    print("Testing Modern Gopher Plugin System")
    print("===================================")
    
    # Get plugin manager
    manager = get_manager("/tmp/test_plugins")
    
    # Register test plugins
    handler = TestItemHandler()
    processor = TestContentProcessor()
    
    manager.registry.register_plugin(handler)
    manager.registry.register_plugin(processor)
    
    print(f"Registered {len(manager.registry.get_all_plugins())} plugins")
    
    # Test content processing
    content = "Hello, world!"
    processed_content, metadata = manager.process_content(
        GopherItemType.TEXT_FILE, content
    )
    
    print(f"Original: {content}")
    print(f"Processed: {processed_content}")
    print(f"Metadata: {metadata}")
    
    # Test plugin info
    info = manager.get_plugin_info()
    print(f"\nPlugin Info:")
    for name, details in info.items():
        print(f"  {name}: {details['description']}")
    
    print("\n✅ Plugin system test completed successfully!")

if __name__ == "__main__":
    test_plugins()

