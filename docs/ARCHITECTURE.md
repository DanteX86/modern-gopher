# Modern-Gopher Architecture

## Overview

Modern-Gopher is a sophisticated terminal-based Gopher protocol client built with a modular, layered architecture that emphasizes separation of concerns, extensibility, and maintainability.

## Table of Contents

- [System Architecture](#system-architecture)
- [Core Components](#core-components)
- [Data Flow](#data-flow)
- [Plugin System](#plugin-system)
- [Browser Architecture](#browser-architecture)
- [Caching Strategy](#caching-strategy)
- [Configuration System](#configuration-system)
- [Session Management](#session-management)
- [Testing Architecture](#testing-architecture)

---

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Modern-Gopher                           │
├─────────────────────────────────────────────────────────────────┤
│  CLI Interface           │  Terminal Browser    │   GUI (Future)│
├─────────────────────────────────────────────────────────────────┤
│                   Application Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  Plugin System   │  Content Processing  │  Session Management  │
├─────────────────────────────────────────────────────────────────┤
│                      Core Library                              │
├─────────────────────────────────────────────────────────────────┤
│  Client API      │  Protocol Handler    │  Type System         │
├─────────────────────────────────────────────────────────────────┤
│  Configuration   │  Caching Layer       │  Bookmark System     │
├─────────────────────────────────────────────────────────────────┤
│                     Infrastructure                              │
├─────────────────────────────────────────────────────────────────┤
│  Networking      │  File I/O            │  Logging             │
└─────────────────────────────────────────────────────────────────┘
```

### Architecture Principles

1. **Layered Design**: Clear separation between presentation, application, and infrastructure layers
2. **Modularity**: Loose coupling between components with well-defined interfaces
3. **Extensibility**: Plugin architecture allows easy feature additions
4. **Testability**: Dependency injection and mocking support comprehensive testing
5. **Configuration-Driven**: Behavior controlled through configuration files
6. **Caching**: Multi-level caching for performance optimization

---

## Core Components

### 1. Core Package (`src/modern_gopher/core/`)

The foundation layer providing essential Gopher protocol functionality.

```
core/
├── __init__.py          # Package initialization
├── protocol.py          # Low-level Gopher protocol implementation
├── client.py            # High-level client API with caching
├── types.py             # Gopher type system and parsing
└── url.py               # URL parsing and manipulation
```

**Key Responsibilities:**
- Gopher protocol implementation (RFC 1436 compliant)
- Socket management with IPv4/IPv6 support
- URL parsing and validation
- Type system for Gopher items
- High-level client interface

### 2. Browser Package (`src/modern_gopher/browser/`)

Interactive terminal browser implementation.

```
browser/
├── __init__.py          # Package exports
├── terminal.py          # Main browser implementation
├── bookmarks.py         # Bookmark management
└── sessions.py          # Session persistence
```

**Key Features:**
- Full-screen terminal UI using prompt_toolkit
- Navigation history management
- Bookmark system with tagging and search
- Session save/restore functionality
- Context-aware keybindings

### 3. Plugin System (`src/modern_gopher/plugins/`)

Extensible plugin architecture for content processing.

```
plugins/
├── __init__.py          # Plugin exports
├── base.py              # Base plugin classes and interfaces
├── manager.py           # Plugin lifecycle management
└── builtin/             # Built-in plugins
    ├── __init__.py
    ├── image_handler.py     # Image content processing
    ├── markdown_processor.py # Markdown rendering
    └── text_cleaner.py      # Text content enhancement
```

**Plugin Types:**
- **ItemTypeHandler**: Process specific Gopher item types
- **ContentProcessor**: Transform content during display
- **ProtocolExtension**: Extend protocol capabilities

### 4. Configuration System (`src/modern_gopher/config.py`)

Centralized configuration management with validation.

**Features:**
- YAML-based configuration files
- Type validation and defaults
- Hierarchical settings (user/system/defaults)
- Runtime configuration updates
- Environment variable support

### 5. Content Processing (`src/modern_gopher/content/`)

Content rendering and transformation.

```
content/
├── __init__.py
└── html_renderer.py     # HTML to terminal text conversion
```

---

## Data Flow

### Request Processing Flow

```
User Input
    │
    ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Parser    │───▶│  Browser UI     │───▶│  User Action    │
│  (argparse)     │    │ (prompt_toolkit)│    │   Handler       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │  GopherClient   │
                                               │   (caching)     │
                                               └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │ Protocol Layer  │
                                               │ (socket/HTTP)   │
                                               └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │ Gopher Server   │
                                               └─────────────────┘
```

### Content Processing Pipeline

```
Raw Content
    │
    ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Type          │───▶│   Plugin        │───▶│   Display       │
│ Detection       │    │  Pipeline       │    │  Rendering      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
    │                          │                        │
    ▼                          ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ GopherItemType  │    │ Content         │    │ Terminal        │
│   Analysis      │    │ Processors      │    │  Output         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## Plugin System

### Plugin Architecture

The plugin system is designed for maximum flexibility and extensibility.

#### Plugin Hierarchy

```
BasePlugin (ABC)
    │
    ├── ItemTypeHandler
    │   ├── ImageHandler
    │   └── CustomHandler
    │
    ├── ContentProcessor  
    │   ├── MarkdownProcessor
    │   ├── TextCleaner
    │   └── CustomProcessor
    │
    └── ProtocolExtension
        └── CustomProtocol
```

#### Plugin Lifecycle

1. **Discovery**: Plugins found in configured directories
2. **Registration**: Plugins registered with PluginManager
3. **Initialization**: Plugin `initialize()` called
4. **Processing**: Content passed through plugin pipeline
5. **Shutdown**: Plugin `shutdown()` called on exit

#### Plugin Configuration

```yaml
plugins:
  enabled:
    - image_handler
    - markdown_processor
    - text_cleaner
  
  configs:
    text_cleaner:
      strip_content: true
      fix_encoding: true
      max_blank_lines: 2
    
    markdown_processor:
      render_tables: true
      syntax_highlighting: false
```

---

## Browser Architecture

### Terminal Browser Components

The browser uses a component-based architecture with prompt_toolkit.

```
┌─────────────────────────────────────────────────────────────────┐
│                        Browser Window                          │
├─────────────────────────────────────────────────────────────────┤
│                        Menu Area                               │
│  [📁 Directory Listing or Content Display]                    │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                      Content Area                              │
│  [📄 Text content, HTML rendering, or item details]           │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                       Status Bar                               │
│  [URL] [Status] [Bookmarked] [History: n/m] [Help: F1]        │
└─────────────────────────────────────────────────────────────────┘
```

#### Component Responsibilities

- **MenuControl**: Directory navigation and item selection
- **ContentView**: Text display with scrolling and search
- **StatusBar**: Current state and navigation information
- **LayoutManager**: Dynamic layout based on content type

#### State Management

```python
BrowserState = {
    'current_url': str,
    'current_items': List[GopherItem],
    'filtered_items': List[GopherItem],
    'selected_index': int,
    'search_query': str,
    'is_searching': bool,
    'history_position': int
}
```

---

## Caching Strategy

### Multi-Level Caching

Modern-Gopher implements a sophisticated caching system for optimal performance.

#### Cache Hierarchy

```
Request
    │
    ▼
┌─────────────────┐    Hit    ┌─────────────────┐
│  Memory Cache   │─────────▶ │     Return      │
│   (LRU, 100)    │           │    Content      │
└─────────────────┘           └─────────────────┘
    │ Miss
    ▼
┌─────────────────┐    Hit    ┌─────────────────┐
│   Disk Cache    │─────────▶ │  Load & Store   │
│  (Persistent)   │           │   in Memory     │
└─────────────────┘           └─────────────────┘
    │ Miss
    ▼
┌─────────────────┐           ┌─────────────────┐
│  Network Fetch  │─────────▶ │ Store in Both   │
│   (Protocol)    │           │     Caches      │
└─────────────────┘           └─────────────────┘
```

#### Cache Types

1. **Memory Cache**
   - LRU eviction policy
   - Configurable TTL (default: 1 hour)
   - Automatic cleanup of expired entries
   - Size limit: 100 entries

2. **Disk Cache**
   - Persistent across sessions
   - JSON metadata + binary data files
   - Configurable location (`~/.cache/modern-gopher`)
   - Respects TTL settings

#### Cache Key Generation

```python
def _cache_key(self, url: Union[str, GopherURL]) -> str:
    """Generate MD5 hash of URL for cache key"""
    return hashlib.md5(str(url).encode()).hexdigest()
```

---

## Configuration System

### Configuration Hierarchy

```
Configuration Sources (Priority Order):
1. Command-line arguments (highest)
2. Environment variables
3. User config file (~/.config/modern-gopher/config.yaml)
4. System config file (/etc/modern-gopher/config.yaml)
5. Default values (lowest)
```

### Configuration Schema

```yaml
# ~/.config/modern-gopher/config.yaml
gopher:
  timeout: 60
  default_port: 70
  use_ipv6: auto
  
browser:
  initial_url: "gopher://gopher.floodgap.com"
  max_history_items: 100
  color_scheme: "default"
  
cache:
  enabled: true
  directory: "~/.cache/modern-gopher"
  ttl: 3600
  max_memory_items: 100
  
plugins:
  enabled:
    - image_handler
    - markdown_processor
    - text_cleaner
  
bookmarks:
  file: "~/.config/modern-gopher/bookmarks.json"
  auto_save: true
  
sessions:
  enabled: true
  file: "~/.config/modern-gopher/sessions.json"
  max_sessions: 10
  backup_sessions: 5
  
keybindings:
  file: "~/.config/modern-gopher/keybindings.json"
  
logging:
  level: "INFO"
  file: "~/.config/modern-gopher/logs/modern-gopher.log"
```

---

## Session Management

### Session Architecture

Sessions provide persistent browser state across application restarts.

#### Session Data Structure

```python
BrowserSession = {
    'name': str,
    'created': datetime,
    'last_accessed': datetime,
    'current_url': str,
    'history': List[str],
    'history_position': int,
    'bookmarks': List[Bookmark],
    'tags': List[str],
    'metadata': Dict[str, Any]
}
```

#### Session Operations

- **Auto-save**: Automatic session saving on navigation
- **Manual save**: User-initiated session creation
- **Restore**: Load previous session state
- **Management**: List, delete, rename sessions
- **Export/Import**: Backup and transfer sessions

---

## Testing Architecture

### Test Organization

```
tests/
├── test_protocol.py         # Low-level protocol tests
├── test_client.py           # Client API tests  
├── test_types.py            # Type system tests
├── test_url_parsing.py      # URL parsing tests
├── test_browser.py          # Browser functionality tests
├── test_config.py           # Configuration tests
├── test_plugins_*.py        # Plugin system tests
├── test_html_renderer.py    # Content rendering tests
├── test_keybindings.py      # Keybinding tests
├── test_cli.py              # CLI interface tests
└── test_integration.py      # End-to-end tests
```

### Test Categories

1. **Unit Tests** (Fast, no network)
   - Mock external dependencies
   - Test individual components
   - 841 total tests

2. **Integration Tests** (Network required)
   - Real Gopher server connections
   - End-to-end workflows
   - Marked with `@pytest.mark.integration`

3. **Test Infrastructure**
   - Custom pytest fixtures
   - Mock implementations
   - Coverage reporting (pytest-cov)

### Mocking Strategy

- **Network calls**: Mock socket operations
- **File I/O**: Use temporary directories
- **Configuration**: Mock config objects
- **Plugins**: Mock plugin interfaces

---

## Performance Considerations

### Optimization Strategies

1. **Lazy Loading**: Components initialized on first use
2. **Connection Pooling**: Reuse connections where possible
3. **Efficient Parsing**: Streaming parsers for large content
4. **Memory Management**: Automatic cache cleanup
5. **Async Operations**: Non-blocking UI during network operations

### Bottlenecks and Mitigations

- **Network Latency**: Multi-level caching
- **Large Directories**: Pagination and filtering
- **Memory Usage**: LRU cache with size limits
- **UI Responsiveness**: Background loading with progress indicators

---

## Future Architecture Considerations

### Planned Enhancements

1. **Async/Await Support**: Non-blocking network operations
2. **GUI Interface**: PySide6-based graphical browser
3. **Multi-tab Support**: Concurrent browsing sessions
4. **Advanced Search**: Full-text indexing and search
5. **Plugin Marketplace**: Remote plugin discovery and installation

### Scalability

- **Plugin System**: Supports unlimited custom plugins
- **Configuration**: Hierarchical and extensible
- **Caching**: Configurable limits and policies
- **Testing**: Comprehensive coverage for reliability

---

## Developer Guidelines

### Adding New Features

1. **Follow layered architecture**: Place components in appropriate layers
2. **Implement interfaces**: Use abstract base classes where appropriate
3. **Add comprehensive tests**: Both unit and integration tests
4. **Update documentation**: API docs and architecture changes
5. **Consider plugins**: Can the feature be implemented as a plugin?

### Plugin Development

1. **Inherit from BasePlugin**: Use appropriate plugin base class
2. **Implement required methods**: Follow plugin interface contracts
3. **Handle errors gracefully**: Don't break the plugin pipeline
4. **Provide configuration**: Allow users to customize behavior
5. **Write tests**: Test plugin functionality independently

---

This architecture provides a solid foundation for Modern-Gopher's current functionality while maintaining flexibility for future enhancements. The modular design ensures that components can be developed, tested, and maintained independently while working together seamlessly.
