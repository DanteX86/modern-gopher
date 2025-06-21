#!/usr/bin/env python3
"""
Tests for Gopher client implementation.
"""

import os
import tempfile
from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

import pytest

from modern_gopher.core.client import CacheEntry
from modern_gopher.core.client import GopherClient
from modern_gopher.core.protocol import DEFAULT_GOPHER_PORT
from modern_gopher.core.protocol import GopherProtocolError
from modern_gopher.core.types import GopherItem
from modern_gopher.core.types import GopherItemType
from modern_gopher.core.url import GopherURL


class TestCacheEntry:
    """Test CacheEntry functionality."""

    def test_cache_entry_creation(self):
        """Test creating a cache entry."""
        content = "test content"
        entry = CacheEntry(content)

        assert entry.content == content
        assert entry.expires is None
        assert isinstance(entry.created, datetime)
        assert isinstance(entry.last_accessed, datetime)
        assert entry.created == entry.last_accessed

    def test_cache_entry_with_expiration(self):
        """Test creating a cache entry with expiration."""
        content = "test content"
        expires = datetime.now() + timedelta(hours=1)
        entry = CacheEntry(content, expires)

        assert entry.content == content
        assert entry.expires == expires
        assert not entry.is_expired()

    def test_cache_entry_expired(self):
        """Test expired cache entry."""
        content = "test content"
        expires = datetime.now() - timedelta(hours=1)  # Expired
        entry = CacheEntry(content, expires)

        assert entry.is_expired()

    def test_cache_entry_no_expiration(self):
        """Test cache entry without expiration."""
        content = "test content"
        entry = CacheEntry(content, expires=None)

        assert not entry.is_expired()


class TestGopherClient:
    """Test GopherClient functionality."""

    def test_client_initialization_basic(self):
        """Test basic client initialization."""
        client = GopherClient()

        assert client.timeout == 30
        assert client.use_ipv6 is None
        assert client.cache_ttl == 3600
        assert client.cache_dir is None
        assert len(client.memory_cache) == 0

    def test_client_initialization_with_params(self):
        """Test client initialization with parameters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            client = GopherClient(
                timeout=60,
                cache_dir=temp_dir,
                use_ipv6=True,
                cache_ttl=7200
            )

            assert client.timeout == 60
            assert client.use_ipv6 is True
            assert client.cache_ttl == 7200
            assert client.cache_dir == temp_dir
            assert os.path.exists(temp_dir)

    def test_client_cache_dir_creation_failure(self):
        """Test handling cache directory creation failure."""
        with patch('os.makedirs', side_effect=OSError("Permission denied")):
            client = GopherClient(cache_dir="/invalid/path")

            # Should gracefully handle the error and disable caching
            assert client.cache_dir is None

    def test_cache_key_generation(self):
        """Test cache key generation."""
        client = GopherClient()

        key1 = client._cache_key("gopher://example.com")
        key2 = client._cache_key("gopher://example.com")
        key3 = client._cache_key("gopher://different.com")

        assert key1 == key2  # Same URL should produce same key
        assert key1 != key3  # Different URLs should produce different keys
        assert len(key1) == 32  # MD5 hash length

    def test_memory_cache_storage_and_retrieval(self):
        """Test storing and retrieving from memory cache."""
        client = GopherClient(cache_ttl=3600)
        url = "gopher://example.com"
        content = "test content"

        # Store in cache
        client._store_in_memory_cache(url, content)

        # Retrieve from cache
        cached_content = client._get_from_memory_cache(url)

        assert cached_content == content

    def test_memory_cache_expiration(self):
        """Test memory cache expiration."""
        client = GopherClient(cache_ttl=-1)  # Expired cache entries
        url = "gopher://example.com"
        content = "test content"

        # Store in cache with expired TTL
        client._store_in_memory_cache(url, content)

        # Manually expire the entry by setting it to the past
        cache_key = client._cache_key(url)
        if cache_key in client.memory_cache:
            from datetime import datetime
            from datetime import timedelta
            client.memory_cache[cache_key].expires = datetime.now(
            ) - timedelta(hours=1)

        # Should be expired
        cached_content = client._get_from_memory_cache(url)
        assert cached_content is None

    def test_memory_cache_cleanup(self):
        """Test memory cache automatic cleanup."""
        client = GopherClient()

        # Fill cache beyond limit (100 items)
        for i in range(110):
            url = f"gopher://example{i}.com"
            content = f"content {i}"
            client._store_in_memory_cache(url, content)

        # Cache should be cleaned up
        assert len(client.memory_cache) < 110
        # Should keep around 80% after cleanup
        assert len(client.memory_cache) >= 80


class TestClientFetching:
    """Test client resource fetching functionality."""

    @patch('modern_gopher.core.client.request_gopher_resource')
    def test_fetch_directory(self, mock_request):
        """Test fetching a directory."""
        # Mock response data
        directory_data = b"""0About\t/about.txt\texample.com\t70
