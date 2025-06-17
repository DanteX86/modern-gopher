#!/usr/bin/env python3
"""
Test script for configuration system functionality.

This tests the configuration loading, saving, validation, and integration.
"""

import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, 'src')

from modern_gopher.config import ModernGopherConfig, get_config
from rich.console import Console
from rich.panel import Panel

console = Console()

def test_config_creation():
    """Test creating a config object with defaults."""
    console.print("\n🔧 Testing Configuration Creation...", style="cyan")
    
    config = ModernGopherConfig()
    
    # Test basic properties
    assert config.default_server == 'gopher://gopher.floodgap.com'
    assert config.timeout == 30
    assert config.cache_enabled is True
    assert config.bookmarks_file.endswith('bookmarks.json')
    
    console.print("  ✅ Default configuration created successfully")
    console.print(f"  📂 Cache directory: {config.cache_directory}")
    console.print(f"  📑 Bookmarks file: {config.bookmarks_file}")
    
    return True

def test_config_serialization():
    """Test config to_dict and from_dict conversion."""
    console.print("\n📦 Testing Configuration Serialization...", style="cyan")
    
    # Create config with custom values
    config = ModernGopherConfig(
        default_server='gopher://test.server.com',
        timeout=60,
        cache_enabled=False
    )
    
    # Convert to dict
    config_dict = config.to_dict()
    assert config_dict['gopher']['default_server'] == 'gopher://test.server.com'
    assert config_dict['gopher']['timeout'] == 60
    assert config_dict['cache']['enabled'] is False
    
    # Convert back from dict
    config2 = ModernGopherConfig.from_dict(config_dict)
    assert config2.default_server == 'gopher://test.server.com'
    assert config2.timeout == 60
    assert config2.cache_enabled is False
    
    console.print("  ✅ Serialization to dict working correctly")
    console.print("  ✅ Deserialization from dict working correctly")
    
    return True

def test_config_file_operations():
    """Test saving and loading config files."""
    console.print("\n💾 Testing Configuration File Operations...", style="cyan")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / 'test_config.yaml'
        
        # Create and save config
        config = ModernGopherConfig(
            default_server='gopher://test.example.com',
            timeout=45,
            cache_max_size_mb=200
        )
        
        success = config.save(config_path)
        assert success is True
        assert config_path.exists()
        
        console.print(f"  ✅ Configuration saved to {config_path}")
        
        # Load config back
        loaded_config = ModernGopherConfig.load(config_path)
        assert loaded_config.default_server == 'gopher://test.example.com'
        assert loaded_config.timeout == 45
        assert loaded_config.cache_max_size_mb == 200
        
        console.print("  ✅ Configuration loaded correctly")
        
        # Test loading non-existent file (should return defaults)
        non_existent = Path(temp_dir) / 'does_not_exist.yaml'
        default_config = ModernGopherConfig.load(non_existent)
        assert default_config.default_server == 'gopher://gopher.floodgap.com'
        
        console.print("  ✅ Non-existent file handling working correctly")
    
    return True

def test_config_validation():
    """Test configuration validation."""
    console.print("\n✅ Testing Configuration Validation...", style="cyan")
    
    # Valid config
    valid_config = ModernGopherConfig()
    assert valid_config.validate() is True
    console.print("  ✅ Valid configuration passes validation")
    
    # Invalid timeout
    invalid_config = ModernGopherConfig(timeout=-5)
    assert invalid_config.validate() is False
    console.print("  ✅ Invalid timeout caught by validation")
    
    # Invalid cache size
    invalid_config2 = ModernGopherConfig(cache_max_size_mb=0)
    assert invalid_config2.validate() is False
    console.print("  ✅ Invalid cache size caught by validation")
    
    # Invalid log level
    invalid_config3 = ModernGopherConfig(log_level='INVALID')
    assert invalid_config3.validate() is False
    console.print("  ✅ Invalid log level caught by validation")
    
    return True

def test_config_directory_creation():
    """Test automatic directory creation."""
    console.print("\n📁 Testing Directory Creation...", style="cyan")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create config with custom paths in temp directory
        custom_cache = os.path.join(temp_dir, 'custom_cache')
        custom_config_dir = os.path.join(temp_dir, 'custom_config')
        custom_bookmarks = os.path.join(custom_config_dir, 'bookmarks.json')
        
        config = ModernGopherConfig(
            cache_directory=custom_cache,
            bookmarks_file=custom_bookmarks
        )
        
        # Ensure directories are created
        config.ensure_directories()
        
        assert Path(custom_cache).exists()
        assert Path(custom_config_dir).exists()
        
        console.print(f"  ✅ Cache directory created: {custom_cache}")
        console.print(f"  ✅ Config directory created: {custom_config_dir}")
    
    return True

def test_get_config_function():
    """Test the get_config convenience function."""
    console.print("\n⚙️  Testing get_config() Function...", style="cyan")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / 'test_get_config.yaml'
        
        # Test with custom config file
        config = get_config(config_path)
        assert config is not None
        assert isinstance(config, ModernGopherConfig)
        assert config_path.exists()  # Should be created with defaults
        
        console.print("  ✅ get_config() creates default config when file doesn't exist")
        
        # Test loading existing config
        config2 = get_config(config_path)
        assert config2.default_server == config.default_server
        
        console.print("  ✅ get_config() loads existing config correctly")
    
    return True

def test_effective_initial_url():
    """Test the effective_initial_url property."""
    console.print("\n🔗 Testing Effective Initial URL...", style="cyan")
    
    # Config with no initial URL (should use default_server)
    config1 = ModernGopherConfig()
    assert config1.effective_initial_url == config1.default_server
    
    # Config with custom initial URL
    config2 = ModernGopherConfig(initial_url='gopher://custom.example.com')
    assert config2.effective_initial_url == 'gopher://custom.example.com'
    
    console.print("  ✅ effective_initial_url works correctly")
    
    return True

def main():
    """Run all configuration tests."""
    console.print(Panel.fit(
        "🔧 Configuration System Test Suite",
        title="Modern Gopher",
        subtitle="Testing configuration functionality"
    ))
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Configuration Creation", test_config_creation),
        ("Serialization", test_config_serialization),
        ("File Operations", test_config_file_operations),
        ("Validation", test_config_validation),
        ("Directory Creation", test_config_directory_creation),
        ("get_config() Function", test_get_config_function),
        ("Effective Initial URL", test_effective_initial_url)
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
    console.print("-" * 40)
    
    all_passed = True
    for test_name, passed in test_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        console.print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        console.print("\n🎉 All configuration tests passed!", style="bold green")
        console.print("\n💡 Configuration system is ready for use:", style="cyan")
        console.print("  • python -m modern_gopher.cli config show")
        console.print("  • python -m modern_gopher.cli config path")
        console.print("  • python -m modern_gopher.cli config reset")
        return 0
    else:
        console.print("\n⚠️  Some configuration tests failed.", style="bold red")
        return 1

if __name__ == "__main__":
    sys.exit(main())

