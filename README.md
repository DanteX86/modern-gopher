# Modern Gopher

[![CI/CD Pipeline](https://github.com/DanteX86/modern-gopher/actions/workflows/ci.yml/badge.svg)](https://github.com/DanteX86/modern-gopher/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/DanteX86/modern-gopher/branch/main/graph/badge.svg)](https://codecov.io/gh/DanteX86/modern-gopher)
[![PyPI version](https://badge.fury.io/py/modern-gopher.svg)](https://badge.fury.io/py/modern-gopher)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A modern, feature-rich terminal-based client for the Gopher protocol built in Python.

> 🔥 **New in v1.2.0**: Enhanced connection stability (60s timeout), improved error handling, and comprehensive bug fixes!

## 🎯 Current Status

### ✅ **Completed Features**
- **Core Protocol Implementation**: Full RFC 1436 compliant Gopher protocol support
- **URL Parsing**: Complete Gopher URL parsing with SSL/TLS support  
- **Rich CLI Interface**: Beautiful terminal output using Rich library
- **Caching System**: Memory and disk caching for improved performance
- **Multiple Item Types**: Support for all standard Gopher item types
- **IPv4/IPv6 Support**: Automatic or forced IP version selection
- **SSL/TLS Support**: Secure Gopher connections (gophers://)
- **Command-Line Tools**: `get`, `info`, and `browse` commands
- **Comprehensive Test Suite**: 224 tests covering protocol, client, types, CLI, HTML rendering, and browser functionality

### ✅ **Recently Completed**
- **Beautiful Soup HTML Rendering**: Full HTML content rendering with Beautiful Soup integration (100% complete)
- **Directory Search Functionality**: Interactive search within directories (100% complete)
- **Terminal Browser**: Interactive browser with navigation (100% complete)
- **Configuration System**: User preferences and settings (100% complete)
- **URL Input Dialog**: Direct URL entry in browser (100% complete)
- **Keybinding Fixes**: All keyboard shortcuts working properly
- **Bookmark Integration**: Full bookmark management in browser
- **BookmarkManager**: Complete bookmark system with persistence, search, tags, and visit tracking
- **Enhanced Help System**: Comprehensive keyboard shortcuts and feature documentation
- **Build System**: Integrated Python build CLI for package distribution
- **Customizable Keybinding System**: Full keybinding customization with context-aware shortcuts, conflict detection, and CLI management

### 📋 **Planned Features**
- **Plugin Architecture**: Extensible item type handlers
- **Enhanced Browser**: Advanced UI features like tabs and split-pane viewing
- **Session Management**: Persistent browser sessions across restarts
- **Advanced Search**: Full-text content search across multiple resources

## Installation

### Requirements

- Python 3.8+
- MacOS (tested on ARM64)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/modern-gopher.git
cd modern-gopher
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install the dependencies:
```bash
pip install -r requirements.txt
```

4. Install the package in development mode:
```bash
pip install -e .
```

## Usage

```bash
# Start the Gopher browser
modern-gopher browse gopher://gopher.floodgap.com

# Fetch a Gopher resource
modern-gopher get gopher://gopher.floodgap.com/0/gopher/proxy.txt

# Manage keybindings
modern-gopher keybindings list   # Show all keybindings
modern-gopher keybindings reset  # Reset to defaults
```

### Customizable Keybindings

Modern Gopher features a comprehensive keybinding system that allows full customization of keyboard shortcuts:

#### Default Keybindings
- **Navigation**: `↑`/`k` (up), `↓`/`j` (down), `Enter` (open), `Backspace` (back)
- **Global**: `q`/`Ctrl+C` (quit), `h`/`F1` (help)
- **Browser**: `r`/`F5` (refresh), `g`/`Ctrl+L` (go to URL)
- **Bookmarks**: `b`/`Ctrl+B` (toggle), `m` (list)
- **Search**: `/`/`Ctrl+F` (search), `Escape` (clear)

#### Keybinding Management
```bash
# List all current keybindings
modern-gopher keybindings list

# Reset to default keybindings
modern-gopher keybindings reset

# Edit keybindings manually
$EDITOR ~/.config/modern-gopher/keybindings.json
```

#### Features
- **Context-aware**: Different keybindings for browser, content, search contexts
- **Conflict detection**: Prevents conflicting keybinding assignments
- **Backup/restore**: Automatic backup before resetting
- **CLI management**: Full command-line interface for keybinding management
- **Persistent storage**: Keybindings saved to `~/.config/modern-gopher/keybindings.json`

See [docs/KEYBINDINGS.md](docs/KEYBINDINGS.md) for comprehensive keybinding documentation.

## Documentation

- **[User Guide](docs/USER_GUIDE.md)** - Comprehensive guide for new and experienced users
- **[Quick Reference](docs/QUICK_REFERENCE.md)** - Essential commands and shortcuts
- **[Manual](MANUAL.md)** - Complete technical documentation
- **[Keybindings](docs/KEYBINDINGS.md)** - Customizable keyboard shortcuts
- **[Changelog](CHANGELOG.md)** - Version history and release notes

## Development

1. Activate the virtual environment:
```bash
source venv/bin/activate
```

2. Run tests:
```bash
# Run unit tests only (fast)
python run_tests.py

# Run all tests including integration tests (requires network)
python run_tests.py --all

# Run with coverage reporting
python run_tests.py --coverage

# Run specific test file
python run_tests.py --file test_protocol

# Or use pytest directly
pytest                           # Run unit tests only
pytest --integration            # Run integration tests only
pytest -m "not integration"    # Run without integration tests
```

### Test Coverage

The project includes comprehensive test coverage with 224 tests:

- **Protocol Tests**: Socket creation, request/response handling, error conditions
- **Types Tests**: Gopher item types, directory parsing, file type detection  
- **Client Tests**: Caching, resource fetching, high-level operations
- **CLI Tests**: Argument parsing, command execution, error handling
- **Browser Tests**: Terminal browser functionality, history, bookmarks, search
- **HTML Renderer Tests**: Beautiful Soup integration, HTML parsing and rendering
- **Configuration Tests**: User preferences, settings persistence
- **Keybinding Tests**: Keyboard shortcuts, validation, conflict detection
- **Integration Tests**: Real network connections to public Gopher servers
- **URL Tests**: URL parsing, validation, and construction

Tests are organized into unit tests (fast, no network) and integration tests (require network access).

## License

MIT

