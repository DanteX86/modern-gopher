"""
Base plugin classes and interfaces.

This module defines the base classes that all plugins must inherit from,
defining the plugin API and contract.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from modern_gopher.core.types import GopherItemType, GopherItem


@dataclass
class PluginMetadata:
    """Metadata about a plugin."""
    name: str
    version: str
    author: str
    description: str
    dependencies: List[str] = None
    supported_item_types: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.supported_item_types is None:
            self.supported_item_types = []


class BasePlugin(ABC):
    """Base class for all Modern Gopher plugins."""
    
    def __init__(self):
        self._enabled = True
        self._config = {}
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass
    
    @property
    def enabled(self) -> bool:
        """Check if the plugin is enabled."""
        return self._enabled
    
    def enable(self) -> None:
        """Enable the plugin."""
        self._enabled = True
        self.on_enable()
    
    def disable(self) -> None:
        """Disable the plugin."""
        self._enabled = False
        self.on_disable()
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the plugin with settings."""
        self._config.update(config)
        self.on_configure(config)
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)
    
    # Hook methods that subclasses can override
    def on_enable(self) -> None:
        """Called when the plugin is enabled."""
        pass
    
    def on_disable(self) -> None:
        """Called when the plugin is disabled."""
        pass
    
    def on_configure(self, config: Dict[str, Any]) -> None:
        """Called when the plugin is configured."""
        pass
    
    def initialize(self) -> None:
        """Initialize the plugin. Called once after loading."""
        pass
    
    def cleanup(self) -> None:
        """Clean up plugin resources. Called before unloading."""
        pass


class ItemTypeHandler(BasePlugin):
    """Base class for plugins that handle specific Gopher item types."""
    
    @abstractmethod
    def can_handle(self, item_type: GopherItemType, content: Union[str, bytes]) -> bool:
        """Check if this handler can process the given item type and content."""
        pass
    
    @abstractmethod
    def process_content(self, item_type: GopherItemType, content: Union[str, bytes], 
                       item: Optional[GopherItem] = None) -> Tuple[str, Dict[str, Any]]:
        """Process content and return (processed_content, metadata)."""
        pass
    
    def get_supported_types(self) -> List[GopherItemType]:
        """Return list of supported Gopher item types."""
        return []
    
    def get_priority(self) -> int:
        """Return handler priority (higher = more preferred). Default is 0."""
        return 0


class ContentProcessor(BasePlugin):
    """Base class for plugins that process content regardless of item type."""
    
    @abstractmethod
    def process(self, content: str, metadata: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Process content and return (processed_content, updated_metadata)."""
        pass
    
    def should_process(self, content: str, metadata: Dict[str, Any]) -> bool:
        """Check if this processor should handle the content."""
        return True
    
    def get_processing_order(self) -> int:
        """Return processing order (lower = processed earlier). Default is 100."""
        return 100


class ProtocolExtension(BasePlugin):
    """Base class for plugins that extend the Gopher protocol."""
    
    def modify_request(self, host: str, selector: str, port: int) -> Tuple[str, str, int]:
        """Modify a Gopher request. Return (host, selector, port)."""
        return host, selector, port
    
    def process_response(self, response: bytes, host: str, selector: str) -> bytes:
        """Process a raw Gopher response."""
        return response
    
    def get_supported_features(self) -> List[str]:
        """Return list of supported protocol features."""
        return []

