# Modern Gopher Quick Reference v1.2.0

## Installation
```bash
pip install modern-gopher
```

## Quick Start
```bash
# Start browsing immediately
modern-gopher browse gopher://gopher.floodgap.com
```

## Essential Commands

### Browser Navigation
| Key | Action |
|-----|--------|
| `↑` / `k` | Move up |
| `↓` / `j` | Move down |
| `Enter` | Open item |
| `Backspace` | Go back |
| `g` / `Ctrl+L` | Enter URL |
| `r` / `F5` | Refresh |
| `q` / `Ctrl+C` | Quit |
| `h` / `F1` | Help |

### Bookmarks & Search
| Key | Action |
|-----|--------|
| `b` / `Ctrl+B` | Toggle bookmark |
| `m` | View bookmarks |
| `/` / `Ctrl+F` | Search directory |
| `Escape` | Clear search |

## Command Line Tools

### Get Resource
```bash
# View text file
modern-gopher get gopher://server.com/0/file.txt

# Save file
modern-gopher get -o file.txt gopher://server.com/0/file.txt

# Extended timeout
modern-gopher get --timeout 120 gopher://server.com/1/
```

### Connection Options
```bash
# IPv4/IPv6
modern-gopher browse --ipv4 gopher://server.com
modern-gopher browse --ipv6 gopher://server.com

# SSL/TLS
modern-gopher browse --ssl gopher://server.com
modern-gopher browse gophers://server.com
```

## Configuration

### Default timeout changed to 60 seconds in v1.2.0

### Config File: `~/.config/modern-gopher/config.json`
```json
{
  "connection": {
    "timeout": 60,
    "use_ipv6": false,
    "use_ssl": false
  }
}
```

### Environment Variables
- `MODERN_GOPHER_TIMEOUT=60` - Connection timeout
- `MODERN_GOPHER_CONFIG=/path/to/config.json` - Config file

## Keybinding Management
```bash
# List all keybindings
modern-gopher keybindings list

# Reset to defaults
modern-gopher keybindings reset
```

## Popular Servers
- `gopher://gopher.floodgap.com` - Floodgap
- `gopher://sdf.org` - SDF
- `gopher://circumlunar.space` - Circumlunar Space
- `gopher://gopher.floodgap.com/7/v2/vs` - Veronica-2 search

## Troubleshooting

### Connection Issues
```bash
# Extended timeout
modern-gopher browse --timeout 120 gopher://server.com

# Force IP version
modern-gopher browse --ipv4 gopher://server.com
```

### Reset Everything
```bash
# Clear cache
rm -rf ~/.cache/modern-gopher/*

# Reset keybindings
modern-gopher keybindings reset
```

## URL Format
```
gopher://[host]:[port]/[type][selector]
```

## Common Item Types
- `0` - Text file
- `1` - Directory
- `7` - Search
- `9` - Binary file
- `g` - GIF image
- `h` - HTML

## Version 1.2.0 Highlights
- ✅ Enhanced connection stability (60s timeout)
- ✅ Improved error handling
- ✅ Bug fixes for shell scripts and sessions
- ✅ 250 tests passing
- ✅ Better reliability and performance

---

*Modern Gopher Quick Reference v1.2.0 - June 21, 2025*

