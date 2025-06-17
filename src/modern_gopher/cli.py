#!/usr/bin/env python3
"""
Command-line interface for modern-gopher.

This module provides the main entry point for the modern-gopher package,
allowing users to interact with Gopher resources through the command line.
"""

import argparse
import os
import sys
import logging
from typing import Optional, List, Dict, Any, Union
from pathlib import Path

try:
    import rich
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.table import Table
    from rich.text import Text
    from rich.panel import Panel
    from rich.markdown import Markdown
except ImportError:
    print("Error: The 'rich' package is required. Please install it with 'pip install rich'.")
    sys.exit(1)

from modern_gopher.core.client import GopherClient
from modern_gopher.core.types import GopherItem, GopherItemType
from modern_gopher.core.url import parse_gopher_url, GopherURL
from modern_gopher.core.protocol import GopherProtocolError, DEFAULT_GOPHER_PORT
from modern_gopher.config import get_config, ModernGopherConfig

# Will be implemented later
from modern_gopher.browser.terminal import launch_browser

# Initialize rich console
console = Console()

# Configure logging with rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, console=console)]
)
logger = logging.getLogger("modern_gopher")


def setup_common_args(parser: argparse.ArgumentParser) -> None:
    """
    Add common arguments to the parser.
    
    Args:
        parser: The argument parser to add arguments to
    """
    parser.add_argument(
        "--timeout", 
        type=int, 
        default=30,
        help="Socket timeout in seconds (default: 30)"
    )
    
    # IPv4/IPv6 group
    ip_group = parser.add_mutually_exclusive_group()
    ip_group.add_argument(
        "--ipv4", 
        action="store_true",
        help="Force IPv4 usage"
    )
    ip_group.add_argument(
        "--ipv6", 
        action="store_true",
        help="Force IPv6 usage"
    )
    
    # SSL/TLS options
    parser.add_argument(
        "--ssl", 
        action="store_true",
        help="Use SSL/TLS for the connection"
    )
    
    # Verbose option
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true",
        help="Enable verbose output"
    )


def display_gopher_items(items: List[GopherItem]) -> None:
    """
    Display a list of Gopher items in a formatted table.
    
    Args:
        items: The list of GopherItem objects to display
    """
    if not items:
        console.print(Panel("No items found", title="Empty Directory"))
        return
    
    table = Table(title="Gopher Directory")
    table.add_column("Type", style="cyan")
    table.add_column("Display", style="green")
    table.add_column("Selector", style="blue")
    table.add_column("Host", style="magenta")
    table.add_column("Port", style="yellow")
    
    for item in items:
        table.add_row(
            item.item_type.display_name,
            item.display_string,
            item.selector,
            item.host,
            str(item.port)
        )
    
    console.print(table)


