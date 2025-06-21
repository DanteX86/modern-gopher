#!/usr/bin/env python3
"""
Keybinding management for Modern Gopher.

This module handles customizable keyboard shortcuts and provides a framework
for managing keybindings across the application.
"""

import json
import logging
import os
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

logger = logging.getLogger(__name__)


class KeyContext(Enum):
    """Context in which keybindings are active."""
    GLOBAL = "global"           # Active everywhere
    BROWSER = "browser"         # Active in browser interface
    DIRECTORY = "directory"     # Active when browsing directories
    CONTENT = "content"         # Active when viewing content
    DIALOG = "dialog"           # Active in dialogs
    SEARCH = "search"           # Active during search


@dataclass
class KeyBinding:
    """Represents a single key binding."""
    action: str                    # Action name (e.g., 'quit', 'refresh')
    keys: List[str]               # Key combinations (e.g., ['q', 'ctrl+c'])
    context: KeyContext           # Context where binding is active
    description: str              # Human-readable description
    category: str = "general"     # Category for organization
    enabled: bool = True          # Whether binding is enabled

    def __post_init__(self):
        """Normalize key representations."""
        self.keys = [self.normalize_key(key) for key in self.keys]

    @staticmethod
    def normalize_key(key: str) -> str:
        """Normalize key representation for consistency."""
        # Convert common aliases
        key = key.lower().strip()

        # Normalize modifier keys
        key = key.replace('ctrl+', 'c-')
        key = key.replace('alt+', 'a-')
        key = key.replace('shift+', 's-')
        key = key.replace('cmd+', 'm-')  # For macOS

        # Normalize special keys
        aliases = {
            'return': 'enter',
            'esc': 'escape',
            'del': 'delete',
            'pgup': 'pageup',
            'pgdn': 'pagedown',
            'pgdown': 'pagedown',
        }

        for alias, canonical in aliases.items():
            if key == alias:
                key = canonical
                break

        return key

    def conflicts_with(self, other: 'KeyBinding') -> bool:
        """Check if this binding conflicts with another."""
        if self.context != other.context and \
           self.context != KeyContext.GLOBAL and \
           other.context != KeyContext.GLOBAL:
            return False

        # Check for overlapping keys
        return bool(set(self.keys) & set(other.keys))


