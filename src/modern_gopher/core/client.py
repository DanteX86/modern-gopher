"""
Main client interface for Gopher connections.

This module provides a high-level client interface for interacting with Gopher
servers, building upon the low-level protocol implementation.
"""

import hashlib
import json
import logging
import os
import tempfile
from datetime import datetime
from datetime import timedelta
from io import BytesIO
from typing import Any
from typing import BinaryIO
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from .protocol import DEFAULT_GOPHER_PORT
from .protocol import request_gopher_resource
from .protocol import save_gopher_resource
from .types import GopherItem
from .types import GopherItemType
from .types import parse_gopher_directory
from .url import GopherURL
from .url import parse_gopher_url

logger = logging.getLogger(__name__)


class CacheEntry:
    """Represents a cached Gopher resource."""

    def __init__(self, content: Any, expires: Optional[datetime] = None):
        """
        Initialize a new cache entry.

        Args:
            content: The cached content
            expires: When the entry expires (None for no expiration)
        """
        self.content = content
        self.expires = expires
        self.created = datetime.now()
        self.last_accessed = self.created

    def is_expired(self) -> bool:
        """
        Check if this entry is expired.

        Returns:
            True if expired, False otherwise
        """
        if self.expires is None:
            return False
        return datetime.now() > self.expires


