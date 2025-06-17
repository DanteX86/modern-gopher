# Modern Gopher

A modern, feature-rich terminal-based client for the Gopher protocol built in Python.

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
```

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

