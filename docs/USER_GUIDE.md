# Modern Gopher User Guide v1.2.0

Welcome to Modern Gopher, a feature-rich terminal-based client for the Gopher protocol! This guide will help you get started and make the most of Modern Gopher's powerful features.

## Quick Start

### Installation

Install Modern Gopher using pip:

```bash
pip install modern-gopher
```

### Your First Session

Start browsing Gopherspace immediately:

```bash
modern-gopher browse gopher://gopher.floodgap.com
```

This connects you to one of the most popular Gopher servers and launches the interactive browser.

## Core Features Overview

### ✅ What's New in v1.2.0

- **Enhanced Connection Stability**: Increased default timeout to 60 seconds for better reliability
- **Improved Error Handling**: Better feedback when connections fail
- **Bug Fixes**: Resolved shell script parsing and session management issues
- **Performance**: All 250 tests passing with improved stability

### Key Capabilities

- **Interactive Browser**: Navigate Gopherspace with an intuitive terminal interface
- **Protocol Support**: Full RFC 1436 compliance with modern extensions
- **Connection Options**: IPv4/IPv6, SSL/TLS support
- **Content Handling**: View text, download files, render HTML
- **Search & Bookmarks**: Find content and save your favorite resources
- **Customization**: Configurable keybindings and settings

## Using the Browser

### Starting the Browser

```bash
# Connect to a specific server
modern-gopher browse gopher://gopher.floodgap.com

# Use SSL/TLS connection
modern-gopher browse gophers://secure.gopher.com

# Force IPv6
modern-gopher browse --ipv6 gopher://ipv6.gopher.com
```

### Navigation Basics

| Key | Action |
|-----|--------|
| `↑` / `k` | Move up |
| `↓` / `j` | Move down |
| `Enter` | Open selected item |
| `Backspace` | Go back |
| `g` / `Ctrl+L` | Enter URL directly |

### Essential Browser Features

#### Bookmarks
- `b` / `Ctrl+B` - Bookmark current page
- `m` - View bookmarks list
- Search and organize your saved pages

#### Search
- `/` / `Ctrl+F` - Search within directories
- `Escape` - Clear search
- Find content quickly in large directories

#### Help
- `h` / `F1` - Show help and all keybindings
- Context-sensitive help available

## Command Line Tools

### `get` Command - Fetch Resources

```bash
# View a text file
modern-gopher get gopher://gopher.floodgap.com/0/gopher/proxy

# Save a file
modern-gopher get -o document.txt gopher://server.com/0/file.txt

# Render text as Markdown
modern-gopher get --markdown gopher://server.com/0/readme.txt

# Use extended timeout for slow servers
modern-gopher get --timeout 120 gopher://slow.server.com/1/
```

### `info` Command - Resource Information

```bash
# Get details about a Gopher URL
modern-gopher info gopher://gopher.floodgap.com/1/fun

# Verbose output for troubleshooting
modern-gopher info -v gopher://problematic.server.com
```

## Configuration

### Configuration File Location

Modern Gopher looks for configuration in:
1. `$MODERN_GOPHER_CONFIG` (if set)
2. `~/.config/modern-gopher/config.json`
3. `~/.modern-gopher/config.json`

### Sample Configuration

```json
{
  "connection": {
    "timeout": 60,
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
  },
  "browser": {
    "default_url": "gopher://gopher.floodgap.com",
    "save_session": true,
    "auto_restore": true
  }
}
```

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `MODERN_GOPHER_CONFIG` | Config file path | (auto-detect) |
| `MODERN_GOPHER_TIMEOUT` | Default timeout | 60 seconds |
| `MODERN_GOPHER_CACHE_DIR` | Cache directory | `~/.cache/modern-gopher` |

## Customizing Keybindings

### View Current Keybindings

```bash
modern-gopher keybindings list
```

### Reset to Defaults

```bash
modern-gopher keybindings reset
```

### Manual Customization

Edit `~/.config/modern-gopher/keybindings.json`:

```json
{
  "quit": {
    "keys": ["q", "c-c"],
    "context": "global",
    "description": "Quit the application",
    "category": "Global",
    "enabled": true
  }
}
```

### Key Format Examples

