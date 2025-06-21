# Modern-Gopher API Reference

## Overview

This document provides comprehensive API documentation for the Modern-Gopher library, covering all public classes, methods, and interfaces.

## Table of Contents

- [Core API](#core-api)
  - [GopherClient](#gopherclient)
  - [GopherURL](#gopherurl)
  - [GopherItem](#gopheritem)
  - [GopherItemType](#gopheritemtype)
- [Browser API](#browser-api)
  - [GopherBrowser](#gopherbrowser)
  - [HistoryManager](#historymanager)
- [Configuration API](#configuration-api)
  - [ModernGopherConfig](#moderngopherconfig)
- [Plugin API](#plugin-api)
  - [BasePlugin](#baseplugin)
  - [PluginManager](#pluginmanager)
- [Content API](#content-api)
  - [HTMLRenderer](#htmlrenderer)
- [CLI API](#cli-api)

---

## Core API

### GopherClient

The main client interface for interacting with Gopher servers.

#### Constructor

```python
GopherClient(
    timeout: int = 30,
    cache_dir: Optional[str] = None,
    use_ipv6: Optional[bool] = None,
    cache_ttl: int = 3600
)
```

**Parameters:**
- `timeout` (int): Socket timeout in seconds (default: 30)
- `cache_dir` (Optional[str]): Directory for caching resources (None disables caching)
- `use_ipv6` (Optional[bool]): IPv6 preference (None for auto-detect)
- `cache_ttl` (int): Time-to-live for cached items in seconds (default: 3600)

#### Methods

##### `get_resource(url, save_to_file=None)`

Fetch a Gopher resource from the specified URL.

```python
def get_resource(
    self, 
    url: Union[str, GopherURL], 
    save_to_file: Optional[str] = None
) -> Union[List[GopherItem], str, bytes]
```

**Parameters:**
- `url`: Gopher URL to fetch
- `save_to_file`: Optional file path to save binary content

**Returns:**
- `List[GopherItem]`: For directory listings
- `str`: For text content
- `bytes`: For binary content

**Raises:**
- `ProtocolError`: On connection or protocol errors
- `ValueError`: On invalid URLs

**Example:**
```python
client = GopherClient()
items = client.get_resource("gopher://gopher.floodgap.com/")
text = client.get_resource("gopher://gopher.floodgap.com/0/gopher/proxy.txt")
```

##### `fetch_directory(url)`

Fetch and parse a Gopher directory listing.

```python
def fetch_directory(self, url: Union[str, GopherURL]) -> List[GopherItem]
```

**Parameters:**
- `url`: Gopher URL pointing to a directory

**Returns:**
- `List[GopherItem]`: Parsed directory items

##### `fetch_text(url)`

Fetch text content from a Gopher URL.

```python
def fetch_text(self, url: Union[str, GopherURL]) -> str
```

**Parameters:**
- `url`: Gopher URL pointing to text content

**Returns:**
- `str`: Text content

##### `fetch_binary(url)`

Fetch binary content from a Gopher URL.

```python
def fetch_binary(self, url: Union[str, GopherURL]) -> bytes
```

**Parameters:**
- `url`: Gopher URL pointing to binary content

**Returns:**
- `bytes`: Binary content

##### `download_file(url, filename)`

Download a file from a Gopher URL to local storage.

```python
def download_file(self, url: Union[str, GopherURL], filename: str) -> None
```

**Parameters:**
- `url`: Gopher URL to download
- `filename`: Local file path to save to

---

### GopherURL

Represents a parsed Gopher URL with easy access to components.

#### Constructor

```python
GopherURL(
    host: str,
    port: int = 70,
    item_type: str = "1",
    selector: str = "",
    use_ssl: bool = False,
    query: Optional[str] = None
)
```

#### Properties

- `host` (str): Server hostname
- `port` (int): Server port
- `item_type` (str): Gopher item type character
- `selector` (str): Resource selector
- `use_ssl` (bool): Whether to use SSL/TLS
- `query` (Optional[str]): Query string

#### Methods

##### `to_tuple()`

Convert URL to tuple format for protocol functions.

```python
def to_tuple(self) -> Tuple[str, int, str, str, bool]
```

**Returns:**
- `Tuple`: (host, port, item_type, selector, use_ssl)

##### `join(path)`

Join a relative path to this URL.

```python
def join(self, path: str) -> "GopherURL"
```

**Example:**
```python
url = GopherURL("gopher.example.com")
new_url = url.join("/subdir/file.txt")
```

---

### GopherItem

Represents a single item in a Gopher directory listing.

#### Constructor

```python
GopherItem(
    item_type: GopherItemType,
    display_string: str,
    selector: str,
    host: str,
    port: int
)
```

#### Properties

- `item_type` (GopherItemType): Type of the item
- `display_string` (str): Human-readable description
- `selector` (str): Resource selector
- `host` (str): Server hostname
- `port` (int): Server port

#### Methods

##### `to_menu_line()`

Convert item back to Gopher menu format.

```python
def to_menu_line(self) -> str
```

##### `from_menu_line(line)`

Parse a Gopher menu line into a GopherItem.

```python
@staticmethod
def from_menu_line(line: str) -> Optional["GopherItem"]
```

---

### GopherItemType

Enumeration of Gopher item types with utility methods.

#### Class Methods

##### `from_char(char)`

Get item type from character.

```python
@classmethod
def from_char(cls, char: str) -> "GopherItemType"
```

#### Properties

- `is_text` (bool): Whether item contains text
- `is_binary` (bool): Whether item contains binary data
- `is_interactive` (bool): Whether item is interactive
- `mime_type` (str): MIME type for the content
- `extension` (str): Typical file extension
- `display_name` (str): Human-readable name

---

## Browser API

### GopherBrowser

Terminal-based interactive Gopher browser.

#### Constructor

```python
GopherBrowser(
    initial_url: str = "gopher://gopher.floodgap.com",
    timeout: int = 30,
    use_ssl: bool = False,
    use_ipv6: Optional[bool] = None,
    cache_dir: Optional[str] = None,
    config: Optional[ModernGopherConfig] = None
)
```

#### Methods

##### `run()`

Start the interactive browser.

```python
def run(self) -> None
```

##### `navigate_to(url)`

Navigate to a specific URL.

```python
def navigate_to(self, url: str) -> None
```

##### `go_back()`

Navigate back in history.

```python
def go_back(self) -> None
```

##### `go_forward()`

Navigate forward in history.

```python
def go_forward(self) -> None
```

##### `refresh()`

Refresh the current page.

```python
def refresh(self) -> None
```

##### `toggle_bookmark()`

Toggle bookmark for current URL.

```python
def toggle_bookmark(self) -> None
```

##### `search(query)`

Search within current directory.

```python
def search(self, query: str) -> None
```

---

### HistoryManager

Manages browser navigation history.

#### Constructor

```python
HistoryManager(max_size: int = 100)
```

#### Methods

##### `add(url)`

Add URL to history.

```python
def add(self, url: str) -> None
```

##### `back()`

Go back in history.

```python
def back(self) -> Optional[str]
```

##### `forward()`

Go forward in history.

```python
def forward(self) -> Optional[str]
```

##### `current()`

Get current URL.

```python
def current(self) -> Optional[str]
```

---

## Configuration API

### ModernGopherConfig

Configuration management for Modern-Gopher.

#### Constructor

```python
ModernGopherConfig(
    config_dir: str = "~/.config/modern-gopher",
    cache_directory: str = "~/.cache/modern-gopher",
    initial_url: str = "",
    ...
)
```

#### Methods

##### `save(filepath)`

Save configuration to file.

```python
def save(self, filepath: Optional[str] = None) -> None
```

##### `load(filepath)`

Load configuration from file.

```python
@classmethod
def load(cls, filepath: str) -> "ModernGopherConfig"
```

##### `get_value(key_path)`

Get configuration value by key path.

```python
def get_value(self, key_path: str) -> Any
```

##### `set_value(key_path, value)`

Set configuration value by key path.

```python
def set_value(self, key_path: str, value: Any) -> None
```

##### `validate()`

Validate configuration values.

```python
def validate(self) -> bool
```

---

## Plugin API

### BasePlugin

Base class for all plugins.

#### Constructor

```python
BasePlugin(config: Optional[Dict[str, Any]] = None)
```

#### Methods

##### `initialize()`

Initialize the plugin.

```python
def initialize(self) -> None
```

##### `shutdown()`

Shutdown the plugin.

```python
def shutdown(self) -> None
```

##### `configure(config)`

Configure the plugin.

```python
def configure(self, config: Dict[str, Any]) -> None
```

##### `get_priority()`

Get plugin priority.

```python
def get_priority(self) -> int
```

---

### PluginManager

Manages plugin lifecycle and execution.

#### Methods

##### `initialize()`

Initialize all plugins.

```python
def initialize(self) -> None
```

##### `process_content(content, metadata)`

Process content through plugin pipeline.

```python
def process_content(
    self, 
    content: Any, 
    metadata: Optional[Dict[str, Any]] = None,
    item: Optional[GopherItem] = None
) -> Any
```

##### `get_available_plugins()`

Get list of available plugins.

```python
def get_available_plugins(self) -> List[Dict[str, Any]]
```

---

## Content API

### HTMLRenderer

Renders HTML content for terminal display.

#### Methods

##### `render(html_content)`

Render HTML to terminal-friendly text.

```python
def render(
    self, 
    html_content: str, 
    extract_links: bool = True,
    terminal_width: int = 80
) -> Tuple[str, List[Dict[str, str]]]
```

**Parameters:**
- `html_content`: HTML string to render
- `extract_links`: Whether to extract links
- `terminal_width`: Terminal width for formatting

**Returns:**
- `Tuple`: (rendered_text, extracted_links)

---

## CLI API

### Main Functions

#### `main()`

Main CLI entry point.

```python
def main() -> None
```

#### `cmd_get(args)`

Execute 'get' command.

```python
def cmd_get(args: argparse.Namespace) -> None
```

#### `cmd_browse(args)`

Execute 'browse' command.

```python
def cmd_browse(args: argparse.Namespace) -> None
```

#### `cmd_info(args)`

Execute 'info' command.

```python
def cmd_info(args: argparse.Namespace) -> None
```

---

## Error Handling

### ProtocolError

Raised for Gopher protocol-related errors.

```python
class ProtocolError(Exception):
    """Raised when there's an error with the Gopher protocol."""
    pass
```

### ConfigurationError

Raised for configuration-related errors.

```python
class ConfigurationError(Exception):
    """Raised when there's an error with configuration."""
    pass
```

---

## Usage Examples

### Basic Client Usage

```python
from modern_gopher.core.client import GopherClient

# Create client
client = GopherClient(timeout=60, cache_dir="~/.cache/gopher")

# Fetch directory
items = client.get_resource("gopher://gopher.floodgap.com/")

# Fetch text file
content = client.get_resource("gopher://gopher.floodgap.com/0/gopher/proxy.txt")

# Download binary file
client.download_file(
    "gopher://gopher.floodgap.com/9/gopher/clients/lynx",
    "lynx.tar.gz"
)
```

### Browser Usage

```python
from modern_gopher.browser.terminal import GopherBrowser

# Create and run browser
browser = GopherBrowser(
    initial_url="gopher://gopher.floodgap.com",
    timeout=60
)
browser.run()
```

### Configuration

```python
from modern_gopher.config import ModernGopherConfig, get_config

# Load default config
config = get_config()

# Modify settings
config.set_value("gopher.timeout", 60)
config.set_value("browser.initial_url", "gopher://example.com")

# Save changes
config.save()
```

### Plugin Development

```python
from modern_gopher.plugins.base import BasePlugin, ContentProcessor

class MyContentProcessor(ContentProcessor):
    def can_process(self, content: Any, metadata: Dict[str, Any]) -> bool:
        return isinstance(content, str) and "special" in content
    
    def process_content(self, content: str, metadata: Dict[str, Any]) -> str:
        return content.replace("special", "ENHANCED")
    
    def get_processing_order(self) -> int:
        return 100  # Process after most other plugins
```

---

## Type Hints

Modern-Gopher uses comprehensive type hints throughout the codebase. Key types include:

```python
from typing import Union, Optional, List, Dict, Any, Tuple
from modern_gopher.core.types import GopherItem, GopherItemType
from modern_gopher.core.url import GopherURL

# Common type aliases
GopherResource = Union[List[GopherItem], str, bytes]
URLLike = Union[str, GopherURL]
```

---

## Thread Safety

- `GopherClient`: Thread-safe for read operations, requires synchronization for cache modifications
- `GopherBrowser`: Not thread-safe (designed for single-threaded terminal use)
- `PluginManager`: Thread-safe after initialization
- `ModernGopherConfig`: Thread-safe for read operations

---

## Performance Considerations

- Use caching (`cache_dir` parameter) for improved performance
- Memory cache automatically manages size (100 items limit)
- Disk cache persists between sessions
- Plugin processing order affects performance
- IPv6 auto-detection may add latency on first connection

---

## Version Compatibility

This API documentation applies to Modern-Gopher v1.2.0+. For version-specific changes, see [CHANGELOG.md](../CHANGELOG.md).
