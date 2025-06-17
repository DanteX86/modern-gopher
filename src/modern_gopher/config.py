#!/usr/bin/env python3
"""
Configuration management for Modern Gopher.

This module handles loading and saving user preferences, default settings,
and application configuration.
"""

import os
import time
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

# Default configuration values
DEFAULT_CONFIG = {
    'gopher': {
        'default_server': 'gopher://gopher.floodgap.com',
        'default_port': 70,
        'timeout': 30,
        'use_ssl': False,
        'use_ipv6': None,  # None for auto-detect
    },
    'cache': {
        'enabled': True,
        'directory': '~/.cache/modern-gopher',
        'max_size_mb': 100,
        'expiration_hours': 24,
    },
    'browser': {
        'initial_url': None,  # Use default_server if None
        'bookmarks_file': '~/.config/modern-gopher/bookmarks.json',
        'history_file': '~/.config/modern-gopher/history.json',
        'max_history_items': 1000,
        'save_session': True,
    },
    'session': {
        'enabled': True,
        'auto_restore': True,
        'session_file': '~/.config/modern-gopher/session.json',
        'backup_sessions': True,
        'max_sessions': 10,
    },
    'ui': {
        'show_icons': True,
        'status_bar_help': True,
        'mouse_support': True,
        'color_scheme': 'default',
    },
    'keybindings': {
        'quit': ['q', 'ctrl+c'],
        'help': ['h', 'f1'],
        'refresh': ['r', 'f5'],
        'go_back': ['backspace', 'alt+left'],
        'go_forward': ['alt+right'],
        'go_to_url': ['g', 'ctrl+l'],
        'bookmark_toggle': ['b', 'ctrl+b'],
        'bookmark_list': ['m'],
        'history_show': ['ctrl+h'],
        'search_directory': ['/', 'ctrl+f'],
        'home': ['home'],
    },
    'logging': {
        'level': 'INFO',
        'file': None,  # None for no file logging
        'console': True,
    }
}


