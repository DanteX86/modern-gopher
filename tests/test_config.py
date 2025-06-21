"""
Tests for the configuration management system.
"""

import os
import tempfile
from pathlib import Path

import yaml

from modern_gopher.config import DEFAULT_CONFIG, ModernGopherConfig, get_config


class TestModernGopherConfig:
    """Test the ModernGopherConfig class."""

    def test_config_creation_with_defaults(self):
        """Test creating config with default values."""
        config = ModernGopherConfig()

        # Test Gopher defaults
        assert config.default_server == "gopher://gopher.floodgap.com"
        assert config.default_port == 70
        assert config.timeout == 30
        assert config.use_ssl is False
        assert config.use_ipv6 is None

        # Test cache defaults
        assert config.cache_enabled is True
        assert config.cache_max_size_mb == 100
        assert config.cache_expiration_hours == 24

        # Test browser defaults
        assert config.initial_url is None
        assert config.max_history_items == 1000
        assert config.save_session is True

        # Test UI defaults
        assert config.show_icons is True
        assert config.mouse_support is True
        assert config.color_scheme == "default"

    def test_config_creation_with_custom_values(self):
        """Test creating config with custom values."""
        config = ModernGopherConfig(
            default_server="gopher://custom.example.com",
            timeout=60,
            use_ssl=True,
            cache_enabled=False,
            color_scheme="dark",
        )

        assert config.default_server == "gopher://custom.example.com"
        assert config.timeout == 60
        assert config.use_ssl is True
        assert config.cache_enabled is False
        assert config.color_scheme == "dark"

    def test_effective_initial_url(self):
        """Test effective initial URL property."""
        # With no initial URL, should use default server
        config = ModernGopherConfig(default_server="gopher://test.com", initial_url=None)
        assert config.effective_initial_url == "gopher://test.com"

        # With initial URL, should use that
        config.initial_url = "gopher://other.com"
        assert config.effective_initial_url == "gopher://other.com"

    def test_path_expansion(self):
        """Test that user paths are expanded."""
        config = ModernGopherConfig(
            cache_directory="~/test-cache", bookmarks_file="~/test-bookmarks.json"
        )

        # Paths should be expanded
        assert not config.cache_directory.startswith("~")
        assert not config.bookmarks_file.startswith("~")
        assert str(Path.home()) in config.cache_directory
        assert str(Path.home()) in config.bookmarks_file

    def test_config_dir_property(self):
        """Test config directory property."""
        config = ModernGopherConfig()
        config_dir = config.config_dir

        assert isinstance(config_dir, Path)
        assert config_dir.name == "modern-gopher"

    def test_ensure_directories(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ModernGopherConfig(
                cache_directory=os.path.join(temp_dir, "cache"),
                bookmarks_file=os.path.join(temp_dir, "config", "bookmarks.json"),
            )

            # Directories shouldn't exist initially
            assert not Path(config.cache_directory).exists()
            assert not config.config_dir.exists()

            # Create directories
            config.ensure_directories()

            # Directories should exist now
            assert Path(config.cache_directory).exists()
            assert config.config_dir.exists()

    def test_to_dict(self):
        """Test config serialization to dictionary."""
        config = ModernGopherConfig(default_server="gopher://test.com", timeout=45, use_ssl=True)

        config_dict = config.to_dict()

        # Check structure
        assert "gopher" in config_dict
        assert "cache" in config_dict
        assert "browser" in config_dict
        assert "ui" in config_dict
        assert "logging" in config_dict

        # Check values
        assert config_dict["gopher"]["default_server"] == "gopher://test.com"
        assert config_dict["gopher"]["timeout"] == 45
        assert config_dict["gopher"]["use_ssl"] is True

    def test_from_dict(self):
        """Test config creation from dictionary."""
        config_dict = {
            "gopher": {"default_server": "gopher://test.com", "timeout": 45, "use_ssl": True},
            "cache": {"enabled": False, "max_size_mb": 50},
            "ui": {"color_scheme": "dark"},
        }

        config = ModernGopherConfig.from_dict(config_dict)

        assert config.default_server == "gopher://test.com"
        assert config.timeout == 45
        assert config.use_ssl is True
        assert config.cache_enabled is False
        assert config.cache_max_size_mb == 50
        assert config.color_scheme == "dark"

    def test_from_dict_with_missing_values(self):
        """Test config creation from incomplete dictionary uses defaults."""
        config_dict = {"gopher": {"timeout": 60}}

        config = ModernGopherConfig.from_dict(config_dict)

        # Should use provided value
        assert config.timeout == 60
        # Should use defaults for missing values
        assert config.default_server == DEFAULT_CONFIG["gopher"]["default_server"]
        assert config.cache_enabled == DEFAULT_CONFIG["cache"]["enabled"]

    def test_validation_success(self):
        """Test validation with valid config."""
        config = ModernGopherConfig()
        assert config.validate() is True

    def test_validation_failure(self):
        """Test validation with invalid config."""
        # Test invalid timeout
        config = ModernGopherConfig(timeout=-1)
        assert config.validate() is False

        # Test invalid cache size
        config = ModernGopherConfig(cache_max_size_mb=0)
        assert config.validate() is False

        # Test invalid log level
        config = ModernGopherConfig(log_level="INVALID")
        assert config.validate() is False

    def test_save_and_load(self):
        """Test saving and loading configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.yaml"

            # Create config with custom values
            original_config = ModernGopherConfig(
                default_server="gopher://test.com",
                timeout=45,
                cache_enabled=False,
                color_scheme="dark",
            )

            # Save config
            assert original_config.save(config_path) is True
            assert config_path.exists()

            # Load config
            loaded_config = ModernGopherConfig.load(config_path)

            # Compare values
            assert loaded_config.default_server == original_config.default_server
            assert loaded_config.timeout == original_config.timeout
            assert loaded_config.cache_enabled == original_config.cache_enabled
            assert loaded_config.color_scheme == original_config.color_scheme

    def test_load_nonexistent_file(self):
        """Test loading from non-existent file creates default config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "nonexistent.yaml"

            # Load should create default config and save it
            config = ModernGopherConfig.load(config_path)

            # Should have default values
            assert config.default_server == DEFAULT_CONFIG["gopher"]["default_server"]
            assert config.timeout == DEFAULT_CONFIG["gopher"]["timeout"]

            # File should be created
            assert config_path.exists()

    def test_load_invalid_yaml(self):
        """Test loading invalid YAML file returns default config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "invalid.yaml"

            # Write invalid YAML
            with open(config_path, "w") as f:
                f.write("invalid: yaml: content: [")

            # Should return default config
            config = ModernGopherConfig.load(config_path)
            assert config.default_server == DEFAULT_CONFIG["gopher"]["default_server"]

    def test_get_default_config_path(self):
        """Test default config path."""
        path = ModernGopherConfig.get_default_config_path()

        assert isinstance(path, Path)
        assert path.name == "config.yaml"
        assert "modern-gopher" in str(path)
        assert str(Path.home()) in str(path)

    def test_yaml_serialization_format(self):
        """Test that saved YAML is properly formatted."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "format_test.yaml"

            config = ModernGopherConfig()
            config.save(config_path)

            # Read and parse YAML
            with open(config_path, "r") as f:
                content = f.read()
                yaml_data = yaml.safe_load(content)

            # Check structure exists
            assert "gopher" in yaml_data
            assert "cache" in yaml_data
            assert "browser" in yaml_data
            assert "ui" in yaml_data
            assert "logging" in yaml_data

            # Check formatting (should be readable)
            assert "default_server:" in content
            assert "timeout:" in content


class TestGetConfig:
    """Test the get_config function."""

    def test_get_config_default_path(self):
        """Test getting config with default path."""
        config = get_config()

        assert isinstance(config, ModernGopherConfig)
        # Should have created directories
        assert config.config_dir.exists()
        if config.cache_enabled:
            assert Path(config.cache_directory).exists()

    def test_get_config_custom_path(self):
        """Test getting config with custom path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "custom_config.yaml"

            # Create a custom config file
            custom_config = ModernGopherConfig(timeout=99)
            custom_config.save(config_path)

            # Load with custom path
            config = get_config(config_path)

            assert config.timeout == 99

    def test_get_config_validation_and_directories(self):
        """Test that get_config validates and creates directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.yaml"

            # Create config with custom directories
            custom_config = ModernGopherConfig(
                cache_directory=os.path.join(temp_dir, "custom_cache"),
                bookmarks_file=os.path.join(temp_dir, "custom_config", "bookmarks.json"),
            )
            custom_config.save(config_path)

            # get_config should validate and create directories
            config = get_config(config_path)

            assert Path(config.cache_directory).exists()
            assert config.config_dir.exists()


class TestDefaultConfig:
    """Test the DEFAULT_CONFIG constant."""

    def test_default_config_structure(self):
        """Test that DEFAULT_CONFIG has expected structure."""
        assert "gopher" in DEFAULT_CONFIG
        assert "cache" in DEFAULT_CONFIG
        assert "browser" in DEFAULT_CONFIG
        assert "ui" in DEFAULT_CONFIG
        assert "keybindings" in DEFAULT_CONFIG
        assert "logging" in DEFAULT_CONFIG

    def test_default_config_values(self):
        """Test that DEFAULT_CONFIG has sensible values."""
        # Gopher defaults
        assert DEFAULT_CONFIG["gopher"]["default_server"].startswith("gopher://")
        assert DEFAULT_CONFIG["gopher"]["default_port"] == 70
        assert DEFAULT_CONFIG["gopher"]["timeout"] > 0

        # Cache defaults
        assert DEFAULT_CONFIG["cache"]["enabled"] is True
        assert DEFAULT_CONFIG["cache"]["max_size_mb"] > 0

        # Keybindings
        assert isinstance(DEFAULT_CONFIG["keybindings"]["quit"], list)
        assert "q" in DEFAULT_CONFIG["keybindings"]["quit"]
