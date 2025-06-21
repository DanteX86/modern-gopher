#!/usr/bin/env python3
"""
Tests for keybinding management system.
"""

import json
import tempfile
import unittest
from pathlib import Path

from modern_gopher.keybindings import KeyBinding, KeyBindingManager, KeyContext


class TestKeyBinding(unittest.TestCase):
    """Test KeyBinding class."""

    def test_key_normalization(self):
        """Test key normalization functionality."""
        # Test modifier normalization
        self.assertEqual(KeyBinding.normalize_key("ctrl+c"), "c-c")
        self.assertEqual(KeyBinding.normalize_key("alt+tab"), "a-tab")
        self.assertEqual(KeyBinding.normalize_key("shift+f1"), "s-f1")
        self.assertEqual(KeyBinding.normalize_key("cmd+z"), "m-z")

        # Test special key aliases
        self.assertEqual(KeyBinding.normalize_key("return"), "enter")
        self.assertEqual(KeyBinding.normalize_key("esc"), "escape")
        self.assertEqual(KeyBinding.normalize_key("del"), "delete")
        self.assertEqual(KeyBinding.normalize_key("pgup"), "pageup")
        self.assertEqual(KeyBinding.normalize_key("pgdn"), "pagedown")

        # Test case insensitive
        self.assertEqual(KeyBinding.normalize_key("CTRL+C"), "c-c")
        self.assertEqual(KeyBinding.normalize_key("Enter"), "enter")

    def test_key_binding_creation(self):
        """Test KeyBinding creation and normalization."""
        binding = KeyBinding(
            action="test_action",
            keys=["ctrl+c", "ESC", "return"],
            context=KeyContext.GLOBAL,
            description="Test binding",
        )

        # Keys should be normalized
        self.assertEqual(binding.keys, ["c-c", "escape", "enter"])
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
            description="First binding",
        )

        binding2 = KeyBinding(
            action="action2",
            keys=["w", "c-c"],  # Conflicts with c-c
            context=KeyContext.GLOBAL,
            description="Second binding",
        )

        binding3 = KeyBinding(
            action="action3",
            keys=["q"],  # Conflicts with q
            context=KeyContext.BROWSER,
            description="Third binding",
        )

        binding4 = KeyBinding(
            action="action4",
            keys=["q"],  # No conflict - different context
            context=KeyContext.CONTENT,
            description="Fourth binding",
        )

        # Test conflicts
        self.assertTrue(binding1.conflicts_with(binding2))
        # Global conflicts with specific
        self.assertTrue(binding1.conflicts_with(binding3))
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
        self.assertEqual(self.manager.get_action_for_key("q", KeyContext.BROWSER), "quit")
        self.assertEqual(self.manager.get_action_for_key("c-c", KeyContext.CONTENT), "quit")

        # Test context-specific actions
        self.assertEqual(self.manager.get_action_for_key("up", KeyContext.BROWSER), "navigate_up")
        self.assertEqual(self.manager.get_action_for_key("k", KeyContext.BROWSER), "navigate_up")

        # Test non-existent key
        self.assertIsNone(self.manager.get_action_for_key("xyz", KeyContext.BROWSER))

    def test_key_lookup(self):
        """Test getting keys for actions."""
        quit_keys = self.manager.get_keys_for_action("quit")
        self.assertIn("q", quit_keys)
        self.assertIn("c-c", quit_keys)

        nav_up_keys = self.manager.get_keys_for_action("navigate_up")
        self.assertIn("up", nav_up_keys)
        self.assertIn("k", nav_up_keys)

        # Non-existent action
        self.assertEqual(self.manager.get_keys_for_action("nonexistent"), [])

    def test_add_binding(self):
        """Test adding new bindings."""
        new_binding = KeyBinding(
            action="custom_action",
            keys=["ctrl+x"],
            context=KeyContext.BROWSER,
            description="Custom action",
            category="custom",
        )

        # Should succeed
        self.assertTrue(self.manager.add_binding(new_binding))
        self.assertIn("custom_action", self.manager.bindings)

        # Should be able to look it up
        self.assertEqual(
            self.manager.get_action_for_key("c-x", KeyContext.BROWSER), "custom_action"
        )

    def test_conflict_prevention(self):
        """Test that conflicting bindings are rejected."""
        conflicting_binding = KeyBinding(
            action="conflicting_action",
            keys=["q"],  # Conflicts with quit
            context=KeyContext.GLOBAL,
            description="Conflicting action",
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
            description="Custom action",
        )
        self.manager.add_binding(custom_binding)

        # Verify it exists
        self.assertIn("custom_action", self.manager.bindings)
        self.assertEqual(
            self.manager.get_action_for_key("c-y", KeyContext.BROWSER), "custom_action"
        )

        # Remove it
        self.assertTrue(self.manager.remove_binding("custom_action"))
        self.assertNotIn("custom_action", self.manager.bindings)
        self.assertIsNone(self.manager.get_action_for_key("c-y", KeyContext.BROWSER))

        # Try to remove non-existent binding
        self.assertFalse(self.manager.remove_binding("nonexistent"))

    def test_set_keys_for_action(self):
        """Test changing keys for an action."""
        # Change keys for navigate_up
        original_keys = self.manager.get_keys_for_action("navigate_up")
        new_keys = ["ctrl+up", "shift+k"]

        self.assertTrue(self.manager.set_keys_for_action("navigate_up", new_keys))

        # Check new keys work
        self.assertEqual(self.manager.get_action_for_key("c-up", KeyContext.BROWSER), "navigate_up")
        self.assertEqual(self.manager.get_action_for_key("s-k", KeyContext.BROWSER), "navigate_up")

        # Check old keys don't work
        for old_key in original_keys:
            self.assertNotEqual(
                self.manager.get_action_for_key(old_key, KeyContext.BROWSER), "navigate_up"
            )

    def test_disable_enable_binding(self):
        """Test disabling and enabling bindings."""
        # Disable quit binding
        self.assertTrue(self.manager.disable_binding("quit"))

        # Should not work anymore
        self.assertIsNone(self.manager.get_action_for_key("q", KeyContext.BROWSER))

        # But binding should still exist
        self.assertIn("quit", self.manager.bindings)
        self.assertFalse(self.manager.bindings["quit"].enabled)

        # Re-enable it
        self.assertTrue(self.manager.enable_binding("quit"))

        # Should work again
        self.assertEqual(self.manager.get_action_for_key("q", KeyContext.BROWSER), "quit")
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
            category="test",
        )
        self.manager.add_binding(custom_binding)

        # Save to file
        self.assertTrue(self.manager.save_to_file())
        self.assertTrue(self.config_file.exists())

        # Create new manager and load
        new_manager = KeyBindingManager(config_file=self.config_file)

        # Should have the custom binding
        self.assertIn("test_action", new_manager.bindings)
        self.assertEqual(new_manager.get_action_for_key("c-t", KeyContext.BROWSER), "test_action")

    def test_backup(self):
        """Test backup functionality."""
        backup_path = Path(self.temp_dir) / "backup.json"

        # Create backup
        self.assertTrue(self.manager.backup_keybindings(backup_path))
        self.assertTrue(backup_path.exists())

        # Backup should contain current bindings
        with open(backup_path, "r") as f:
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
            description="Custom action",
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
        self.assertEqual(set(self.manager.bindings.keys()), set(new_manager.bindings.keys()))

        # Should work the same
        self.assertEqual(
            self.manager.get_action_for_key("q", KeyContext.BROWSER),
            new_manager.get_action_for_key("q", KeyContext.BROWSER),
        )

    def test_categories(self):
        """Test category management."""
        categories = self.manager.get_all_categories()

        # Should have expected categories
        expected_categories = {
            "global",
            "navigation",
            "browser",
            "bookmarks",
            "history",
            "search",
            "content",
        }

        self.assertTrue(expected_categories.issubset(categories))


