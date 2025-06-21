#!/usr/bin/env python3
"""
Base plugin classes and interfaces for Modern Gopher.

This module provides the foundation for the plugin system, defining
abstract base classes for different types of plugins.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass

from modern_gopher.core.types import GopherItem, GopherItemType

logger = logging.getLogger(__name__)


@dataclass
class PluginMetadata:
    """Metadata for a plugin."""
    name: str
    version: str
    author: str
    description: str
    supported_item_types: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    enabled: bool = True


class BasePlugin(ABC):
    """Abstract base class for all Modern Gopher plugins."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the plugin.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self._enabled = True
        self._initialized = False
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass
    
    def initialize(self) -> bool:
        """
        Initialize the plugin.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self._initialized = True
            logger.debug(f"Plugin {self.metadata.name} initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize plugin {self.metadata.name}: {e}")
            return False
    
    def shutdown(self) -> bool:
        """
        Shutdown the plugin and clean up resources.
        
        Returns:
            True if shutdown successful, False otherwise
        """
        try:
            self._initialized = False
            logger.debug(f"Plugin {self.metadata.name} shut down")
            return True
        except Exception as e:
            logger.error(f"Failed to shutdown plugin {self.metadata.name}: {e}")
            return False
    
    def configure(self, config: Dict[str, Any]) -> bool:
        """
        Configure the plugin with new settings.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if configuration successful, False otherwise
        """
        try:
            self.config.update(config)
            logger.debug(f"Plugin {self.metadata.name} configured")
            return True
        except Exception as e:
            logger.error(f"Failed to configure plugin {self.metadata.name}: {e}")
            return False
    
    @property
    def enabled(self) -> bool:
        """Check if plugin is enabled."""
        return self._enabled and self._initialized
    
    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Enable or disable the plugin."""
        self._enabled = value
    
    def get_priority(self) -> int:
        """
        Get plugin execution priority.
        
        Returns:
            Priority value (higher = executed first)
        """
        return 50  # Default priority


