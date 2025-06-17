# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions CI/CD pipeline
- Modern pyproject.toml configuration
- Security scanning with bandit and safety
- Code formatting with black and isort
- Type checking with mypy
- Coverage reporting integration

### Changed
- Improved repository organization and .gitignore
- Updated development workflows

## [0.2.0] - 2025-06-17

### Added
- Comprehensive session management system
- Context-aware keybinding system with CLI management
- Enhanced configuration system with validation
- Beautiful Soup HTML rendering integration
- Directory search functionality
- URL input dialog for browser
- Bookmark management with persistence and search
- Build system with integrated Python CLI

### Improved
- Terminal browser with advanced navigation
- Help system with comprehensive documentation
- Test coverage (260 tests)
- Code organization and structure

### Fixed
- All keyboard shortcuts working properly
- Browser stability and performance
- Configuration persistence

## [0.1.0] - 2025-06-10

### Added
- Initial project setup
- Core Gopher protocol implementation (RFC 1436 compliant)
- URL parsing with SSL/TLS support
- Rich CLI interface with beautiful terminal output
- Caching system (memory and disk)
- Support for all standard Gopher item types
- IPv4/IPv6 support with automatic or forced selection
- SSL/TLS support for secure connections (gophers://)
- Command-line tools: `get`, `info`, and `browse` commands
- Basic terminal browser functionality
- Comprehensive test suite
- MIT License

### Technical Details
- Python 3.8+ compatibility
- Rich library integration for terminal UI
- Prompt Toolkit for interactive features
- Beautiful Soup for HTML content handling
- PyYAML for configuration management
- Comprehensive error handling and logging

---

## Release Notes

### Version 0.2.0 Highlights
This release represents a major milestone with the completion of core browser functionality, session management, and a sophisticated keybinding system. The project now provides a full-featured Gopher client suitable for daily use.

### Version 0.1.0 Highlights
Initial release establishing the foundation with a solid protocol implementation and basic browser functionality.