class GopherClient:
    """
    High-level client for interacting with Gopher servers.

    This class provides methods for fetching various types of Gopher resources
    and handling the different item types.
    """

    def __init__(self, timeout: int = 30, cache_dir: Optional[str] = None,
                 use_ipv6: Optional[bool] = None, cache_ttl: int = 3600):
        """
        Initialize a new GopherClient.

        Args:
            timeout: Socket timeout in seconds
            cache_dir: Directory to cache downloaded resources (None for no caching)
            use_ipv6: Preference for IPv6 usage (None for auto-detect)
            cache_ttl: Time-to-live for cached items in seconds (default: 1 hour)
        """
        self.timeout = timeout
        self.use_ipv6 = use_ipv6
        self.cache_ttl = cache_ttl

        # Initialize cache
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.cache_dir = os.path.expanduser(cache_dir) if cache_dir else None

        # Create cache directory if it doesn't exist
        if self.cache_dir and not os.path.exists(self.cache_dir):
            try:
                os.makedirs(self.cache_dir)
                logger.debug(f"Created cache directory: {self.cache_dir}")
            except OSError as e:
                logger.warning(f"Could not create cache directory: {e}")
                self.cache_dir = None

    def _cache_key(self, url: Union[str, GopherURL]) -> str:
        """
        Generate a cache key for a URL.

        Args:
            url: URL to generate key for

        Returns:
            A string key for the cache
        """
        url_str = str(url)
        return hashlib.md5(url_str.encode(), usedforsecurity=False).hexdigest()

    def _get_from_memory_cache(
            self, url: Union[str, GopherURL]) -> Optional[Any]:
        """
        Get an item from the memory cache.

        Args:
            url: URL to get from cache

        Returns:
            Cached content or None if not found/expired
        """
        key = self._cache_key(url)
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if entry.is_expired():
                # Remove expired entry
                del self.memory_cache[key]
                return None

            # Update last accessed time
            entry.last_accessed = datetime.now()
            return entry.content

        return None

    def _store_in_memory_cache(
            self, url: Union[str, GopherURL], content: Any) -> None:
        """
        Store an item in the memory cache.

        Args:
            url: URL to cache
            content: Content to cache
        """
        key = self._cache_key(url)
        expires = datetime.now() + timedelta(seconds=self.cache_ttl) if self.cache_ttl > 0 else None
        self.memory_cache[key] = CacheEntry(content, expires)

        # Clean cache if it gets too big (simple strategy: remove oldest
        # entries)
        if len(self.memory_cache) > 100:  # arbitrary limit
            items = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1].last_accessed)
            # Remove oldest 20% of entries
            for i in range(int(len(items) * 0.2)):
                del self.memory_cache[items[i][0]]

    def _get_from_disk_cache(
            self, url: Union[str, GopherURL]) -> Optional[Any]:
        """
        Get an item from the disk cache.

        Args:
            url: URL to get from cache

        Returns:
            Cached content or None if not found/expired
        """
        if not self.cache_dir:
            return None

        key = self._cache_key(url)
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        data_file = os.path.join(self.cache_dir, f"{key}.data")

        if not os.path.exists(cache_file):
            return None

        try:
            with open(cache_file, 'r') as f:
                metadata = json.load(f)

            # Check expiration
            if 'expires' in metadata:
                expires = datetime.fromisoformat(metadata['expires'])
                if datetime.now() > expires:
                    # Expired
                    return None

            # Load content based on type
            content_type = metadata.get('type', 'unknown')

            if content_type == 'directory':
                # Load directory listing from JSON
                with open(data_file, 'r') as f:
                    items_data = json.load(f)

                # Reconstruct GopherItems
                items = []
                for item_data in items_data:
                    item_type = GopherItemType.from_char(
                        item_data.get('type', '1'))
                    items.append(GopherItem(
                        item_type=item_type,
                        display_string=item_data.get('display', ''),
                        selector=item_data.get('selector', ''),
                        host=item_data.get('host', ''),
                        port=item_data.get('port', DEFAULT_GOPHER_PORT)
                    ))
                return items

            elif content_type == 'text':
                # Load text content
                with open(data_file, 'r') as f:
                    return f.read()

            elif content_type == 'binary':
                # Load binary content
                with open(data_file, 'rb') as f:
                    return f.read()

            return None

        except (json.JSONDecodeError, OSError, ValueError) as e:
            logger.warning(f"Error reading from cache: {e}")
            return None

    def _store_in_disk_cache(
            self, url: Union[str, GopherURL], content: Any) -> None:
        """
        Store an item in the disk cache.

        Args:
            url: URL to cache
            content: Content to cache
        """
        if not self.cache_dir:
            return

        key = self._cache_key(url)
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        data_file = os.path.join(self.cache_dir, f"{key}.data")

        try:
            # Determine content type and create metadata
            metadata = {
                'url': str(url),
                'created': datetime.now().isoformat()
            }

            if self.cache_ttl > 0:
                metadata['expires'] = (
                    datetime.now() +
                    timedelta(
                        seconds=self.cache_ttl)).isoformat()

            # Store based on content type
            if isinstance(
                content,
                list) and all(
                isinstance(
                    item,
                    GopherItem) for item in content):
                # Directory listing
                metadata['type'] = 'directory'

                # Convert GopherItems to serializable format
                items_data = []
                for item in content:
                    items_data.append({
                        'type': item.item_type.value,
                        'display': item.display_string,
                        'selector': item.selector,
                        'host': item.host,
                        'port': item.port
                    })

                # Write metadata
                with open(cache_file, 'w') as f:
                    json.dump(metadata, f)

                # Write items data
                with open(data_file, 'w') as f:
                    json.dump(items_data, f)

            elif isinstance(content, str):
                # Text content
                metadata['type'] = 'text'

                # Write metadata
                with open(cache_file, 'w') as f:
                    json.dump(metadata, f)

                # Write text content
                with open(data_file, 'w') as f:
                    f.write(content)

            elif isinstance(content, bytes):
                # Binary content
                metadata['type'] = 'binary'

                # Write metadata
                with open(cache_file, 'w') as f:
                    json.dump(metadata, f)

                # Write binary content
                with open(data_file, 'wb') as f:
                    f.write(content)

        except (OSError, TypeError) as e:
            logger.warning(f"Error writing to cache: {e}")

    def fetch_directory(self, host: str, selector: str = "",
                        port: int = DEFAULT_GOPHER_PORT,
                        use_ssl: bool = False) -> List[GopherItem]:
        """
        Fetch a Gopher directory (menu) and parse it into GopherItems.

        Args:
            host: Hostname of the Gopher server
            selector: Selector string (path) to the directory
            port: Port to connect to
            use_ssl: Whether to use SSL/TLS

        Returns:
            A list of GopherItem objects representing the directory contents

        Raises:
            GopherProtocolError: If the connection or request fails
        """
        # Collect all the data into a single bytes object
        data = BytesIO()
        for chunk in request_gopher_resource(
            host, selector, port, use_ssl, self.timeout, self.use_ipv6
        ):
            data.write(chunk)

        # Parse the directory content
        return parse_gopher_directory(data.getvalue())

    def fetch_text(self, host: str, selector: str,
                   port: int = DEFAULT_GOPHER_PORT,
                   use_ssl: bool = False,
                   encoding: str = 'utf-8') -> str:
        """
        Fetch a Gopher text resource and return it as a string.

        Args:
            host: Hostname of the Gopher server
            selector: Selector string (path) to the text resource
            port: Port to connect to
            use_ssl: Whether to use SSL/TLS
            encoding: Text encoding to use for decoding the response

        Returns:
            The text content as a string

        Raises:
            GopherProtocolError: If the connection or request fails
            UnicodeDecodeError: If the content cannot be decoded with the specified encoding
        """
        # Collect all the data into a single bytes object
        data = BytesIO()
        for chunk in request_gopher_resource(
            host, selector, port, use_ssl, self.timeout, self.use_ipv6
        ):
            data.write(chunk)

        # Try to decode with the specified encoding
        try:
            return data.getvalue().decode(encoding)
        except UnicodeDecodeError:
            # Fall back to latin-1, which can't fail
            return data.getvalue().decode('latin-1')

    def fetch_binary(self, host: str, selector: str,
                     port: int = DEFAULT_GOPHER_PORT,
                     use_ssl: bool = False) -> bytes:
        """
        Fetch a Gopher binary resource and return it as bytes.

        Args:
            host: Hostname of the Gopher server
            selector: Selector string (path) to the binary resource
            port: Port to connect to
            use_ssl: Whether to use SSL/TLS

        Returns:
            The binary content as bytes

        Raises:
            GopherProtocolError: If the connection or request fails
        """
        # Collect all the data into a single bytes object
        data = BytesIO()
        for chunk in request_gopher_resource(
            host, selector, port, use_ssl, self.timeout, self.use_ipv6
        ):
            data.write(chunk)

        return data.getvalue()

    def download_file(self, host: str, selector: str, file_path: str,
                      port: int = DEFAULT_GOPHER_PORT,
                      use_ssl: bool = False) -> int:
        """
        Download a Gopher resource to a file.

        Args:
            host: Hostname of the Gopher server
            selector: Selector string (path) to the resource
            file_path: Path where the file should be saved
            port: Port to connect to
            use_ssl: Whether to use SSL/TLS

        Returns:
            The number of bytes written to the file

        Raises:
            GopherProtocolError: If the connection or request fails
            IOError: If the file cannot be written
        """
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

        with open(file_path, 'wb') as f:
            return save_gopher_resource(
                host, selector, f, port, use_ssl, self.timeout, self.use_ipv6
            )

    def get_resource(self, url: Union[str, GopherURL],
                     file_path: Optional[str] = None,
                     use_cache: bool = True) -> Any:
        """
        Fetch a Gopher resource using a URL.

        This method detects the resource type based on the URL and calls
        the appropriate fetch method.

        Args:
            url: A Gopher URL as a string or GopherURL object
            file_path: Optional path to save the resource to a file
            use_cache: Whether to check/update the cache

        Returns:
            - For directories: List[GopherItem]
            - For text: str
            - For binary: bytes
            - When file_path is provided: int (bytes written)

        Raises:
            GopherProtocolError: If the connection or request fails
            ValueError: If the URL is invalid
        """
        # Parse the URL if it's a string
        if isinstance(url, str):
            url = parse_gopher_url(url)

        # Check cache if enabled
        if use_cache and not file_path:
            # Try memory cache first
            cached_content = self._get_from_memory_cache(url)
            if cached_content:
                return cached_content

            # Then disk cache
            cached_content = self._get_from_disk_cache(url)
            if cached_content:
                # Store in memory cache for faster access next time
                self._store_in_memory_cache(url, cached_content)
                return cached_content

        # If type is specified in the URL, use it; otherwise, assume it's a
        # directory
        if url.item_type == GopherItemType.DIRECTORY or not url.item_type:
            if file_path:
                with open(file_path, 'wb') as f:
                    return save_gopher_resource(
                        url.host, url.selector, f, url.port, url.use_ssl,
                        self.timeout, self.use_ipv6
                    )
            else:
                content = self.fetch_directory(
                    url.host, url.selector, url.port, url.use_ssl
                )

                # Cache the result if enabled
                if use_cache:
                    self._store_in_memory_cache(url, content)
                    self._store_in_disk_cache(url, content)

                return content

        elif url.item_type.is_text:
            if file_path:
                return self.download_file(
                    url.host, url.selector, file_path, url.port, url.use_ssl
                )
            else:
                content = self.fetch_text(
                    url.host, url.selector, url.port, url.use_ssl
                )

                # Cache the result if enabled
                if use_cache:
                    self._store_in_memory_cache(url, content)
                    self._store_in_disk_cache(url, content)

                return content

        else:  # Binary or other type
            if file_path:
                return self.download_file(
                    url.host, url.selector, file_path, url.port, url.use_ssl
                )
            else:
                content = self.fetch_binary(
                    url.host, url.selector, url.port, url.use_ssl
                )

                # Cache the result if enabled
                if use_cache:
                    self._store_in_memory_cache(url, content)
                    self._store_in_disk_cache(url, content)

                return content
