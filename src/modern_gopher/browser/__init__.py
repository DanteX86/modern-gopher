"""
Browser module for modern-gopher.

This package provides terminal-based browsing capabilities for Gopher resources.
"""

from modern_gopher.browser.terminal import launch_browser
from modern_gopher.browser.bookmarks import BookmarkManager, Bookmark

__all__ = ['launch_browser', 'BookmarkManager', 'Bookmark']

