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
from datetime import datetime

try:
    from prompt_toolkit import Application
    from prompt_toolkit.layout import Layout, HSplit, VSplit, Window, FormattedTextControl
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.styles import Style
    from prompt_toolkit.widgets import Frame, TextArea, Label
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.filters import has_focus
    from prompt_toolkit.shortcuts import input_dialog
    from prompt_toolkit.validation import Validator, ValidationError
except ImportError:
    print("Error: The 'prompt_toolkit' package is required. Please install it with 'pip install prompt_toolkit'.")
    sys.exit(1)

from modern_gopher.core.client import GopherClient
from modern_gopher.core.types import GopherItem, GopherItemType
from modern_gopher.core.url import GopherURL, parse_gopher_url
from modern_gopher.core.protocol import GopherProtocolError
from modern_gopher.browser.bookmarks import BookmarkManager
from modern_gopher.browser.sessions import SessionManager
from modern_gopher.config import ModernGopherConfig, get_config
from modern_gopher.content.html_renderer import render_html_to_text
from modern_gopher.keybindings import KeyBindingManager, KeyContext

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
                 cache_dir: Optional[str] = None, config: Optional[ModernGopherConfig] = None):
        """
        Initialize the browser.
        
        Args:
            initial_url: Starting URL
            timeout: Connection timeout
            use_ssl: Whether to use SSL
            use_ipv6: IPv6 preference (None for auto)
            cache_dir: Directory for caching
            config: Configuration object (loads default if None)
        """
        # Load configuration
        self.config = config or get_config()
        
        # Apply configuration defaults for parameters not explicitly provided
        if initial_url == DEFAULT_URL and self.config.initial_url:
            initial_url = self.config.initial_url
        if cache_dir is None and self.config.cache_enabled:
            cache_dir = self.config.cache_directory
        
        # Create client
        self.client = GopherClient(
            timeout=timeout, 
            cache_dir=cache_dir,
            use_ipv6=use_ipv6
        )
        
        # State
        self.current_url = initial_url
        self.current_items: List[GopherItem] = []
        self.filtered_items: List[GopherItem] = []  # For search filtering
        self.search_query = ""  # Current search query
        self.is_searching = False  # Whether we're in search mode
        self.selected_index = 0
        self.history = HistoryManager(max_size=self.config.max_history_items)
        self.use_ssl = use_ssl
        self.extracted_html_links: List[Dict[str, str]] = []  # Links extracted from HTML content
        
        # Initialize bookmark manager with config path
        self.bookmarks = BookmarkManager(self.config.bookmarks_file)
        
        # Initialize session manager if enabled
        self.session_manager = None
        if getattr(self.config, 'session_enabled', False):
            try:
                self.session_manager = SessionManager(
                    session_file=self.config.session_file,
                    backup_sessions=getattr(self.config, 'session_backup_sessions', 5),
                    max_sessions=getattr(self.config, 'session_max_sessions', 10)
                )
            except (AttributeError, TypeError) as e:
                # Handle case where config attributes are mocks or invalid in tests
                logger.debug(f"Session manager initialization skipped: {e}")
                self.session_manager = None
        
        # Initialize keybinding manager
        self.keybinding_manager = KeyBindingManager()
        self.current_context = KeyContext.BROWSER
        self._last_keybinding_context = None  # Track context changes
        
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
        """Set up the key bindings for navigation using KeyBindingManager."""
        kb = self.kb
        
        # Create action mappings
        action_handlers = {
            'navigate_up': lambda event: self._handle_navigate_up(),
            'navigate_down': lambda event: self._handle_navigate_down(),
            'open_item': lambda event: self.open_selected_item(),
            'go_back': lambda event: self.go_back(),
            'go_forward': lambda event: self.go_forward(),
            'quit': lambda event: event.app.exit(),
            'refresh': lambda event: self.refresh(),
            'help': lambda event: self.show_help(),
            'bookmark_toggle': lambda event: self.toggle_bookmark(),
            'bookmark_list': lambda event: self.show_bookmarks(),
            'history_show': lambda event: self.show_history(),
            'go_to_url': lambda event: self.show_url_input(),
            'go_home': lambda event: self.navigate_to(DEFAULT_URL),
            'search_directory': lambda event: self._handle_search(),
            'search_clear': lambda event: self._handle_search_clear(),
        }
        
        # Get all bindings for the current context
        bindings = self.keybinding_manager.get_bindings_by_context(self.current_context)
        
        # Add keybindings to prompt_toolkit
        for action, binding in bindings.items():
            if action in action_handlers and binding.enabled:
                handler = action_handlers[action]
                
                # Add all keys for this action
                for key in binding.keys:
                    # Convert our normalized format to prompt_toolkit format
                    pt_key = self._convert_key_to_prompt_toolkit(key)
                    
                    # Add all keys for this action
                    try:
                        # Fix closure bug by creating a factory function
                        def create_handler(h):
                            @kb.add(pt_key)
                            def _(event):
                                h(event)
                            return _
                        
                        create_handler(handler)
                    except ValueError as e:
                        logger.warning(f"Failed to add keybinding {pt_key} for {action}: {e}")
                        continue
        
        # Add session management keybindings (if available)
        if self.session_manager:
            @kb.add('s')
            def _(event):
                self.show_session_dialog()
            
            @kb.add('c-s')
            def _(event):
                self.save_current_session()
    
    def _convert_key_to_prompt_toolkit(self, key: str) -> str:
        """Convert normalized keybinding format to prompt_toolkit format."""
        # Convert our normalized format (c-c, a-f1) to prompt_toolkit format
        if '-' in key:
            modifier, base_key = key.split('-', 1)
            
            # Special handling for certain key combinations that prompt_toolkit doesn't support
            # Map unsupported combinations to supported ones
            unsupported_combinations = {
                'a-left': 'left',  # Alt+left not widely supported
                'a-right': 'right',  # Alt+right not widely supported
                's-tab': 'tab',  # Shift+tab becomes just tab
            }
            
            full_key = f"{modifier}-{base_key}"
            if full_key in unsupported_combinations:
                return unsupported_combinations[full_key]
            
            pt_modifiers = {
                'c': 'c-',
                'a': 'a-', 
                's': 's-',
                'm': 'm-'  # cmd on mac
            }
            if modifier in pt_modifiers:
                return f"{pt_modifiers[modifier]}{base_key}"
        
        return key
    
    def _handle_navigate_up(self) -> None:
        """Handle navigate up action."""
        if self.selected_index > 0:
            self.selected_index -= 1
            self.update_display()
    
    def _handle_navigate_down(self) -> None:
        """Handle navigate down action."""
        if self.selected_index < len(self.current_items) - 1:
            self.selected_index += 1
            self.update_display()
    
    def _handle_search(self) -> None:
        """Handle search action based on current context."""
        if self.current_context == KeyContext.DIRECTORY or not self.current_items:
            self.show_search_dialog()
    
    def _handle_search_clear(self) -> None:
        """Handle search clear action."""
        if self.is_searching:
            self.clear_search()
    
    def _update_context(self) -> None:
        """Update the current keybinding context based on application state."""
        new_context = self._determine_context()
        
        if new_context != self.current_context:
            logger.debug(f"Context switching from {self.current_context} to {new_context}")
            self.current_context = new_context
            
            # Only rebuild keybindings if context actually changed
            if new_context != self._last_keybinding_context:
                self._rebuild_keybindings()
                self._last_keybinding_context = new_context
    
    def _determine_context(self) -> KeyContext:
        """Determine the appropriate context based on current application state."""
        # Priority order for context determination:
        
        # 1. Search context - when actively searching
        if self.is_searching:
            return KeyContext.SEARCH
        
        # 2. Content context - when viewing text/binary content (no directory items)
        if not self.current_items and self.content_view.text:
            # Check if we're viewing actual content (not just preview)
            if len(self.content_view.text) > 100:  # Arbitrary threshold for "real content"
                return KeyContext.CONTENT
        
        # 3. Directory context - when viewing directory listings
        if self.current_items:
            return KeyContext.DIRECTORY
        
        # 4. Default to browser context
        return KeyContext.BROWSER
    
    def _rebuild_keybindings(self) -> None:
        """Rebuild keybindings for the current context."""
        # Clear existing dynamic keybindings (keep session management ones)
        self.kb = KeyBindings()
        
        # Create action mappings
        action_handlers = {
            'navigate_up': lambda event: self._handle_navigate_up(),
            'navigate_down': lambda event: self._handle_navigate_down(),
            'open_item': lambda event: self.open_selected_item(),
            'go_back': lambda event: self.go_back(),
            'go_forward': lambda event: self.go_forward(),
            'quit': lambda event: event.app.exit(),
            'refresh': lambda event: self.refresh(),
            'help': lambda event: self.show_help(),
            'bookmark_toggle': lambda event: self.toggle_bookmark(),
            'bookmark_list': lambda event: self.show_bookmarks(),
            'history_show': lambda event: self.show_history(),
            'go_to_url': lambda event: self.show_url_input(),
            'go_home': lambda event: self.navigate_to(DEFAULT_URL),
            'search_directory': lambda event: self._handle_search(),
            'search_clear': lambda event: self._handle_search_clear(),
            'scroll_up': lambda event: self._handle_scroll_up(),
            'scroll_down': lambda event: self._handle_scroll_down(),
        }
        
        # Get bindings for current context
        bindings = self.keybinding_manager.get_bindings_by_context(self.current_context)
        
        # Add keybindings to prompt_toolkit
        for action, binding in bindings.items():
            if action in action_handlers and binding.enabled:
                handler = action_handlers[action]
                
                # Add all keys for this action
                for key in binding.keys:
                    # Convert our normalized format to prompt_toolkit format
                    pt_key = self._convert_key_to_prompt_toolkit(key)
                    
                    try:
                        # Fix closure bug by creating a factory function
                        def create_handler(h):
                            @self.kb.add(pt_key)
                            def _(event):
                                h(event)
                            return _
                        
                        create_handler(handler)
                    except ValueError as e:
                        logger.warning(f"Failed to add keybinding {pt_key} for {action}: {e}")
                        continue
        
        # Add session management keybindings (if available)
        if self.session_manager:
            @self.kb.add('s')
            def _(event):
                self.show_session_dialog()
            
            @self.kb.add('c-s')
            def _(event):
                self.save_current_session()
        
        # Update the application's key bindings
        self.app.key_bindings = self.kb
    
    def _handle_scroll_up(self) -> None:
        """Handle scroll up action in content context."""
        if hasattr(self.content_view, 'buffer'):
            # Scroll the content view up
            self.content_view.buffer.cursor_up(count=5)
    
    def _handle_scroll_down(self) -> None:
        """Handle scroll down action in content context."""
        if hasattr(self.content_view, 'buffer'):
            # Scroll the content view down
            self.content_view.buffer.cursor_down(count=5)
    
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
        if not self.history.history:
            self.status_bar.text = "No browsing history"
            return
            
        # Create history text
        text = "Browsing History:\n\n"
        for i, url in enumerate(self.history.history):
            current = " (current)" if i == self.history.position else ""
            text += f"{i+1}. {url}{current}\n"
        
        # Update content view with history
        self.content_view.text = text
    
    def show_bookmarks(self):
        """Show the bookmarks list."""
        bookmarks = self.bookmarks.get_all()
        if not bookmarks:
            self.status_bar.text = "No bookmarks saved"
            return
            
        # Create bookmarks text
        text = "Bookmarks:\n\n"
        for i, bookmark in enumerate(bookmarks):
            text += f"{i+1}. {bookmark.title}\n"
            text += f"    URL: {bookmark.url}\n"
            if bookmark.description:
                text += f"    Description: {bookmark.description}\n"
            if bookmark.tags:
                text += f"    Tags: {', '.join(bookmark.tags)}\n"
            text += "\n"
        
        # Update content view with bookmarks
        self.content_view.text = text
    
    def show_url_input(self):
        """Show URL input dialog for direct URL navigation."""
        try:
            # Show input dialog with current URL as default
            result = input_dialog(
                title='Go to URL',
                text='Enter a Gopher URL:',
                default=self.current_url or 'gopher://',
                validator=self._url_validator()
            ).run()
            
            # If user provided a URL, navigate to it
            if result and result.strip():
                url = result.strip()
                
                # Add gopher:// prefix if not present
                if not url.startswith(('gopher://', 'gophers://')):
                    url = 'gopher://' + url
                
                self.navigate_to(url)
                self.status_bar.text = f"Navigating to: {url}"
            else:
                self.status_bar.text = "URL input cancelled"
                
        except Exception as e:
            self.status_bar.text = f"Error with URL input: {e}"
            logger.exception(f"URL input error: {e}")
    
    def _url_validator(self):
        """Get a URL validator instance."""
        
        class GopherURLValidator(Validator):
            def validate(self, document):
                text = document.text.strip()
                
                # Allow empty text (will be cancelled)
                if not text:
                    return
                
                # Add gopher:// prefix if not present for validation
                if not text.startswith(('gopher://', 'gophers://')):
                    text = 'gopher://' + text
                
                # Try to parse the URL
                try:
                    parse_gopher_url(text)
                except Exception as e:
                    raise ValidationError(
                        message=f"Invalid Gopher URL: {str(e)}",
                        cursor_position=len(document.text)
                    )
        
        return GopherURLValidator()
    
    def format_display_string(self, text: str, max_length: int = 100) -> str:
        """Format a display string, truncating if necessary."""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    def show_search_dialog(self):
        """Show directory search dialog."""
        if not self.current_items:
            self.status_bar.text = "No directory to search"
            return
        
        try:
            # Use input_dialog to get search query
            search_query = input_dialog(
                title="Search Directory",
                text="Enter search term (case-insensitive):",
                validator=None  # No validation needed for search
            )
            
            if search_query:
                self.perform_search(search_query)
            
        except Exception as e:
            logger.error(f"Error in search dialog: {e}")
            self.status_bar.text = "Error opening search dialog"
    
    def perform_search(self, query: str):
        """Perform search on current directory items."""
        if not query.strip():
            self.clear_search()
            return
        
        # Store original items if not already searching
        if not self.is_searching:
            self.filtered_items = self.current_items.copy()
        
        # Filter items based on search query (case-insensitive)
        query_lower = query.lower()
        matching_items = []
        
        for item in self.filtered_items:
            # Search in display string and selector
            if (query_lower in item.display_string.lower() or 
                query_lower in item.selector.lower()):
                matching_items.append(item)
        
        # Update current items to show search results
        self.current_items = matching_items
        self.search_query = query
        self.is_searching = True
        self.selected_index = 0
        
        # Update display and status
        self.update_display()
        if matching_items:
            self.status_bar.text = f"Search: '{query}' - {len(matching_items)} results (ESC to clear)"
        else:
            self.status_bar.text = f"Search: '{query}' - No results found (ESC to clear)"
    
    def clear_search(self):
        """Clear search and restore original directory listing."""
        if self.is_searching:
            # Restore original items
            self.current_items = self.filtered_items.copy()
            self.filtered_items = []
            self.search_query = ""
            self.is_searching = False
            self.selected_index = 0
            
            # Update display
            self.update_display()
            self.status_bar.text = "Search cleared"
    
    def show_help(self):
        """Show the help dialog with current keybindings."""
        help_text = "Modern Gopher Terminal Browser Help\n"
        help_text += "═══════════════════════════════════\n\n"
        
        # Group keybindings by category and show them
        categories = self.keybinding_manager.get_all_categories()
        
        for category in sorted(categories):
            bindings = self.keybinding_manager.get_bindings_by_category(category)
            if not bindings:
                continue
                
            help_text += f"{category.title()}:\n"
            
            for action, binding in bindings.items():
                if binding.enabled:
                    # Format keys nicely
                    key_display = " / ".join(self._format_key_for_display(key) for key in binding.keys)
                    help_text += f"  {key_display:<18} {binding.description}\n"
            
            help_text += "\n"
        
        help_text += "Mouse Support:\n"
        help_text += "  Click on items to select them\n"
        help_text += "  Double-click to open items\n\n"
        help_text += "Features:\n"
        help_text += "  • Customizable keybindings\n"
        help_text += "  • Automatic bookmark management\n"
        help_text += "  • Browsing history tracking\n"
        help_text += "  • Content caching for performance\n"
        help_text += "  • Support for all Gopher item types\n"
        help_text += "  • SSL/TLS support (gophers://)\n\n"
        help_text += "Press any key to return to browsing.\n\n"
        help_text += "Keybindings can be customized by editing ~/.config/modern-gopher/keybindings.json"
        
        # Show in content view
        self.content_view.text = help_text
    
    def _format_key_for_display(self, key: str) -> str:
        """Format a key for display in help text."""
        # Convert normalized format back to readable format
        if '-' in key:
            modifier, base_key = key.split('-', 1)
            modifier_names = {
                'c': 'Ctrl',
                'a': 'Alt',
                's': 'Shift',
                'm': 'Cmd'
            }
            modifier_name = modifier_names.get(modifier, modifier.upper())
            return f"{modifier_name}+{base_key.title()}"
        
        # Special key names
        special_keys = {
            'up': '↑',
            'down': '↓',
            'left': '←',
            'right': '→',
            'enter': 'Enter',
            'space': 'Space',
            'escape': 'Esc',
            'backspace': 'Backspace',
            'pageup': 'PgUp',
            'pagedown': 'PgDn',
            'home': 'Home',
            'f1': 'F1',
            'f5': 'F5'
        }
        
        return special_keys.get(key.lower(), key.upper())
    
    def close_dialog(self):
        """Close any open dialog."""
        # We're not using actual floating dialogs yet, so just restore the content
        self.update_display()
    
    def exit_browser(self):
        """Exit the browser."""
        self.app.exit()
    
    def get_item_icon(self, item_type: GopherItemType) -> str:
        """Get an icon representing the item type."""
        # Use Unicode icons with fallback to text
        try:
            if item_type == GopherItemType.DIRECTORY:
                return "📁"
            elif item_type == GopherItemType.TEXT_FILE:
                return "📄"
            elif item_type in (GopherItemType.BINARY_FILE, GopherItemType.DOS_BINARY):
                return "📎"
            elif item_type in (GopherItemType.GIF_IMAGE, GopherItemType.IMAGE_FILE):
                return "🖼️"
            elif item_type == GopherItemType.SEARCH_SERVER:
                return "🔍"
            elif item_type == GopherItemType.HTML:
                return "🌐"
            elif item_type == GopherItemType.SOUND_FILE:
                return "🔊"
            else:
                return "❓"
        except:
            # Fallback to text representations if Unicode fails
            icon_map = {
                GopherItemType.DIRECTORY: "[DIR]",
                GopherItemType.TEXT_FILE: "[TXT]", 
                GopherItemType.BINARY_FILE: "[BIN]",
                GopherItemType.DOS_BINARY: "[BIN]",
                GopherItemType.GIF_IMAGE: "[IMG]",
                GopherItemType.IMAGE_FILE: "[IMG]",
                GopherItemType.SEARCH_SERVER: "[?]",
                GopherItemType.HTML: "[HTM]",
                GopherItemType.SOUND_FILE: "[SND]",
            }
            return icon_map.get(item_type, "[?]")
    
    def update_status(self, message: str) -> None:
        """Update the status bar with a custom message."""
        if self.current_items and len(self.current_items) > 0:
            position_info = f" ({self.selected_index + 1}/{len(self.current_items)})"
            self.status_bar.text = f"{message}{position_info}"
        else:
            self.status_bar.text = message
    
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
                # Text content - check if it's HTML
                self.current_items = []
                
                # Detect HTML content by checking for HTML tags and item type
                is_html = (gopher_url.item_type == 'h' or 
                          '<html' in content.lower() or 
                          '<body' in content.lower() or 
                          '<!doctype html' in content.lower())
                
                if is_html:
                    try:
                        # Render HTML content using Beautiful Soup
                        rendered_text, extracted_links = render_html_to_text(content)
                        self.content_view.text = rendered_text
                        
                        # Store extracted links for potential future use
                        self.extracted_html_links = extracted_links
                        
                        # Update status to indicate HTML rendering
                        self.status_bar.text = f"HTML content rendered ({len(extracted_links)} links found)"
                        
                    except Exception as e:
                        # Fall back to raw text if HTML rendering fails
                        logger.warning(f"HTML rendering failed, showing raw content: {e}")
                        self.content_view.text = content
                        self.status_bar.text = "HTML rendering failed, showing raw content"
                else:
                    # Regular text content
                    self.content_view.text = content
            else:
                # Binary content
                self.current_items = []
                self.content_view.text = f"Binary content ({len(content)} bytes)"
            
            # Update display
            self.update_display()
            
            # Update context based on new state
            self._update_context()
            
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
    
    def refresh(self) -> None:
        """Refresh the current page."""
        if self.current_url:
            # Clear cache for current URL and reload
            cache_key = self.client._cache_key(self.current_url)
            if cache_key in self.client.memory_cache:
                del self.client.memory_cache[cache_key]
            self.navigate_to(self.current_url)
    
    def get_browser_state(self) -> Dict[str, Any]:
        """Get current browser state for session saving."""
        return {
            'current_url': self.current_url,
            'history': self.history.history.copy(),
            'history_position': self.history.position,
            'selected_index': self.selected_index,
            'is_searching': self.is_searching,
            'search_query': self.search_query,
        }
    
    def restore_browser_state(self, state: Dict[str, Any]) -> None:
        """Restore browser state from session data."""
        try:
            # Restore URL and navigate
            if state.get('current_url'):
                self.current_url = state['current_url']
            
            # Restore history
            if state.get('history'):
                self.history.history = state['history'].copy()
                self.history.position = state.get('history_position', -1)
            
            # Restore search state
            self.is_searching = state.get('is_searching', False)
            self.search_query = state.get('search_query', '')
            self.selected_index = state.get('selected_index', 0)
            
            # Navigate to the restored URL
            if self.current_url:
                self.navigate_to(self.current_url)
            
            logger.info("Browser state restored from session")
            
        except Exception as e:
            logger.error(f"Failed to restore browser state: {e}")
            self.status_bar.text = "Failed to restore session"
    
    def save_current_session(self, session_name: Optional[str] = None) -> None:
        """Save current browser state as a session."""
        if not self.session_manager:
            self.status_bar.text = "Session management disabled"
            return
        
        try:
            browser_state = self.get_browser_state()
            session_id = self.session_manager.save_session(
                browser_state=browser_state,
                session_name=session_name
            )
            
            if session_id:
                session_name = session_name or f"Session {len(self.session_manager.sessions)}"
                self.status_bar.text = f"Session saved: {session_name}"
                logger.info(f"Session saved with ID: {session_id}")
            else:
                self.status_bar.text = "Failed to save session"
                
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            self.status_bar.text = f"Session save error: {e}"
    
    def load_session(self, session_id: str) -> None:
        """Load a specific session."""
        if not self.session_manager:
            self.status_bar.text = "Session management disabled"
            return
        
        try:
            browser_state = self.session_manager.load_session(session_id)
            if browser_state:
                self.restore_browser_state(browser_state)
                self.status_bar.text = f"Session loaded: {session_id}"
            else:
                self.status_bar.text = f"Session not found: {session_id}"
                
        except Exception as e:
            logger.error(f"Error loading session: {e}")
            self.status_bar.text = f"Session load error: {e}"
    
    def auto_restore_session(self) -> bool:
        """Automatically restore the most recent session if enabled."""
        if not self.session_manager or not self.config.session_auto_restore:
            return False
        
        try:
            browser_state = self.session_manager.get_default_session()
            if browser_state:
                self.restore_browser_state(browser_state)
                logger.info("Auto-restored previous session")
                return True
            else:
                logger.info("No previous session to restore")
                return False
                
        except Exception as e:
            logger.error(f"Failed to auto-restore session: {e}")
            return False
    
    def show_session_dialog(self) -> None:
        """Show session management dialog."""
        if not self.session_manager:
            self.status_bar.text = "Session management disabled"
            return
        
        try:
            sessions = self.session_manager.list_sessions()
            
            if not sessions:
                self.status_bar.text = "No saved sessions"
                return
            
            # Create sessions text
            text = "Saved Sessions:\n\n"
            for i, session in enumerate(sessions):
                text += f"{i+1}. {session.name}\n"
                text += f"    URL: {session.current_url}\n"
                text += f"    Created: {session.created_datetime.strftime('%Y-%m-%d %H:%M')}\n"
                text += f"    Last Used: {session.last_used_datetime.strftime('%Y-%m-%d %H:%M')}\n"
                if session.description:
                    text += f"    Description: {session.description}\n"
                if session.tags:
                    text += f"    Tags: {', '.join(session.tags)}\n"
                text += "\n"
            
            text += "\nSession Management:\n"
            text += "  Ctrl+S: Save current session\n"
            text += "  S: Show this session list\n"
            text += "\nTo load a session, use the CLI: modern-gopher session load <session_id>\n"
            
            # Update content view with sessions
            self.content_view.text = text
            self.status_bar.text = f"Showing {len(sessions)} saved sessions"
            
        except Exception as e:
            logger.error(f"Error showing session dialog: {e}")
            self.status_bar.text = f"Session dialog error: {e}"
    
    def auto_save_session_on_exit(self) -> None:
        """Automatically save session on exit if enabled."""
        if not self.session_manager or not self.config.save_session:
            return
        
        try:
            # Save current session with auto-generated name
            browser_state = self.get_browser_state()
            session_id = self.session_manager.save_session(
                browser_state=browser_state,
                session_name="Auto-saved on exit",
                description=f"Automatically saved on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            
            if session_id:
                logger.info(f"Auto-saved session on exit: {session_id}")
                
        except Exception as e:
            logger.error(f"Failed to auto-save session on exit: {e}")
    
    def run(self) -> int:
        """Run the browser application."""
        try:
            # Try to auto-restore session if enabled
            session_restored = False
            if self.session_manager and self.config.session_auto_restore:
                session_restored = self.auto_restore_session()
                if session_restored:
                    self.status_bar.text = "Previous session restored"
            
            # Initial navigation (only if session wasn't restored)
            if not session_restored:
                self.navigate_to(self.current_url)
            
            # Run the application
            self.app.run()
            
            # Auto-save session on exit if enabled
            self.auto_save_session_on_exit()
            
            return 0
        except KeyboardInterrupt:
            # Auto-save session on interrupt if enabled
            self.auto_save_session_on_exit()
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