1Subdirectory\t/sub\texample.com\t70
.
"""
        mock_request.return_value = iter([directory_data])

        client = GopherClient()
        items = client.fetch_directory("example.com", "/")

        assert len(items) == 2
        assert items[0].item_type == GopherItemType.TEXT_FILE
        assert items[0].display_string == "About"
        assert items[1].item_type == GopherItemType.DIRECTORY
        assert items[1].display_string == "Subdirectory"

        mock_request.assert_called_once_with(
            "example.com", "/", DEFAULT_GOPHER_PORT, False, 30, None
        )

    @patch('modern_gopher.core.client.request_gopher_resource')
    def test_fetch_text(self, mock_request):
        """Test fetching text content."""
        text_data = b"Hello, World!\nThis is a test."
        mock_request.return_value = iter([text_data])

        client = GopherClient()
        content = client.fetch_text("example.com", "/test.txt")

        assert content == "Hello, World!\nThis is a test."

        mock_request.assert_called_once_with(
            "example.com", "/test.txt", DEFAULT_GOPHER_PORT, False, 30, None
        )

    @patch('modern_gopher.core.client.request_gopher_resource')
    def test_fetch_text_encoding_fallback(self, mock_request):
        """Test text fetching with encoding fallback."""
        # Invalid UTF-8 but valid Latin-1
        text_data = b"Caf\xe9"
        mock_request.return_value = iter([text_data])

        client = GopherClient()
        content = client.fetch_text("example.com", "/test.txt")

        assert content == "Café"

    @patch('modern_gopher.core.client.request_gopher_resource')
    def test_fetch_binary(self, mock_request):
        """Test fetching binary content."""
        binary_data = b"\x00\x01\x02\x03\xFF"
        mock_request.return_value = iter([binary_data])

        client = GopherClient()
        content = client.fetch_binary("example.com", "/test.bin")

        assert content == binary_data

        mock_request.assert_called_once_with(
            "example.com", "/test.bin", DEFAULT_GOPHER_PORT, False, 30, None
        )

    @patch('modern_gopher.core.client.save_gopher_resource')
    def test_download_file(self, mock_save):
        """Test downloading a file."""
        mock_save.return_value = 1024  # bytes written

        with tempfile.NamedTemporaryFile() as temp_file:
            client = GopherClient()
            bytes_written = client.download_file(
                "example.com", "/test.bin", temp_file.name
            )

            assert bytes_written == 1024

            mock_save.assert_called_once()
            args = mock_save.call_args[0]
            assert args[0] == "example.com"
            assert args[1] == "/test.bin"
            # args[2] is the file handle
            assert args[3] == DEFAULT_GOPHER_PORT
            assert args[4] is False  # use_ssl
            assert args[5] == 30     # timeout
            assert args[6] is None   # use_ipv6


class TestClientHighLevel:
    """Test high-level client functionality."""

    @patch('modern_gopher.core.client.GopherClient.fetch_directory')
    def test_get_resource_directory(self, mock_fetch_directory):
        """Test getting a directory resource."""
        mock_items = [
            GopherItem(
                GopherItemType.TEXT_FILE,
                "Test",
                "/test",
                "example.com",
                70)]
        mock_fetch_directory.return_value = mock_items

        client = GopherClient()
        url = GopherURL("example.com", "/", 70, GopherItemType.DIRECTORY)

        result = client.get_resource(url)

        assert result == mock_items
        mock_fetch_directory.assert_called_once_with(
            "example.com", "/", 70, False)

    @patch('modern_gopher.core.client.GopherClient.fetch_text')
    def test_get_resource_text(self, mock_fetch_text):
        """Test getting a text resource."""
        mock_text = "Hello, World!"
        mock_fetch_text.return_value = mock_text

        client = GopherClient()
        url = GopherURL(
            "example.com",
            "/test.txt",
            70,
            GopherItemType.TEXT_FILE)

        result = client.get_resource(url)

        assert result == mock_text
        mock_fetch_text.assert_called_once_with(
            "example.com", "/test.txt", 70, False)

    @patch('modern_gopher.core.client.GopherClient.fetch_binary')
    def test_get_resource_binary(self, mock_fetch_binary):
        """Test getting a binary resource."""
        mock_binary = b"\x00\x01\x02"
        mock_fetch_binary.return_value = mock_binary

        client = GopherClient()
        url = GopherURL(
            "example.com",
            "/test.bin",
            70,
            GopherItemType.BINARY_FILE)

        result = client.get_resource(url)

        assert result == mock_binary
        mock_fetch_binary.assert_called_once_with(
            "example.com", "/test.bin", 70, False)

    @patch('modern_gopher.core.client.GopherClient.download_file')
    def test_get_resource_to_file(self, mock_download):
        """Test getting a resource and saving to file."""
        mock_download.return_value = 1024

        client = GopherClient()
        url = GopherURL(
            "example.com",
            "/test.bin",
            70,
            GopherItemType.BINARY_FILE)

        with tempfile.NamedTemporaryFile() as temp_file:
            result = client.get_resource(url, file_path=temp_file.name)

            assert result == 1024
            mock_download.assert_called_once_with(
                "example.com", "/test.bin", temp_file.name, 70, False
            )

    def test_get_resource_string_url(self):
        """Test getting a resource using string URL."""
        with patch('modern_gopher.core.client.GopherClient.fetch_directory') as mock_fetch:
            mock_items = []
            mock_fetch.return_value = mock_items

            client = GopherClient()
            result = client.get_resource("gopher://example.com/")

            assert result == mock_items

    def test_get_resource_with_caching(self):
        """Test resource caching functionality."""
        with patch('modern_gopher.core.client.GopherClient.fetch_directory') as mock_fetch:
            mock_items = [
                GopherItem(
                    GopherItemType.TEXT_FILE,
                    "Test",
                    "/test",
                    "example.com",
                    70)]
            mock_fetch.return_value = mock_items

            client = GopherClient()
            url = "gopher://example.com/"

            # First call should fetch from server
            result1 = client.get_resource(url)
            assert result1 == mock_items
            assert mock_fetch.call_count == 1

            # Second call should use cache
            result2 = client.get_resource(url)
            assert result2 == mock_items
            assert mock_fetch.call_count == 1  # No additional calls

    def test_get_resource_cache_disabled(self):
        """Test resource fetching with caching disabled."""
        with patch('modern_gopher.core.client.GopherClient.fetch_directory') as mock_fetch:
            mock_items = []
            mock_fetch.return_value = mock_items

            client = GopherClient()
            url = "gopher://example.com/"

            # Both calls should fetch from server
            client.get_resource(url, use_cache=False)
            client.get_resource(url, use_cache=False)

            assert mock_fetch.call_count == 2


class TestDiskCaching:
    """Test disk caching functionality."""

    def test_disk_cache_directory_storage(self):
        """Test storing directory in disk cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            client = GopherClient(cache_dir=temp_dir)
            url = "gopher://example.com/"
            items = [
                GopherItem(
                    GopherItemType.TEXT_FILE,
                    "Test",
                    "/test",
                    "example.com",
                    70)]

            client._store_in_disk_cache(url, items)

            # Check that cache files were created
            cache_key = client._cache_key(url)
            cache_file = os.path.join(temp_dir, f"{cache_key}.json")
            data_file = os.path.join(temp_dir, f"{cache_key}.data")

            assert os.path.exists(cache_file)
            assert os.path.exists(data_file)

    def test_disk_cache_directory_retrieval(self):
        """Test retrieving directory from disk cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            client = GopherClient(cache_dir=temp_dir)
            url = "gopher://example.com/"
            items = [
                GopherItem(
                    GopherItemType.TEXT_FILE,
                    "Test",
                    "/test",
                    "example.com",
                    70)]

            # Store and retrieve
            client._store_in_disk_cache(url, items)
            cached_items = client._get_from_disk_cache(url)

            assert len(cached_items) == 1
            assert cached_items[0].item_type == GopherItemType.TEXT_FILE
            assert cached_items[0].display_string == "Test"
            assert cached_items[0].selector == "/test"
            assert cached_items[0].host == "example.com"
            assert cached_items[0].port == 70

    def test_disk_cache_text_storage_retrieval(self):
        """Test storing and retrieving text content from disk cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            client = GopherClient(cache_dir=temp_dir)
            url = "gopher://example.com/test.txt"
            content = "Hello, World!"

            # Store and retrieve
            client._store_in_disk_cache(url, content)
            cached_content = client._get_from_disk_cache(url)

            assert cached_content == content

    def test_disk_cache_binary_storage_retrieval(self):
        """Test storing and retrieving binary content from disk cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            client = GopherClient(cache_dir=temp_dir)
            url = "gopher://example.com/test.bin"
            content = b"\x00\x01\x02\x03"

            # Store and retrieve
            client._store_in_disk_cache(url, content)
            cached_content = client._get_from_disk_cache(url)

            assert cached_content == content

    def test_disk_cache_expiration(self):
        """Test disk cache expiration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            client = GopherClient(
                cache_dir=temp_dir,
                cache_ttl=1)  # 1 second expiration
            url = "gopher://example.com/test.txt"
            content = "Hello, World!"

            # Store and try to retrieve immediately
            client._store_in_disk_cache(url, content)

            # Sleep to ensure expiration
            import time
            time.sleep(1.1)

            cached_content = client._get_from_disk_cache(url)

            # Should be None due to expiration
            assert cached_content is None

    def test_disk_cache_no_cache_dir(self):
        """Test disk caching when no cache directory is set."""
        client = GopherClient(cache_dir=None)
        url = "gopher://example.com/test.txt"
        content = "Hello, World!"

        # Should not raise any errors
        client._store_in_disk_cache(url, content)
        cached_content = client._get_from_disk_cache(url)

        assert cached_content is None

    def test_disk_cache_corrupted_metadata(self):
        """Test handling corrupted cache metadata."""
        with tempfile.TemporaryDirectory() as temp_dir:
            client = GopherClient(cache_dir=temp_dir)
            url = "gopher://example.com/test.txt"

            # Create corrupted cache file
            cache_key = client._cache_key(url)
            cache_file = os.path.join(temp_dir, f"{cache_key}.json")

            with open(cache_file, 'w') as f:
                f.write("invalid json")

            # Should handle gracefully
            cached_content = client._get_from_disk_cache(url)
            assert cached_content is None


class TestErrorHandling:
    """Test error handling in client."""

    @patch('modern_gopher.core.client.request_gopher_resource')
    def test_fetch_directory_protocol_error(self, mock_request):
        """Test handling protocol errors when fetching directory."""
        mock_request.side_effect = GopherProtocolError("Connection failed")

        client = GopherClient()

        with pytest.raises(GopherProtocolError):
            client.fetch_directory("example.com", "/")

    @patch('modern_gopher.core.client.request_gopher_resource')
    def test_fetch_text_protocol_error(self, mock_request):
        """Test handling protocol errors when fetching text."""
        mock_request.side_effect = GopherProtocolError("Connection failed")

        client = GopherClient()

        with pytest.raises(GopherProtocolError):
            client.fetch_text("example.com", "/test.txt")

    @patch('modern_gopher.core.client.save_gopher_resource')
    def test_download_file_io_error(self, mock_save):
        """Test handling IO errors when downloading files."""
        mock_save.side_effect = IOError("Disk full")

        client = GopherClient()

        with tempfile.NamedTemporaryFile() as temp_file:
            with pytest.raises(IOError):
                client.download_file(
                    "example.com", "/test.bin", temp_file.name)


if __name__ == "__main__":
    pytest.main([__file__])
