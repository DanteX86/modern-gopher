#!/usr/bin/env python3
"""
Script to fix common flake8 violations in the modern-gopher codebase.
"""

import os
import re
from pathlib import Path


def fix_file_issues(file_path):
    """Fix common issues in a Python file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Remove trailing whitespace
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Remove trailing whitespace
        line = line.rstrip()
        fixed_lines.append(line)
    
    # Remove multiple blank lines at end, keep max 1
    while len(fixed_lines) > 1 and fixed_lines[-1] == '' and fixed_lines[-2] == '':
        fixed_lines.pop()
    
    # Join lines back
    content = '\n'.join(fixed_lines)
    
    # Remove unused imports (simple cases)
    common_unused_patterns = [
        r'^import os$',
        r'^import tempfile$', 
        r'^import json$',
        r'^import ssl$',
        r'^import re$',
        r'^from typing import.*Tuple.*$',
        r'^from typing import.*Dict.*$',
        r'^from typing import.*Any.*$',
        r'^from typing import.*Union.*$',
        r'^from typing import.*Optional.*$',
    ]
    
    # Only write if content changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed: {file_path}")


def main():
    """Main function to fix code style issues."""
    src_dir = Path(__file__).parent / 'src'
    tests_dir = Path(__file__).parent / 'tests'
    
    for directory in [src_dir, tests_dir]:
        if directory.exists():
            for py_file in directory.rglob('*.py'):
                try:
                    fix_file_issues(py_file)
                except Exception as e:
                    print(f"Error fixing {py_file}: {e}")


if __name__ == '__main__':
    main()

