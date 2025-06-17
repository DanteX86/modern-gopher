"""
Plugin registry for managing loaded plugins.

This module provides the central registry where plugins are registered
and can be discovered by the plugin manager.
"""

from typing import Dict, List, Optional, Type, Any
from collections import defaultdict
import logging
from .base import BasePlugin, ItemTypeHandler, ContentProcessor, ProtocolExtension
from modern_gopher.core.types import GopherItemType

logger = logging.getLogger(__name__)


class PluginRegistry:
    """Central registry for all plugins."""
    
    def __init__(self):
        self._plugins: Dict[str, BasePlugin] = {}
        self._item_handlers: Dict[GopherItemType, List[ItemTypeHandler]] = defaultdict(list)
        self._content_processors: List[ContentProcessor] = []
        self._protocol_extensions: List[ProtocolExtension] = []
        self._plugin_types: Dict[str, Type[BasePlugin]] = {}
    
    def register_plugin(self, plugin: BasePlugin) -> None:
        """Register a plugin instance."""
        if not isinstance(plugin, BasePlugin):
            raise TypeError(f"Plugin must inherit from BasePlugin, got {type(plugin)}")
        
        plugin_name = plugin.metadata.name
        
        if plugin_name in self._plugins:
            logger.warning(f"Plugin '{plugin_name}' is already registered, replacing")
        
        # Register the plugin
        self._plugins[plugin_name] = plugin
        self._plugin_types[plugin_name] = type(plugin)
        
        # Register in specialized collections based on type
        if isinstance(plugin, ItemTypeHandler):
            self._register_item_handler(plugin)
        
        if isinstance(plugin, ContentProcessor):
            self._register_content_processor(plugin)
        
        if isinstance(plugin, ProtocolExtension):
            self._register_protocol_extension(plugin)
        
        logger.info(f"Registered plugin: {plugin_name} v{plugin.metadata.version}")
    
    def unregister_plugin(self, plugin_name: str) -> bool:
        """Unregister a plugin by name."""
        if plugin_name not in self._plugins:
            return False
        
        plugin = self._plugins[plugin_name]
        
        # Remove from specialized collections
        if isinstance(plugin, ItemTypeHandler):
            self._unregister_item_handler(plugin)
        
        if isinstance(plugin, ContentProcessor):
            try:
                self._content_processors.remove(plugin)
            except ValueError:
                pass
        
        if isinstance(plugin, ProtocolExtension):
            try:
                self._protocol_extensions.remove(plugin)
            except ValueError:
                pass
        
        # Clean up plugin
        try:
            plugin.cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up plugin {plugin_name}: {e}")
        
        # Remove from main registry
        del self._plugins[plugin_name]
        del self._plugin_types[plugin_name]
        
        logger.info(f"Unregistered plugin: {plugin_name}")
        return True
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get a plugin by name."""
        return self._plugins.get(plugin_name)
    
    def get_all_plugins(self) -> Dict[str, BasePlugin]:
        """Get all registered plugins."""
        return self._plugins.copy()
    
    def get_enabled_plugins(self) -> Dict[str, BasePlugin]:
        """Get all enabled plugins."""
        return {name: plugin for name, plugin in self._plugins.items() if plugin.enabled}
    
    def get_item_handlers(self, item_type: GopherItemType) -> List[ItemTypeHandler]:
        """Get all handlers for a specific item type, sorted by priority."""
        handlers = [h for h in self._item_handlers[item_type] if h.enabled]
        return sorted(handlers, key=lambda h: h.get_priority(), reverse=True)
    
    def get_all_item_handlers(self) -> List[ItemTypeHandler]:
        """Get all item type handlers."""
        all_handlers = []
        for handlers in self._item_handlers.values():
            all_handlers.extend(h for h in handlers if h.enabled)
        return all_handlers
    
    def get_content_processors(self) -> List[ContentProcessor]:
        """Get all content processors, sorted by processing order."""
        processors = [p for p in self._content_processors if p.enabled]
        return sorted(processors, key=lambda p: p.get_processing_order())
    
    def get_protocol_extensions(self) -> List[ProtocolExtension]:
        """Get all protocol extensions."""
        return [e for e in self._protocol_extensions if e.enabled]
    
    def _register_item_handler(self, handler: ItemTypeHandler) -> None:
        """Register an item type handler."""
        supported_types = handler.get_supported_types()
        if not supported_types:
            # If no specific types, register for all types
            # This allows handlers to check can_handle() for each type
            for item_type in GopherItemType:
                self._item_handlers[item_type].append(handler)
        else:
            for item_type in supported_types:
                self._item_handlers[item_type].append(handler)
    
    def _unregister_item_handler(self, handler: ItemTypeHandler) -> None:
        """Unregister an item type handler."""
        for handlers in self._item_handlers.values():
            try:
                handlers.remove(handler)
            except ValueError:
                pass
    
    def _register_content_processor(self, processor: ContentProcessor) -> None:
        """Register a content processor."""
        self._content_processors.append(processor)
    
    def _register_protocol_extension(self, extension: ProtocolExtension) -> None:
        """Register a protocol extension."""
        self._protocol_extensions.append(extension)
    
    def clear(self) -> None:
        """Clear all plugins from the registry."""
        # Clean up all plugins
        for plugin in self._plugins.values():
            try:
                plugin.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up plugin {plugin.metadata.name}: {e}")
        
        # Clear all collections
        self._plugins.clear()
        self._item_handlers.clear()
        self._content_processors.clear()
        self._protocol_extensions.clear()
        self._plugin_types.clear()
        
        logger.info("Cleared all plugins from registry")


# Global plugin registry instance
_registry = PluginRegistry()


def get_registry() -> PluginRegistry:
    """Get the global plugin registry."""
    return _registry

