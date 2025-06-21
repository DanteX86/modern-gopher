# Browser Enhancement Plan for Modern Gopher

## 🎯 Priority 1: Navigation & Usability Enhancements

### A. **Tabs System**
```python
# Enhanced browser with tab support
class TabManager:
    def __init__(self):
        self.tabs = []
        self.active_tab = 0
    
    def create_tab(self, url=None):
        """Create new tab with optional URL."""
        pass
    
    def close_tab(self, tab_index):
        """Close tab by index."""
        pass
    
    def switch_tab(self, tab_index):
        """Switch to tab by index."""
        pass
```

**Benefits:**
- Multi-page browsing without losing context
- Compare content side-by-side
- Standard browser-like experience

### B. **Split-Pane Viewing**
```python
class SplitPaneManager:
    def __init__(self):
        self.panes = []
        self.active_pane = 0
        self.split_direction = 'horizontal'  # or 'vertical'
    
    def split_horizontal(self):
        """Split current pane horizontally."""
        pass
    
    def split_vertical(self):
        """Split current pane vertically."""
        pass
```

**Benefits:**
- View directory and content simultaneously
- Compare multiple documents
- Enhanced productivity

### C. **Enhanced Status Bar**
```python
def enhanced_status_bar(self):
    """Multi-line status bar with rich information."""
    status_parts = [
        f"📍 {self.current_url}",
        f"📊 {len(self.current_items)} items" if self.current_items else "📄 Content view",
        f"🔍 Search: {self.search_query}" if self.is_searching else "",
        f"📚 {len(self.history.history)} history",
        f"⭐ {len(self.bookmarks.get_all())} bookmarks"
    ]
    return " | ".join(filter(None, status_parts))
```

## 🎯 Priority 2: Advanced Search & Content Features

### A. **Full-Text Content Search**
```python
class ContentSearchManager:
    def __init__(self):
        self.search_index = {}
        self.search_history = []
    
    def index_content(self, url, content):
        """Index content for full-text search."""
        pass
    
    def search_across_content(self, query):
        """Search across all cached content."""
        pass
    
    def search_with_filters(self, query, filters):
        """Search with type, date, or tag filters."""
        pass
```

### B. **Smart Link Detection**
```python
def extract_gopher_links(self, text_content):
    """Extract Gopher URLs from text content."""
    gopher_pattern = r'gophers?://[^\s\]>)"]+'
    links = re.findall(gopher_pattern, text_content)
    return [{'url': link, 'context': self._get_context(text_content, link)} 
            for link in links]
```

### C. **Content Preview**
```python
def show_content_preview(self, item):
    """Show content preview without full navigation."""
    if item.item_type in [GopherItemType.TEXT_FILE, GopherItemType.HTML]:
        preview = self.client.get_resource_preview(item, max_chars=500)
        self.show_popup_preview(preview)
```

## 🎯 Priority 3: Performance & Caching Enhancements

### A. **Advanced Caching**
```python
class AdvancedCacheManager:
    def __init__(self):
        self.memory_cache = {}
        self.persistent_cache = {}
        self.cache_stats = {'hits': 0, 'misses': 0}
    
    def preload_links(self, items):
        """Preload commonly accessed items."""
        for item in items[:5]:  # Preload first 5 items
            asyncio.create_task(self._preload_item(item))
    
    def smart_cache_cleanup(self):
        """Remove least recently used items."""
        pass
```

### B. **Background Content Loading**
```python
import asyncio

async def background_load_directory(self, url):
    """Load directory content in background."""
    try:
        content = await self.client.get_resource_async(url)
        self.cache.store(url, content)
    except Exception as e:
        logger.debug(f"Background load failed for {url}: {e}")
```

## 🎯 Priority 4: Enhanced User Experience

### A. **Breadcrumb Navigation**
```python
def generate_breadcrumbs(self):
    """Generate breadcrumb trail for current location."""
    url_parts = self.current_url.split('/')
    breadcrumbs = []
    
    for i, part in enumerate(url_parts):
        partial_url = '/'.join(url_parts[:i+1])
        breadcrumbs.append({
            'text': part or 'Root',
            'url': partial_url,
            'is_current': i == len(url_parts) - 1
        })
    
    return breadcrumbs
```

### B. **Quick Actions Menu**
```python
def show_quick_actions(self):
    """Show context-sensitive quick actions."""
    actions = []
    
    if self.current_items:
        actions.extend([
            ('↵', 'Open selected'),
            ('Space', 'Preview'),
            ('b', 'Bookmark'),
        ])
    
    if self.is_searching:
        actions.append(('Esc', 'Clear search'))
    
    return actions
```