class TestKeyBindingManagerEdgeCases(unittest.TestCase):
    """Test edge cases and error handling for KeyBindingManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test config
        import tempfile
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_config = self.test_dir / "test_keybindings.json"
        self.manager = KeyBindingManager(self.test_config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_get_default_config_path(self):
        """Test get_default_config_path with missing directories."""
        # Test the static method directly
        default_path = KeyBindingManager.get_default_config_path()
        
        # Should return a Path object with correct structure
        self.assertIsInstance(default_path, Path)
        self.assertTrue(str(default_path).endswith("keybindings.json"))
        self.assertIn(".config", str(default_path))
        self.assertIn("modern-gopher", str(default_path))

    def test_set_keys_for_nonexistent_action(self):
        """Test set_keys_for_action with non-existent action."""
        result = self.manager.set_keys_for_action("nonexistent_action", ["x"])
        
        # Should return False and log error
        self.assertFalse(result)

    def test_set_keys_with_conflicts(self):
        """Test set_keys_for_action with conflicting keys."""
        # Try to set keys that conflict with existing binding
        result = self.manager.set_keys_for_action("refresh", ["q"])  # q is used by quit
        
        # Should return False due to conflict
        self.assertFalse(result)
        
        # Original keys should be restored
        original_keys = self.manager.get_keys_for_action("refresh")
        self.assertIn("r", original_keys)

    def test_disable_nonexistent_binding(self):
        """Test disable_binding with non-existent action."""
        result = self.manager.disable_binding("nonexistent_action")
        
        # Should return False
        self.assertFalse(result)

    def test_enable_nonexistent_binding(self):
        """Test enable_binding with non-existent action."""
        result = self.manager.enable_binding("nonexistent_action")
        
        # Should return False
        self.assertFalse(result)

    def test_enable_binding_with_conflicts(self):
        """Test enable_binding when conflicts exist."""
        # First disable a binding
        self.manager.disable_binding("quit")
        
        # Add a new binding with same keys using add_binding (which forces even conflicts)
        new_binding = KeyBinding(
            action="test_action",
            keys=["q"],
            context=KeyContext.GLOBAL,
            description="Test action"
        )
        # Force add it by directly manipulating the internal state
        self.manager.bindings["test_action"] = new_binding
        for key in new_binding.keys:
            self.manager.key_to_action[(key, new_binding.context)] = new_binding.action
            if new_binding.context == KeyContext.GLOBAL:
                for context in KeyContext:
                    self.manager.key_to_action[(key, context)] = new_binding.action
        
        # Try to enable the original quit binding
        result = self.manager.enable_binding("quit")
        
        # Should return False due to conflict
        self.assertFalse(result)

    def test_validate_key_edge_cases(self):
        """Test validate_key with various edge cases."""
        # Test invalid modifier count
        self.assertFalse(self.manager.validate_key("c-a-x"))  # Multiple modifiers
        
        # Test empty key part
        self.assertFalse(self.manager.validate_key("c-"))  # Empty after modifier
        
        # Test key with + (not normalized)
        self.assertFalse(self.manager.validate_key("ctrl+x"))  # Should be c-x
        
        # Test exception handling by passing invalid input
        self.assertFalse(self.manager.validate_key(""))  # Empty string
        self.assertFalse(self.manager.validate_key(None))  # None input

    def test_from_dict_error_handling(self):
        """Test from_dict with invalid data."""
        # Add some valid data first so we have a baseline
        valid_data = {
            "test_valid_action": {
                "keys": ["x"],
                "context": "global",
                "description": "Valid test action",
                "category": "test",
                "enabled": True
            }
        }
        
        mixed_data = {
            **valid_data,
            "invalid_action": {
                "keys": ["y"],
                "context": "invalid_context",  # Invalid context
                "description": "Test"
            },
            "missing_keys_action": {
                "context": "global",
                "description": "Test missing keys"
                # Missing "keys" field
            }
        }
        
        # Should not raise exception, but log warnings
        self.manager.from_dict(mixed_data)
        
        # Should only have the valid binding, not the invalid ones
        self.assertIn("test_valid_action", self.manager.bindings)
        self.assertNotIn("invalid_action", self.manager.bindings)
        self.assertNotIn("missing_keys_action", self.manager.bindings)

    def test_save_to_file_error_handling(self):
        """Test save_to_file with invalid path."""
        # Try to save to an invalid path (like a directory that can't be created)
        invalid_path = Path("/root/cannot_create_this/keybindings.json")
        
        result = self.manager.save_to_file(invalid_path)
        
        # Should return False on error
        self.assertFalse(result)

    def test_load_from_nonexistent_file(self):
        """Test load_from_file with non-existent file."""
        nonexistent_file = Path("/nonexistent/path/keybindings.json")
        
        result = self.manager.load_from_file(nonexistent_file)
        
        # Should return False
        self.assertFalse(result)

    def test_load_from_file_error_handling(self):
        """Test load_from_file with corrupted file."""
        # Create a corrupted JSON file
        corrupted_file = self.test_dir / "corrupted.json"
        with open(corrupted_file, "w") as f:
            f.write("{ invalid json content ")
        
        result = self.manager.load_from_file(corrupted_file)
        
        # Should return False on error
        self.assertFalse(result)

    def test_backup_keybindings_default_path(self):
        """Test backup_keybindings with default path generation."""
        # Test backup with auto-generated timestamp path
        result = self.manager.backup_keybindings()
        
        # Should succeed
        self.assertTrue(result)
        
        # Check that backup file was created
        backup_files = list(self.test_config.parent.glob("keybindings_backup_*.json"))
        self.assertGreater(len(backup_files), 0)

    def test_from_dict_with_disabled_bindings(self):
        """Test from_dict with disabled bindings to hit line 575."""
        data_with_disabled = {
            "disabled_action": {
                "keys": ["z"],
                "context": "global",
                "description": "Disabled action",
                "category": "test",
                "enabled": False  # This should hit line 575
            }
        }
        
        self.manager.from_dict(data_with_disabled)
        
        # Should have the binding but it should be disabled
        self.assertIn("disabled_action", self.manager.bindings)
        self.assertFalse(self.manager.bindings["disabled_action"].enabled)
        
        # Should not be in key mappings since it's disabled
        self.assertIsNone(self.manager.get_action_for_key("z", KeyContext.GLOBAL))

    def test_enable_binding_conflict_scenario(self):
        """Test enable_binding conflict detection to hit lines 439, 442-443."""
        # Disable a binding first
        self.manager.disable_binding("quit")
        
        # Manually add a conflicting binding to force the conflict scenario
        conflicting_binding = KeyBinding(
            action="conflicting_action",
            keys=["q"],  # Same key as quit
            context=KeyContext.GLOBAL,
            description="Conflicting action"
        )
        
        # Add it manually to force the conflict
        self.manager.bindings["conflicting_action"] = conflicting_binding
        for key in conflicting_binding.keys:
            self.manager.key_to_action[(key, conflicting_binding.context)] = conflicting_binding.action
            if conflicting_binding.context == KeyContext.GLOBAL:
                for context in KeyContext:
                    self.manager.key_to_action[(key, context)] = conflicting_binding.action
        
        # Now try to enable the quit binding - this should trigger conflict detection
        result = self.manager.enable_binding("quit")
        
        # Should return False due to conflict (hits lines 439, 442-443)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
