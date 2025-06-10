"""
Gopher URL parsing and manipulation.

This module provides utilities for working with Gopher URLs, following both
RFC 1436 and common modern extensions to the format.
"""

import re
from typing import Optional, Tuple, Dict, Any
from urllib.parse import parse_qs, urlparse, unquote
import logging

from .protocol import DEFAULT_GOPHER_PORT
from .types import GopherItemType

logger = logging.getLogger(__name__)


class GopherURL:
    """
    Class representing a parsed Gopher URL.
    
    A Gopher URL typically follows the format:
    gopher://host[:port]/[item_type]selector
    
    Where:
    - item_type is a single character indicating the Gopher item type
    - selector is the path on the server
    """
    
    def __init__(self, host: str, selector: str = "", 
                port: int = DEFAULT_GOPHER_PORT,
                item_type: Optional[GopherItemType] = None,
                use_ssl: bool = False,
                query: str = ""):
        """
        Initialize a new GopherURL.
        
        Args:
            host: The hostname of the Gopher server
            selector: The selector string (path) on the server
            port: The port to connect to
            item_type: The type of the Gopher item
            use_ssl: Whether to use SSL/TLS for the connection
            query: Optional query string for search resources
        """
        self.host = host
        self.selector = selector
        self.port = port
        self.item_type = item_type
        self.use_ssl = use_ssl
        self.query = query
    
    def __str__(self) -> str:
        """
        Convert this GopherURL to its string representation.
        
        Returns:
            The URL as a string in standard Gopher URL format
        """
        scheme = "gophers" if self.use_ssl else "gopher"
        port_str = f":{self.port}" if self.port != DEFAULT_GOPHER_PORT else ""
        
        if self.item_type:
            type_char = self.item_type.value
        else:
            # Default to directory type if not specified
            type_char = GopherItemType.DIRECTORY.value
            
        url = f"{scheme}://{self.host}{port_str}/{type_char}{self.selector}"
        
        # Add query if present
        if self.query:
            url += f"?{self.query}"
            
        return url
    
    def to_tuple(self) -> Tuple[str, str, int, Optional[GopherItemType], bool, str]:
        """
        Convert this GopherURL to a tuple of its components.
        
        Returns:
            A tuple of (host, selector, port, item_type, use_ssl, query)
        """
        return (self.host, self.selector, self.port, 
                self.item_type, self.use_ssl, self.query)
    
    @classmethod
    def from_components(cls, host: str, selector: str = "", 
                       port: int = DEFAULT_GOPHER_PORT,
                       item_type: Optional[GopherItemType] = None,
                       use_ssl: bool = False,
                       query: str = "") -> 'GopherURL':
        """
        Create a GopherURL from its individual components.
        
        Args:
            host: The hostname of the Gopher server
            selector: The selector string (path) on the server
            port: The port to connect to
            item_type: The type of the Gopher item
            use_ssl: Whether to use SSL/TLS for the connection
            query: Optional query string for search resources
            
        Returns:
            A new GopherURL instance
        """
        return cls(host, selector, port, item_type, use_ssl, query)

    def join(self, selector: str) -> 'GopherURL':
        """
        Join this URL with a new selector to create a new URL.
        
        This is useful for navigating relative paths within the same server.
        
        Args:
            selector: The selector to join with
            
        Returns:
            A new GopherURL with the joined selector
        """
        if selector.startswith('/'):
            # Absolute path - replace the selector
            new_selector = selector[1:]  # Remove leading slash
        else:
            # Relative path - join with current selector
            current_dir = self.selector.rsplit('/', 1)[0] if '/' in self.selector else ''
            new_selector = f"{current_dir}/{selector}" if current_dir else selector
            
        return GopherURL(
            host=self.host,
            selector=new_selector,
            port=self.port,
            item_type=None,  # Reset item type for the new selector
            use_ssl=self.use_ssl,
            query=""  # Reset query for the new selector
        )
        

def parse_gopher_url(url: str) -> GopherURL:
    """
    Parse a Gopher URL string into a GopherURL object.
    
    The function handles both standard Gopher URLs (gopher://) and
    secure Gopher URLs (gophers://). It also extracts the item type
    from the selector if present.
    
    Args:
        url: The URL string to parse
        
    Returns:
        A GopherURL object representing the parsed URL
        
    Raises:
        ValueError: If the URL is not a valid Gopher URL
    """
    # Check if it's a Gopher URL
    if not url.startswith(('gopher://', 'gophers://')):
        raise ValueError(f"Not a Gopher URL: {url}")
    
    # Parse URL
    parsed = urlparse(url)
    
    # Determine if SSL is being used
    use_ssl = parsed.scheme == 'gophers'
    
    # Get host and port
    host = parsed.netloc
    port = DEFAULT_GOPHER_PORT
    
    if ':' in host:
        host, port_str = host.split(':', 1)
        try:
            port = int(port_str)
        except ValueError:
            logger.warning(f"Invalid port in URL, using default: {url}")
    
    # Parse path to get item type and selector
    path = parsed.path
    item_type = None
    selector = ''
    
    if path:
        # Remove leading slash
        if path.startswith('/'):
            path = path[1:]
            
        # First character is the item type
        if path:
            type_char = path[0]
            item_type = GopherItemType.from_char(type_char)
            selector = path[1:]  # Rest is selector
    
    # Handle query string
    query = parsed.query
    
    return GopherURL(
        host=host,
        selector=selector,
        port=port,
        item_type=item_type,
        use_ssl=use_ssl,
        query=query
    )


def is_gopher_url(url: str) -> bool:
    """
    Check if a string is a valid Gopher URL.
    
    Args:
        url: The string to check
        
    Returns:
        True if the string is a valid Gopher URL, False otherwise
    """
    try:
        # Simple check for scheme
        if not url.startswith(('gopher://', 'gophers://')):
            return False
            
        # Try parsing it
        parse_gopher_url(url)
        return True
    except (ValueError, AttributeError):
        return False


def build_gopher_url(host: str, selector: str = "", 
                    port: int = DEFAULT_GOPHER_PORT,
                    item_type: Optional[GopherItemType] = None,
                    use_ssl: bool = False,
                    query: str = "") -> str:
    """
    Build a Gopher URL string from its components.
    
    This is a convenience function that creates a GopherURL object
    and returns its string representation.
    
    Args:
        host: The hostname of the Gopher server
        selector: The selector string (path) on the server
        port: The port to connect to
        item_type: The type of the Gopher item
        use_ssl: Whether to use SSL/TLS for the connection
        query: Optional query string for search resources
        
    Returns:
        A string containing the Gopher URL
    """
    url = GopherURL(host, selector, port, item_type, use_ssl, query)
    return str(url)