### C. **Keyboard Shortcut Hints**
```python
def show_contextual_hints(self):
    """Show relevant keyboard shortcuts for current context."""
    if self.current_context == KeyContext.DIRECTORY:
        return "↑↓:Navigate | ↵:Open | /:Search | b:Bookmark | ?:Help"
    elif self.current_context == KeyContext.CONTENT:
        return "PgUp/PgDn:Scroll | ←:Back | b:Bookmark | ?:Help"
    elif self.current_context == KeyContext.SEARCH:
        return "↑↓:Navigate results | ↵:Open | Esc:Clear | ?:Help"
```

## 🎯 Priority 5: Content Enhancement Features

### A. **Improved HTML Rendering**
```python
class EnhancedHTMLRenderer(HTMLRenderer):
    def __init__(self):
        super().__init__()
        self.table_formatter = RichTableFormatter()
        self.image_placeholder = True
        self.link_extraction = True
    
    def render_with_styling(self, html_content):
        """Render HTML with better terminal styling."""
        # Enhanced table rendering
        # Better list formatting
        # Syntax highlighting for code blocks
        pass
```

### B. **Content Type Handlers**
```python
class ContentTypeManager:
    def __init__(self):
        self.handlers = {
            'text/plain': self.handle_text,
            'text/html': self.handle_html,
            'image/*': self.handle_image,
            'application/json': self.handle_json,
        }
    
    def handle_image(self, content, metadata):
        """Handle image files with ASCII art conversion."""
        pass
    
    def handle_json(self, content, metadata):
        """Handle JSON with syntax highlighting."""
        pass
```

## 🎯 Implementation Timeline

### Phase 1 (Week 1-2): Navigation Enhancements
- [ ] Enhanced status bar with rich information
- [ ] Breadcrumb navigation
- [ ] Quick actions menu
- [ ] Contextual keyboard hints

### Phase 2 (Week 3-4): Search & Content
- [ ] Full-text content search
- [ ] Smart link detection in content
- [ ] Content preview functionality
- [ ] Search history and suggestions

### Phase 3 (Week 5-6): Performance & Caching
- [ ] Advanced caching system
- [ ] Background content loading
- [ ] Cache statistics and management
- [ ] Preloading optimization

### Phase 4 (Week 7-8): Advanced UI
- [ ] Tab system implementation
- [ ] Split-pane viewing
- [ ] Enhanced HTML rendering
- [ ] Content type handlers

## 🔧 Technical Implementation Notes

### Required Dependencies
```python
# Add to requirements.txt
aiofiles>=0.8.0          # Async file operations
rich>=12.0.0             # Enhanced terminal formatting
textual>=0.1.0           # Advanced TUI components (optional)
pillow>=9.0.0            # Image processing for ASCII art
pygments>=2.10.0         # Syntax highlighting
```

### Configuration Extensions
```json
// ~/.config/modern-gopher/config.json
{
  "browser": {
    "enable_tabs": true,
    "max_tabs": 10,
    "enable_split_panes": true,
    "background_loading": true,
    "preload_count": 5,
    "content_preview": true,
    "show_breadcrumbs": true,
    "quick_actions_menu": true
  },
  "search": {
    "enable_full_text": true,
    "index_content": true,
    "search_history_size": 100,
    "search_suggestions": true
  },
  "rendering": {
    "enhanced_html": true,
    "syntax_highlighting": true,
    "ascii_art_images": false,
    "table_formatting": "rich"
  }
}
```

## 📈 Expected Benefits

### User Experience
- **50% faster navigation** with preloading and caching
- **Enhanced discoverability** with better search
- **Improved productivity** with tabs and split-panes
- **Better content presentation** with enhanced rendering

### Developer Experience
- **Modular architecture** for easy feature addition
- **Extensible plugin system** for custom content handlers
- **Comprehensive testing** for all new features
- **Clear configuration** for user customization

## 🚀 Quick Wins (Can implement immediately)

1. **Enhanced Status Bar** - 2 hours
2. **Breadcrumb Navigation** - 3 hours  
3. **Quick Actions Menu** - 2 hours
4. **Content Preview** - 4 hours
5. **Smart Link Detection** - 3 hours

Total: ~14 hours for significant UX improvements

---

*This enhancement plan provides a comprehensive roadmap for evolving the Modern Gopher browser into a more powerful and user-friendly terminal-based browsing experience.*

