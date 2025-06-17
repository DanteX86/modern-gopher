# Keybinding System

Modern Gopher includes a comprehensive, customizable keybinding system that allows users to configure keyboard shortcuts for all browser actions.

## Features

- **Customizable keybindings**: All keyboard shortcuts can be customized
- **Context-aware bindings**: Different contexts (browser, content, search) support different keybindings
- **Conflict detection**: Prevents conflicting keybindings from being saved
- **Backup and restore**: Automatic backup when resetting to defaults
- **CLI management**: Full command-line interface for managing keybindings
- **Persistent storage**: Keybindings are saved to `~/.config/modern-gopher/keybindings.json`

## Default Keybindings

### Global Actions (Available everywhere)
- `q`, `Ctrl+C` - Quit the application
- `h`, `F1` - Show help information

### Navigation (Browser context)
- `↑`, `k` - Move selection up
- `↓`, `j` - Move selection down
- `Enter`, `→`, `l` - Open selected item
- `Backspace`, `←` - Go back in history
- `Alt+→` - Go forward in history
- `Home` - Go to home/default URL
- `g`, `Ctrl+L` - Open URL input dialog

### Browser Actions
- `r`, `F5` - Refresh current page

### Bookmark Management
- `b`, `Ctrl+B` - Toggle bookmark for current URL
- `m` - Show bookmarks list

### History
- `Ctrl+H` - Show browsing history

### Search (Directory context)
- `/`, `Ctrl+F` - Search within current directory
- `Escape` - Clear search and exit search mode (Search context)

### Content Viewing (Content context)
- `Page Up`, `Ctrl+B` - Scroll content up
- `Page Down`, `Ctrl+F`, `Space` - Scroll content down

## Keybinding Contexts

The keybinding system supports different contexts to avoid conflicts:

- **GLOBAL**: Active everywhere in the application
- **BROWSER**: Active in the main browser interface
- **DIRECTORY**: Active when browsing directory listings
- **CONTENT**: Active when viewing text content
- **DIALOG**: Active in dialog boxes
- **SEARCH**: Active during search operations

## CLI Management

You can manage keybindings through the command line:

### List All Keybindings
```bash
modern-gopher keybindings list
```

This displays a table showing all current keybindings with their categories, keys, descriptions, contexts, and enabled status.

### Reset to Defaults
```bash
modern-gopher keybindings reset
```

This resets all keybindings to their default values. A backup of the current keybindings is automatically created before resetting.

## Customization

Keybindings are stored in `~/.config/modern-gopher/keybindings.json`. You can edit this file directly to customize keybindings.

### Configuration File Format

```json
{
  "action_name": {
    "keys": ["key1", "key2"],
    "context": "browser",
    "description": "Action description",
    "category": "category_name",
    "enabled": true
  }
}
```

### Key Format

Keys can be specified in several formats:
- Single keys: `"q"`, `"enter"`, `"escape"`
- Modified keys: `"c-c"` (Ctrl+C), `"a-tab"` (Alt+Tab), `"s-f1"` (Shift+F1)
- Special keys: `"up"`, `"down"`, `"left"`, `"right"`, `"home"`, `"pageup"`, `"pagedown"`

### Example Customization

To change the quit key from `q` to `Ctrl+Q`:

1. Edit `~/.config/modern-gopher/keybindings.json`
2. Find the `"quit"` action
3. Change `"keys": ["q", "c-c"]` to `"keys": ["c-q", "c-c"]`
4. Save the file

The changes will take effect the next time you start the browser.

## Key Normalization

The system automatically normalizes key representations for consistency:
- `"ctrl+c"` becomes `"c-c"`
- `"alt+tab"` becomes `"a-tab"`
- `"return"` becomes `"enter"`
- `"esc"` becomes `"escape"`

## Conflict Resolution

The keybinding system prevents conflicts by:
1. Checking for overlapping keys in the same context
2. Considering global bindings as conflicting with context-specific ones
3. Preventing duplicate key assignments
4. Warning when conflicts are detected

## Integration with Terminal Browser

The terminal browser automatically loads keybindings from the KeyBindingManager and translates them to prompt_toolkit key bindings. Unsupported key combinations are automatically mapped to supported alternatives.

## Help in Browser

Press `h` or `F1` in the browser to see a dynamically generated help screen that shows all current keybindings organized by category.

## Advanced Features

### Backup Management

Keybindings are automatically backed up before major changes. Backup files are saved with timestamps in the same directory as the main configuration file.

### Validation

The system validates all keybindings to ensure:
- Keys are in the correct format
- No circular dependencies exist
- Required fields are present
- Context values are valid

### API Access

The KeyBindingManager class provides a full API for programmatic access:

```python
from modern_gopher.keybindings import KeyBindingManager, KeyContext

manager = KeyBindingManager()

# Get action for key
action = manager.get_action_for_key('q', KeyContext.BROWSER)

# Get keys for action
keys = manager.get_keys_for_action('quit')

# Add custom binding
from modern_gopher.keybindings import KeyBinding
binding = KeyBinding(
    action="custom_action",
    keys=["c-x"],
    context=KeyContext.BROWSER,
    description="Custom action"
)
manager.add_binding(binding)
```

This comprehensive keybinding system makes Modern Gopher highly customizable while maintaining usability and preventing configuration conflicts.

