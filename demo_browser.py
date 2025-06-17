#!/usr/bin/env python3
"""
Demo script for the Modern Gopher terminal browser.
Shows the browser features and keyboard navigation.
"""

import sys
import os

# Add the source directory to the path
sys.path.insert(0, 'src')

from modern_gopher.browser.terminal import launch_browser
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

def show_instructions():
    """Show browser instructions before starting."""
    
    instructions = Text()
    instructions.append("Modern Gopher Terminal Browser Demo\n\n", style="bold cyan")
    instructions.append("Navigation Controls:\n", style="bold yellow")
    instructions.append("  ↑/↓ Keys    - Navigate through directory items\n")
    instructions.append("  Enter       - Open selected item\n")
    instructions.append("  Backspace   - Go back in history\n")
    instructions.append("  Home        - Go to default URL\n")
    instructions.append("  r / F5      - Refresh current page\n")
    instructions.append("  h / F1      - Show help\n\n")
    
    instructions.append("Bookmark Features:\n", style="bold yellow")
    instructions.append("  b / Ctrl+B  - Toggle bookmark\n")
    instructions.append("  m           - Show bookmarks\n")
    instructions.append("  Ctrl+H      - Show history\n\n")
    
    instructions.append("Other Features:\n", style="bold yellow")
    instructions.append("  g / Ctrl+L  - URL input (planned)\n")
    instructions.append("  q / Ctrl+C  - Quit browser\n\n")
    
    instructions.append("The browser will start at gopher://gopher.floodgap.com\n", style="green")
    instructions.append("Try navigating to different directories and files!\n", style="green")
    
    panel = Panel(instructions, title="📚 Browser Instructions", border_style="blue")
    console.print(panel)
    
    input("\nPress Enter to start the browser...")

def main():
    """Main demo function."""
    console.print("\n🚀 Modern Gopher Browser Demo", style="bold green")
    console.print("=" * 40)
    
    # Show instructions
    show_instructions()
    
    # Start the browser
    console.print("\n🌐 Starting terminal browser...", style="cyan")
    
    try:
        # Use a well-known Gopher server for the demo
        demo_url = "gopher://gopher.floodgap.com"
        result = launch_browser(url=demo_url, timeout=10)
        
        console.print(f"\n✅ Browser session ended with exit code: {result}", style="green")
        
    except KeyboardInterrupt:
        console.print("\n⚠️  Browser demo interrupted by user", style="yellow")
    except Exception as e:
        console.print(f"\n❌ Error running browser demo: {e}", style="bold red")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