class KeyBindingManager:
    """Manages application keybindings."""

    def __init__(self, config_file: Optional[Path] = None):
        """Initialize the keybinding manager.

        Args:
            config_file: Path to keybinding configuration file
        """
        self.config_file = config_file or self.get_default_config_path()
        self.bindings: Dict[str, KeyBinding] = {}
        self.key_to_action: Dict[Tuple[str, KeyContext], str] = {}

        # Load default bindings
        self._setup_default_bindings()

        # Load custom bindings if file exists
        if self.config_file.exists():
            self.load_from_file()
        else:
            # Save defaults to file
            self.save_to_file()

    @staticmethod
    def get_default_config_path() -> Path:
        """Get the default keybinding configuration file path."""
        config_dir = Path.home() / '.config' / 'modern-gopher'
        return config_dir / 'keybindings.json'

    def _setup_default_bindings(self) -> None:
        """Set up default keybindings."""
        default_bindings = [
            # Global actions
            KeyBinding(
                action="quit",
                keys=["q", "c-c"],
                context=KeyContext.GLOBAL,
                description="Quit the application",
                category="global"
            ),
            KeyBinding(
                action="help",
                keys=["h", "f1"],
                context=KeyContext.GLOBAL,
                description="Show help information",
                category="global"
            ),

            # Browser navigation
            KeyBinding(
                action="navigate_up",
                keys=["up", "k"],
                context=KeyContext.BROWSER,
                description="Move selection up",
                category="navigation"
            ),
            KeyBinding(
                action="navigate_down",
                keys=["down", "j"],
                context=KeyContext.BROWSER,
                description="Move selection down",
                category="navigation"
            ),
            KeyBinding(
                action="open_item",
                keys=["enter", "right", "l"],
                context=KeyContext.BROWSER,
                description="Open selected item",
                category="navigation"
            ),
            KeyBinding(
                action="go_back",
                keys=["backspace", "left"],
                context=KeyContext.BROWSER,
                description="Go back in history",
                category="navigation"
            ),
            KeyBinding(
                action="go_forward",
                keys=["a-right"],
                context=KeyContext.BROWSER,
                description="Go forward in history",
                category="navigation"
            ),
            KeyBinding(
                action="refresh",
                keys=["r", "f5"],
                context=KeyContext.BROWSER,
                description="Refresh current page",
                category="browser"
            ),
            KeyBinding(
                action="go_home",
                keys=["home"],
                context=KeyContext.BROWSER,
                description="Go to home/default URL",
                category="navigation"
            ),

            # Bookmark management
            KeyBinding(
                action="bookmark_toggle",
                keys=["b", "c-b"],
                context=KeyContext.BROWSER,
                description="Toggle bookmark for current URL",
                category="bookmarks"
            ),
            KeyBinding(
                action="bookmark_list",
                keys=["m"],
                context=KeyContext.BROWSER,
                description="Show bookmarks list",
                category="bookmarks"
            ),

            # History
            KeyBinding(
                action="history_show",
                keys=["c-h"],
                context=KeyContext.BROWSER,
                description="Show browsing history",
                category="history"
            ),

            # URL navigation
            KeyBinding(
                action="go_to_url",
                keys=["g", "c-l"],
                context=KeyContext.BROWSER,
                description="Open URL input dialog",
                category="navigation"
            ),

            # Search
            KeyBinding(
                action="search_directory",
                keys=["/", "c-f"],
                context=KeyContext.DIRECTORY,
                description="Search within current directory",
                category="search"
            ),
            KeyBinding(
                action="search_clear",
                keys=["escape"],
                context=KeyContext.SEARCH,
                description="Clear search and exit search mode",
                category="search"
            ),

            # Content viewing
            KeyBinding(
                action="scroll_up",
                keys=["pageup", "c-b"],
                context=KeyContext.CONTENT,
                description="Scroll content up",
                category="content"
            ),
            KeyBinding(
                action="scroll_down",
                keys=["pagedown", "c-f", "space"],
                context=KeyContext.CONTENT,
                description="Scroll content down",
                category="content"
            ),
        ]

        for binding in default_bindings:
            self.add_binding(binding)

    def add_binding(self, binding: KeyBinding) -> bool:
        """Add a keybinding.

        Args:
            binding: The keybinding to add

        Returns:
            True if successful, False if conflicts exist
        """
        # Check for conflicts
        conflicts = self.find_conflicts(binding)
        if conflicts:
            logger.warning(
                f"Keybinding conflicts found for {
                    binding.action}: {conflicts}")
            return False

        # Add binding
        self.bindings[binding.action] = binding

        # Update key-to-action mapping
        for key in binding.keys:
            self.key_to_action[(key, binding.context)] = binding.action
            # Also add to global context if it's a global binding
            if binding.context == KeyContext.GLOBAL:
                for context in KeyContext:
                    self.key_to_action[(key, context)] = binding.action

        return True

    def remove_binding(self, action: str) -> bool:
        """Remove a keybinding by action name.

        Args:
            action: The action name to remove

        Returns:
            True if removed, False if not found
        """
        if action not in self.bindings:
            return False

        binding = self.bindings[action]

        # Remove from key-to-action mapping
        for key in binding.keys:
            self.key_to_action.pop((key, binding.context), None)
            if binding.context == KeyContext.GLOBAL:
                for context in KeyContext:
                    self.key_to_action.pop((key, context), None)

        # Remove binding
        del self.bindings[action]
        return True

    def find_conflicts(self, binding: KeyBinding) -> List[str]:
        """Find conflicting keybindings.

        Args:
            binding: The binding to check for conflicts

        Returns:
            List of conflicting action names
        """
        conflicts = []

        for action, existing_binding in self.bindings.items():
            if existing_binding.conflicts_with(binding):
                conflicts.append(action)

        return conflicts

    def get_action_for_key(
            self,
            key: str,
            context: KeyContext) -> Optional[str]:
        """Get the action for a key in a given context.

        Args:
            key: The key combination
            context: The current context

        Returns:
            Action name if found, None otherwise
        """
        key = KeyBinding.normalize_key(key)

        # Check specific context first
        action = self.key_to_action.get((key, context))
        if action:
            return action

        # Check global context
        return self.key_to_action.get((key, KeyContext.GLOBAL))

    def get_keys_for_action(self, action: str) -> List[str]:
        """Get the keys bound to an action.

        Args:
            action: The action name

        Returns:
            List of key combinations
        """
        binding = self.bindings.get(action)
        return binding.keys if binding else []

    def set_keys_for_action(self, action: str, keys: List[str]) -> bool:
        """Set the keys for an action.

        Args:
            action: The action name
            keys: List of key combinations

        Returns:
            True if successful, False if conflicts exist
        """
        if action not in self.bindings:
            logger.error(f"Action '{action}' not found")
            return False

        binding = self.bindings[action]
        old_keys = binding.keys.copy()

        # Create temporary binding with new keys to check conflicts
        temp_binding = KeyBinding(
            action=binding.action,
            keys=keys,
            context=binding.context,
            description=binding.description,
            category=binding.category
        )

        # Remove current binding temporarily
        self.remove_binding(action)

        # Try to add with new keys
        if self.add_binding(temp_binding):
            return True
        else:
            # Restore old binding on conflict
            binding.keys = old_keys
            self.add_binding(binding)
            return False

    def disable_binding(self, action: str) -> bool:
        """Disable a keybinding.

        Args:
            action: The action name

        Returns:
            True if successful, False if action not found
        """
        if action not in self.bindings:
            return False

        binding = self.bindings[action]
        binding.enabled = False

        # Remove from key-to-action mapping
        for key in binding.keys:
            self.key_to_action.pop((key, binding.context), None)
            if binding.context == KeyContext.GLOBAL:
                for context in KeyContext:
                    self.key_to_action.pop((key, context), None)

        return True

    def enable_binding(self, action: str) -> bool:
        """Enable a keybinding.

        Args:
            action: The action name

        Returns:
            True if successful, False if action not found or conflicts exist
        """
        if action not in self.bindings:
            return False

        binding = self.bindings[action]

        # Check for conflicts if currently disabled
        if not binding.enabled:
            # Create a copy to check conflicts without self-conflict
            temp_bindings = {k: v for k,
                             v in self.bindings.items() if k != action}
            conflicts = []

            for existing_action, existing_binding in temp_bindings.items():
                if existing_binding.enabled and existing_binding.conflicts_with(
                        binding):
                    conflicts.append(existing_action)

            if conflicts:
                logger.warning(
                    f"Cannot enable {action}: conflicts with {conflicts}")
                return False

            # Re-add to key-to-action mapping
            for key in binding.keys:
                self.key_to_action[(key, binding.context)] = binding.action
                if binding.context == KeyContext.GLOBAL:
                    for context in KeyContext:
                        self.key_to_action[(key, context)] = binding.action

        binding.enabled = True
        return True

    def get_bindings_by_category(self, category: str) -> Dict[str, KeyBinding]:
        """Get all bindings in a category.

        Args:
            category: The category name

        Returns:
            Dictionary of action -> binding
        """
        return {
            action: binding
            for action, binding in self.bindings.items()
            if binding.category == category
        }

    def get_bindings_by_context(
            self, context: KeyContext) -> Dict[str, KeyBinding]:
        """Get all bindings for a context.

        Args:
            context: The context

        Returns:
            Dictionary of action -> binding
        """
        return {
            action: binding
            for action, binding in self.bindings.items()
            if binding.context == context or binding.context == KeyContext.GLOBAL
        }

    def get_all_categories(self) -> Set[str]:
        """Get all categories used by bindings.

        Returns:
            Set of category names
        """
        return {binding.category for binding in self.bindings.values()}

    def validate_key(self, key: str) -> bool:
        """Validate that a key combination is valid.

        Args:
            key: The key combination to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            normalized = KeyBinding.normalize_key(key)

            # Basic validation - check for empty or invalid characters
            if not normalized or normalized.isspace():
                return False

            # Check for valid modifiers
            if '-' in normalized:
                parts = normalized.split('-')
                # Only allow one modifier (should be exactly 2 parts)
                if len(parts) != 2:
                    return False

                modifier, key_part = parts
                valid_modifiers = {'c', 'a', 's', 'm'}  # ctrl, alt, shift, cmd
                if modifier not in valid_modifiers:
                    return False

                # Key part should not be empty
                if not key_part:
                    return False

            # Reject keys with multiple + signs (not normalized properly)
            if '+' in key:
                return False

            return True

        except Exception:
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert keybindings to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            action: {
                'keys': binding.keys,
                'context': binding.context.value,
                'description': binding.description,
                'category': binding.category,
                'enabled': binding.enabled
            }
            for action, binding in self.bindings.items()
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load keybindings from dictionary.

        Args:
            data: Dictionary representation
        """
        self.bindings.clear()
        self.key_to_action.clear()

        for action, binding_data in data.items():
            try:
                binding = KeyBinding(
                    action=action,
                    keys=binding_data['keys'],
                    context=KeyContext(binding_data['context']),
                    description=binding_data['description'],
                    category=binding_data.get('category', 'general'),
                    enabled=binding_data.get('enabled', True)
                )

                if binding.enabled:
                    self.add_binding(binding)
                else:
                    # Add disabled binding without key mappings
                    self.bindings[binding.action] = binding

            except (KeyError, ValueError) as e:
                logger.warning(f"Failed to load binding for {action}: {e}")

    def save_to_file(self, file_path: Optional[Path] = None) -> bool:
        """Save keybindings to file.

        Args:
            file_path: Optional file path (defaults to config file)

        Returns:
            True if successful, False otherwise
        """
        file_path = file_path or self.config_file

        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, sort_keys=True)

            logger.info(f"Keybindings saved to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save keybindings to {file_path}: {e}")
            return False

    def load_from_file(self, file_path: Optional[Path] = None) -> bool:
        """Load keybindings from file.

        Args:
            file_path: Optional file path (defaults to config file)

        Returns:
            True if successful, False otherwise
        """
        file_path = file_path or self.config_file

        if not file_path.exists():
            logger.info(f"Keybinding file not found: {file_path}")
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.from_dict(data)
            logger.info(f"Keybindings loaded from {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load keybindings from {file_path}: {e}")
            return False

    def reset_to_defaults(self) -> None:
        """Reset all keybindings to defaults."""
        self.bindings.clear()
        self.key_to_action.clear()
        self._setup_default_bindings()

    def backup_keybindings(self, backup_path: Optional[Path] = None) -> bool:
        """Create a backup of current keybindings.

        Args:
            backup_path: Optional backup file path

        Returns:
            True if successful, False otherwise
        """
        if backup_path is None:
            import time
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_path = self.config_file.parent / \
                f"keybindings_backup_{timestamp}.json"

        return self.save_to_file(backup_path)
