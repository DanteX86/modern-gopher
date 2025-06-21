"""
Main window for the Modern Gopher GUI application.
"""

import logging
import sys
from typing import List, Optional

try:
    from PySide6.QtCore import QThread, QTimer, QUrl, Signal, Qt
    from PySide6.QtGui import QAction, QFont, QIcon, QKeySequence
    from PySide6.QtWidgets import (
        QApplication, QHBoxLayout, QLineEdit, QMainWindow, QMenuBar,
        QMessageBox, QPushButton, QSplitter, QStatusBar, QTextEdit,
        QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
    )
except ImportError:
    # Handle gracefully if PySide6 not installed
    pass

from ..config import get_config
from ..core.client import GopherClient
from ..core.types import GopherItem, GopherItemType
from ..core.url import parse_gopher_url

logger = logging.getLogger(__name__)


class GopherFetchThread(QThread):
    """Thread for fetching Gopher content without blocking the UI."""
    
    content_ready = Signal(object)  # content (list of items or str)
    error_occurred = Signal(str)    # error message
    
    def __init__(self, client: GopherClient, url: str):
        super().__init__()
        self.client = client
        self.url = url
        
    def run(self):
        """Fetch content in background thread."""
        try:
            gopher_url = parse_gopher_url(self.url)
            content = self.client.get_resource(gopher_url)
            self.content_ready.emit(content)
        except Exception as e:
            self.error_occurred.emit(str(e))


