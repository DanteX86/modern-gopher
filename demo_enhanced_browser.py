#!/usr/bin/env python3
"""
Demo script to showcase enhanced browser features in Modern Gopher.

This script demonstrates the new enhanced status bar and other browser improvements.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add src to path so we can import modern_gopher
sys.path.insert(0, str(Path(__file__).parent / "src"))

from modern_gopher.browser.terminal import launch_browser

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(description="Enhanced Modern Gopher Browser Demo")
    parser.add_argument(
        "--url",
        default="gopher://gopher.floodgap.com",
        help="Initial URL to browse (default: gopher://gopher.floodgap.com)"
    )
    parser.add_argument(
        "--ssl",
        action="store_true",
        help="Use SSL/TLS connections (gophers://)"
    )
    parser.add_argument(
        "--ipv6",
        action="store_true",
        help="Prefer IPv6 connections"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Connection timeout in seconds (default: 30)"
    )
    
    args = parser.parse_args()
    
    print("🚀 Modern Gopher Browser - Enhanced Features Demo")
    print("=" * 60)
    print()
    print("🌟 New Features in This Demo:")
    print("   • Enhanced status bar with rich information")
    print("   • Context-sensitive help hints")
    print("   • Visual indicators for search, bookmarks, and history")
    print("   • Improved position tracking and item counts")
    print("   • Loading indicators with emojis")
    print()
    print("📖 How to Use:")
    print("   • Navigate directories with ↑/↓ or j/k keys")
    print("   • Press Enter to open selected items")
    print("   • Use / or Ctrl+F to search within directories")
    print("   • Press b to bookmark current location")
    print("   • Press m to view bookmarks")
    print("   • Press h to view browsing history")
    print("   • Press g or Ctrl+L to go to a specific URL")
    print("   • Press ? for complete help")
    print("   • Press q or Ctrl+C to quit")
    print()
    print("🔍 Enhanced Status Bar Information:")
    print("   📍 Current URL with navigation path")
    print("   📊 Item counts and position indicators")
    print("   🔍 Active search queries and result counts")
    print("   📚 History and bookmark counts")
    print("   💡 Context-sensitive keyboard hints")
    print()
    print(f"🌐 Starting browser at: {args.url}")
    print()
    print("Press any key in the browser to start exploring...")
    print()
    
    try:
        # Launch the enhanced browser
        exit_code = launch_browser(
            url=args.url,
            timeout=args.timeout,
            use_ssl=args.ssl,
            use_ipv6=args.ipv6 if args.ipv6 else None
        )
        
        print("\n🎉 Thank you for trying the Enhanced Modern Gopher Browser!")
        print("   Your browsing session has been saved automatically.")
        print("   Visit https://github.com/yourusername/modern-gopher for more info.")
        
        return exit_code
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Session auto-saved.")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

