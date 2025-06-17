#!/usr/bin/env python3
"""
Tests for keybinding management system.
"""

import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from modern_gopher.keybindings import (
    KeyBinding, KeyBindingManager, KeyContext
)


class TestKeyBinding(unittest.TestCase):
    """Test KeyBinding class."""
    
    def test_key_normalization(self):
        """Test key normalization functionality."""
        # Test modifier normalization
        self.assertEqual(KeyBinding.normalize_key('ctrl+c'), 'c-c')
        self.assertEqual(KeyBinding.normalize_key('alt+tab'), 'a-tab')
        self.assertEqual(KeyBinding.normalize_key('shift+f1'), 's-f1')
        self.assertEqual(KeyBinding.normalize_key('cmd+z'), 'm-z')
        
        # Test special key aliases
        self.assertEqual(KeyBinding.normalize_key('return'), 'enter')
        self.assertEqual(KeyBinding.normalize_key('esc'), 'escape')
        self.assertEqual(KeyBinding.normalize_key('del'), 'delete')
        self.assertEqual(KeyBinding.normalize_key('pgup'), 'pageup')
        self.assertEqual(KeyBinding.normalize_key('pgdn'), 'pagedown')
        
        # Test case insensitive
        self.assertEqual(KeyBinding.normalize_key('CTRL+C'), 'c-c')
        self.assertEqual(KeyBinding.normalize_key('Enter'), 'enter')
    
    def test_key_binding_creation(self):
        """Test KeyBinding creation and normalization."""
        binding = KeyBinding(
            action="test_action",
            keys=["ctrl+c", "ESC", "return"],
            context=KeyContext.GLOBAL,
            description="Test binding"
        )
        
        # Keys should be normalized
        self.assertEqual(binding.keys, ['c-c', 'escape', 'enter'])
        self.assertEqual(binding.action, "test_action")
        self.assertEqual(binding.context, KeyContext.GLOBAL)
        self.assertEqual(binding.description, "Test binding")
        self.assertEqual(binding.category, "general")  # Default
        self.assertTrue(binding.enabled)  # Default
    
    def test_conflict_detection(self):
        """Test conflict detection between bindings."""
        binding1 = KeyBinding(
            action="action1",
            keys=["q", "c-c"],
            context=KeyContext.GLOBAL,
            description="First binding"
        )
        
        binding2 = KeyBinding(
            action="action2",
            keys=["w", "c-c"],  # Conflicts with c-c
            context=KeyContext.GLOBAL,
            description="Second binding"
        )
        
        binding3 = KeyBinding(
            action="action3",
            keys=["q"],  # Conflicts with q
            context=KeyContext.BROWSER,
            description="Third binding"
        )
        
        binding4 = KeyBinding(
            action="action4",
            keys=["q"],  # No conflict - different context
            context=KeyContext.CONTENT,
            description="Fourth binding"
        )
        
        # Test conflicts
        self.assertTrue(binding1.conflicts_with(binding2))
        self.assertTrue(binding1.conflicts_with(binding3))  # Global conflicts with specific
        self.assertFalse(binding3.conflicts_with(binding4))  # Different contexts


