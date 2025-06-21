#!/usr/bin/env python3
"""
Modern Gopher Fix CLI

A comprehensive tool to automatically fix common issues in the Modern Gopher project.
"""

import argparse
import ast
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Color codes for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color

class FixCLI:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.dry_run = False
        self.verbose = False
        self.fixes_applied = 0
        self.issues_found = 0
        
    def log_info(self, message: str):
        """Log info message with color."""
        print(f"{Colors.BLUE}ℹ️  {message}{Colors.NC}")
        
    def log_success(self, message: str):
        """Log success message with color."""
        print(f"{Colors.GREEN}✅ {message}{Colors.NC}")
        
    def log_warning(self, message: str):
        """Log warning message with color."""
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.NC}")
        
    def log_error(self, message: str):
        """Log error message with color."""
        print(f"{Colors.RED}❌ {message}{Colors.NC}")
        
    def log_action(self, message: str):
        """Log action message with color."""
        print(f"{Colors.CYAN}🔧 {message}{Colors.NC}")

    def run_command(self, cmd: List[str], cwd: Path = None) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr."""
        try:
            result = subprocess.run(
                cmd, 
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)

    def fix_browser_terminal_missing_container(self):
        """Fix the missing main_container attribute in GopherBrowser."""
        self.log_info("🔍 Checking browser terminal for missing main_container...")
        
        terminal_file = self.project_root / "src/modern_gopher/browser/terminal.py"
        if not terminal_file.exists():
            self.log_warning("Browser terminal file not found")
            return
            
        content = terminal_file.read_text()
        
        # Check if main_container is referenced but not defined
        if "self.main_container" in content and "self.main_container =" not in content:
            self.issues_found += 1
            self.log_warning("Found missing main_container attribute")
            
            if not self.dry_run:
                # Find the __init__ method and add main_container initialization
                lines = content.split('\n')
                new_lines = []
                in_init = False
                container_added = False
                
                for i, line in enumerate(lines):
                    new_lines.append(line)
                    
                    # Detect __init__ method start
                    if "def __init__(self" in line:
                        in_init = True
                    
                    # Add main_container after other UI setup but before layout
                    if in_init and not container_added and ("self.status_bar" in line or "self.content_area" in line):
                        # Add main_container setup after next few lines
                        if i + 1 < len(lines) and lines[i + 1].strip() == "":
                            new_lines.append("")
                            new_lines.append("        # Main container setup")
                            new_lines.append("        self.main_container = HSplit([")
                            new_lines.append("            self.content_area,")
                            new_lines.append("            self.status_bar,")
                            new_lines.append("        ])")
                            container_added = True
                
                if container_added:
                    # Also need to add the import
                    if "from prompt_toolkit.layout import HSplit" not in content:
                        # Find import section and add HSplit import
                        for i, line in enumerate(new_lines):
                            if "from prompt_toolkit.layout" in line and "Layout" in line:
                                if "HSplit" not in line:
                                    new_lines[i] = line.replace("Layout", "Layout, HSplit")
                                break
                        else:
                            # Add new import if not found
                            for i, line in enumerate(new_lines):
                                if line.startswith("from prompt_toolkit"):
                                    new_lines.insert(i, "from prompt_toolkit.layout import HSplit")
                                    break
                    
                    terminal_file.write_text('\n'.join(new_lines))
                    self.fixes_applied += 1
                    self.log_success("Fixed missing main_container attribute")
                else:
                    self.log_warning("Could not automatically fix main_container - manual intervention needed")

    def fix_test_mock_decorators(self):
        """Fix test mock decorators with incorrect parameter counts."""
        self.log_info("🔍 Checking for test mock decorator issues...")
        
        test_files = [
            "tests/test_browser_terminal_advanced.py",
            "tests/test_browser_terminal_simplified.py"
        ]
        
        for test_file_path in test_files:
            test_file = self.project_root / test_file_path
            if not test_file.exists():
                continue
                
            content = test_file.read_text()
            lines = content.split('\n')
            new_lines = []
            file_modified = False
            
            i = 0
            while i < len(lines):
                line = lines[i]
                
                # Look for @patch decorators
                if line.strip().startswith('@patch(') or line.strip().startswith('@mock.patch('):
                    # Count the number of @patch decorators for this test method
                    patch_count = 0
                    j = i
                    
                    while j < len(lines) and (lines[j].strip().startswith('@patch') or 
                                            lines[j].strip().startswith('@mock.patch') or
                                            lines[j].strip() == ''):
                        if lines[j].strip().startswith('@patch') or lines[j].strip().startswith('@mock.patch'):
                            patch_count += 1
                        j += 1
                    
                    # Find the test method definition
                    while j < len(lines) and not lines[j].strip().startswith('def test_'):
                        j += 1
                    
                    if j < len(lines):
                        method_line = lines[j]
                        # Extract method parameters
                        method_match = re.match(r'(\s*)def\s+(\w+)\s*\((.*?)\):', method_line)
                        if method_match:
                            indent, method_name, params = method_match.groups()
                            param_list = [p.strip() for p in params.split(',') if p.strip()]
                            
                            # Calculate expected parameters: self + patch_count
                            expected_params = ['self'] + [f'mock_{k}' for k in range(patch_count)]
                            
                            if len(param_list) != len(expected_params):
                                self.issues_found += 1
                                self.log_warning(f"Found parameter mismatch in {method_name}: expected {len(expected_params)}, got {len(param_list)}")
                                
                                if not self.dry_run:
                                    # Fix the method signature
                                    new_params = ', '.join(expected_params)
                                    new_method_line = f"{indent}def {method_name}({new_params}):"
                                    lines[j] = new_method_line
                                    file_modified = True
                                    self.fixes_applied += 1
                
                new_lines.append(lines[i])
                i += 1
            
            if file_modified and not self.dry_run:
                test_file.write_text('\n'.join(lines))
                self.log_success(f"Fixed mock decorator issues in {test_file_path}")

    def fix_coverage_configuration(self):
        """Fix coverage configuration issues."""
        self.log_info("🔍 Checking coverage configuration...")
        
        # Check if .coveragerc exists and has proper configuration
        coveragerc = self.project_root / ".coveragerc"
        if not coveragerc.exists():
            self.issues_found += 1
            self.log_warning("Missing .coveragerc file")
            
            if not self.dry_run:
                coveragerc_content = """[run]
