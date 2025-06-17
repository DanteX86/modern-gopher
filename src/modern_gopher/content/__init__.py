"""
Content rendering package for Modern Gopher.

This package provides modules for rendering different types of content
in a terminal-friendly format.
"""

from .html_renderer import HTMLRenderer, render_html_to_text

__all__ = ['HTMLRenderer', 'render_html_to_text']

