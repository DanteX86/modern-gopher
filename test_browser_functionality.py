#!/usr/bin/env python3
"""
Automated test script to verify browser functionality.
This runs without user interaction to test the browser components.
"""

import sys
import os

# Add the source directory to the path
sys.path.insert(0, 'src')

from modern_gopher.browser.terminal import GopherBrowser
from modern_gopher.browser.bookmarks import BookmarkManager
from modern_gopher.core.client import GopherClient
from rich.console import Console
from rich.panel import Panel

console = Console()

def test_bookmark_manager():
    """Test the bookmark manager functionality."""
    console.print("\n🔖 Testing Bookmark Manager...", style="cyan")
    
    # Create temporary bookmark manager
    bm = BookmarkManager("/tmp/test_bookmarks.json")
    
    # Test adding bookmarks
    result1 = bm.add("gopher://gopher.floodgap.com", "Floodgap", "Test bookmark")
    result2 = bm.add("gopher://sdf.org", "SDF", "Another test")
    
    console.print(f"  ✅ Added bookmark 1: {result1}")
    console.print(f"  ✅ Added bookmark 2: {result2}")
    
    # Use assertions instead of returning True
    assert result1 is not None, "Failed to add first bookmark"
    assert result2 is not None, "Failed to add second bookmark"
    
    # Test searching
    search_results = bm.search("flood")
    console.print(f"  🔍 Search results for 'flood': {len(search_results)} found")
    assert len(search_results) > 0, "Search should find at least one result"
    
    # Test getting all bookmarks
    all_bookmarks = bm.get_all()
    console.print(f"  📚 Total bookmarks: {len(all_bookmarks)}")
    assert len(all_bookmarks) >= 2, "Should have at least 2 bookmarks"
    
    # Clean up
    if os.path.exists("/tmp/test_bookmarks.json"):
        os.remove("/tmp/test_bookmarks.json")

def test_gopher_client():
    """Test the Gopher client functionality."""
    console.print("\n🌐 Testing Gopher Client...", style="cyan")
    
    try:
        client = GopherClient(timeout=5)
        
        # Test URL parsing
        from modern_gopher.core.url import parse_gopher_url
        url = parse_gopher_url("gopher://gopher.floodgap.com/1/")
        console.print(f"  ✅ URL parsing successful: {url.host}:{url.port}")
        
        # Use assertions for proper testing
        assert url.host == "gopher.floodgap.com", "URL host should be correct"
        assert url.port == 70, "Default Gopher port should be 70"
        
        # Test connection (basic)
        console.print("  🔌 Testing connection...")
        resource = client.get_resource(url)
        
        if isinstance(resource, list) and len(resource) > 0:
            console.print(f"  ✅ Retrieved directory with {len(resource)} items")
            console.print(f"  📁 First item: {resource[0].display_string[:50]}...")
            assert len(resource) > 0, "Should retrieve at least one directory item"
        else:
            console.print("  ⚠️  Unexpected response format")
            assert False, "Expected a list of directory items"
        
    except Exception as e:
        console.print(f"  ❌ Client test failed: {e}")
        # For network tests, we can be more lenient and just ensure the client was created
        assert False, f"Client test failed with error: {e}"

def test_browser_components():
    """Test browser component creation without running the UI."""
    console.print("\n🖥️  Testing Browser Components...", style="cyan")
    
    try:
        # Create browser instance (without running)
        browser = GopherBrowser(
            initial_url="gopher://gopher.floodgap.com",
            timeout=5
        )
        
        console.print("  ✅ Browser instance created successfully")
        console.print(f"  🌐 Initial URL: {browser.current_url}")
        console.print(f"  📚 Bookmark manager initialized: {browser.bookmarks is not None}")
        console.print(f"  📖 History manager initialized: {browser.history is not None}")
        
        # Use assertions instead of returning True/False
        assert browser is not None, "Browser instance should be created"
        assert browser.current_url == "gopher://gopher.floodgap.com", "Initial URL should be set correctly"
        assert browser.bookmarks is not None, "Bookmark manager should be initialized"
        assert browser.history is not None, "History manager should be initialized"
        
        # Test keybinding setup
        console.print(f"  ⌨️  Keybindings configured: {len(browser.kb.bindings)} bindings")
        assert len(browser.kb.bindings) > 0, "Should have keybindings configured"
        
        # Test URL validator functionality
        console.print("  🔍 Testing URL validator...")
        validator = browser._url_validator()
        assert validator is not None, "URL validator should be created"
        console.print("  ✅ URL validator working correctly")
        
    except Exception as e:
        console.print(f"  ❌ Browser component test failed: {e}")
        assert False, f"Browser component test failed with error: {e}"

def main():
    """Run all tests."""
    console.print("\n🧪 Modern Gopher Browser Functionality Test", style="bold green")
    console.print("=" * 50)
    
    test_results = []
    
    # Run tests with proper exception handling
    tests = [
        ("Bookmark Manager", test_bookmark_manager),
        ("Gopher Client", test_gopher_client),
        ("Browser Components", test_browser_components)
    ]
    
    for test_name, test_func in tests:
        try:
            test_func()
            test_results.append((test_name, True))
        except Exception as e:
            console.print(f"  ❌ {test_name} failed: {e}", style="red")
            test_results.append((test_name, False))
    
    # Show results
    console.print("\n📊 Test Results:", style="bold yellow")
    console.print("-" * 20)
    
    all_passed = True
    for test_name, passed in test_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        console.print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        console.print("\n🎉 All tests passed! The browser is ready to use.", style="bold green")
        console.print("\n💡 Try running: python demo_browser.py", style="cyan")
        return 0
    else:
        console.print("\n⚠️  Some tests failed. Check the errors above.", style="bold red")
        return 1

if __name__ == "__main__":
    sys.exit(main())