class GopherMainWindow(QMainWindow):
    """Main window for the Modern Gopher browser."""
    
    def __init__(self, initial_url: Optional[str] = None):
        super().__init__()
        
        # Load configuration
        self.config = get_config()
        
        # Initialize Gopher client
        self.client = GopherClient(
            timeout=self.config.timeout,
            cache_dir=self.config.cache_directory if self.config.cache_enabled else None,
            use_ipv6=self.config.use_ipv6
        )
        
        # Navigation history
        self.history = []
        self.history_index = -1
        
        # Current fetch thread
        self.fetch_thread = None
        
        self.init_ui()
        
        # Navigate to initial URL
        if initial_url:
            self.navigate_to(initial_url)
        else:
            self.navigate_to(self.config.effective_initial_url)
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Modern Gopher Browser")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Create toolbar
        toolbar_layout = QHBoxLayout()
        
        # Back button
        self.back_button = QPushButton("◀")
        self.back_button.setMaximumWidth(40)
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setEnabled(False)
        toolbar_layout.addWidget(self.back_button)
        
        # Forward button
        self.forward_button = QPushButton("▶")
        self.forward_button.setMaximumWidth(40)
        self.forward_button.clicked.connect(self.go_forward)
        self.forward_button.setEnabled(False)
        toolbar_layout.addWidget(self.forward_button)
        
        # Refresh button
        self.refresh_button = QPushButton("⟳")
        self.refresh_button.setMaximumWidth(40)
        self.refresh_button.clicked.connect(self.refresh)
        toolbar_layout.addWidget(self.refresh_button)
        
        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter Gopher URL (e.g., gopher://gopher.floodgap.com)")
        self.url_bar.returnPressed.connect(self.navigate_from_url_bar)
        toolbar_layout.addWidget(self.url_bar)
        
        # Go button
        self.go_button = QPushButton("Go")
        self.go_button.clicked.connect(self.navigate_from_url_bar)
        toolbar_layout.addWidget(self.go_button)
        
        layout.addLayout(toolbar_layout)
        
        # Create splitter for main content
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel: Directory/Navigation tree
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("Gopher Directory")
        self.tree_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.tree_widget.setMaximumWidth(400)
        self.tree_widget.setMinimumWidth(300)
        splitter.addWidget(self.tree_widget)
        
        # Right panel: Content display
        self.content_display = QTextEdit()
        self.content_display.setReadOnly(True)
        self.content_display.setFont(QFont("Monaco", 12))  # Monospace font for text content
        splitter.addWidget(self.content_display)
        
        # Set splitter proportions
        splitter.setSizes([350, 850])
        
        layout.addWidget(splitter)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Create menu bar
        self.create_menu_bar()
    
    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        quit_action = QAction("Quit", self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Navigate menu
        nav_menu = menubar.addMenu("Navigate")
        
        back_action = QAction("Back", self)
        back_action.setShortcut(QKeySequence.Back)
        back_action.triggered.connect(self.go_back)
        nav_menu.addAction(back_action)
        
        forward_action = QAction("Forward", self)
        forward_action.setShortcut(QKeySequence.Forward)
        forward_action.triggered.connect(self.go_forward)
        nav_menu.addAction(forward_action)
        
        refresh_action = QAction("Refresh", self)
        refresh_action.setShortcut(QKeySequence.Refresh)
        refresh_action.triggered.connect(self.refresh)
        nav_menu.addAction(refresh_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def navigate_to(self, url: str):
        """Navigate to a specific URL."""
        if not url:
            return
            
        self.status_bar.showMessage(f"Loading {url}...")
        self.url_bar.setText(url)
        
        # Cancel any existing fetch
        if self.fetch_thread and self.fetch_thread.isRunning():
            self.fetch_thread.terminate()
            self.fetch_thread.wait()
        
        # Start new fetch
        self.fetch_thread = GopherFetchThread(self.client, url)
        self.fetch_thread.content_ready.connect(self.display_content)
        self.fetch_thread.error_occurred.connect(self.display_error)
        self.fetch_thread.start()
        
        # Add to history
        if not self.history or self.history[self.history_index] != url:
            # Remove any forward history when navigating to new page
            self.history = self.history[:self.history_index + 1]
            self.history.append(url)
            self.history_index = len(self.history) - 1
            
        self.update_navigation_buttons()
    
    def navigate_from_url_bar(self):
        """Navigate to URL from the URL bar."""
        url = self.url_bar.text().strip()
        if url:
            # Add gopher:// prefix if not present
            if not url.startswith(('gopher://', 'gophers://')):
                url = f"gopher://{url}"
            self.navigate_to(url)
    
    def display_content(self, content):
        """Display fetched content."""
        self.status_bar.showMessage("Ready")
        
        if isinstance(content, list):
            # Directory listing
            self.display_directory(content)
        elif isinstance(content, str):
            # Text content
            self.display_text(content)
        else:
            # Binary content
            self.content_display.setText(
                f"Binary content ({len(content)} bytes)\\n"
                "Use 'File > Save As' to save this content."
            )
    
    def display_directory(self, items: List[GopherItem]):
        """Display a Gopher directory listing."""
        self.tree_widget.clear()
        self.content_display.clear()
        
        info_text = f"Gopher Directory ({len(items)} items)\\n\\n"
        
        for item in items:
            # Add to tree widget
            tree_item = QTreeWidgetItem(self.tree_widget)
            
            # Set icon based on item type
            icon = self.get_item_icon(item.item_type)
            tree_item.setText(0, f"{icon} {item.display_string}")
            tree_item.setData(0, Qt.UserRole, item)  # Store the GopherItem
            
            # Add to text display
            info_text += f"{icon} {item.display_string}\\n"
        
        self.content_display.setText(info_text)
        
        # Expand all items
        self.tree_widget.expandAll()
    
    def display_text(self, text: str):
        """Display text content."""
        self.tree_widget.clear()
        self.content_display.setText(text)
    
    def display_error(self, error_message: str):
        """Display an error message."""
        self.status_bar.showMessage("Error occurred")
        self.content_display.setText(f"Error: {error_message}")
        
        # Show error dialog
        QMessageBox.warning(self, "Navigation Error", f"Failed to load page:\\n{error_message}")
    
    def get_item_icon(self, item_type: GopherItemType) -> str:
        """Get an icon/emoji for a Gopher item type."""
        icons = {
            GopherItemType.TEXT_FILE: "📄",
            GopherItemType.DIRECTORY: "📁",
            GopherItemType.CSO_PHONE_BOOK: "📞",
            GopherItemType.ERROR: "❌",
            GopherItemType.BINHEX_FILE: "📦",
            GopherItemType.DOS_BINARY: "🗜️",
            GopherItemType.UUENCODED_FILE: "📦",
            GopherItemType.SEARCH_SERVER: "🔍",
            GopherItemType.TELNET: "💻",
            GopherItemType.BINARY_FILE: "📁",
            GopherItemType.REDUNDANT_SERVER: "🪞",
            GopherItemType.GIF_IMAGE: "🖼️",
            GopherItemType.IMAGE_FILE: "🖼️",
            GopherItemType.TN3270_SESSION: "💻",
            GopherItemType.HTML: "🌐",
            GopherItemType.INFORMATION: "ℹ️",
            GopherItemType.SOUND_FILE: "🔊",
            GopherItemType.DOCUMENT: "📑",
            GopherItemType.PDF: "📄",
            GopherItemType.CALENDAR: "📅",
        }
        return icons.get(item_type, "📄")
    
    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle double-click on tree item."""
        gopher_item = item.data(0, Qt.UserRole)
        if gopher_item and gopher_item.item_type != GopherItemType.INFORMATION:
            # Build URL from item
            protocol = "gophers" if hasattr(gopher_item, 'use_ssl') and gopher_item.use_ssl else "gopher"
            url = f"{protocol}://{gopher_item.host}:{gopher_item.port}/{gopher_item.item_type.value}{gopher_item.selector}"
            self.navigate_to(url)
    
    def go_back(self):
        """Navigate to previous page in history."""
        if self.history_index > 0:
            self.history_index -= 1
            url = self.history[self.history_index]
            self.url_bar.setText(url)
            self.fetch_and_display(url)
            self.update_navigation_buttons()
    
    def go_forward(self):
        """Navigate to next page in history."""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            url = self.history[self.history_index]
            self.url_bar.setText(url)
            self.fetch_and_display(url)
            self.update_navigation_buttons()
    
    def refresh(self):
        """Refresh current page."""
        if self.history and self.history_index >= 0:
            url = self.history[self.history_index]
            self.fetch_and_display(url)
    
    def fetch_and_display(self, url: str):
        """Helper method to fetch and display without adding to history."""
        self.status_bar.showMessage(f"Loading {url}...")
        
        # Cancel any existing fetch
        if self.fetch_thread and self.fetch_thread.isRunning():
            self.fetch_thread.terminate()
            self.fetch_thread.wait()
        
        # Start new fetch
        self.fetch_thread = GopherFetchThread(self.client, url)
        self.fetch_thread.content_ready.connect(self.display_content)
        self.fetch_thread.error_occurred.connect(self.display_error)
        self.fetch_thread.start()
    
    def update_navigation_buttons(self):
        """Update the state of navigation buttons."""
        self.back_button.setEnabled(self.history_index > 0)
        self.forward_button.setEnabled(self.history_index < len(self.history) - 1)
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Modern Gopher",
            "Modern Gopher Browser\\n\\n"
            "A modern, feature-rich client for the Gopher protocol\\n\\n"
            "Built with Python and PySide6"
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Cancel any running fetch
        if self.fetch_thread and self.fetch_thread.isRunning():
            self.fetch_thread.terminate()
            self.fetch_thread.wait()
        
        event.accept()

