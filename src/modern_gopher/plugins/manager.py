#!/usr/bin/env python3
"""
Plugin manager for Modern Gopher.

This module provides a comprehensive plugin system for extending Modern Gopher's
functionality with custom content processors, item handlers, and protocol extensions.
"""

import importlib
import importlib.util
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from modern_gopher.core.types import GopherItem, GopherItemType

from .base import BasePlugin, ContentProcessor, ItemTypeHandler, PluginRegistry, ProtocolExtension

logger = logging.getLogger(__name__)


class PluginManager:
    """Comprehensive plugin manager for Modern Gopher."""

    def __init__(self, config_dir: str):
        """
        Initialize the plugin manager.

        Args:
            config_dir: Configuration directory path
        """
        self.config_dir = Path(config_dir)
        self.registry = PluginRegistry()
        self.initialized = False
        self.config_file = self.config_dir / "plugins.json"
        self.plugin_config: Dict[str, Any] = {}

    def initialize(self) -> None:
        """Initialize the plugin system."""
        try:
            # Ensure config directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)

            # Load plugin configuration
            self._load_plugin_config()

            # Load built-in plugins
            self._load_builtin_plugins()

            # Load external plugins
            self._load_external_plugins()

            self.initialized = True
            logger.info(
                f"Plugin system initialized with {len(self.registry.get_all_plugins())} plugins"
            )

        except Exception as e:
            logger.error(f"Failed to initialize plugin system: {e}")
            raise
    
    def _load_plugin_config(self) -> None:
        """Load plugin configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.plugin_config = json.load(f)
            else:
                # Create default config
                self.plugin_config = {
                    "enabled_plugins": [],
                    "disabled_plugins": [],
                    "plugin_settings": {}
                }
                self._save_plugin_config()
        except Exception as e:
            logger.error(f"Failed to load plugin config: {e}")
            self.plugin_config = {"enabled_plugins": [], "disabled_plugins": [], "plugin_settings": {}}
    
    def _save_plugin_config(self) -> None:
        """Save plugin configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.plugin_config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save plugin config: {e}")
    
    def _load_builtin_plugins(self) -> None:
        """Load built-in plugins."""
        try:
            # Import and register built-in plugins
            builtin_plugins = [
                "modern_gopher.plugins.builtin.markdown_processor",
                "modern_gopher.plugins.builtin.image_handler", 
                "modern_gopher.plugins.builtin.text_cleaner"
            ]
            
            for plugin_module in builtin_plugins:
                try:
                    module = importlib.import_module(plugin_module)
                    
                    # Look for plugin classes in the module
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, BasePlugin) and 
                            attr not in (BasePlugin, ItemTypeHandler, ContentProcessor, ProtocolExtension) and
                            not attr.__name__.startswith('_')):
                            
                            # Get plugin config
                            plugin_name = attr.__name__.lower()
                            plugin_config = self.plugin_config.get("plugin_settings", {}).get(plugin_name, {})
                            
                            # Create and register plugin
                            plugin_instance = attr(plugin_config)
                            plugin_instance.initialize()
                            
                            # Set enabled state from config
                            if plugin_name in self.plugin_config.get("disabled_plugins", []):
                                plugin_instance.enabled = False
                            
                            success = self.registry.register_plugin(plugin_instance)
                            if success:
                                logger.debug(f"Loaded built-in plugin: {plugin_name}")
                            
                except Exception as e:
                    logger.warning(f"Failed to load built-in plugin {plugin_module}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to load built-in plugins: {e}")
    
    def _load_external_plugins(self) -> None:
        """Load external plugins from plugins directory."""
        try:
            plugins_dir = self.config_dir / "plugins"
            if not plugins_dir.exists():
                plugins_dir.mkdir()
                return
            
            # Scan for Python files in plugins directory
            for plugin_file in plugins_dir.glob("*.py"):
                if plugin_file.name.startswith("_"):
                    continue
                    
                try:
                    # Load the plugin module
                    spec = importlib.util.spec_from_file_location(plugin_file.stem, plugin_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Register plugin classes
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, BasePlugin) and 
                            attr != BasePlugin):
                            
                            plugin_name = attr.__name__.lower()
                            plugin_config = self.plugin_config.get("plugin_settings", {}).get(plugin_name, {})
                            
                            plugin_instance = attr(plugin_config)
                            plugin_instance.initialize()
                            
                            if plugin_name in self.plugin_config.get("disabled_plugins", []):
                                plugin_instance.enabled = False
                            
                            success = self.registry.register_plugin(plugin_instance)
                            if success:
                                logger.info(f"Loaded external plugin: {plugin_name}")
                                
                except Exception as e:
                    logger.warning(f"Failed to load external plugin {plugin_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to load external plugins: {e}")

    def _load_plugin_config(self) -> None:
        """Load plugin configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r") as f:
                    self.plugin_config = json.load(f)
            else:
                # Create default config
                self.plugin_config = {
                    "enabled_plugins": [],
                    "disabled_plugins": [],
                    "plugin_settings": {},
                }
                self._save_plugin_config()
        except Exception as e:
            logger.error(f"Failed to load plugin config: {e}")
            self.plugin_config = {
                "enabled_plugins": [],
                "disabled_plugins": [],
                "plugin_settings": {},
            }

    def _save_plugin_config(self) -> None:
        """Save plugin configuration to file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.plugin_config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save plugin config: {e}")

    def _load_builtin_plugins(self) -> None:
        """Load built-in plugins."""
        try:
            # Import and register built-in plugins
            builtin_plugins = [
                "modern_gopher.plugins.builtin.markdown_processor",
                "modern_gopher.plugins.builtin.image_handler",
                "modern_gopher.plugins.builtin.text_cleaner",
            ]

            for plugin_module in builtin_plugins:
                try:
                    module = importlib.import_module(plugin_module)

                    # Look for plugin classes in the module
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (
                            isinstance(attr, type)
                            and issubclass(attr, BasePlugin)
                            and attr
                            not in (
                                BasePlugin,
                                ItemTypeHandler,
                                ContentProcessor,
                                ProtocolExtension,
                            )
                            and not attr.__name__.startswith("_")
                        ):

                            # Get plugin config
                            plugin_name = attr.__name__.lower()
                            plugin_config = self.plugin_config.get("plugin_settings", {}).get(
                                plugin_name, {}
                            )

                            # Create and register plugin
                            plugin_instance = attr(plugin_config)
                            plugin_instance.initialize()

                            # Set enabled state from config
                            if plugin_name in self.plugin_config.get("disabled_plugins", []):
                                plugin_instance.enabled = False

                            success = self.registry.register_plugin(plugin_instance)
                            if success:
                                logger.debug(f"Loaded built-in plugin: {plugin_name}")

                except Exception as e:
                    logger.warning(f"Failed to load built-in plugin {plugin_module}: {e}")

        except Exception as e:
            logger.error(f"Failed to load built-in plugins: {e}")

    def _load_external_plugins(self) -> None:
        """Load external plugins from plugins directory."""
        try:
            plugins_dir = self.config_dir / "plugins"
            if not plugins_dir.exists():
                plugins_dir.mkdir()
                return

            # Scan for Python files in plugins directory
            for plugin_file in plugins_dir.glob("*.py"):
                if plugin_file.name.startswith("_"):
                    continue

                try:
                    # Load the plugin module
                    spec = importlib.util.spec_from_file_location(plugin_file.stem, plugin_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Register plugin classes
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (
                            isinstance(attr, type)
                            and issubclass(attr, BasePlugin)
                            and attr != BasePlugin
                        ):

                            plugin_name = attr.__name__.lower()
                            plugin_config = self.plugin_config.get("plugin_settings", {}).get(
                                plugin_name, {}
                            )

                            plugin_instance = attr(plugin_config)
                            plugin_instance.initialize()

                            if plugin_name in self.plugin_config.get("disabled_plugins", []):
                                plugin_instance.enabled = False

                            success = self.registry.register_plugin(plugin_instance)
                            if success:
                                logger.info(f"Loaded external plugin: {plugin_name}")

                except Exception as e:
                    logger.warning(f"Failed to load external plugin {plugin_file}: {e}")

        except Exception as e:
            logger.error(f"Failed to load external plugins: {e}")

    def process_content(
        self,
        item_type: GopherItemType,
        content: Union[str, bytes],
        item: Optional[GopherItem] = None,
    ) -> Tuple[Union[str, bytes], Dict[str, Any]]:
        """
        Process content through available plugins.

        Args:
            item_type: The type of Gopher item
            content: The content to process
            item: Optional GopherItem for additional context

        Returns:
            Tuple of (processed_content, metadata)
        """
        if not self.initialized:
            return content, {}

        metadata = {
            "processing_steps": [],
            "original_size": len(content) if isinstance(content, (str, bytes)) else 0,
            "plugins_applied": [],
        }

        try:
            # First try item type handlers
            handlers = self.registry.get_item_handlers(item_type)
            for handler in handlers:
                if handler.can_handle(item_type, content):
                    try:
                        processed_content, handler_metadata = handler.process_content(
                            item_type, content, item
                        )
                        content = processed_content
                        metadata["processing_steps"].append(f"ItemHandler: {handler.metadata.name}")
                        metadata["plugins_applied"].append(handler.metadata.name)
                        metadata.update(handler_metadata)
                        logger.debug(f"Applied item handler: {handler.metadata.name}")
                        break  # Only use the first matching handler
                    except Exception as e:
                        logger.warning(f"Item handler {handler.metadata.name} failed: {e}")

            # Then apply content processors
            processors = self.registry.get_content_processors()
            for processor in processors:
                if processor.can_process(content, metadata):
                    try:
                        processed_content, updated_metadata = processor.process(content, metadata)
                        content = processed_content
                        metadata.update(updated_metadata)
                        metadata["processing_steps"].append(
                            f"ContentProcessor: {processor.metadata.name}"
                        )
                        metadata["plugins_applied"].append(processor.metadata.name)
                        logger.debug(f"Applied content processor: {processor.metadata.name}")
                    except Exception as e:
                        logger.warning(f"Content processor {processor.metadata.name} failed: {e}")

        except Exception as e:
            logger.error(f"Error in plugin processing pipeline: {e}")

        return content, metadata

    def get_plugin_info(self) -> Dict[str, Any]:
        """Get information about all registered plugins."""
        if not self.initialized:
            return {}

        plugins_info = {}
        for name, plugin in self.registry.get_all_plugins().items():
            plugins_info[name] = {
                "name": plugin.metadata.name,
                "version": plugin.metadata.version,
                "author": plugin.metadata.author,
                "description": plugin.metadata.description,
                "enabled": plugin.enabled,
                "type": type(plugin).__name__,
                "priority": plugin.get_priority(),
            }
            if hasattr(plugin, "get_supported_types"):
                plugins_info[name]["supported_types"] = [
                    t.value for t in plugin.get_supported_types()
                ]
        return plugins_info

    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a specific plugin."""
        if not self.initialized:
            return False

        success = self.registry.enable_plugin(plugin_name)
        if success:
            # Update config
            disabled = self.plugin_config.get("disabled_plugins", [])
            if plugin_name in disabled:
                disabled.remove(plugin_name)
                self.plugin_config["disabled_plugins"] = disabled
                self._save_plugin_config()
            logger.info(f"Enabled plugin: {plugin_name}")
        return success

    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a specific plugin."""
        if not self.initialized:
            return False

        success = self.registry.disable_plugin(plugin_name)
        if success:
            # Update config
            disabled = self.plugin_config.get("disabled_plugins", [])
            if plugin_name not in disabled:
                disabled.append(plugin_name)
                self.plugin_config["disabled_plugins"] = disabled
                self._save_plugin_config()
            logger.info(f"Disabled plugin: {plugin_name}")
        return success

    def configure_plugin(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """Configure a specific plugin."""
        if not self.initialized:
            return False

        plugin = self.registry.get_plugin(plugin_name)
        if plugin:
            success = plugin.configure(config)
            if success:
                # Save config
                settings = self.plugin_config.get("plugin_settings", {})
                settings[plugin_name] = config
                self.plugin_config["plugin_settings"] = settings
                self._save_plugin_config()
                logger.info(f"Configured plugin: {plugin_name}")
            return success
        return False

    def get_available_plugins(self) -> List[str]:
        """Get list of available plugins."""
        if not self.initialized:
            return []
        return list(self.registry.get_all_plugins().keys())

    def load_plugin(self, plugin_path: str) -> bool:
        """
        Load a plugin from a file path.

        Args:
            plugin_path: Path to the plugin file

        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            plugin_file = Path(plugin_path)
            if not plugin_file.exists():
                logger.error(f"Plugin file not found: {plugin_path}")
                return False

            # Load the plugin module
            spec = importlib.util.spec_from_file_location(plugin_file.stem, plugin_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Register plugin classes
            loaded_any = False
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BasePlugin) and attr != BasePlugin:

                    plugin_name = attr.__name__.lower()
                    plugin_config = self.plugin_config.get("plugin_settings", {}).get(
                        plugin_name, {}
                    )

                    plugin_instance = attr(plugin_config)
                    plugin_instance.initialize()

                    success = self.registry.register_plugin(plugin_instance)
                    if success:
                        logger.info(f"Loaded plugin: {plugin_name} from {plugin_path}")
                        loaded_any = True

            return loaded_any

        except Exception as e:
            logger.error(f"Failed to load plugin from {plugin_path}: {e}")
            return False


# Global plugin manager instance
_plugin_manager: Optional[PluginManager] = None


def get_manager(config_dir: str) -> PluginManager:
    """
    Get or create the global plugin manager instance.

    Args:
        config_dir: Configuration directory path

    Returns:
        PluginManager instance
    """
    global _plugin_manager

    if _plugin_manager is None:
        _plugin_manager = PluginManager(config_dir)

    return _plugin_manager


def reset_manager() -> None:
    """Reset the global plugin manager (mainly for testing)."""
    global _plugin_manager
    _plugin_manager = None