def cmd_config(args: argparse.Namespace) -> int:
    """
    Manage configuration settings.
    
    Args:
        args: Command line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        config_path = args.config_file if hasattr(args, 'config_file') else None
        config = get_config(config_path)
        
        if args.config_action == 'show':
            # Display current configuration
            table = Table(title="Modern Gopher Configuration")
            table.add_column("Section", style="cyan")
            table.add_column("Setting", style="blue")
            table.add_column("Value", style="green")
            
            config_dict = config.to_dict()
            for section, settings in config_dict.items():
                if isinstance(settings, dict):
                    for key, value in settings.items():
                        table.add_row(section, key, str(value))
                else:
                    table.add_row("", section, str(settings))
            
            console.print(table)
            console.print(f"\nConfiguration file: {config.get_default_config_path()}")
            
        elif args.config_action == 'get':
            # Get specific configuration value
            if not hasattr(args, 'key') or not args.key:
                console.print("Error: key required for get command", style="red")
                return 1
            
            value = config.get_value(args.key)
            if value is not None:
                console.print(f"{args.key}: [green]{value}[/green]")
            else:
                console.print(f"Key '{args.key}' not found", style="red")
                return 1
        
        elif args.config_action == 'set':
            # Set configuration value
            if not hasattr(args, 'key') or not args.key:
                console.print("Error: key required for set command", style="red")
                return 1
            if not hasattr(args, 'value') or args.value is None:
                console.print("Error: value required for set command", style="red")
                return 1
            
            # Validate the setting first
            is_valid, error_msg = config.validate_setting(args.key, args.value)
            if not is_valid:
                console.print(f"Validation error: {error_msg}", style="red")
                return 1
            
            # Set the value
            if config.set_value(args.key, args.value):
                # Save the configuration
                config_save_path = config_path or config.get_default_config_path()
                if config.save(config_save_path):
                    console.print(f"Set {args.key} = [green]{args.value}[/green]")
                    console.print(f"Configuration saved to {config_save_path}", style="dim")
                else:
                    console.print("Failed to save configuration", style="red")
                    return 1
            else:
                console.print(f"Failed to set {args.key}", style="red")
                return 1
        
        elif args.config_action == 'list':
            # List all available configuration keys
            from modern_gopher.config import DEFAULT_CONFIG
            
            table = Table(title="Available Configuration Keys")
            table.add_column("Key", style="cyan")
            table.add_column("Type", style="blue")
            table.add_column("Current Value", style="green")
            table.add_column("Default", style="yellow")
            
            config_dict = config.to_dict()
            
            for section, settings in DEFAULT_CONFIG.items():
                for key, default_value in settings.items():
                    key_path = f"{section}.{key}"
                    current_value = config_dict.get(section, {}).get(key, "N/A")
                    value_type = type(default_value).__name__ if default_value is not None else "None"
                    
                    table.add_row(
                        key_path,
                        value_type,
                        str(current_value),
                        str(default_value)
                    )
            
            console.print(table)
            console.print("\n[dim]Use 'modern-gopher config set <key> <value>' to change values[/dim]")
            
        elif args.config_action == 'reset':
            # Reset to defaults or specific section
            if hasattr(args, 'section') and args.section:
                # Reset specific section
                if config.reset_section(args.section):
                    config_save_path = config_path or config.get_default_config_path()
                    if config.save(config_save_path):
                        console.print(f"Section '{args.section}' reset to defaults", style="green")
                    else:
                        console.print("Failed to save configuration", style="red")
                        return 1
                else:
                    console.print(f"Failed to reset section '{args.section}'", style="red")
                    return 1
            else:
                # Reset entire configuration
                config_save_path = config_path or config.get_default_config_path()
                default_config = ModernGopherConfig()
                if default_config.save(config_save_path):
                    console.print(f"Configuration reset to defaults: {config_save_path}", style="green")
                else:
                    console.print("Failed to reset configuration", style="red")
                    return 1
        
        elif args.config_action == 'backup':
            # Create configuration backup
            backup_path = getattr(args, 'backup_path', None)
            if config.backup_config(backup_path):
                console.print("Configuration backup created successfully", style="green")
            else:
                console.print("Failed to create configuration backup", style="red")
                return 1
                
        elif args.config_action == 'path':
            # Show config file path
            config_path = config.get_default_config_path()
            console.print(f"Configuration file: {config_path}")
            if config_path.exists():
                console.print("✅ File exists", style="green")
            else:
                console.print("❌ File does not exist (will be created on first save)", style="yellow")
        
        return 0
    
    except Exception as e:
        console.print(f"Configuration error: {e}", style="bold red")
        if hasattr(args, 'verbose') and args.verbose:
            console.print_exception()
        return 1


def cmd_browse(args: argparse.Namespace) -> int:
    """
    Launch the interactive Gopher browser.
    
    Args:
        args: Command line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Load configuration
        config = get_config(args.config_file if hasattr(args, 'config_file') else None)
        
        # Use URL from args or config default
        url = args.url if hasattr(args, 'url') and args.url else config.effective_initial_url
        
        # Set log level based on verbosity
        if args.verbose:
            logger.setLevel(logging.DEBUG)
        
        # Determine IPv4/IPv6 preference (args override config)
        use_ipv6 = config.use_ipv6
        if args.ipv4:
            use_ipv6 = False
        elif args.ipv6:
            use_ipv6 = True
        
        # Determine timeout (args override config)
        timeout = getattr(args, 'timeout', None) or config.timeout
        
        # Determine SSL usage (args override config)
        use_ssl = getattr(args, 'ssl', None) or config.use_ssl
        
        # Use cache directory from config
        cache_dir = config.cache_directory if config.cache_enabled else None
        
        # Show startup message
        console.print(Panel.fit(
            "Launching Modern Gopher Browser", 
            title="Modern Gopher", 
            subtitle=f"Initial URL: {url}"
        ))
        
        # Launch the browser interface
        return launch_browser(
            url=url,
            timeout=timeout,
            use_ssl=use_ssl,
            use_ipv6=use_ipv6,
            cache_dir=cache_dir
        )
    
    except Exception as e:
        if args.verbose:
            console.print_exception()
        else:
            console.print(f"Error: {e}", style="bold red")
        return 1


