#!/usr/bin/env python3
"""
Test-Driven Development CLI for Modern Gopher
A comprehensive testing toolkit for TDD workflow
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_header(text: str) -> None:
    """Print a colored header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")


def print_success(text: str) -> None:
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text: str) -> None:
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_warning(text: str) -> None:
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_info(text: str) -> None:
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


def run_command(cmd: List[str], description: str = "", capture_output: bool = False) -> bool:
    """Run a command and return success status"""
    if description:
        print_info(f"{description}...")
    
    try:
        if capture_output:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True
        else:
            result = subprocess.run(cmd, check=True)
            return True
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {' '.join(cmd)}")
        if capture_output and hasattr(e, 'stdout') and e.stdout:
            print(e.stdout)
        if capture_output and hasattr(e, 'stderr') and e.stderr:
            print(e.stderr)
        return False
    except FileNotFoundError:
        print_error(f"Command not found: {cmd[0]}")
        return False


class TDDCLItools:
    """Test-Driven Development CLI Tools"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.test_dir = self.project_root / "tests"
        self.src_dir = self.project_root / "src"
    
    def watch_tests(self, pattern: Optional[str] = None, verbose: bool = False) -> None:
        """Watch files and automatically run tests on changes"""
        print_header("TDD WATCH MODE")
        print_info("Watching for file changes... Press Ctrl+C to stop")
        
        cmd = ["ptw", "--runner", "pytest"]
        
        if verbose:
            cmd.extend(["-v"])
        
        if pattern:
            cmd.extend(["-k", pattern])
        
        # Add pytest arguments for better output
        cmd.extend(["--", "-v", "--tb=short", "--strict-markers"])
        
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print_info("Watch mode stopped")
    
    def run_tests(self, 
                  pattern: Optional[str] = None,
                  coverage: bool = False,
                  parallel: bool = False,
                  failed_only: bool = False,
                  verbose: bool = False,
                  integration: bool = False) -> bool:
        """Run tests with various options"""
        
        print_header("RUNNING TESTS")
        
        cmd = ["pytest"]
        
        # Test selection
        if pattern:
            cmd.extend(["-k", pattern])
        
        if failed_only:
            cmd.append("--lf")  # Last failed
        
        if integration:
            cmd.extend(["-m", "integration"])
        else:
            cmd.extend(["-m", "not integration"])
        
        # Output options
        if verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")
        
        # Coverage
        if coverage:
            cmd.extend(["--cov=src/modern_gopher", "--cov-report=term-missing", "--cov-report=html"])
        
        # Parallel execution
        if parallel:
            cmd.extend(["-n", "auto"])
        
        # Better output
        cmd.extend(["--tb=short", "--strict-markers"])
        
        return run_command(cmd, "Running tests")
    
    def run_quick_tests(self) -> bool:
        """Run a quick subset of tests for TDD feedback"""
        print_header("QUICK TDD TESTS")
        
        cmd = [
            "pytest", 
            "-q", 
            "--tb=line",
            "-x",  # Stop on first failure
            "-m", "not integration",
            "--durations=10"
        ]
        
        return run_command(cmd, "Running quick tests")
    
    def run_coverage(self) -> bool:
        """Run full coverage analysis"""
        print_header("COVERAGE ANALYSIS")
        
        cmd = [
            "pytest",
            "--cov=src/modern_gopher",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=xml",
            "-q"
        ]
        
        success = run_command(cmd, "Analyzing test coverage")
        
        if success:
            print_success("Coverage report generated in htmlcov/index.html")
        
        return success
    
    def lint_code(self) -> bool:
        """Run linting tools"""
        print_header("CODE LINTING")
        
        success = True
        
        # Black formatting check
        if not run_command(["black", "--check", "src", "tests"], "Checking code formatting"):
            success = False
        
        # Import sorting check
        if not run_command(["isort", "--check-only", "src", "tests"], "Checking import sorting"):
            success = False
        
        # Flake8 linting
        if not run_command(["flake8", "src", "tests"], "Running flake8 linting"):
            success = False
        
        # Type checking
        if not run_command(["mypy", "src"], "Running type checking"):
            success = False
        
        if success:
            print_success("All linting checks passed!")
        else:
            print_error("Some linting checks failed")
        
        return success
    
    def fix_formatting(self) -> bool:
        """Auto-fix code formatting"""
        print_header("FIXING CODE FORMATTING")
        
        success = True
        
        if not run_command(["black", "src", "tests"], "Formatting code with Black"):
            success = False
        
        if not run_command(["isort", "src", "tests"], "Sorting imports"):
            success = False
        
        if success:
            print_success("Code formatting fixed!")
        
        return success
    
    def security_check(self) -> bool:
        """Run security analysis"""
        print_header("SECURITY ANALYSIS")
        
        success = True
        
        if not run_command(["bandit", "-r", "src"], "Running security analysis"):
            success = False
        
        if not run_command(["safety", "check"], "Checking dependencies for vulnerabilities"):
            success = False
        
        return success
    
    def create_test_file(self, module_name: str) -> None:
        """Create a new test file from template"""
        print_header("CREATING TEST FILE")
        
        test_file = self.test_dir / f"test_{module_name}.py"
        
        if test_file.exists():
            print_warning(f"Test file already exists: {test_file}")
            return
        
        template = f'''"""
