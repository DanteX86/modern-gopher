#!/usr/bin/env python3
"""
Enhanced Configuration System Test Script

This tests the new configuration management features including:
- set/get/list commands
- validation system
- backup functionality
- section reset
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, 'src')

from modern_gopher.config import ModernGopherConfig, get_config
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def test_enhanced_config_methods():
    """Test the new configuration methods."""
    console.print("\n🔧 Testing Enhanced Configuration Methods...", style="cyan")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / 'test_config.yaml'
        config = ModernGopherConfig()
        
        # Test set_value method
        console.print("  Testing set_value method...")
        assert config.set_value('gopher.timeout', 60) == True
        assert config.timeout == 60
        
        assert config.set_value('cache.enabled', False) == True
        assert config.cache_enabled == False
        
        # Test invalid key
        assert config.set_value('invalid.key', 'value') == False
        
        # Test get_value method
        console.print("  Testing get_value method...")
        assert config.get_value('gopher.timeout') == 60
        assert config.get_value('cache.enabled') == False
        assert config.get_value('invalid.key') is None
        
        # Test list_all_settings method
        console.print("  Testing list_all_settings method...")
        all_settings = config.list_all_settings()
        assert 'gopher' in all_settings
        assert 'cache' in all_settings
        assert all_settings['gopher']['timeout'] == 60
        
        # Test reset_section method
        console.print("  Testing reset_section method...")
        assert config.reset_section('gopher') == True
        assert config.timeout == 30  # Should be back to default
        
        # Test backup_config method
        console.print("  Testing backup_config method...")
        backup_path = Path(temp_dir) / 'backup.yaml'
        assert config.backup_config(backup_path) == True
        assert backup_path.exists()
        
    console.print("  ✅ All enhanced configuration methods working correctly")
    return True

def test_validation_system():
    """Test the configuration validation system."""
    console.print("\n✅ Testing Configuration Validation System...", style="cyan")
    
    config = ModernGopherConfig()
    
    # Test valid settings
    console.print("  Testing valid settings...")
    is_valid, msg = config.validate_setting('gopher.timeout', 45)
    assert is_valid == True
    
    is_valid, msg = config.validate_setting('cache.enabled', 'true')
    assert is_valid == True
    
    is_valid, msg = config.validate_setting('ui.color_scheme', 'dark')
    assert is_valid == True
    
    # Test invalid settings
    console.print("  Testing invalid settings...")
    is_valid, msg = config.validate_setting('gopher.timeout', -5)
    assert is_valid == False
    assert 'positive' in msg
    
    is_valid, msg = config.validate_setting('gopher.default_port', 70000)
    assert is_valid == False
    assert 'between 1 and 65535' in msg
    
    is_valid, msg = config.validate_setting('logging.level', 'INVALID')
    assert is_valid == False
    assert 'must be one of' in msg
    
    # Test invalid key path
    is_valid, msg = config.validate_setting('invalid.key', 'value')
    assert is_valid == False
    
    is_valid, msg = config.validate_setting('gopher.invalid_key', 'value')
    assert is_valid == False
    
    console.print("  ✅ Configuration validation system working correctly")
    return True

def test_type_conversion():
    """Test automatic type conversion in set_value."""
    console.print("\n🔄 Testing Type Conversion...", style="cyan")
    
    config = ModernGopherConfig()
    
    # Test boolean conversion
    console.print("  Testing boolean conversion...")
    assert config.set_value('cache.enabled', 'true') == True
    assert config.cache_enabled == True
    
    assert config.set_value('cache.enabled', 'false') == True
    assert config.cache_enabled == False
    
    assert config.set_value('cache.enabled', '1') == True
    assert config.cache_enabled == True
    
    # Test integer conversion
    console.print("  Testing integer conversion...")
    assert config.set_value('gopher.timeout', '45') == True
    assert config.timeout == 45
    assert isinstance(config.timeout, int)
    
    # Test string values
    console.print("  Testing string conversion...")
    assert config.set_value('ui.color_scheme', 'dark') == True
    assert config.color_scheme == 'dark'
    
    console.print("  ✅ Type conversion working correctly")
    return True

def test_cli_integration():
    """Test CLI integration with enhanced config commands."""
    console.print("\n🖥️  Testing CLI Integration...", style="cyan")
    
    import subprocess
    import json
    
    # Test config list command
    console.print("  Testing config list command...")
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'modern_gopher.cli', 'config', 'list'],
            capture_output=True,
            text=True,
            timeout=10
        )
        # Should exit successfully
        assert result.returncode == 0
        console.print("    ✅ config list command works")
    except Exception as e:
        console.print(f"    ❌ config list command failed: {e}")
        return False
    
    # Test config show command
    console.print("  Testing config show command...")
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'modern_gopher.cli', 'config', 'show'],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result.returncode == 0
        console.print("    ✅ config show command works")
    except Exception as e:
        console.print(f"    ❌ config show command failed: {e}")
        return False
    
    # Test config path command
    console.print("  Testing config path command...")
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'modern_gopher.cli', 'config', 'path'],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result.returncode == 0
        console.print("    ✅ config path command works")
    except Exception as e:
        console.print(f"    ❌ config path command failed: {e}")
        return False
    
    console.print("  ✅ CLI integration working correctly")
    return True

def test_error_handling():
    """Test error handling in configuration system."""
    console.print("\n🚨 Testing Error Handling...", style="cyan")
    
    config = ModernGopherConfig()
    
    # Test setting invalid values
    console.print("  Testing invalid value handling...")
    assert config.set_value('gopher.timeout', 'not_a_number') == False
    assert config.set_value('cache.max_size_mb', -100) == False
    
    # Test getting non-existent keys
    console.print("  Testing non-existent key handling...")
    assert config.get_value('nonexistent.key') is None
    assert config.get_value('gopher.nonexistent') is None
    
    # Test resetting invalid section
    console.print("  Testing invalid section reset...")
    assert config.reset_section('nonexistent_section') == False
    
    console.print("  ✅ Error handling working correctly")
    return True

def show_demo_usage():
    """Show demo of the enhanced configuration commands."""
    console.print("\n🎮 Configuration System Demo", style="bold green")
    console.print("=" * 50)
    
    # Create example usage table
    table = Table(title="Enhanced Configuration Commands")
    table.add_column("Command", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Example", style="green")
    
    commands = [
        ("config show", "Display all configuration", "modern-gopher config show"),
        ("config list", "List all available keys", "modern-gopher config list"),
        ("config get", "Get specific value", "modern-gopher config get gopher.timeout"),
        ("config set", "Set specific value", "modern-gopher config set gopher.timeout 60"),
        ("config reset", "Reset to defaults", "modern-gopher config reset gopher"),
        ("config backup", "Create backup", "modern-gopher config backup"),
        ("config path", "Show config file path", "modern-gopher config path"),
    ]
    
    for cmd, desc, example in commands:
        table.add_row(cmd, desc, example)
    
    console.print(table)
    
    console.print("\n💡 Pro Tips:", style="bold yellow")
    console.print("  • Use 'config list' to see all available settings")
    console.print("  • Boolean values accept: true/false, 1/0, yes/no, on/off")
    console.print("  • Changes are automatically validated before saving")
    console.print("  • Use 'config backup' before making major changes")
    console.print("  • Reset specific sections with 'config reset <section>'")

def main():
    """Run all enhanced configuration tests."""
    console.print(Panel.fit(
        "🔧 Enhanced Configuration System Test Suite",
        title="Modern Gopher",
        subtitle="Testing advanced configuration features"
    ))
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Enhanced Config Methods", test_enhanced_config_methods),
        ("Validation System", test_validation_system),
        ("Type Conversion", test_type_conversion),
        ("CLI Integration", test_cli_integration),
        ("Error Handling", test_error_handling),
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, True))
        except Exception as e:
            console.print(f"  ❌ {test_name} failed: {e}", style="red")
            test_results.append((test_name, False))
    
    # Show results summary
    console.print("\n📊 Test Results Summary:", style="bold yellow")
    console.print("-" * 50)
    
    all_passed = True
    for test_name, passed in test_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        console.print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        console.print("\n🎉 All enhanced configuration tests passed!", style="bold green")
        show_demo_usage()
        return 0
    else:
        console.print("\n⚠️  Some enhanced configuration tests failed.", style="bold red")
        return 1

if __name__ == "__main__":
    sys.exit(main())

