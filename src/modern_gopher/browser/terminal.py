"""
Terminal-based Gopher browser implementation.

This module provides a simple terminal-based browser for navigating
Gopher resources using prompt_toolkit.
"""

import os
import sys
import logging
from typing import List, Dict, Optional, Any, Tuple
from urllib.parse import urljoin

try:
    from prompt_toolkit import Application
    from prompt_toolkit.layout import Layout, HSplit, VSplit, Window, FormattedTextControl
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.styles import Style
    from prompt_toolkit.widgets import Frame, TextArea, Label
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.filters import has_focus
except ImportError:
    print("Error: The 'prompt_toolkit' package is required. Please install it with 'pip install prompt_toolkit'.")
    sys.exit(1)

from modern_gopher.core.client import GopherClient
from modern_gopher.core.types import GopherItem, GopherItemType
from modern_gopher.core.url import GopherURL, parse_gopher_url
from modern_gopher.core.protocol import GopherProtocolError

# Set up logging
logger = logging.getLogger(__name__)

# Default URL when none is provided
DEFAULT_URL = "gopher://gopher.floodgap.com"


class HistoryManager:
    """Simple history management for the browser."""
    
    def __init__(self, max_size: int = 100):
        """Initialize history manager with maximum size."""
        self.history: List[str] = []
        self.position = -1
        self.max_size = max_size
    
    def add(self, url: str) -> None:
        """Add a URL to history."""
        # If we're not at the end of history, truncate
        if self.position < len(self.history) - 1:
            self.history = self.history[:self.position + 1]
        
        # Add the URL if it's different from the current one
        if not self.history or self.history[-1] != url:
            self.history.append(url)
            if len(self.history) > self.max_size:
                self.history.pop(0)
            self.position = len(self.history) - 1
    
    def back(self) -> Optional[str]:
        """Go back in history."""
        if self.position > 0:
            self.position -= 1
            return self.history[self.position]
        return None
    
    def forward(self) -> Optional[str]:
        """Go forward in history."""
        if self.position < len(self.history) - 1:
            self.position += 1
            return self.history[self.position]
        return None
    
    def current(self) -> Optional[str]:
        """Get current URL."""
        if 0 <= self.position < len(self.history):
            return self.history[self.position]
        return None


