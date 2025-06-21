#!/usr/bin/env python3
"""
Modern Gopher Project Cleanup CLI

A comprehensive cleanup tool for managing test artifacts, cache files,
and other temporary files in the Modern Gopher project.
"""

import argparse
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import List, Set

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

class CleanupCLI:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.dry_run = False
        self.verbose = False
        self.files_removed = 0
        self.dirs_removed = 0
        self.space_freed = 0
        
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
        
    def get_directory_size(self, path: Path) -> int:
        """Calculate directory size in bytes."""
        if not path.exists() or not path.is_dir():
            return 0
            
        total_size = 0
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    total_size += entry.stat().st_size
        except (OSError, PermissionError):
            pass
        return total_size
    
    def format_size(self, size_bytes: int) -> str:
        """Format size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}TB"
    
    def remove_path(self, path: Path, description: str = ""):
        """Safely remove a file or directory."""
        if not path.exists():
            return
            
        try:
            size = 0
            if path.is_file():
                size = path.stat().st_size
                if not self.dry_run:
                    path.unlink()
                self.files_removed += 1
                action = "Would remove" if self.dry_run else "Removed"
                self.log_action(f"{action} file: {path} {description}")
                
            elif path.is_dir():
                size = self.get_directory_size(path)
                if not self.dry_run:
                    shutil.rmtree(path)
                self.dirs_removed += 1
                action = "Would remove" if self.dry_run else "Removed"
                self.log_action(f"{action} directory: {path} {description}")
                
            self.space_freed += size
            
        except (OSError, PermissionError) as e:
            self.log_error(f"Failed to remove {path}: {e}")
    
    def find_mock_directories(self) -> List[Path]:
        """Find all mock test artifact directories."""
        mock_dirs = []
        patterns = [
            "<Mock name='get_config().config_dir'*",
            "<Mock name='mock.config_dir'*",
            "Mock*",
        ]
        
        for pattern in patterns:
            mock_dirs.extend(self.project_root.glob(pattern))
            
        return [d for d in mock_dirs if d.is_dir()]
    
    def find_cache_files(self) -> List[Path]:
        """Find Python cache files and directories."""
        cache_items = []
        
        # __pycache__ directories
        cache_items.extend(self.project_root.rglob("__pycache__"))
        
        # .pyc files
        cache_items.extend(self.project_root.rglob("*.pyc"))
        
        # .pyo files
        cache_items.extend(self.project_root.rglob("*.pyo"))
        
        return cache_items
    
    def find_test_artifacts(self) -> List[Path]:
        """Find test-related artifacts."""
        artifacts = []
        
        # pytest cache
        pytest_cache = self.project_root / ".pytest_cache"
        if pytest_cache.exists():
            artifacts.append(pytest_cache)
            
        # coverage files
        artifacts.extend(self.project_root.glob(".coverage*"))
        
        # htmlcov directory
        htmlcov = self.project_root / "htmlcov"
        if htmlcov.exists():
            artifacts.append(htmlcov)
            
        # .tox directory
        tox_dir = self.project_root / ".tox"
        if tox_dir.exists():
            artifacts.append(tox_dir)
            
        return artifacts
    
    def find_build_artifacts(self) -> List[Path]:
        """Find build and distribution artifacts."""
        artifacts = []
        
        # build directory
        build_dir = self.project_root / "build"
        if build_dir.exists():
            artifacts.append(build_dir)
            
        # dist directory
        dist_dir = self.project_root / "dist"
        if dist_dir.exists():
            artifacts.append(dist_dir)
            
        # .egg-info directories
        artifacts.extend(self.project_root.glob("*.egg-info"))
        
        # .eggs directory
        eggs_dir = self.project_root / ".eggs"
        if eggs_dir.exists():
            artifacts.append(eggs_dir)
            
        return artifacts
    
    def find_editor_files(self) -> List[Path]:
        """Find editor temporary files."""
        files = []
        
        # Vim files
        files.extend(self.project_root.rglob("*.swp"))
        files.extend(self.project_root.rglob("*.swo"))
        files.extend(self.project_root.rglob("*~"))
        
        # Emacs files
        files.extend(self.project_root.rglob("#*#"))
        files.extend(self.project_root.rglob(".#*"))
        
        # VS Code files
        vscode_dir = self.project_root / ".vscode"
        if vscode_dir.exists() and (vscode_dir / "settings.json").exists():
            # Only remove if it contains default/generated content
            pass
            
        return files
    
    def find_macos_files(self) -> List[Path]:
        """Find macOS specific files."""
        files = []
        
        # .DS_Store files
        files.extend(self.project_root.rglob(".DS_Store"))
        
        # .AppleDouble directories
        files.extend(self.project_root.rglob(".AppleDouble"))
        
        # .LSOverride files
        files.extend(self.project_root.rglob(".LSOverride"))
        
        return files
    
    def cleanup_mock_artifacts(self):
        """Clean up mock test artifacts."""
        self.log_info("Cleaning up mock test artifacts...")
        mock_dirs = self.find_mock_directories()
        
        if not mock_dirs:
            self.log_success("No mock artifacts found")
            return
            
        for mock_dir in mock_dirs:
            self.remove_path(mock_dir, "(mock test artifact)")
            
        self.log_success(f"Cleaned up {len(mock_dirs)} mock artifacts")
    
    def cleanup_cache(self):
        """Clean up Python cache files."""
        self.log_info("Cleaning up Python cache files...")
        cache_items = self.find_cache_files()
        
        if not cache_items:
            self.log_success("No cache files found")
            return
            
        for item in cache_items:
            self.remove_path(item, "(Python cache)")
            
        self.log_success(f"Cleaned up {len(cache_items)} cache items")
    
    def cleanup_test_artifacts(self):
        """Clean up test artifacts."""
        self.log_info("Cleaning up test artifacts...")
        artifacts = self.find_test_artifacts()
        
        if not artifacts:
            self.log_success("No test artifacts found")
            return
            
        for artifact in artifacts:
            self.remove_path(artifact, "(test artifact)")
            
        self.log_success(f"Cleaned up {len(artifacts)} test artifacts")
    
    def cleanup_build_artifacts(self):
        """Clean up build artifacts."""
        self.log_info("Cleaning up build artifacts...")
        artifacts = self.find_build_artifacts()
        
        if not artifacts:
            self.log_success("No build artifacts found")
            return
            
        for artifact in artifacts:
            self.remove_path(artifact, "(build artifact)")
            
        self.log_success(f"Cleaned up {len(artifacts)} build artifacts")
    
    def cleanup_editor_files(self):
        """Clean up editor temporary files."""
        self.log_info("Cleaning up editor temporary files...")
        files = self.find_editor_files()
        
        if not files:
            self.log_success("No editor temporary files found")
            return
            
        for file in files:
            self.remove_path(file, "(editor temp file)")
            
        self.log_success(f"Cleaned up {len(files)} editor temporary files")
    
    def cleanup_macos_files(self):
        """Clean up macOS specific files."""
        self.log_info("Cleaning up macOS files...")
        files = self.find_macos_files()
        
        if not files:
            self.log_success("No macOS files found")
            return
            
        for file in files:
            self.remove_path(file, "(macOS file)")
            
        self.log_success(f"Cleaned up {len(files)} macOS files")
    
    def show_summary(self):
        """Show cleanup summary."""
        print(f"\n{Colors.WHITE}🧹 Cleanup Summary{Colors.NC}")
        print("=" * 50)
        print(f"Files removed: {Colors.GREEN}{self.files_removed}{Colors.NC}")
        print(f"Directories removed: {Colors.GREEN}{self.dirs_removed}{Colors.NC}")
        print(f"Space freed: {Colors.GREEN}{self.format_size(self.space_freed)}{Colors.NC}")
        
        if self.dry_run:
            print(f"\n{Colors.YELLOW}Note: This was a dry run. Use --execute to actually remove files.{Colors.NC}")
    
    def run_full_cleanup(self):
        """Run all cleanup operations."""
        self.log_info(f"Starting full cleanup of {self.project_root}")
        
        if self.dry_run:
            self.log_warning("DRY RUN MODE - No files will be actually removed")
        
        # Order matters - most specific to least specific
        self.cleanup_mock_artifacts()
        self.cleanup_test_artifacts()
        self.cleanup_cache()
        self.cleanup_build_artifacts()
        self.cleanup_editor_files()
        self.cleanup_macos_files()
        
        self.show_summary()

def main():
    parser = argparse.ArgumentParser(
        description="Modern Gopher Project Cleanup CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --mock                    # Clean only mock artifacts
  %(prog)s --cache                   # Clean only cache files
  %(prog)s --test                    # Clean only test artifacts
  %(prog)s --all                     # Clean everything
  %(prog)s --all --dry-run           # Show what would be cleaned
  %(prog)s --all --execute           # Actually perform cleanup
        """
    )
    
    # Cleanup options
    parser.add_argument("--mock", action="store_true", help="Clean mock test artifacts")
    parser.add_argument("--cache", action="store_true", help="Clean Python cache files")
    parser.add_argument("--test", action="store_true", help="Clean test artifacts")
    parser.add_argument("--build", action="store_true", help="Clean build artifacts")
    parser.add_argument("--editor", action="store_true", help="Clean editor temporary files")
    parser.add_argument("--macos", action="store_true", help="Clean macOS files")
    parser.add_argument("--all", action="store_true", help="Clean everything")
    
    # Execution options
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Show what would be cleaned (default)")
    parser.add_argument("--execute", action="store_true",
                        help="Actually perform cleanup operations")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose output")
    
    # Project options
    parser.add_argument("--project-root", type=Path,
                        help="Project root directory (default: current directory)")
    
    args = parser.parse_args()
    
    # Set up cleanup instance
    cleanup = CleanupCLI(args.project_root)
    cleanup.dry_run = not args.execute
    cleanup.verbose = args.verbose
    
    # Determine what to clean
    if not any([args.mock, args.cache, args.test, args.build, args.editor, args.macos, args.all]):
        # Default to showing mock artifacts if no specific option given
        args.mock = True
    
    # Run cleanup operations
    try:
        if args.all:
            cleanup.run_full_cleanup()
        else:
            if args.mock:
                cleanup.cleanup_mock_artifacts()
            if args.cache:
                cleanup.cleanup_cache()
            if args.test:
                cleanup.cleanup_test_artifacts()
            if args.build:
                cleanup.cleanup_build_artifacts()
            if args.editor:
                cleanup.cleanup_editor_files()
            if args.macos:
                cleanup.cleanup_macos_files()
            
            cleanup.show_summary()
            
    except KeyboardInterrupt:
        cleanup.log_warning("Cleanup interrupted by user")
        sys.exit(130)
    except Exception as e:
        cleanup.log_error(f"Cleanup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