source = src/modern_gopher
omit = 
    */tests/*
    */test_*
    */venv/*
    */build/*
    */dist/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    if self.debug:
    if settings.DEBUG
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
    class .*\bProtocol\):
    @(abc\.)?abstractmethod

[html]
directory = htmlcov
"""
                coveragerc.write_text(coveragerc_content)
                self.fixes_applied += 1
                self.log_success("Created .coveragerc configuration file")

    def fix_import_issues(self):
        """Fix common import issues in the codebase."""
        self.log_info("🔍 Checking for import issues...")
        
        # Find all Python files
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                lines = content.split('\n')
                new_lines = []
                file_modified = False
                
                for line in lines:
                    # Fix common import issues
                    new_line = line
                    
                    # Fix relative imports that should be absolute
                    if re.match(r'^\s*from\s+\..*modern_gopher', line):
                        new_line = re.sub(r'from\s+\.+', 'from ', line)
                        if new_line != line:
                            file_modified = True
                            self.fixes_applied += 1
                    
                    new_lines.append(new_line)
                
                if file_modified and not self.dry_run:
                    py_file.write_text('\n'.join(new_lines))
                    
            except Exception as e:
                if self.verbose:
                    self.log_error(f"Error processing {py_file}: {e}")

    def fix_test_paths(self):
        """Fix test path issues."""
        self.log_info("🔍 Checking test path configuration...")
        
        # Check pytest.ini
        pytest_ini = self.project_root / "pytest.ini"
        if pytest_ini.exists():
            content = pytest_ini.read_text()
            if "testpaths = tests" not in content:
                self.issues_found += 1
                if not self.dry_run:
                    # Add testpaths if missing
                    lines = content.split('\n')
                    new_lines = []
                    added_testpaths = False
                    
                    for line in lines:
                        new_lines.append(line)
                        if line.strip().startswith('[pytest]') and not added_testpaths:
                            new_lines.append("testpaths = tests")
                            added_testpaths = True
                            file_modified = True
                    
                    if added_testpaths:
                        pytest_ini.write_text('\n'.join(new_lines))
                        self.fixes_applied += 1
                        self.log_success("Fixed pytest.ini testpaths configuration")

    def run_tests_to_verify_fixes(self):
        """Run tests to verify that fixes work."""
        self.log_info("🧪 Running tests to verify fixes...")
        
        # Run a subset of tests to check if basic issues are fixed
        exit_code, stdout, stderr = self.run_command([
            "python", "-m", "pytest", 
            "tests/test_browser_terminal.py", 
            "-v", "--tb=short", "-x"
        ])
        
        if exit_code == 0:
            self.log_success("Basic browser terminal tests are now passing!")
        else:
            self.log_warning("Some tests are still failing. Manual intervention may be needed.")
            if self.verbose:
                self.log_info(f"Test output:\n{stdout}")
                if stderr:
                    self.log_error(f"Test errors:\n{stderr}")

    def create_fix_script(self):
        """Create a fix script for future use."""
        fix_script = self.project_root / "fix"
        if not fix_script.exists():
            script_content = f"""#!/bin/bash
