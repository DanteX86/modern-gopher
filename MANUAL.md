# Modern Gopher Manual

## Table of Contents

1. [Overview and Introduction](#overview-and-introduction)
2. [Installation Guide](#installation-guide)
3. [Command Reference](#command-reference)
4. [Configuration](#configuration)
5. [Advanced Usage](#advanced-usage)
6. [Troubleshooting](#troubleshooting)
7. [Examples](#examples)
8. [Technical Details](#technical-details)

---

## Overview and Introduction

### What is Modern Gopher?

Modern Gopher is a set of command-line tools designed to interact with the Gopher protocol (RFC 1436) in a modern, user-friendly way. Despite being created in the early 1990s, the Gopher protocol continues to be used and maintained by enthusiasts who value its simplicity, efficiency, and focus on content rather than presentation.

### Key Features

- **Pure Python Implementation**: Written entirely in Python for maximum portability
- **Rich Terminal Interface**: Color-coded, formatted output for improved readability
- **Interactive Browser**: Terminal-based browser for navigating Gopherspace
- **Multiple Connection Options**: Support for IPv4, IPv6, and SSL/TLS connections
- **Content Caching**: Local caching to reduce bandwidth usage and improve performance
- **Rich Output Formats**: View text files with Markdown rendering
- **Comprehensive Protocol Support**: Handles all standard Gopher item types (0-9, g, I, etc.)

### About the Gopher Protocol

The Gopher protocol (RFC 1436) is a TCP/IP application layer protocol designed for distributing, searching, and retrieving documents over the Internet. Developed at the University of Minnesota in 1991, Gopher predates the World Wide Web and offers a menu-driven interface to Internet resources.

Key characteristics of Gopher:

- **Hierarchical Structure**: Information is organized in a hierarchy of menus and documents
- **Simple Text-Based Protocol**: Easy to implement and lightweight
- **Document Types**: Supports various document types including text, images, binary files, etc.
- **Search Capability**: Built-in search functionality (Veronica, Jughead)

---

## Installation Guide

### Requirements

- Python 3.8 or higher
- pip (Python package installer)
- Terminal with 256-color support (for best experience)

### Installation Methods

#### 1. From PyPI (Recommended)

```bash
pip install modern-gopher
```

#### 2. From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/modern-gopher.git
cd modern-gopher

# Install in development mode
pip install -e .
```

#### 3. From Homebrew (macOS)

```bash
brew install modern-gopher
```

### Verifying Installation

After installation, verify that Modern Gopher is correctly installed:

```bash
modern-gopher --version
```

This should display the version number of Modern Gopher.

---

## Command Reference

Modern Gopher provides several commands for interacting with Gopher servers. Here's a complete reference of all available commands and their options.

### Global Options

These options apply to all Modern Gopher commands:

| Option | Description |
|--------|-------------|
| `--version` | Show the version number and exit |
| `-h, --help` | Show help message and exit |

### `browse` Command

Launches the interactive terminal-based browser for navigating Gopherspace.

```bash
modern-gopher browse [options] <url>
```

#### Options

| Option | Description |
|--------|-------------|
| `--timeout SECONDS` | Socket timeout in seconds (default: 30) |
| `--ipv4` | Force IPv4 usage |
| `--ipv6` | Force IPv6 usage |
| `--ssl` | Use SSL/TLS for the connection |
| `-v, --verbose` | Enable verbose output |

#### Example

```bash
modern-gopher browse gopher://gopher.floodgap.com
```

### `get` Command

Fetches a Gopher resource and displays it or saves it to a file.

```bash
modern-gopher get [options] <url>
```

#### Options

| Option | Description |
|--------|-------------|
| `-o, --output FILE` | Save resource to specified file |
| `--markdown` | Render text content as Markdown |
| `--timeout SECONDS` | Socket timeout in seconds (default: 30) |
| `--ipv4` | Force IPv4 usage |
| `--ipv6` | Force IPv6 usage |
| `--ssl` | Use SSL/TLS for the connection |
| `-v, --verbose` | Enable verbose output |

#### Examples

```bash
# Display a Gopher directory
modern-gopher get gopher://gopher.floodgap.com

# Save a text file
modern-gopher get -o document.txt gopher://gopher.floodgap.com/0/gopher/proxy

# Display a text file with Markdown rendering
modern-gopher get --markdown gopher://gopher.floodgap.com/0/gopher/proxy
```

### `info` Command

Displays information about a Gopher URL.

```bash
modern-gopher info [options] <url>
```

#### Options

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Enable verbose output |

#### Example

```bash
modern-gopher info gopher://gopher.floodgap.com/1/fun
```

---

## Configuration

Modern Gopher can be configured through command-line options or a configuration file.

### Configuration File

Modern Gopher looks for a configuration file in the following locations (in order of precedence):

1. Path specified by the `MODERN_GOPHER_CONFIG` environment variable
2. `~/.config/modern-gopher/config.json`
3. `~/.modern-gopher/config.json`

#### Sample Configuration File

```json
{
  "connection": {
    "timeout": 30,
    "use_ipv6": false,
    "use_ssl": false
  },
  "cache": {
    "enabled": true,
    "dir": "~/.cache/modern-gopher",
    "ttl": 3600
  },
  "display": {
    "use_markdown": true,
    "color_scheme": "default"
  }
}
```

### Environment Variables

The following environment variables can be used to configure Modern Gopher:

| Variable | Description |
|----------|-------------|
| `MODERN_GOPHER_CONFIG` | Path to the configuration file |
| `MODERN_GOPHER_CACHE_DIR` | Directory for caching Gopher resources |
| `MODERN_GOPHER_TIMEOUT` | Default socket timeout in seconds |
| `MODERN_GOPHER_USE_IPV6` | Set to "1" to enable IPv6 by default |
| `MODERN_GOPHER_USE_SSL` | Set to "1" to enable SSL/TLS by default |

---

## Advanced Usage

### Gopher URLs

Gopher URLs follow this format:

```
gopher://[host]:[port]/[item_type][selector]
```

- **host**: The hostname of the Gopher server
- **port**: The port number (default: 70)
- **item_type**: A single character indicating the type of resource
- **selector**: The path to the resource on the server

Example:
```
gopher://gopher.floodgap.com/0/gopher/proxy
```

In this example:
- Host: `gopher.floodgap.com`
- Port: `70` (default, not specified)
- Item Type: `0` (text file)
- Selector: `/gopher/proxy`

### Using SSL/TLS with Gopher

Some modern Gopher servers support SSL/TLS connections. To connect to these servers, use the `--ssl` option or the `gophers://` URL scheme:

```bash
modern-gopher get --ssl gopher://gopher.example.com
# or
modern-gopher get gophers://gopher.example.com
```

### Caching Behavior

Modern Gopher caches content to improve performance and reduce bandwidth usage. By default, cached content is stored in `~/.cache/modern-gopher` and has a time-to-live (TTL) of 1 hour.

To clear the cache:

```bash
rm -rf ~/.cache/modern-gopher/*
```

---

## Troubleshooting

### Common Issues

#### Unable to Connect to Server

If you cannot connect to a Gopher server, try the following:

1. Verify that the server is online
2. Check that you have internet connectivity
3. Try specifying IPv4 or IPv6 explicitly
4. Increase the timeout value
5. Check if the server requires SSL/TLS

Example:
```bash
modern-gopher get --ipv4 --timeout 60 gopher://gopher.floodgap.com
```

#### Content Not Displayed Correctly

If content isn't displayed correctly:

1. Try specifying a different encoding
2. For text files, try the `--markdown` option
3. Check if the file is actually binary and save it to disk instead

#### Certificate Validation Errors

If you encounter SSL certificate validation errors:

1. Verify that the server has a valid certificate
2. Consider using the `--no-verify-ssl` option (use with caution)

### Logging and Debugging

For troubleshooting, use the verbose mode to see more detailed information:

```bash
modern-gopher -v get gopher://gopher.floodgap.com
```

This will display additional information about the connection, request, and response.

---

## Examples

### Browsing Popular Gopher Servers

```bash
# Floodgap (one of the most popular Gopher servers)
modern-gopher browse gopher://gopher.floodgap.com

# SDF Public Access UNIX System
modern-gopher browse gopher://sdf.org

# Circumlunar Space (another popular Gopher server)
modern-gopher browse gopher://circumlunar.space
```

### Searching Gopher Space

Veronica-2 is a service that indexes Gopherspace. You can use it to search for content:

```bash
# Open Veronica-2 search
modern-gopher browse gopher://gopher.floodgap.com/7/v2/vs
```

### Downloading Files

```bash
# Save a text file
modern-gopher get -o filename.txt gopher://gopher.floodgap.com/0/gopher/proxy

# Save a binary file
modern-gopher get -o image.gif gopher://gopher.example.com/g/image.gif
```

### Working with Different Item Types

```bash
# Text file (item type 0)
modern-gopher get gopher://gopher.floodgap.com/0/gopher/proxy

# Directory (item type 1)
modern-gopher get gopher://gopher.floodgap.com/1/fun

# GIF image (item type g)
modern-gopher get -o fun.gif gopher://gopher.example.com/g/fun.gif
```

---

## Technical Details

### Architecture

Modern Gopher follows a modular architecture with the following components:

1. **Core Protocol Module**: Handles the low-level Gopher protocol implementation
2. **Parser Module**: Processes Gopher responses and converts them to structured data
3. **Client Module**: Provides high-level functions for interacting with Gopher servers
4. **CLI Module**: Implements the command-line interface
5. **Browser Module**: Implements the interactive terminal-based browser

### Gopher Item Types

Modern Gopher supports all standard Gopher item types as defined in RFC 1436 and common extensions:

| Type | Description | MIME Type |
|------|-------------|-----------|
| 0 | Text File | text/plain |
| 1 | Directory | text/plain |
| 2 | CSO Phone Book | application/x-cso |
| 3 | Error | text/plain |
| 4 | BinHex File | application/mac-binhex40 |
| 5 | DOS Binary | application/octet-stream |
| 6 | UUEncoded File | text/x-uuencode |
| 7 | Search Server | text/plain |
| 8 | Telnet Session | application/x-telnet |
| 9 | Binary File | application/octet-stream |
| + | Redundant Server | text/plain |
| g | GIF Image | image/gif |
| I | Image File | image/unknown |
| T | TN3270 Session | application/x-tn3270 |
| h | HTML File | text/html |
| i | Information | text/plain |
| s | Sound File | audio/unknown |

### Caching Implementation

Modern Gopher uses a two-level caching system:

1. **Memory Cache**: Recent items are kept in memory for quick access
2. **Disk Cache**: Items are stored on disk for persistence across sessions

Cached items include:
- Directory listings
- Text files
- Binary files

Each cached item includes metadata such as:
- URL
- Content type
- Timestamp
- Expiration date

### Protocol Implementation

Modern Gopher implements the Gopher protocol as defined in RFC 1436, with the following enhancements:

- Support for Gopher+ extensions
- Support for SSL/TLS connections
- Support for IPv6
- Automatic charset detection and conversion

---

## Contributing

Contributions to Modern Gopher are welcome! To contribute:

1. Fork the repository
2. Create a branch for your changes
3. Make your changes
4. Submit a pull request

Please ensure your code follows the project's style guidelines and includes appropriate tests.

---

## License

Modern Gopher is released under the MIT License. See the LICENSE file for details.

---

## Acknowledgments

Modern Gopher would not have been possible without the work of the original Gopher protocol developers at the University of Minnesota, the maintainers of various Gopher servers around the world, and the continued interest of the Gopher community.

Special thanks to:
- The Floodgap team for maintaining one of the most important Gopher servers
- The developers of the Python libraries that Modern Gopher depends on
- Everyone who has contributed to the project

---

*This manual was last updated on May 20, 2025.*

