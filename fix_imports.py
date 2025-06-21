#!/usr/bin/env python3
"""
Script to remove unused imports from the modern-gopher codebase.
"""

import os
import re
from pathlib import Path

def remove_unused_imports(file_path, unused_imports):
    """Remove specific unused imports from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modified = False
    new_lines = []
    
    for line in lines:
        should_remove = False
        stripped = line.strip()
        
        for unused in unused_imports:
            # Match various import patterns
            patterns = [
                f"import {unused}",
                f"from {unused} import",
                f"    {unused},",  # Multi-line imports
                f"    {unused}",   # Multi-line imports
            ]
            
            # Check if line matches any pattern or contains the unused import
            if any(pattern in stripped for pattern in patterns) or stripped == f"import {unused}":
                should_remove = True
                break
        
        if not should_remove:
            new_lines.append(line)
        else:
            modified = True
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"Fixed imports in: {file_path}")

def main():
    """Fix common unused imports based on flake8 output."""
    
    # Map of files to their unused imports
    fixes = {
        "src/modern_gopher/browser/bookmarks.py": ["os"],
        "src/modern_gopher/browser/terminal.py": ["os", "urllib.parse.urljoin", 
                                                 "prompt_toolkit.filters.has_focus",
                                                 "prompt_toolkit.formatted_text.HTML",
                                                 "prompt_toolkit.layout.VSplit",
                                                 "prompt_toolkit.widgets.Frame",
                                                 "modern_gopher.core.url.GopherURL"],
        "src/modern_gopher/cli.py": ["typing.Any", "typing.Dict", "typing.Optional", 
                                    "typing.Union", "rich", 
                                    "modern_gopher.core.protocol.DEFAULT_GOPHER_PORT",
                                    "modern_gopher.core.types.GopherItemType",
                                    "modern_gopher.core.url.GopherURL",
                                    "modern_gopher.keybindings.KeyContext"],
        "src/modern_gopher/config.py": ["dataclasses.asdict"],
        "src/modern_gopher/content/html_renderer.py": ["rich.markdown.Markdown",
                                                      "rich.panel.Panel", "rich.rule.Rule",
                                                      "rich.table.Table", "rich.text.Text"],
        "src/modern_gopher/core/client.py": ["tempfile", "typing.BinaryIO", 
                                           "typing.Iterator", "typing.Tuple"],
        "src/modern_gopher/core/protocol.py": ["typing.List", "typing.Tuple", "typing.Union"],
        "src/modern_gopher/core/types.py": ["typing.Dict", "typing.Tuple"],
        "src/modern_gopher/core/url.py": ["re", "typing.Any", "typing.Dict",
                                         "urllib.parse.parse_qs", "urllib.parse.unquote"],
        "src/modern_gopher/keybindings.py": ["os", "dataclasses.field", "typing.Callable"],
        "src/modern_gopher/plugins/manager.py": ["os"],
        # Test files
        "tests/test_bookmarks.py": ["os", "datetime.datetime", "pytest"],
        "tests/test_browser.py": ["os", "tempfile", "pathlib.Path", "unittest.mock.MagicMock",
                                 "modern_gopher.config.ModernGopherConfig"],
        "tests/test_cli.py": ["os", "io.StringIO", "unittest.mock.MagicMock",
                             "modern_gopher.cli.setup_common_args"],
        "tests/test_client.py": ["json", "io.BytesIO", "unittest.mock.MagicMock",
                                "unittest.mock.Mock", "unittest.mock.mock_open"],
        "tests/test_config.py": ["pytest"],
        "tests/test_html_renderer.py": ["unittest.mock.MagicMock", "unittest.mock.patch"],
        "tests/test_keybindings.py": ["unittest.mock.MagicMock", "unittest.mock.patch"],
        "tests/test_protocol.py": ["ssl", "unittest.mock.MagicMock"],
        "tests/test_sessions.py": ["unittest.mock.MagicMock", "pytest"],
    }
    
    for file_path, unused_imports in fixes.items():
        abs_path = Path(__file__).parent / file_path
        if abs_path.exists():
            remove_unused_imports(abs_path, unused_imports)

if __name__ == '__main__':
    main()