@dataclass
class ModernGopherConfig:
    """Main configuration class for Modern Gopher."""
    
    # Gopher settings
    default_server: str = 'gopher://gopher.floodgap.com'
    default_port: int = 70
    timeout: int = 30
    use_ssl: bool = False
    use_ipv6: Optional[bool] = None
    
    # Cache settings
    cache_enabled: bool = True
    cache_directory: str = '~/.cache/modern-gopher'
    cache_max_size_mb: int = 100
    cache_expiration_hours: int = 24
    
    # Browser settings
    initial_url: Optional[str] = None
    bookmarks_file: str = '~/.config/modern-gopher/bookmarks.json'
    history_file: str = '~/.config/modern-gopher/history.json'
    max_history_items: int = 1000
    save_session: bool = True
    
    # Session settings
    session_enabled: bool = True
    session_auto_restore: bool = True
    session_file: str = '~/.config/modern-gopher/session.json'
    session_backup_sessions: bool = True
    session_max_sessions: int = 10
    
    # UI settings
    show_icons: bool = True
    status_bar_help: bool = True
    mouse_support: bool = True
    color_scheme: str = 'default'
    
    # Logging settings
    log_level: str = 'INFO'
    log_file: Optional[str] = None
    log_console: bool = True
    
    def __post_init__(self):
        """Expand user paths after initialization."""
        self.cache_directory = os.path.expanduser(self.cache_directory)
        self.bookmarks_file = os.path.expanduser(self.bookmarks_file)
        self.history_file = os.path.expanduser(self.history_file)
        self.session_file = os.path.expanduser(self.session_file)
        if self.log_file:
            self.log_file = os.path.expanduser(self.log_file)
    
    @property
    def effective_initial_url(self) -> str:
        """Get the effective initial URL (falls back to default_server)."""
        return self.initial_url or self.default_server
    
    @property
    def config_dir(self) -> Path:
        """Get the configuration directory path."""
        return Path(self.bookmarks_file).parent
    
    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        directories = [
            Path(self.cache_directory),
            self.config_dir,
        ]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Ensured directory exists: {directory}")
            except OSError as e:
                logger.warning(f"Failed to create directory {directory}: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for serialization."""
        config_dict = {
            'gopher': {
                'default_server': self.default_server,
                'default_port': self.default_port,
                'timeout': self.timeout,
                'use_ssl': self.use_ssl,
                'use_ipv6': self.use_ipv6,
            },
            'cache': {
                'enabled': self.cache_enabled,
                'directory': self.cache_directory,
                'max_size_mb': self.cache_max_size_mb,
                'expiration_hours': self.cache_expiration_hours,
            },
            'browser': {
                'initial_url': self.initial_url,
                'bookmarks_file': self.bookmarks_file,
                'history_file': self.history_file,
                'max_history_items': self.max_history_items,
                'save_session': self.save_session,
            },
            'session': {
                'enabled': self.session_enabled,
                'auto_restore': self.session_auto_restore,
                'session_file': self.session_file,
                'backup_sessions': self.session_backup_sessions,
                'max_sessions': self.session_max_sessions,
            },
            'ui': {
                'show_icons': self.show_icons,
                'status_bar_help': self.status_bar_help,
                'mouse_support': self.mouse_support,
                'color_scheme': self.color_scheme,
            },
            'logging': {
                'level': self.log_level,
                'file': self.log_file,
                'console': self.log_console,
            }
        }
        return config_dict
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ModernGopherConfig':
        """Create config from dictionary."""
        # Flatten nested dictionary to match dataclass fields
        gopher = config_dict.get('gopher', {})
        cache = config_dict.get('cache', {})
        browser = config_dict.get('browser', {})
        session = config_dict.get('session', {})
        ui = config_dict.get('ui', {})
        logging_config = config_dict.get('logging', {})
        
        return cls(
            # Gopher settings
            default_server=gopher.get('default_server', DEFAULT_CONFIG['gopher']['default_server']),
            default_port=gopher.get('default_port', DEFAULT_CONFIG['gopher']['default_port']),
            timeout=gopher.get('timeout', DEFAULT_CONFIG['gopher']['timeout']),
            use_ssl=gopher.get('use_ssl', DEFAULT_CONFIG['gopher']['use_ssl']),
            use_ipv6=gopher.get('use_ipv6', DEFAULT_CONFIG['gopher']['use_ipv6']),
            
            # Cache settings
            cache_enabled=cache.get('enabled', DEFAULT_CONFIG['cache']['enabled']),
            cache_directory=cache.get('directory', DEFAULT_CONFIG['cache']['directory']),
            cache_max_size_mb=cache.get('max_size_mb', DEFAULT_CONFIG['cache']['max_size_mb']),
            cache_expiration_hours=cache.get('expiration_hours', DEFAULT_CONFIG['cache']['expiration_hours']),
            
            # Browser settings
            initial_url=browser.get('initial_url', DEFAULT_CONFIG['browser']['initial_url']),
            bookmarks_file=browser.get('bookmarks_file', DEFAULT_CONFIG['browser']['bookmarks_file']),
            history_file=browser.get('history_file', DEFAULT_CONFIG['browser']['history_file']),
            max_history_items=browser.get('max_history_items', DEFAULT_CONFIG['browser']['max_history_items']),
            save_session=browser.get('save_session', DEFAULT_CONFIG['browser']['save_session']),
            
            # Session settings
            session_enabled=session.get('enabled', DEFAULT_CONFIG['session']['enabled']),
            session_auto_restore=session.get('auto_restore', DEFAULT_CONFIG['session']['auto_restore']),
            session_file=session.get('session_file', DEFAULT_CONFIG['session']['session_file']),
            session_backup_sessions=session.get('backup_sessions', DEFAULT_CONFIG['session']['backup_sessions']),
            session_max_sessions=session.get('max_sessions', DEFAULT_CONFIG['session']['max_sessions']),
            
            # UI settings
            show_icons=ui.get('show_icons', DEFAULT_CONFIG['ui']['show_icons']),
            status_bar_help=ui.get('status_bar_help', DEFAULT_CONFIG['ui']['status_bar_help']),
            mouse_support=ui.get('mouse_support', DEFAULT_CONFIG['ui']['mouse_support']),
            color_scheme=ui.get('color_scheme', DEFAULT_CONFIG['ui']['color_scheme']),
            
            # Logging settings
            log_level=logging_config.get('level', DEFAULT_CONFIG['logging']['level']),
            log_file=logging_config.get('file', DEFAULT_CONFIG['logging']['file']),
            log_console=logging_config.get('console', DEFAULT_CONFIG['logging']['console']),
        )
    
    def save(self, config_path: Optional[Union[str, Path]] = None) -> bool:
        """Save configuration to file."""
        if config_path is None:
            config_path = self.get_default_config_path()
        
        config_path = Path(config_path)
        
        try:
            # Ensure directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save as YAML
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.to_dict(), f, default_flow_style=False, indent=2)
            
            logger.info(f"Configuration saved to {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration to {config_path}: {e}")
            return False
    
    @classmethod
    def load(cls, config_path: Optional[Union[str, Path]] = None) -> 'ModernGopherConfig':
        """Load configuration from file."""
        if config_path is None:
            config_path = cls.get_default_config_path()
        
        config_path = Path(config_path)
        
        if not config_path.exists():
            logger.info(f"Config file not found at {config_path}, using defaults")
            config = cls()
            # Save default config for future reference
            config.save(config_path)
            return config
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_dict = yaml.safe_load(f) or {}
            
            logger.info(f"Configuration loaded from {config_path}")
            return cls.from_dict(config_dict)
            
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
            logger.info("Using default configuration")
            return cls()
    
    @staticmethod
    def get_default_config_path() -> Path:
        """Get the default configuration file path."""
        config_dir = Path.home() / '.config' / 'modern-gopher'
        return config_dir / 'config.yaml'
    
    def validate(self) -> bool:
        """Validate configuration values."""
        issues = []
        
        # Validate timeout
        if self.timeout <= 0:
            issues.append("Timeout must be positive")
        
        # Validate cache size
        if self.cache_max_size_mb <= 0:
            issues.append("Cache max size must be positive")
        
        # Validate expiration
        if self.cache_expiration_hours <= 0:
            issues.append("Cache expiration must be positive")
        
        # Validate max history items
        if self.max_history_items <= 0:
            issues.append("Max history items must be positive")
        
        # Validate log level
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level.upper() not in valid_levels:
            issues.append(f"Log level must be one of: {', '.join(valid_levels)}")
        
        if issues:
            for issue in issues:
                logger.warning(f"Configuration validation issue: {issue}")
            return False
        
        return True

    def validate_setting(self, key_path: str, value: Any) -> Tuple[bool, str]:
        """Validate a single configuration setting.
        
        Args:
            key_path: Dot-separated path like 'gopher.timeout'
            value: The value to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            parts = key_path.split('.')
            if len(parts) != 2:
                return False, "Invalid key path format. Use 'section.key'"
            
            section, key = parts
            
            # Check if section and key exist
            if section not in DEFAULT_CONFIG:
                return False, f"Unknown section: {section}"
            
            if key not in DEFAULT_CONFIG[section]:
                return False, f"Unknown key '{key}' in section '{section}'"
            
            # Type validation
            default_value = DEFAULT_CONFIG[section][key]
            if default_value is not None:
                expected_type = type(default_value)
                
                if expected_type == bool:
                    if isinstance(value, str):
                        if value.lower() not in ('true', 'false', '1', '0', 'yes', 'no', 'on', 'off'):
                            return False, f"Boolean value expected, got '{value}'"
                    elif not isinstance(value, bool):
                        try:
                            bool(value)
                        except:
                            return False, f"Cannot convert '{value}' to boolean"
                
                elif expected_type in (int, float):
                    try:
                        expected_type(value)
                    except (ValueError, TypeError):
                        return False, f"Numeric value expected, got '{value}'"
            
            # Value-specific validation
            if key_path == 'gopher.timeout' and int(value) <= 0:
                return False, "Timeout must be positive"
            
            if key_path == 'gopher.default_port' and not (1 <= int(value) <= 65535):
                return False, "Port must be between 1 and 65535"
            
            if key_path == 'cache.max_size_mb' and int(value) <= 0:
                return False, "Cache size must be positive"
            
            if key_path == 'cache.expiration_hours' and int(value) <= 0:
                return False, "Cache expiration must be positive"
            
            if key_path == 'browser.max_history_items' and int(value) <= 0:
                return False, "Max history items must be positive"
            
            if key_path == 'logging.level':
                valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
                if str(value).upper() not in valid_levels:
                    return False, f"Log level must be one of: {', '.join(valid_levels)}"
            
            if key_path == 'ui.color_scheme':
                valid_schemes = ['default', 'dark', 'light', 'monochrome']
                if str(value) not in valid_schemes:
                    return False, f"Color scheme must be one of: {', '.join(valid_schemes)}"
            
            return True, ""
            
        except Exception as e:
            return False, f"Validation error: {e}"

    def set_value(self, key_path: str, value: Any) -> bool:
        """Set a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path like 'gopher.timeout' or 'cache.enabled'
            value: The value to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            parts = key_path.split('.')
            if len(parts) != 2:
                logger.error(f"Invalid key path: {key_path}. Use format 'section.key'")
                return False
            
            section, key = parts
            
            # Validate section exists
            if section not in DEFAULT_CONFIG:
                logger.error(f"Unknown section: {section}")
                return False
            
            # Validate key exists in section
            if key not in DEFAULT_CONFIG[section]:
                logger.error(f"Unknown key '{key}' in section '{section}'")
                return False
            
            # Type conversion based on default type
            default_value = DEFAULT_CONFIG[section][key]
            if default_value is not None:
                try:
                    if isinstance(default_value, bool):
                        # Handle boolean conversion
                        if isinstance(value, str):
                            value = value.lower() in ('true', '1', 'yes', 'on')
                        else:
                            value = bool(value)
                    elif isinstance(default_value, int):
                        value = int(value)
                    elif isinstance(default_value, float):
                        value = float(value)
                    elif isinstance(default_value, str):
                        value = str(value)
                except (ValueError, TypeError) as e:
                    logger.error(f"Cannot convert '{value}' to {type(default_value).__name__}: {e}")
                    return False
            
            # Validate the setting first
            is_valid, error_msg = self.validate_setting(key_path, value)
            if not is_valid:
                logger.error(f"Validation failed for {key_path}: {error_msg}")
                return False
            
            # Set the value using attribute mapping
            try:
                if section == 'gopher':
                    if key == 'default_server':
                        self.default_server = value
                    elif key == 'default_port':
                        self.default_port = value
                    elif key == 'timeout':
                        self.timeout = value
                    elif key == 'use_ssl':
                        self.use_ssl = value
                    elif key == 'use_ipv6':
                        self.use_ipv6 = value
                    else:
                        logger.error(f"Unknown gopher key: {key}")
                        return False
                elif section == 'cache':
                    if key == 'enabled':
                        self.cache_enabled = value
                    elif key == 'directory':
                        self.cache_directory = os.path.expanduser(str(value))
                    elif key == 'max_size_mb':
                        self.cache_max_size_mb = value
                    elif key == 'expiration_hours':
                        self.cache_expiration_hours = value
                    else:
                        logger.error(f"Unknown cache key: {key}")
                        return False
                elif section == 'browser':
                    if key == 'initial_url':
                        self.initial_url = value
                    elif key == 'bookmarks_file':
                        self.bookmarks_file = os.path.expanduser(str(value))
                    elif key == 'history_file':
                        self.history_file = os.path.expanduser(str(value))
                    elif key == 'max_history_items':
                        self.max_history_items = value
                    elif key == 'save_session':
                        self.save_session = value
                    else:
                        logger.error(f"Unknown browser key: {key}")
                        return False
                elif section == 'session':
                    if key == 'enabled':
                        self.session_enabled = value
                    elif key == 'auto_restore':
                        self.session_auto_restore = value
                    elif key == 'session_file':
                        self.session_file = os.path.expanduser(str(value))
                    elif key == 'backup_sessions':
                        self.session_backup_sessions = value
                    elif key == 'max_sessions':
                        self.session_max_sessions = value
                    else:
                        logger.error(f"Unknown session key: {key}")
                        return False
                elif section == 'ui':
                    if key == 'show_icons':
                        self.show_icons = value
                    elif key == 'status_bar_help':
                        self.status_bar_help = value
                    elif key == 'mouse_support':
                        self.mouse_support = value
                    elif key == 'color_scheme':
                        self.color_scheme = value
                    else:
                        logger.error(f"Unknown ui key: {key}")
                        return False
                elif section == 'logging':
                    if key == 'level':
                        self.log_level = value
                    elif key == 'file':
                        self.log_file = value
                    elif key == 'console':
                        self.log_console = value
                    else:
                        logger.error(f"Unknown logging key: {key}")
                        return False
                else:
                    logger.error(f"Unknown section: {section}")
                    return False
                
                return True
                
            except Exception as e:
                logger.error(f"Error setting {key_path}: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to set {key_path}: {e}")
            return False
    
    def get_value(self, key_path: str) -> Any:
        """Get a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path like 'gopher.timeout' or 'cache.enabled'
            
        Returns:
            The configuration value or None if not found
        """
        try:
            parts = key_path.split('.')
            if len(parts) != 2:
                return None
            
            section, key = parts
            config_dict = self.to_dict()
            
            if section in config_dict and key in config_dict[section]:
                return config_dict[section][key]
            
            return None
            
        except Exception:
            return None
    
    def list_all_settings(self) -> Dict[str, Dict[str, Any]]:
        """Get all configuration settings organized by section.
        
        Returns:
            Dictionary with sections as keys and settings as values
        """
        return self.to_dict()
    
    def reset_section(self, section: str) -> bool:
        """Reset a configuration section to defaults.
        
        Args:
            section: The section name to reset
            
        Returns:
            True if successful, False otherwise
        """
        if section not in DEFAULT_CONFIG:
            logger.error(f"Unknown section: {section}")
            return False
        
        try:
            defaults = DEFAULT_CONFIG[section]
            for key, value in defaults.items():
                self.set_value(f"{section}.{key}", value)
            
            logger.info(f"Section '{section}' reset to defaults")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset section {section}: {e}")
            return False
    
    def backup_config(self, backup_path: Optional[Union[str, Path]] = None) -> bool:
        """Create a backup of the current configuration.
        
        Args:
            backup_path: Optional path for backup file
            
        Returns:
            True if successful, False otherwise
        """
        if backup_path is None:
            config_dir = self.get_default_config_path().parent
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_path = config_dir / f"config_backup_{timestamp}.yaml"
        
        backup_path = Path(backup_path)
        
        try:
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.to_dict(), f, default_flow_style=False, indent=2)
            
            logger.info(f"Configuration backed up to {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to backup configuration: {e}")
            return False


def get_config(config_path: Optional[Union[str, Path]] = None) -> ModernGopherConfig:
    """Get the global configuration instance."""
    config = ModernGopherConfig.load(config_path)
    config.validate()
    config.ensure_directories()
    return config