Tests for {module_name} module
"""

import pytest
from unittest.mock import Mock, patch

# Import the module to test
# from modern_gopher.{module_name} import YourClass


class Test{module_name.title()}:
    """Test cases for {module_name} module"""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        pass
    
    def teardown_method(self):
        """Tear down test fixtures after each test method."""
        pass
    
    def test_placeholder(self):
        """Placeholder test - replace with actual tests"""
        # TODO: Write your first test here
        assert True
    
    @pytest.mark.parametrize("input_val,expected", [
        (1, 1),
        (2, 2),
        # Add more test cases
    ])
    def test_parametrized_example(self, input_val, expected):
        """Example of parametrized test"""
        assert input_val == expected
    
    def test_with_mock(self):
        """Example test using mocks"""
        with patch('some.module.function') as mock_func:
            mock_func.return_value = "mocked"
            # Your test code here
            assert True
'''
        
        test_file.write_text(template)
        print_success(f"Created test file: {test_file}")
    
    def run_specific_test(self, test_name: str) -> bool:
        """Run a specific test by name"""
        print_header(f"RUNNING SPECIFIC TEST: {test_name}")
        
        cmd = ["pytest", "-v", "-k", test_name, "--tb=short"]
        
        return run_command(cmd, f"Running test: {test_name}")
    
    def test_file(self, file_path: str) -> bool:
        """Run tests for a specific file"""
        print_header(f"TESTING FILE: {file_path}")
        
        cmd = ["pytest", "-v", file_path, "--tb=short"]
        
        return run_command(cmd, f"Testing file: {file_path}")
    
    def show_test_summary(self) -> None:
        """Show a summary of all tests"""
        print_header("TEST SUMMARY")
        
        cmd = ["pytest", "--collect-only", "-q"]
        
        run_command(cmd, "Collecting test information")
    
    def benchmark_tests(self) -> bool:
        """Run performance benchmarks if available"""
        print_header("PERFORMANCE BENCHMARKS")
        
        # Check if pytest-benchmark is available
        try:
            import pytest_benchmark
            cmd = ["pytest", "--benchmark-only", "-v"]
            return run_command(cmd, "Running performance benchmarks")
        except ImportError:
            print_warning("pytest-benchmark not installed. Install with: pip install pytest-benchmark")
            return False


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Test-Driven Development CLI for Modern Gopher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s watch                    # Watch files and auto-run tests
  %(prog)s test                     # Run all unit tests  
  %(prog)s test -c                  # Run tests with coverage
  %(prog)s test -p browser          # Run tests matching 'browser'
  %(prog)s quick                    # Run quick feedback tests
  %(prog)s lint                     # Run all linting tools
  %(prog)s fix                      # Auto-fix formatting issues
  %(prog)s security                 # Run security analysis
  %(prog)s create auth              # Create test_auth.py template
  %(prog)s file tests/test_cli.py   # Test specific file
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Watch command
    watch_parser = subparsers.add_parser('watch', help='Watch files and auto-run tests')
    watch_parser.add_argument('-p', '--pattern', help='Test pattern to match')
    watch_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run tests')
    test_parser.add_argument('-p', '--pattern', help='Test pattern to match')
    test_parser.add_argument('-c', '--coverage', action='store_true', help='Include coverage')
    test_parser.add_argument('-j', '--parallel', action='store_true', help='Run tests in parallel')
    test_parser.add_argument('-f', '--failed', action='store_true', help='Run only failed tests')
    test_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    test_parser.add_argument('-i', '--integration', action='store_true', help='Run integration tests')
    
    # Quick command
    subparsers.add_parser('quick', help='Run quick TDD feedback tests')
    
    # Coverage command
    subparsers.add_parser('coverage', help='Run full coverage analysis')
    
    # Lint command
    subparsers.add_parser('lint', help='Run linting tools')
    
    # Fix command
    subparsers.add_parser('fix', help='Auto-fix code formatting')
    
    # Security command
    subparsers.add_parser('security', help='Run security analysis')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create new test file')
    create_parser.add_argument('module', help='Module name for test file')
    
    # File command
    file_parser = subparsers.add_parser('file', help='Test specific file')
    file_parser.add_argument('path', help='Path to test file')
    
    # Specific test command
    specific_parser = subparsers.add_parser('run', help='Run specific test')
    specific_parser.add_argument('name', help='Test name to run')
    
    # Summary command
    subparsers.add_parser('summary', help='Show test summary')
    
    # Benchmark command
    subparsers.add_parser('benchmark', help='Run performance benchmarks')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    tdd = TDDCLItools()
    
    try:
        if args.command == 'watch':
            tdd.watch_tests(args.pattern, args.verbose)
        elif args.command == 'test':
            success = tdd.run_tests(
                pattern=args.pattern,
                coverage=args.coverage,
                parallel=args.parallel,
                failed_only=args.failed,
                verbose=args.verbose,
                integration=args.integration
            )
            sys.exit(0 if success else 1)
        elif args.command == 'quick':
            success = tdd.run_quick_tests()
            sys.exit(0 if success else 1)
        elif args.command == 'coverage':
            success = tdd.run_coverage()
            sys.exit(0 if success else 1)
        elif args.command == 'lint':
            success = tdd.lint_code()
            sys.exit(0 if success else 1)
        elif args.command == 'fix':
            success = tdd.fix_formatting()
            sys.exit(0 if success else 1)
        elif args.command == 'security':
            success = tdd.security_check()
            sys.exit(0 if success else 1)
        elif args.command == 'create':
            tdd.create_test_file(args.module)
        elif args.command == 'file':
            success = tdd.test_file(args.path)
            sys.exit(0 if success else 1)
        elif args.command == 'run':
            success = tdd.run_specific_test(args.name)
            sys.exit(0 if success else 1)
        elif args.command == 'summary':
            tdd.show_test_summary()
        elif args.command == 'benchmark':
            success = tdd.benchmark_tests()
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print_info("\nOperation cancelled by user")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

