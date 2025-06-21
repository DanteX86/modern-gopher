"""
GUI components for Modern Gopher.

This module provides a graphical user interface for the modern-gopher client,
built using PySide6 for native macOS integration.
"""

__all__ = ["launch_gui", "GopherMainWindow"]

from .main_window import GopherMainWindow


def launch_gui(initial_url: str = None) -> int:
    """
    Launch the Modern Gopher GUI application.
    
    Args:
        initial_url: Initial URL to navigate to
        
    Returns:
        Exit code (0 for success)
    """
    try:
        from PySide6.QtWidgets import QApplication
        import sys
        
        app = QApplication(sys.argv)
        app.setApplicationName("Modern Gopher")
        app.setApplicationDisplayName("Modern Gopher Browser")
        app.setOrganizationName("ModernGopher")
        app.setOrganizationDomain("modern-gopher.org")
        
        window = GopherMainWindow(initial_url=initial_url)
        window.show()
        
        return app.exec()
        
    except ImportError:
        print("Error: PySide6 is not installed. Install it with:")
        print("pip install PySide6")
        return 1
    except Exception as e:
        print(f"GUI Error: {e}")
        return 1

