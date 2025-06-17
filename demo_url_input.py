#!/usr/bin/env python3
"""
Simple demo to test the URL input dialog functionality.
"""

import sys
sys.path.insert(0, 'src')

from modern_gopher.browser.terminal import GopherBrowser
from rich.console import Console
from rich.panel import Panel

console = Console()

def demo_url_input_dialog():
    """Demo the URL input dialog without running full browser."""
    console.print(Panel.fit(
        "🌐 URL Input Dialog Demo",
        title="Modern Gopher",
        subtitle="Testing URL validation and input"
    ))
    
    try:
        # Create browser instance
        browser = GopherBrowser(
            initial_url="gopher://gopher.floodgap.com",
            timeout=5
        )
        
        # Test the URL validator directly
        console.print("\n📝 Testing URL validator...")
        validator = browser._url_validator()
        console.print("✅ URL validator created successfully")
        
        # Test validation with different URLs
        test_urls = [
            "gopher.floodgap.com",  # Valid without prefix
            "gopher://gopher.floodgap.com",  # Valid with prefix
            "sdf.org:70",  # Valid with port
            "invalid://protocol",  # Invalid protocol
            "",  # Empty (should be allowed)
        ]
        
        console.print("\n🧪 Testing URL validation:")
        for test_url in test_urls:
            try:
                # Create a mock document for testing
                class MockDocument:
                    def __init__(self, text):
                        self.text = text
                
                validator.validate(MockDocument(test_url))
                console.print(f"  ✅ '{test_url}' - Valid")
            except Exception as e:
                console.print(f"  ❌ '{test_url}' - Invalid: {e}")
        
        console.print("\n✨ URL input dialog is ready to use!")
        console.print("\n💡 In the browser, press 'G' or 'Ctrl+L' to open the URL input dialog.")
        console.print("💡 Try running: python demo_browser.py")
        
        return True
        
    except Exception as e:
        console.print(f"❌ Demo failed: {e}")
        return False

if __name__ == "__main__":
    success = demo_url_input_dialog()
    sys.exit(0 if success else 1)