# Modern Gopher Fix Script
cd "{self.project_root}"
python3 fix_cli.py "$@"
"""
            fix_script.write_text(script_content)
            fix_script.chmod(0o755)
            self.log_success("Created 'fix' script for future use")

    def run_all_fixes(self):
        """Run all available fixes."""
        self.log_info("🚀 Starting comprehensive fix process...")
        
        # Order matters - fix fundamental issues first
        self.fix_coverage_configuration()
        self.fix_import_issues()
        self.fix_test_paths()
        self.fix_browser_terminal_missing_container()
        self.fix_test_mock_decorators()
        
        # Create convenience script
        self.create_fix_script()
        
        # Verify fixes if not in dry run mode
        if not self.dry_run:
            self.run_tests_to_verify_fixes()
        
        # Summary
        self.log_info(f"\n📊 Fix Summary:")
        self.log_info(f"   Issues found: {self.issues_found}")
        self.log_info(f"   Fixes applied: {self.fixes_applied}")
        
        if self.dry_run:
            self.log_warning("This was a dry run. Use --apply to actually apply fixes.")
        elif self.fixes_applied > 0:
            self.log_success(f"Applied {self.fixes_applied} fixes successfully!")
        else:
            self.log_info("No fixes needed - your codebase looks good!")

def main():
    parser = argparse.ArgumentParser(description="Modern Gopher Fix CLI")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be fixed without making changes")
    parser.add_argument("--apply", action="store_true", 
                       help="Actually apply the fixes")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Verbose output")
    parser.add_argument("--project-root", type=Path, 
                       help="Project root directory")
    
    # Specific fix options
    parser.add_argument("--fix-browser", action="store_true", 
                       help="Fix browser terminal issues only")
    parser.add_argument("--fix-tests", action="store_true", 
                       help="Fix test issues only")
    parser.add_argument("--fix-coverage", action="store_true", 
                       help="Fix coverage configuration only")
    
    args = parser.parse_args()
    
    # Default to dry run unless --apply is specified
    if not args.apply:
        args.dry_run = True
    
    fixer = FixCLI(args.project_root)
    fixer.dry_run = args.dry_run
    fixer.verbose = args.verbose
    
    if args.fix_browser:
        fixer.fix_browser_terminal_missing_container()
    elif args.fix_tests:
        fixer.fix_test_mock_decorators()
    elif args.fix_coverage:
        fixer.fix_coverage_configuration()
    else:
        fixer.run_all_fixes()

if __name__ == "__main__":
    main()
