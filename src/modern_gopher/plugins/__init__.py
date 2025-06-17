"""
Plugin system for Modern Gopher.

This module provides the plugin architecture that allows extending
Modern Gopher with custom item type handlers, content processors,
and UI extensions.
"""

from .manager import PluginManager
from .base import BasePlugin, ItemTypeHandler, ContentProcessor, ProtocolExtension
from .registry import PluginRegistry

__all__ = [
    'PluginManager',
    'BasePlugin', 
    'ItemTypeHandler',
    'ContentProcessor',
    'ProtocolExtension',
    'PluginRegistry'
]

