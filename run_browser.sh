#!/bin/bash
"""
Convenience script to run the Modern Gopher terminal browser.
This script activates the virtual environment and launches the browser.
"""

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Default URL if none provided
URL="${1:-gopher://gopher.floodgap.com}"

echo "==========================================="
echo "    Modern Gopher Terminal Browser"
echo "==========================================="
echo "Starting browser with URL: $URL"
echo "Use Arrow Keys to navigate, Enter to select"
echo "Press 'q' or Ctrl+C to quit"
echo "Press 'h' for help"
echo "==========================================="
echo

# Launch the browser
modern-gopher browse "$URL" --timeout 30

echo "Browser session ended."