class ItemTypeHandler(BasePlugin):
    """Base class for plugins that handle specific Gopher item types."""
    
    @abstractmethod
    def get_supported_types(self) -> List[GopherItemType]:
        """
        Get list of supported Gopher item types.
        
        Returns:
            List of GopherItemType values this handler supports
        """
        pass
    
    @abstractmethod
    def can_handle(self, item_type: GopherItemType, content: Union[str, bytes]) -> bool:
        """
        Check if this handler can process the given content.
        
        Args:
            item_type: The Gopher item type
            content: The content to check
            
        Returns:
            True if this handler can process the content
        """
        pass
    
    @abstractmethod
    def process_content(
        self,
        item_type: GopherItemType,
        content: Union[str, bytes],
        item: Optional[GopherItem] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Process content and return transformed content with metadata.
        
        Args:
            item_type: The Gopher item type
            content: The content to process
            item: Optional GopherItem for additional context
            
        Returns:
            Tuple of (processed_content, metadata)
        """
        pass


class ContentProcessor(BasePlugin):
    """Base class for plugins that process content regardless of item type."""
    
    @abstractmethod
    def can_process(self, content: Union[str, bytes], metadata: Dict[str, Any]) -> bool:
        """
        Check if this processor can handle the given content.
        
        Args:
            content: The content to check
            metadata: Content metadata
            
        Returns:
            True if this processor can handle the content
        """
        pass
    
    @abstractmethod
    def process(
        self,
        content: Union[str, bytes],
        metadata: Dict[str, Any]
    ) -> Tuple[Union[str, bytes], Dict[str, Any]]:
        """
        Process content and return transformed content with updated metadata.
        
        Args:
            content: The content to process
            metadata: Content metadata
            
        Returns:
            Tuple of (processed_content, updated_metadata)
        """
        pass


class ProtocolExtension(BasePlugin):
    """Base class for plugins that extend the Gopher protocol."""
    
    @abstractmethod
    def get_protocol_schemes(self) -> List[str]:
        """
        Get list of protocol schemes this extension handles.
        
        Returns:
            List of protocol schemes (e.g., ['gopher', 'gophers'])
        """
        pass
    
    @abstractmethod
    def can_handle_url(self, url: str) -> bool:
        """
        Check if this extension can handle the given URL.
        
        Args:
            url: The URL to check
            
        Returns:
            True if this extension can handle the URL
        """
        pass
    
    @abstractmethod
    def process_request(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None
    ) -> Tuple[bytes, Dict[str, Any]]:
        """
        Process a protocol request and return response data.
        
        Args:
            url: The URL to request
            headers: Optional headers
            
        Returns:
            Tuple of (response_data, response_metadata)
        """
        pass


class PluginRegistry:
    """Registry for managing plugins."""
    
    def __init__(self):
        """Initialize the plugin registry."""
        self._item_handlers: List[ItemTypeHandler] = []
        self._content_processors: List[ContentProcessor] = []
        self._protocol_extensions: List[ProtocolExtension] = []
        self._all_plugins: Dict[str, BasePlugin] = {}
    
    def register_plugin(self, plugin: BasePlugin) -> bool:
        """
        Register a plugin with the registry.
        
        Args:
            plugin: The plugin to register
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            plugin_name = plugin.metadata.name
            
            if plugin_name in self._all_plugins:
                logger.warning(f"Plugin {plugin_name} already registered")
                return False
            
            # Add to appropriate collection
            if isinstance(plugin, ItemTypeHandler):
                self._item_handlers.append(plugin)
                self._item_handlers.sort(key=lambda p: p.get_priority(), reverse=True)
            
            if isinstance(plugin, ContentProcessor):
                self._content_processors.append(plugin)
                self._content_processors.sort(key=lambda p: p.get_priority(), reverse=True)
            
            if isinstance(plugin, ProtocolExtension):
                self._protocol_extensions.append(plugin)
                self._protocol_extensions.sort(key=lambda p: p.get_priority(), reverse=True)
            
            # Add to main registry
            self._all_plugins[plugin_name] = plugin
            
            logger.info(f"Registered plugin: {plugin_name} v{plugin.metadata.version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register plugin: {e}")
            return False
    
    def unregister_plugin(self, plugin_name: str) -> bool:
        """
        Unregister a plugin from the registry.
        
        Args:
            plugin_name: Name of the plugin to unregister
            
        Returns:
            True if unregistration successful, False otherwise
        """
        try:
            if plugin_name not in self._all_plugins:
                logger.warning(f"Plugin {plugin_name} not found")
                return False
            
            plugin = self._all_plugins[plugin_name]
            
            # Remove from collections
            if isinstance(plugin, ItemTypeHandler):
                self._item_handlers.remove(plugin)
            
            if isinstance(plugin, ContentProcessor):
                self._content_processors.remove(plugin)
            
            if isinstance(plugin, ProtocolExtension):
                self._protocol_extensions.remove(plugin)
            
            # Remove from main registry
            del self._all_plugins[plugin_name]
            
            # Shutdown plugin
            plugin.shutdown()
            
            logger.info(f"Unregistered plugin: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister plugin {plugin_name}: {e}")
            return False
    
    def get_item_handlers(self, item_type: GopherItemType) -> List[ItemTypeHandler]:
        """
        Get item handlers that support the given item type.
        
        Args:
            item_type: The Gopher item type
            
        Returns:
            List of matching item handlers
        """
        return [
            handler for handler in self._item_handlers
            if handler.enabled and item_type in handler.get_supported_types()
        ]
    
    def get_content_processors(self) -> List[ContentProcessor]:
        """
        Get all enabled content processors.
        
        Returns:
            List of enabled content processors
        """
        return [processor for processor in self._content_processors if processor.enabled]
    
    def get_protocol_extensions(self, scheme: str) -> List[ProtocolExtension]:
        """
        Get protocol extensions that support the given scheme.
        
        Args:
            scheme: The protocol scheme
            
        Returns:
            List of matching protocol extensions
        """
        return [
            ext for ext in self._protocol_extensions
            if ext.enabled and scheme in ext.get_protocol_schemes()
        ]
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """
        Get a plugin by name.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            The plugin instance or None if not found
        """
        return self._all_plugins.get(plugin_name)
    
    def get_all_plugins(self) -> Dict[str, BasePlugin]:
        """
        Get all registered plugins.
        
        Returns:
            Dictionary of plugin name to plugin instance
        """
        return self._all_plugins.copy()
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """
        Enable a plugin.
        
        Args:
            plugin_name: Name of the plugin to enable
            
        Returns:
            True if successful, False otherwise
        """
        plugin = self.get_plugin(plugin_name)
        if plugin:
            plugin.enabled = True
            return True
        return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """
        Disable a plugin.
        
        Args:
            plugin_name: Name of the plugin to disable
            
        Returns:
            True if successful, False otherwise
        """
        plugin = self.get_plugin(plugin_name)
        if plugin:
            plugin.enabled = False
            return True
        return False

