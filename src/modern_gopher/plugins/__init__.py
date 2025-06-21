"""
Plugin system for Modern Gopher.

This package provides extensible functionality for handling different
content types and integrating with external applications.
"""

from .manager import get_manager
from .manager import reset_manager

__all__ = ['get_manager', 'reset_manager']