- Single keys: `"q"`, `"enter"`, `"escape"`
- Modified keys: `"c-c"` (Ctrl+C), `"a-tab"` (Alt+Tab)
- Special keys: `"up"`, `"down"`, `"pageup"`, `"pagedown"`

## Popular Gopher Servers

### General Interest
- `gopher://gopher.floodgap.com` - Floodgap (news, software, culture)
- `gopher://sdf.org` - SDF Public Access UNIX System
- `gopher://circumlunar.space` - Circumlunar Space community

### Search Services
- `gopher://gopher.floodgap.com/7/v2/vs` - Veronica-2 search
- `gopher://gopher.floodgap.com/7/v2/vs?help` - Search help

### Technical Resources
- `gopher://gopher.floodgap.com/1/comp` - Computing resources
- `gopher://sdf.org/1/software` - Software archives

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to server
```bash
# Try with extended timeout
modern-gopher browse --timeout 120 gopher://server.com

# Force IPv4 or IPv6
modern-gopher browse --ipv4 gopher://server.com
modern-gopher browse --ipv6 gopher://server.com

# Try SSL/TLS
modern-gopher browse --ssl gopher://server.com
```

**Problem**: Slow connections
- Increase timeout: `--timeout 120`
- Check your internet connection
- Try a different server

### Content Display Issues

**Problem**: Text not displaying correctly
```bash
# Try Markdown rendering
modern-gopher get --markdown gopher://server.com/0/file.txt

# Save to file and view externally
modern-gopher get -o file.txt gopher://server.com/0/file.txt
```

**Problem**: Binary files shown as text
```bash
# Save binary files instead of displaying
modern-gopher get -o image.gif gopher://server.com/g/image.gif
```

### Browser Issues

**Problem**: Keybindings not working
```bash
# Reset to defaults
modern-gopher keybindings reset

# Check current bindings
modern-gopher keybindings list
```

**Problem**: Configuration not loading
```bash
# Check config file location
echo $MODERN_GOPHER_CONFIG

# Use verbose mode for debugging
modern-gopher -v browse gopher://server.com
```

## Advanced Usage

### Session Management

Modern Gopher automatically saves your browsing session:
- History is preserved between sessions
- Bookmarks persist automatically
- Session restoration happens on startup

### Caching

Content is cached to improve performance:
- Location: `~/.cache/modern-gopher`
- TTL: 1 hour (configurable)
- Clear cache: `rm -rf ~/.cache/modern-gopher/*`

### URL Formats

Standard Gopher URL format:
```
gopher://[host]:[port]/[type][selector]
```

Examples:
- `gopher://gopher.floodgap.com/1/` - Directory
- `gopher://gopher.floodgap.com/0/gopher/proxy` - Text file
- `gophers://secure.example.com/1/` - SSL/TLS connection

### Protocol Support

Modern Gopher supports all standard Gopher item types:

| Type | Description | Example |
|------|-------------|---------|
| 0 | Text file | Documents, README files |
| 1 | Directory | Menu listings |
| 7 | Search | Veronica, Jughead |
| 9 | Binary | Software, archives |
| g | GIF image | Pictures |
| h | HTML | Web content |
| I | Image | Various formats |

## Getting Help

### In-Browser Help
- Press `h` or `F1` in the browser for context-sensitive help
- View all keybindings and their descriptions

### Command Line Help
```bash
# General help
modern-gopher --help

# Command-specific help
modern-gopher browse --help
modern-gopher get --help
modern-gopher info --help
```

### Community Resources
- GitHub Issues: Report bugs and request features
- Documentation: Check the repository for latest docs
- Gopher Community: Join discussions on Gopher servers

## Best Practices

### Performance Tips
1. Use bookmarks for frequently visited sites
2. Let caching work - avoid unnecessary refreshes
3. Use appropriate timeouts for your connection speed

### Security Considerations
1. Be cautious with SSL certificate validation
2. Verify downloads from untrusted sources
3. Use secure connections when available

### Efficient Navigation
1. Learn the core keybindings (`j`/`k`, `Enter`, `Backspace`)
2. Use search (`/`) in large directories
3. Bookmark important resources early
4. Use the URL dialog (`g`) for quick navigation

---

*Modern Gopher User Guide v1.2.0 - Updated June 21, 2025*

For the latest updates and documentation, visit the project repository.