class TestKeyBindingManager(unittest.TestCase):
    """Test KeyBindingManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_keybindings.json"
        self.manager = KeyBindingManager(config_file=self.config_file)
    
    def test_initialization(self):
        """Test manager initialization."""
        # Should have default bindings loaded
        self.assertGreater(len(self.manager.bindings), 0)
        
        # Check some expected default bindings
        self.assertIn("quit", self.manager.bindings)
        self.assertIn("help", self.manager.bindings)
        self.assertIn("navigate_up", self.manager.bindings)
        self.assertIn("navigate_down", self.manager.bindings)
        
        # Config file should be created with defaults
        self.assertTrue(self.config_file.exists())
    
    def test_action_lookup(self):
        """Test getting actions for keys."""
        # Test global actions
        self.assertEqual(
            self.manager.get_action_for_key("q", KeyContext.BROWSER),
            "quit"
        )
        self.assertEqual(
            self.manager.get_action_for_key("c-c", KeyContext.CONTENT),
            "quit"
        )
        
        # Test context-specific actions
        self.assertEqual(
            self.manager.get_action_for_key("up", KeyContext.BROWSER),
            "navigate_up"
        )
        self.assertEqual(
            self.manager.get_action_for_key("k", KeyContext.BROWSER),
            "navigate_up"
        )
        
        # Test non-existent key
        self.assertIsNone(
            self.manager.get_action_for_key("xyz", KeyContext.BROWSER)
        )
    
    def test_key_lookup(self):
        """Test getting keys for actions."""
        quit_keys = self.manager.get_keys_for_action("quit")
        self.assertIn("q", quit_keys)
        self.assertIn("c-c", quit_keys)
        
        nav_up_keys = self.manager.get_keys_for_action("navigate_up")
        self.assertIn("up", nav_up_keys)
        self.assertIn("k", nav_up_keys)
        
        # Non-existent action
        self.assertEqual(
            self.manager.get_keys_for_action("nonexistent"),
            []
        )
    
    def test_add_binding(self):
        """Test adding new bindings."""
        new_binding = KeyBinding(
            action="custom_action",
            keys=["ctrl+x"],
            context=KeyContext.BROWSER,
            description="Custom action",
            category="custom"
        )
        
        # Should succeed
        self.assertTrue(self.manager.add_binding(new_binding))
        self.assertIn("custom_action", self.manager.bindings)
        
        # Should be able to look it up
        self.assertEqual(
            self.manager.get_action_for_key("c-x", KeyContext.BROWSER),
            "custom_action"
        )
    
    def test_conflict_prevention(self):
        """Test that conflicting bindings are rejected."""
        conflicting_binding = KeyBinding(
            action="conflicting_action",
            keys=["q"],  # Conflicts with quit
            context=KeyContext.GLOBAL,
            description="Conflicting action"
        )
        
        # Should fail due to conflict
        self.assertFalse(self.manager.add_binding(conflicting_binding))
        self.assertNotIn("conflicting_action", self.manager.bindings)
    
    def test_remove_binding(self):
        """Test removing bindings."""
        # Add a custom binding first
        custom_binding = KeyBinding(
            action="custom_action",
            keys=["ctrl+y"],
            context=KeyContext.BROWSER,
            description="Custom action"
        )
        self.manager.add_binding(custom_binding)
        
        # Verify it exists
        self.assertIn("custom_action", self.manager.bindings)
        self.assertEqual(
            self.manager.get_action_for_key("c-y", KeyContext.BROWSER),
            "custom_action"
        )
        
        # Remove it
        self.assertTrue(self.manager.remove_binding("custom_action"))
        self.assertNotIn("custom_action", self.manager.bindings)
        self.assertIsNone(
            self.manager.get_action_for_key("c-y", KeyContext.BROWSER)
        )
        
        # Try to remove non-existent binding
        self.assertFalse(self.manager.remove_binding("nonexistent"))
    
    def test_set_keys_for_action(self):
        """Test changing keys for an action."""
        # Change keys for navigate_up
        original_keys = self.manager.get_keys_for_action("navigate_up")
        new_keys = ["ctrl+up", "shift+k"]
        
        self.assertTrue(self.manager.set_keys_for_action("navigate_up", new_keys))
        
        # Check new keys work
        self.assertEqual(
            self.manager.get_action_for_key("c-up", KeyContext.BROWSER),
            "navigate_up"
        )
        self.assertEqual(
            self.manager.get_action_for_key("s-k", KeyContext.BROWSER),
            "navigate_up"
        )
        
        # Check old keys don't work
        for old_key in original_keys:
            self.assertNotEqual(
                self.manager.get_action_for_key(old_key, KeyContext.BROWSER),
                "navigate_up"
            )
    
    def test_disable_enable_binding(self):
        """Test disabling and enabling bindings."""
        # Disable quit binding
        self.assertTrue(self.manager.disable_binding("quit"))
        
        # Should not work anymore
        self.assertIsNone(
            self.manager.get_action_for_key("q", KeyContext.BROWSER)
        )
        
        # But binding should still exist
        self.assertIn("quit", self.manager.bindings)
        self.assertFalse(self.manager.bindings["quit"].enabled)
        
        # Re-enable it
        self.assertTrue(self.manager.enable_binding("quit"))
        
        # Should work again
        self.assertEqual(
            self.manager.get_action_for_key("q", KeyContext.BROWSER),
            "quit"
        )
        self.assertTrue(self.manager.bindings["quit"].enabled)
    
    def test_filtering_by_category(self):
        """Test filtering bindings by category."""
        global_bindings = self.manager.get_bindings_by_category("global")
        self.assertIn("quit", global_bindings)
        self.assertIn("help", global_bindings)
        
        nav_bindings = self.manager.get_bindings_by_category("navigation")
        self.assertIn("navigate_up", nav_bindings)
        self.assertIn("navigate_down", nav_bindings)
        
        # Non-existent category
        empty_bindings = self.manager.get_bindings_by_category("nonexistent")
        self.assertEqual(len(empty_bindings), 0)
    
    def test_filtering_by_context(self):
        """Test filtering bindings by context."""
        browser_bindings = self.manager.get_bindings_by_context(KeyContext.BROWSER)
        
        # Should include browser-specific bindings
        self.assertIn("navigate_up", browser_bindings)
        self.assertIn("bookmark_toggle", browser_bindings)
        
        # Should also include global bindings
        self.assertIn("quit", browser_bindings)
        self.assertIn("help", browser_bindings)
        
        # Content context should have different bindings
        content_bindings = self.manager.get_bindings_by_context(KeyContext.CONTENT)
        self.assertIn("scroll_up", content_bindings)
        self.assertIn("scroll_down", content_bindings)
        
        # But also global ones
        self.assertIn("quit", content_bindings)
    
    def test_key_validation(self):
        """Test key validation."""
        # Valid keys (both normalized and original forms)
        self.assertTrue(self.manager.validate_key("q"))
        self.assertTrue(self.manager.validate_key("c-c"))  # Normalized form
        self.assertTrue(self.manager.validate_key("a-f4"))  # Normalized form
        self.assertTrue(self.manager.validate_key("s-tab"))  # Normalized form
        self.assertTrue(self.manager.validate_key("enter"))
        
        # Invalid keys
        self.assertFalse(self.manager.validate_key(""))
        self.assertFalse(self.manager.validate_key("   "))
        self.assertFalse(self.manager.validate_key("invalid+modifier+key"))  # Multiple + signs
        self.assertFalse(self.manager.validate_key("x-y"))  # Invalid modifier
        self.assertFalse(self.manager.validate_key("c-"))  # Empty key part
    
    def test_serialization(self):
        """Test saving and loading keybindings."""
        # Add a custom binding
        custom_binding = KeyBinding(
            action="test_action",
            keys=["ctrl+t"],
            context=KeyContext.BROWSER,
            description="Test action",
            category="test"
        )
        self.manager.add_binding(custom_binding)
        
        # Save to file
        self.assertTrue(self.manager.save_to_file())
        self.assertTrue(self.config_file.exists())
        
        # Create new manager and load
        new_manager = KeyBindingManager(config_file=self.config_file)
        
        # Should have the custom binding
        self.assertIn("test_action", new_manager.bindings)
        self.assertEqual(
            new_manager.get_action_for_key("c-t", KeyContext.BROWSER),
            "test_action"
        )
    
    def test_backup(self):
        """Test backup functionality."""
        backup_path = Path(self.temp_dir) / "backup.json"
        
        # Create backup
        self.assertTrue(self.manager.backup_keybindings(backup_path))
        self.assertTrue(backup_path.exists())
        
        # Backup should contain current bindings
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)
        
        self.assertIn("quit", backup_data)
        self.assertIn("help", backup_data)
    
    def test_reset_to_defaults(self):
        """Test resetting to default bindings."""
        # Add custom binding
        custom_binding = KeyBinding(
            action="custom_action",
            keys=["ctrl+z"],
            context=KeyContext.BROWSER,
            description="Custom action"
        )
        self.manager.add_binding(custom_binding)
        
        # Modify existing binding
        self.manager.set_keys_for_action("quit", ["ctrl+q"])
        
        # Reset to defaults
        self.manager.reset_to_defaults()
        
        # Custom binding should be gone
        self.assertNotIn("custom_action", self.manager.bindings)
        
        # Quit binding should be back to default
        quit_keys = self.manager.get_keys_for_action("quit")
        self.assertIn("q", quit_keys)
        self.assertIn("c-c", quit_keys)
    
    def test_dict_conversion(self):
        """Test dictionary conversion methods."""
        # Convert to dict
        data = self.manager.to_dict()
        
        # Should contain all bindings
        self.assertIn("quit", data)
        self.assertIn("help", data)
        
        # Check structure
        quit_data = data["quit"]
        self.assertIn("keys", quit_data)
        self.assertIn("context", quit_data)
        self.assertIn("description", quit_data)
        self.assertIn("category", quit_data)
        self.assertIn("enabled", quit_data)
        
        # Create new manager from dict
        new_manager = KeyBindingManager(config_file=Path(self.temp_dir) / "new.json")
        new_manager.from_dict(data)
        
        # Should have same bindings
        self.assertEqual(
            set(self.manager.bindings.keys()),
            set(new_manager.bindings.keys())
        )
        
        # Should work the same
        self.assertEqual(
            self.manager.get_action_for_key("q", KeyContext.BROWSER),
            new_manager.get_action_for_key("q", KeyContext.BROWSER)
        )
    
    def test_categories(self):
        """Test category management."""
        categories = self.manager.get_all_categories()
        
        # Should have expected categories
        expected_categories = {
            "global", "navigation", "browser", "bookmarks", "history", "search", "content"
        }
        
        self.assertTrue(expected_categories.issubset(categories))


if __name__ == '__main__':
    unittest.main()

