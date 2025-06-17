#!/usr/bin/env python3
"""
Test runner script for modern-gopher.

This script provides convenient ways to run different types of tests.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle the output."""
    print(f"\n{description}")
    print("=" * len(description))
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Run tests for modern-gopher")
    parser.add_argument(
        "--unit", action="store_true",
        help="Run only unit tests (no network/integration)"
    )
    parser.add_argument(
        "--integration", action="store_true",
        help="Run only integration tests (requires network)"
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Run all tests including integration tests"
    )
    parser.add_argument(
        "--coverage", action="store_true",
        help="Run tests with coverage reporting"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--file", "-f", type=str,
        help="Run tests from a specific file"
    )
    
    args = parser.parse_args()
    
    # Ensure we're in the project directory
    project_root = Path(__file__).parent
    if not (project_root / "src" / "modern_gopher").exists():
        print("Error: This script must be run from the project root directory")
        sys.exit(1)
    
    # Activate virtual environment if it exists
    venv_activate = project_root / "venv" / "bin" / "activate"
    if venv_activate.exists():
        activation_cmd = f"source {venv_activate} &&"
    else:
        activation_cmd = ""
        print("Warning: Virtual environment not found. Make sure dependencies are installed.")
    
    # Base pytest command
    pytest_cmd = "python -m pytest"
    
    if args.verbose:
        pytest_cmd += " -v"
    
    if args.coverage:
        # Check if coverage is installed
        try:
            import coverage
            pytest_cmd = "python -m pytest --cov=modern_gopher --cov-report=html --cov-report=term"
        except ImportError:
            print("Warning: coverage not installed. Install with: pip install coverage pytest-cov")
    
    success = True
    
    if args.file:
        # Run specific test file
        test_file = args.file
        if not test_file.startswith("tests/"):
            test_file = f"tests/{test_file}"
        if not test_file.endswith(".py"):
            test_file += ".py"
        
        cmd = f"{activation_cmd} {pytest_cmd} {test_file}"
        success = run_command(cmd, f"Running tests from {test_file}")
        
    elif args.unit:
        # Run only unit tests (exclude integration and network tests)
        cmd = f'{activation_cmd} {pytest_cmd} -m "not integration and not network"'
        success = run_command(cmd, "Running unit tests only")
        
    elif args.integration:
        # Run only integration tests
        cmd = f'{activation_cmd} {pytest_cmd} -m "integration"'
        success = run_command(cmd, "Running integration tests only")
        
    elif args.all:
        # Run all tests including integration
        cmd = f"{activation_cmd} {pytest_cmd}"
        success = run_command(cmd, "Running all tests")
        
    else:
        # Default: run unit tests only
        cmd = f'{activation_cmd} {pytest_cmd} -m "not integration and not network"'
        success = run_command(cmd, "Running unit tests (default)")
        
        print("\nNote: Use --all to include integration tests, or --integration for integration tests only.")
    
    # Show coverage report location if coverage was used
    if args.coverage and success:
        coverage_html = project_root / "htmlcov" / "index.html"
        if coverage_html.exists():
            print(f"\nCoverage report generated: file://{coverage_html.absolute()}")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