def cmd_get(args: argparse.Namespace) -> int:
    """
    Fetch a Gopher resource and display or save it.
    
    Args:
        args: Command line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        url = args.url
        
        # Set log level based on verbosity
        if args.verbose:
            logger.setLevel(logging.DEBUG)
        
        # Parse IPv4/IPv6 preference
        use_ipv6 = None
        if args.ipv4:
            use_ipv6 = False
        elif args.ipv6:
            use_ipv6 = True
        
        # Create client
        client = GopherClient(
            timeout=args.timeout,
            use_ipv6=use_ipv6
        )
        
        # Parse URL
        gopher_url = parse_gopher_url(url)
        if args.ssl and not gopher_url.use_ssl:
            gopher_url.use_ssl = True
        
        with console.status(f"Fetching {url}..."):
            if args.output:
                # Save to file
                output_path = os.path.expanduser(args.output)
                
                # Create directory if it doesn't exist
                output_dir = os.path.dirname(output_path)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                bytes_written = client.get_resource(gopher_url, file_path=output_path)
                console.print(f"Saved {bytes_written} bytes to [bold]{args.output}[/bold]")
            else:
                # Display in console
                resource = client.get_resource(gopher_url)
                
                if isinstance(resource, list):
                    # Directory listing
                    display_gopher_items(resource)
                elif isinstance(resource, str):
                    # Text file
                    if args.markdown:
                        try:
                            # Try to render as markdown if requested
                            md = Markdown(resource)
                            console.print(md)
                        except Exception:
                            # Fall back to plain text if rendering fails
                            console.print(Text(resource))
                    else:
                        console.print(Text(resource))
                else:
                    # Binary content
                    console.print(f"Binary content ({len(resource)} bytes). "
                                f"Use --output to save to file.")
        
        return 0
    
    except GopherProtocolError as e:
        console.print(f"Protocol Error: {e}", style="bold red")
        if args.verbose:
            console.print_exception()
        return 1
    
    except Exception as e:
        if args.verbose:
            console.print_exception()
        else:
            console.print(f"Error: {e}", style="bold red")
        return 1


def cmd_info(args: argparse.Namespace) -> int:
    """
    Display information about a Gopher URL.
    
    Args:
        args: Command line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        url = args.url
        
        # Set log level based on verbosity
        if args.verbose:
            logger.setLevel(logging.DEBUG)
        
        # Parse URL
        gopher_url = parse_gopher_url(url)
        
        # Create table with URL information
        table = Table(title=f"Gopher URL: {url}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Host", gopher_url.host)
        table.add_row("Port", str(gopher_url.port))
        table.add_row("Selector", gopher_url.selector)
        
        if gopher_url.item_type:
            table.add_row("Item Type", f"{gopher_url.item_type.display_name} ({gopher_url.item_type.value})")
        else:
            table.add_row("Item Type", "Not specified (defaults to Directory)")
        
        table.add_row("Use SSL", "Yes" if gopher_url.use_ssl else "No")
        
        if gopher_url.query:
            table.add_row("Query", gopher_url.query)
        
        console.print(table)
        return 0
    
    except Exception as e:
        if args.verbose:
            console.print_exception()
        else:
            console.print(f"Error: {e}", style="bold red")
        return 1


