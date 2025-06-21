# Quick Actions Menu Implementation Plan

## 🎯 **Feature Overview**
Context-sensitive popup menu showing available actions with keybindings, triggered by `Space` or `F2`.

## 📋 **Implementation Steps**

### Step 1: Add Quick Actions Logic (45 minutes)
```python
# Add to src/modern_gopher/browser/terminal.py

def _get_context_actions(self) -> List[Tuple[str, str, str]]:
    """Get available actions for current context."""
    actions = []
    
    if self.current_context == KeyContext.DIRECTORY:
        if self.current_items:
            actions.extend([
                ('↵', 'Enter', 'Open selected item'),
                ('Space', 'Space', 'Preview content'),
                ('b', 'b', 'Toggle bookmark'),
                ('/', '/', 'Search directory'),
            ])
        actions.extend([
            ('g', 'g/Ctrl+L', 'Go to URL'),
            ('m', 'm', 'Show bookmarks'),
            ('h', 'h', 'Show history'),
            ('r', 'r/F5', 'Refresh page'),
        ])
    elif self.current_context == KeyContext.CONTENT:
        actions.extend([
            ('←', 'Backspace', 'Go back'),
            ('PgUp', 'PgUp/PgDn', 'Scroll content'),
            ('b', 'b', 'Bookmark page'),
            ('g', 'g', 'Go to URL'),
        ])
    elif self.current_context == KeyContext.SEARCH:
        actions.extend([
            ('↑↓', '↑/↓', 'Navigate results'),
            ('↵', 'Enter', 'Open result'),
            ('Esc', 'Esc', 'Clear search'),
            ('b', 'b', 'Bookmark result'),
        ])
    
    # Global actions
    actions.extend([
        ('?', '?', 'Show help'),
        ('q', 'q/Ctrl+C', 'Quit browser'),
    ])
    
    return actions

def show_quick_actions(self):
    """Show quick actions popup."""
    actions = self._get_context_actions()
    
    # Format actions text
    text = "Quick Actions Menu\n"
    text += "=" * 20 + "\n\n"
    
    for key, display_key, description in actions:
        text += f"  {display_key:<12} {description}\n"
    
    text += f"\nContext: {self.current_context.value.title()}\n"
    text += "\nPress Space again or Esc to close"
    
    # Show in content area temporarily
    self._previous_content = self.content_view.text
    self.content_view.text = text
    self.status_bar.text = "Quick Actions Menu - Press Space or Esc to close"
    self._showing_quick_actions = True

def hide_quick_actions(self):
    """Hide quick actions popup."""
    if hasattr(self, '_showing_quick_actions') and self._showing_quick_actions:
        self.content_view.text = getattr(self, '_previous_content', '')
        self._showing_quick_actions = False
        self.update_status_bar()
```

### Step 2: Add Keybinding (15 minutes)
```python
# Add to setup_keybindings method
@kb.add('space')
def _(event):
    if getattr(self, '_showing_quick_actions', False):
        self.hide_quick_actions()
    else:
        self.show_quick_actions()

@kb.add('f2') 
def _(event):
    self.show_quick_actions()

@kb.add('escape')
def _(event):
    if getattr(self, '_showing_quick_actions', False):
        self.hide_quick_actions()
    elif self.is_searching:
        self.clear_search()
```

### Step 3: Add Tests (30 minutes)
```python
# Add to tests/test_browser.py
def test_quick_actions_menu_content(self):
    """Test quick actions menu shows correct actions for context."""
    browser = GopherBrowser()
    browser.current_context = KeyContext.DIRECTORY
    
    actions = browser._get_context_actions()
    assert any('Open selected item' in action[2] for action in actions)
    assert any('Search directory' in action[2] for action in actions)

def test_show_hide_quick_actions(self):
    """Test showing and hiding quick actions menu."""
    browser = GopherBrowser()
    original_content = browser.content_view.text
    
    browser.show_quick_actions()
    assert browser._showing_quick_actions is True
    assert "Quick Actions Menu" in browser.content_view.text
    
    browser.hide_quick_actions()
    assert browser._showing_quick_actions is False
    assert browser.content_view.text == original_content
```

## 📈 **Expected Benefits**
- **Discoverability**: Users discover features without memorizing keys
- **Efficiency**: Quick access to common actions
- **Context Awareness**: Only shows relevant actions
- **Learning**: Helps users learn keybindings naturally