class GopherBrowser:
    """Simple terminal-based Gopher browser."""
    
    def __init__(self, initial_url: str = DEFAULT_URL, timeout: int = 30, 
                 use_ssl: bool = False, use_ipv6: Optional[bool] = None,
                 cache_dir: Optional[str] = None):
        """
        Initialize the browser.
        
        Args:
            initial_url: Starting URL
            timeout: Connection timeout
            use_ssl: Whether to use SSL
            use_ipv6: IPv6 preference (None for auto)
            cache_dir: Directory for caching
        """
        # Create client
        self.client = GopherClient(
            timeout=timeout, 
            cache_dir=cache_dir,
            use_ipv6=use_ipv6
        )
        
        # State
        self.current_url = initial_url
        self.current_items: List[GopherItem] = []
        self.selected_index = 0
        self.history = HistoryManager()
        self.use_ssl = use_ssl
        
        # Create UI components
        self.setup_ui()
        
        # Create keybindings
        self.kb = KeyBindings()
        self.setup_keybindings()
        
        # Create the application
        self.app = Application(
            layout=Layout(self.main_container),
            key_bindings=self.kb,
            full_screen=True,
            mouse_support=True,
            style=self.style
        )
    
    def setup_ui(self) -> None:
        """Set up the user interface components."""
        # Define styles
        self.style = Style.from_dict({
            'status': 'bg:#333333 #ffffff',
            'menu': 'bg:#000000 #aaaaaa',
            'menu.selection': 'bg:#0000aa #ffffff',
            'content': '',
        })
        
        # Create directory list
        self.menu_control = FormattedTextControl(
            self.get_menu_text,
            focusable=True,
            show_cursor=False
        )
        
        self.menu_window = Window(
            content=self.menu_control,
            style='class:menu',
            height=15,
            dont_extend_height=False
        )
        
        # Create content view
        self.content_view = TextArea(
            text="", 
            focusable=True,
            scrollbar=True,
            read_only=True,
            style='class:content'
        )
        
        # Create status bar
        self.status_bar = Label(
            text="", 
            style='class:status'
        )
        
        # Create main container
        self.main_container = HSplit([
            # Menu area
            self.menu_window,
            # Content area
            self.content_view,
            # Status bar
            self.status_bar
        ])
    
    def setup_keybindings(self) -> None:
        """Set up the key bindings for navigation."""
        kb = self.kb
        
        # Navigation in directory listing
        @kb.add('up')
        def _(event):
            if self.selected_index > 0:
                self.selected_index -= 1
                self.update_display()
        
        @kb.add('down')
        def _(event):
            if self.selected_index < len(self.current_items) - 1:
                self.selected_index += 1
                self.update_display()
        
        @kb.add('enter')
        def _(event):
            self.open_selected_item()
        
        # History navigation
        @kb.add('backspace')
        @kb.add('left', 'escape')
        def _(event):
            self.go_back()
        
        @kb.add('right', 'escape')
        def _(event):
            self.go_forward()
        
        # Quit
        @kb.add('c-c')
        @kb.add('c-q')
        def _(event):
            event.app.exit()
    
    def get_menu_text(self) -> List[Tuple[str, str]]:
        """Get the formatted text for the menu display."""
        result = []
        
        for i, item in enumerate(self.current_items):
            # Format the display line
            style = 'class:menu.selection' if i == self.selected_index else ''
            icon = self.get_item_icon(item.item_type)
            text = f"{icon} {item.display_string}"
            
            result.append((style, f"{text}\n"))
        
        return result

    def get_directory_formatted_text(self) -> List[Tuple[str, str]]:
        """Get formatted text for directory listing display (used in the rich UI version)."""
        result = []
        
        for i, item in enumerate(self.current_items):
            # Format the display line
            style = 'class:dir-list.selected' if i == self.selected_index else ''
            icon = self.get_item_icon(item.item_type)
            text = f"{icon} {item.display_string}"
            
            result.append((style, f"{text}\n"))
        
        return result
        
    def create_list_bindings(self) -> KeyBindings:
        """Create key bindings for the directory listing."""
        kb = KeyBindings()
        
        @kb.add('up')
        def _(event):
            if self.selected_index > 0:
                self.selected_index -= 1
                self.update_display()
        
        @kb.add('down')
        def _(event):
            if self.selected_index < len(self.current_items) - 1:
                self.selected_index += 1
                self.update_display()
        
        @kb.add('enter')
        def _(event):
            self.open_selected_item()
            
        return kb
    
    def handle_list_click(self, event):
        """Handle mouse clicks on the directory list."""
        # Calculate which item was clicked based on the line
        clicked_index = event.position.y
        
        if 0 <= clicked_index < len(self.current_items):
            # Update selection
            self.selected_index = clicked_index
            self.update_display()
            
            # If double-clicked, open the item
            if event.event_type == MouseEventType.MOUSE_UP and event.click_count == 2:
                self.open_selected_item()
    
    def toggle_bookmark(self):
        """Toggle bookmark for the current URL."""
        if not self.current_url:
            return
            
        if self.bookmarks.is_bookmarked(self.current_url):
            self.bookmarks.remove(self.current_url)
            self.status_bar.text = f"Bookmark removed: {self.current_url}"
        else:
            # Use the title from the selected item if available, otherwise use URL
            title = self.current_url
            if 0 <= self.selected_index < len(self.current_items):
                title = self.current_items[self.selected_index].display_string
                
            self.bookmarks.add(self.current_url, title)
            self.status_bar.text = f"Bookmark added: {self.current_url}"
    
    def show_history(self):
        """Show the browsing history."""
        history = self.history.get_history()
        if not history:
            self.status_bar.text = "No browsing history"
            return
            
        # Create history text
        text = "Browsing History:\n\n"
        for i, url in enumerate(history):
            current = " (current)" if i == self.history.position else ""
            text += f"{i+1}. {url}{current}\n"
        
        # Update content view with history
        self.content_view.text = text
    
    def show_help(self):
        """Show the help dialog."""
        # Set the help text in the dialog
        # Dialog is created in setup_ui
        # We would display it in a float, but for now we'll just show in the content area
        help_text = "Keyboard Navigation:\n"
        help_text += "  ↑/↓: Navigate directory list\n"
        help_text += "  Enter: Open selected item\n"
        help_text += "  Backspace/Alt+Left: Go back\n"
        help_text += "  Alt+Right: Go forward\n"
        help_text += "  Ctrl+B: Toggle bookmark\n"
        help_text += "  Ctrl+H: Show history\n"
        help_text += "  Ctrl+Q: Quit\n"
        help_text += "  F1: Help\n\n"
        help_text += "You can also use the mouse to click on items and buttons.\n\n"
        help_text += "Press Escape or any key to close this help screen."
        
        # Show in content view for simplicity
        self.content_view.text = help_text
    
    def close_dialog(self):
        """Close any open dialog."""
        # We're not using actual floating dialogs yet, so just restore the content
        self.update_display()
    
    def exit_browser(self):
        """Exit the browser."""
        self.app.exit()
    
    def get_item_icon(self, item_type: GopherItemType) -> str:
        """Get an icon representing the item type."""
        if item_type == GopherItemType.DIRECTORY:
            return "📁"
        elif item_type == GopherItemType.TEXT_FILE:
            return "📄"
        elif item_type == GopherItemType.BINARY_FILE or item_type == GopherItemType.DOS_BINARY:
            return "📦"
        elif item_type == GopherItemType.GIF_IMAGE or item_type == GopherItemType.IMAGE_FILE:
            return "🖼️"
        elif item_type == GopherItemType.SEARCH_SERVER:
            return "🔍"
        elif item_type == GopherItemType.HTML:
            return "🌐"
        elif item_type == GopherItemType.SOUND_FILE:
            return "🔊"
        else:
            return "❓"
    
    def update_status_bar(self) -> None:
        """Update the status bar with current URL and navigation help."""
        self.status_bar.text = f" {self.current_url} | ↑↓:Navigate | Enter:Open | Backspace:Back | Ctrl-Q:Quit"
    
    def update_display(self) -> None:
        """Update the display to reflect current state."""
        # Update the status bar
        self.update_status_bar()
        
        # Update the content view if we have an item selected
        if 0 <= self.selected_index < len(self.current_items):
            item = self.current_items[self.selected_index]
            # Show a preview in the content area
            preview = f"Type: {item.item_type.display_name}\n"
            preview += f"Selector: {item.selector}\n"
            preview += f"Server: {item.host}:{item.port}\n\n"
            preview += "Press Enter to open this item."
            self.content_view.text = preview
    
    def navigate_to(self, url: str) -> None:
        """Navigate to a specified URL."""
        try:
            # Parse the URL
            gopher_url = parse_gopher_url(url)
            if self.use_ssl and not gopher_url.use_ssl:
                gopher_url.use_ssl = True
            
            # Fetch the content
            content = self.client.get_resource(gopher_url)
            
            # Update current URL
            self.current_url = str(gopher_url)
            self.history.add(self.current_url)
            
            # Handle different content types
            if isinstance(content, list):
                # Directory listing
                self.current_items = content
                self.selected_index = 0
                self.content_view.text = "Select an item to view."
            elif isinstance(content, str):
                # Text content
                self.current_items = []
                self.content_view.text = content
            else:
                # Binary content
                self.current_items = []
                self.content_view.text = f"Binary content ({len(content)} bytes)"
            
            # Update display
            self.update_display()
            
        except GopherProtocolError as e:
            self.content_view.text = f"Error: {e}"
            logger.error(f"Protocol error: {e}")
        except Exception as e:
            self.content_view.text = f"Unexpected error: {e}"
            logger.exception(f"Error navigating to {url}: {e}")
    
    def open_selected_item(self) -> None:
        """Open the currently selected item."""
        if not self.current_items or self.selected_index >= len(self.current_items):
            return
        
        item = self.current_items[self.selected_index]
        
        # Create URL for the item
        scheme = "gophers" if self.use_ssl else "gopher"
        url = f"{scheme}://{item.host}:{item.port}/{item.item_type.value}{item.selector}"
        
        # Navigate to the URL
        self.navigate_to(url)
    
    def go_back(self) -> None:
        """Go back in history."""
        url = self.history.back()
        if url:
            self.navigate_to(url)
    
    def go_forward(self) -> None:
        """Go forward in history."""
        url = self.history.forward()
        if url:
            self.navigate_to(url)
    
    def run(self) -> int:
        """Run the browser application."""
        try:
            # Initial navigation
            self.navigate_to(self.current_url)
            
            # Run the application
            self.app.run()
            return 0
        except KeyboardInterrupt:
            return 130
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return 1


def launch_browser(url: str = DEFAULT_URL, 
                  timeout: int = 30, 
                  use_ssl: bool = False,
                  use_ipv6: Optional[bool] = None,
                  cache_dir: Optional[str] = None) -> int:
    """
    Launch the Gopher browser.
    
    Args:
        url: Initial URL to browse
        timeout: Connection timeout in seconds
        use_ssl: Whether to use SSL
        use_ipv6: IPv6 preference (None for auto)
        cache_dir: Directory for caching
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Create and run the browser
        browser = GopherBrowser(
            initial_url=url,
            timeout=timeout,
            use_ssl=use_ssl,
            use_ipv6=use_ipv6,
            cache_dir=cache_dir
        )
        
        return browser.run()
    
    except Exception as e:
        logger.exception(f"Error launching browser: {e}")
        return 1


if __name__ == "__main__":
    # When run directly, start the browser with default settings
    sys.exit(launch_browser())
