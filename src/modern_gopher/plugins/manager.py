"""
Plugin manager for loading, configuring, and managing plugins.

This module provides the main interface for working with plugins,
handling loading from files, dependency resolution, and lifecycle management.
"""

import os
import sys
import json
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
import logging

from .base import BasePlugin, ItemTypeHandler, ContentProcessor, ProtocolExtension
from .registry import get_registry, PluginRegistry
from modern_gopher.core.types import GopherItemType, GopherItem

logger = logging.getLogger(__name__)


class PluginManager:
    """Main plugin manager for Modern Gopher."""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir or os.path.expanduser("~/.config/modern-gopher"))
        self.plugins_dir = self.config_dir / "plugins"
        self.config_file = self.config_dir / "plugins.json"
        self.registry = get_registry()
        self._config = {}
        
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
    
    def load_configuration(self) -> None:
        """Load plugin configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self._config = json.load(f)
                logger.info(f"Loaded plugin configuration from {self.config_file}")
            except Exception as e:
                logger.error(f"Failed to load plugin configuration: {e}")
                self._config = {}
        else:
            self._config = self._get_default_config()
            self.save_configuration()
    
    def save_configuration(self) -> None:
        """Save plugin configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
            logger.info(f"Saved plugin configuration to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save plugin configuration: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default plugin configuration."""
        return {
            "enabled_plugins": [],
            "plugin_settings": {},
            "auto_load_plugins": True,
            "plugin_paths": [str(self.plugins_dir)]
        }
    
    def initialize(self) -> None:
        """Initialize the plugin manager."""
        self.load_configuration()
        
        if self._config.get("auto_load_plugins", True):
            self.discover_and_load_plugins()
        
        self._configure_plugins()
        logger.info("Plugin manager initialized")
    
    def discover_and_load_plugins(self) -> None:
        """Discover and load plugins from configured paths."""
        plugin_paths = self._config.get("plugin_paths", [str(self.plugins_dir)])
        
        for path_str in plugin_paths:
            path = Path(path_str)
            if path.exists() and path.is_dir():
                self._discover_plugins_in_directory(path)
    
    def _discover_plugins_in_directory(self, directory: Path) -> None:
        """Discover plugins in a specific directory."""
        logger.info(f"Discovering plugins in {directory}")
        
        for item in directory.iterdir():
            if item.is_file() and item.suffix == '.py':
                self._load_plugin_file(item)
            elif item.is_dir() and (item / '__init__.py').exists():
                self._load_plugin_package(item)
    
    def _load_plugin_file(self, plugin_file: Path) -> None:
        """Load a plugin from a Python file."""
        try:
            spec = importlib.util.spec_from_file_location(
                plugin_file.stem, plugin_file
            )
            if spec is None or spec.loader is None:
                logger.error(f"Could not load spec for {plugin_file}")
                return
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for plugin classes in the module
            self._register_plugins_from_module(module, plugin_file.name)
            
        except Exception as e:
            logger.error(f"Failed to load plugin file {plugin_file}: {e}")
    
    def _load_plugin_package(self, plugin_dir: Path) -> None:
        """Load a plugin from a Python package directory."""
        try:
            # Add the parent directory to sys.path temporarily
            parent_dir = str(plugin_dir.parent)
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
                remove_from_path = True
            else:
                remove_from_path = False
            
            try:
                module = importlib.import_module(plugin_dir.name)
                self._register_plugins_from_module(module, plugin_dir.name)
            finally:
                if remove_from_path:
                    sys.path.remove(parent_dir)
                    
        except Exception as e:
            logger.error(f"Failed to load plugin package {plugin_dir}: {e}")
    
    def _register_plugins_from_module(self, module: Any, module_name: str) -> None:
        """Register all plugins found in a module."""
        plugin_count = 0
        
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            
            if (isinstance(attr, type) and 
                issubclass(attr, BasePlugin) and 
                attr is not BasePlugin and
                attr is not ItemTypeHandler and
                attr is not ContentProcessor and
                attr is not ProtocolExtension):
                
                try:
                    plugin_instance = attr()
                    self.registry.register_plugin(plugin_instance)
                    plugin_count += 1
                except Exception as e:
                    logger.error(f"Failed to instantiate plugin {attr_name} from {module_name}: {e}")
        
        if plugin_count > 0:
            logger.info(f"Loaded {plugin_count} plugin(s) from {module_name}")
    
    def _configure_plugins(self) -> None:
        """Configure all registered plugins with their settings."""
        plugin_settings = self._config.get("plugin_settings", {})
        enabled_plugins = set(self._config.get("enabled_plugins", []))
        
        for plugin_name, plugin in self.registry.get_all_plugins().items():
            # Configure plugin if settings exist
            if plugin_name in plugin_settings:
                try:
                    plugin.configure(plugin_settings[plugin_name])
                except Exception as e:
                    logger.error(f"Failed to configure plugin {plugin_name}: {e}")
            
            # Enable/disable plugin based on configuration
            if enabled_plugins:
                if plugin_name in enabled_plugins:
                    plugin.enable()
                else:
                    plugin.disable()
            else:
                # If no explicit enabled list, enable all plugins by default
                plugin.enable()
            
            # Initialize plugin
            try:
                plugin.initialize()
            except Exception as e:
                logger.error(f"Failed to initialize plugin {plugin_name}: {e}")
    
    def process_content(self, item_type: GopherItemType, content: Union[str, bytes], 
                      item: Optional[GopherItem] = None) -> Tuple[str, Dict[str, Any]]:
        """Process content using registered plugins."""
        # Convert bytes to string if needed
        if isinstance(content, bytes):
            try:
                content = content.decode('utf-8')
            except UnicodeDecodeError:
                content = content.decode('latin-1')
        
        metadata = {
            'item_type': item_type,
            'original_content': content,
            'processing_steps': []
        }
        
        if item:
            metadata.update({
                'selector': item.selector,
                'host': item.host,
                'port': item.port,
                'display_string': item.display_string
            })
        
        processed_content = content
        
        # First, try item type handlers
        handlers = self.registry.get_item_handlers(item_type)
        for handler in handlers:
            try:
                if handler.can_handle(item_type, processed_content):
                    processed_content, handler_metadata = handler.process_content(
                        item_type, processed_content, item
                    )
                    metadata.update(handler_metadata)
                    metadata['processing_steps'].append(f"ItemHandler: {handler.metadata.name}")
                    break  # Use only the first matching handler
            except Exception as e:
                logger.error(f"Error in item handler {handler.metadata.name}: {e}")
        
        # Then, apply content processors
        processors = self.registry.get_content_processors()
        for processor in processors:
            try:
                if processor.should_process(processed_content, metadata):
                    processed_content, metadata = processor.process(processed_content, metadata)
                    metadata['processing_steps'].append(f"ContentProcessor: {processor.metadata.name}")
            except Exception as e:
                logger.error(f"Error in content processor {processor.metadata.name}: {e}")
        
        return processed_content, metadata
    
    def get_plugin_info(self) -> Dict[str, Any]:
        """Get information about all registered plugins."""
        plugins_info = {}
        
        for plugin_name, plugin in self.registry.get_all_plugins().items():
            plugins_info[plugin_name] = {
                'name': plugin.metadata.name,
                'version': plugin.metadata.version,
                'author': plugin.metadata.author,
                'description': plugin.metadata.description,
                'enabled': plugin.enabled,
                'type': type(plugin).__name__,
                'dependencies': plugin.metadata.dependencies,
                'supported_item_types': plugin.metadata.supported_item_types
            }
        
        return plugins_info
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a specific plugin."""
        plugin = self.registry.get_plugin(plugin_name)
        if plugin:
            plugin.enable()
            
            # Update configuration
            enabled_plugins = set(self._config.get("enabled_plugins", []))
            enabled_plugins.add(plugin_name)
            self._config["enabled_plugins"] = list(enabled_plugins)
            self.save_configuration()
            
            logger.info(f"Enabled plugin: {plugin_name}")
            return True
        return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a specific plugin."""
        plugin = self.registry.get_plugin(plugin_name)
        if plugin:
            plugin.disable()
            
            # Update configuration
            enabled_plugins = set(self._config.get("enabled_plugins", []))
            enabled_plugins.discard(plugin_name)
            self._config["enabled_plugins"] = list(enabled_plugins)
            self.save_configuration()
            
            logger.info(f"Disabled plugin: {plugin_name}")
            return True
        return False
    
    def configure_plugin(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """Configure a specific plugin."""
        plugin = self.registry.get_plugin(plugin_name)
        if plugin:
            try:
                plugin.configure(config)
                
                # Update configuration
                if "plugin_settings" not in self._config:
                    self._config["plugin_settings"] = {}
                self._config["plugin_settings"][plugin_name] = config
                self.save_configuration()
                
                logger.info(f"Configured plugin: {plugin_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to configure plugin {plugin_name}: {e}")
        return False
    
    def shutdown(self) -> None:
        """Shutdown the plugin manager and clean up all plugins."""
        self.registry.clear()
        logger.info("Plugin manager shutdown complete")


# Global plugin manager instance
_manager = None


def get_manager(config_dir: Optional[str] = None) -> PluginManager:
    """Get the global plugin manager instance."""
    global _manager
    if _manager is None:
        _manager = PluginManager(config_dir)
    return _manager

