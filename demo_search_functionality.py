#!/usr/bin/env python3
"""
Demo script to showcase the new directory search functionality.
"""

import sys
import os
from unittest.mock import Mock

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from modern_gopher.browser.terminal import GopherBrowser
from modern_gopher.core.types import GopherItem, GopherItemType
from modern_gopher.config import ModernGopherConfig


def demo_search_functionality():
    """Demonstrate the directory search functionality."""
    print("🔍 Modern Gopher Directory Search Demo")
    print("═" * 40)
    
    # Create mock config
    config = Mock(spec=ModernGopherConfig)
    config.initial_url = None
    config.cache_enabled = False
    config.cache_directory = '/tmp/test'
    config.max_history_items = 100
    config.bookmarks_file = '/tmp/bookmarks.json'
    
    # Create sample directory items
    sample_items = [
        GopherItem(GopherItemType.TEXT_FILE, "README.txt", "/readme.txt", "gopher.floodgap.com", 70),
        GopherItem(GopherItemType.TEXT_FILE, "documentation.txt", "/docs/documentation.txt", "gopher.floodgap.com", 70),
        GopherItem(GopherItemType.DIRECTORY, "source code", "/src", "gopher.floodgap.com", 70),
        GopherItem(GopherItemType.TEXT_FILE, "LICENSE", "/license", "gopher.floodgap.com", 70),
        GopherItem(GopherItemType.BINARY_FILE, "program.exe", "/bin/program.exe", "gopher.floodgap.com", 70),
        GopherItem(GopherItemType.TEXT_FILE, "CHANGELOG.md", "/changelog.md", "gopher.floodgap.com", 70),
        GopherItem(GopherItemType.DIRECTORY, "examples", "/examples", "gopher.floodgap.com", 70),
        GopherItem(GopherItemType.HTML, "index.html", "/web/index.html", "gopher.floodgap.com", 70),
        GopherItem(GopherItemType.TEXT_FILE, "user_documentation.pdf", "/docs/user_docs.pdf", "gopher.floodgap.com", 70),
    ]
    
    print(f"📁 Sample directory with {len(sample_items)} items:")
    for i, item in enumerate(sample_items, 1):
        print(f"  {i:2d}. {item.display_string} ({item.item_type.display_name})")
    
    print("\n" + "═" * 40)
    print("🔍 Testing Search Functionality")
    print("═" * 40)
    
    # Create browser instance
    try:
        # We need to mock some browser setup to avoid GUI dependencies
        browser = Mock()
        browser.current_items = sample_items.copy()
        browser.filtered_items = []
        browser.search_query = ""
        browser.is_searching = False
        browser.selected_index = 0
        
        # Import the actual search methods from the browser
        from modern_gopher.browser.terminal import GopherBrowser
        
        # Bind the methods to our mock browser
        browser.perform_search = GopherBrowser.perform_search.__get__(browser)
        browser.clear_search = GopherBrowser.clear_search.__get__(browser)
        
        # Mock update_display method
        browser.update_display = Mock()
        
        # Mock status_bar 
        browser.status_bar = Mock()
        
        # Test 1: Search for "doc"
        print("\n1️⃣  Search for 'doc':")
        browser.perform_search("doc")
        print(f"   Found {len(browser.current_items)} items:")
        for item in browser.current_items:
            print(f"   • {item.display_string}")
        print(f"   Status: {browser.status_bar.text}")
        
        # Test 2: Search for "src" (in selector)
        print("\n2️⃣  Search for 'src' (in selector):")
        browser.clear_search()  # Reset first
        browser.perform_search("src")
        print(f"   Found {len(browser.current_items)} items:")
        for item in browser.current_items:
            print(f"   • {item.display_string} (selector: {item.selector})")
        
        # Test 3: Case-insensitive search
        print("\n3️⃣  Case-insensitive search for 'LICENSE':")
        browser.clear_search()
        browser.perform_search("license")  # lowercase
        print(f"   Found {len(browser.current_items)} items:")
        for item in browser.current_items:
            print(f"   • {item.display_string}")
        
        # Test 4: Search with no results
        print("\n4️⃣  Search for non-existent term 'xyz':")
        browser.clear_search()
        browser.perform_search("xyz")
        print(f"   Found {len(browser.current_items)} items")
        if not browser.current_items:
            print("   (No matches found)")
        
        # Test 5: Clear search
        print("\n5️⃣  Clear search and restore all items:")
        browser.clear_search()
        print(f"   Restored {len(browser.current_items)} items")
        print(f"   Search mode: {'active' if browser.is_searching else 'inactive'}")
        
        print("\n" + "═" * 40)
        print("✅ All search functionality tests completed successfully!")
        print("\n📝 Keyboard Shortcuts in the browser:")
        print("   / or Ctrl+F  : Open search dialog")
        print("   ESC          : Clear search when searching")
        print("   ↑/↓          : Navigate through results")
        print("   Enter        : Open selected item")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(demo_search_functionality())

