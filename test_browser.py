#!/usr/bin/env python3
"""
Test script for the terminal browser.
This can be used to launch the browser for testing.
"""

import sys
import os

# Add the source directory to the path
sys.path.insert(0, 'src')

from modern_gopher.browser.terminal import launch_browser

if __name__ == "__main__":
    # Test the browser with a simple URL
    url = sys.argv[1] if len(sys.argv) > 1 else "gopher://gopher.floodgap.com"
    print(f"Testing terminal browser with URL: {url}")
    print("Press Ctrl+C to exit")
    
    try:
        result = launch_browser(url=url, timeout=10)
        print(f"Browser exited with code: {result}")
    except KeyboardInterrupt:
        print("\nBrowser test interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