def parse_args(args: List[str] = None) -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Args:
        args: Command line arguments (defaults to sys.argv[1:])
        
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        prog="modern-gopher",
        description="Modern tools for interacting with the Gopher protocol"
    )
    
    # Add version option
    parser.add_argument(
        "--version", 
        action="version",
        version="%(prog)s 0.1.0"
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(
        dest="command",
        help="Command to execute",
        required=True
    )
    
    # Browse command
    browse_parser = subparsers.add_parser(
        "browse",
        help="Launch the interactive browser"
    )
    browse_parser.add_argument(
        "url", 
        help="The Gopher URL to browse"
    )
    setup_common_args(browse_parser)
    browse_parser.set_defaults(func=cmd_browse)
    
    # Get command
    get_parser = subparsers.add_parser(
        "get",
        help="Fetch a Gopher resource"
    )
    get_parser.add_argument(
        "url", 
        help="The Gopher URL to fetch"
    )
    get_parser.add_argument(
        "-o", "--output", 
        help="Save resource to specified file"
    )
    get_parser.add_argument(
        "--markdown", 
        action="store_true",
        help="Render text content as Markdown"
    )
    setup_common_args(get_parser)
    get_parser.set_defaults(func=cmd_get)
    
    # Info command
    info_parser = subparsers.add_parser(
        "info",
        help="Display information about a Gopher URL"
    )
    info_parser.add_argument(
        "url", 
        help="The Gopher URL to display information about"
    )
    info_parser.add_argument(
        "-v", "--verbose", 
        action="store_true",
        help="Enable verbose output"
    )
    info_parser.set_defaults(func=cmd_info)
    
    # Config command with subcommands
    config_parser = subparsers.add_parser(
        "config",
        help="Manage configuration settings"
    )
    
    # Config subcommands
    config_subparsers = config_parser.add_subparsers(
        dest="config_action",
        help="Configuration action to perform",
        required=True
    )
    
    # Show command
    show_parser = config_subparsers.add_parser(
        "show",
        help="Display current configuration"
    )
    
    # Get command
    get_parser = config_subparsers.add_parser(
        "get",
        help="Get a configuration value"
    )
    get_parser.add_argument(
        "key",
        help="Configuration key in format 'section.key' (e.g., 'gopher.timeout')"
    )
    
    # Set command
    set_parser = config_subparsers.add_parser(
        "set",
        help="Set a configuration value"
    )
    set_parser.add_argument(
        "key",
        help="Configuration key in format 'section.key' (e.g., 'gopher.timeout')"
    )
    set_parser.add_argument(
        "value",
        help="Value to set"
    )
    
    # List command
    list_parser = config_subparsers.add_parser(
        "list",
        help="List all available configuration keys"
    )
    
    # Reset command
    reset_parser = config_subparsers.add_parser(
        "reset",
        help="Reset configuration to defaults"
    )
    reset_parser.add_argument(
        "section",
        nargs="?",
        help="Optional section to reset (resets entire config if not specified)"
    )
    
    # Backup command
    backup_parser = config_subparsers.add_parser(
        "backup",
        help="Create a configuration backup"
    )
    backup_parser.add_argument(
        "backup_path",
        nargs="?",
        help="Optional backup file path (auto-generated if not specified)"
    )
    
    # Path command
    path_parser = config_subparsers.add_parser(
        "path",
        help="Show configuration file path"
    )
    
    # Common config arguments
    for subparser in [show_parser, get_parser, set_parser, list_parser, 
                     reset_parser, backup_parser, path_parser]:
        subparser.add_argument(
            "--config-file",
            help="Path to configuration file (defaults to ~/.config/modern-gopher/config.yaml)"
        )
        subparser.add_argument(
            "-v", "--verbose", 
            action="store_true",
            help="Enable verbose output"
        )
    
    config_parser.set_defaults(func=cmd_config)
    
    return parser.parse_args(args)


def main() -> int:
    """
    Main entry point for the modern-gopher command-line interface.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        args = parse_args()
        return args.func(args)
    except KeyboardInterrupt:
        console.print("\nOperation cancelled by user", style="bold yellow")
        return 130
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        console.print_exception()
        return 1


if __name__ == "__main__":
    sys.exit(main())

