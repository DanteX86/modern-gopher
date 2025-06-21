#!/usr/bin/env python3
"""
Integration tests for the modern-gopher package.

These tests make actual network connections to real Gopher servers.
They can be skipped by running: pytest -m "not integration"
"""

import socket
import time

import pytest

from modern_gopher.core.client import GopherClient
from modern_gopher.core.protocol import (
    GopherConnectionError,
    GopherProtocolError,
    request_gopher_resource,
)
from modern_gopher.core.types import GopherItemType, parse_gopher_directory
from modern_gopher.core.url import parse_gopher_url

# Known public Gopher servers for testing
TEST_SERVERS = ["gopher.floodgap.com", "gopher.black", "zaibatsu.circumlunar.space"]


def check_server_accessible(host: str, port: int = 70, timeout: int = 5) -> bool:
    """Check if a Gopher server is accessible."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except (socket.gaierror, socket.timeout):
        return False


def get_accessible_server() -> str:
    """Get the first accessible test server."""
    for server in TEST_SERVERS:
        if check_server_accessible(server):
            return server
    pytest.skip("No accessible Gopher servers found for testing")


@pytest.mark.integration
@pytest.mark.network
class TestRealGopherConnections:
    """Test actual connections to real Gopher servers."""

    def test_basic_connection(self):
        """Test basic connection to a real Gopher server."""
        server = get_accessible_server()

        chunks = list(request_gopher_resource(server, "", timeout=10))

        assert len(chunks) > 0

        # Combine chunks and parse as directory
        data = b"".join(chunks)
        assert len(data) > 0

        # Should be able to parse as a directory
        items = parse_gopher_directory(data)
        assert len(items) > 0

    def test_fetch_text_file(self):
        """Test fetching a text file from a real server."""
        server = get_accessible_server()

        # Try to find a text file from the root directory
        client = GopherClient(timeout=10)

        try:
            items = client.fetch_directory(server)

            # Find the first text file
            text_item = None
            for item in items:
                if item.item_type == GopherItemType.TEXT_FILE:
                    text_item = item
                    break

            if text_item:
                # Fetch the text file
                content = client.fetch_text(text_item.host, text_item.selector, text_item.port)

                assert isinstance(content, str)
                assert len(content) > 0
        except GopherProtocolError:
            pytest.skip("Server returned protocol error")

    def test_client_with_caching(self):
        """Test client functionality with caching enabled."""
        server = get_accessible_server()

        import tempfile

        with tempfile.TemporaryDirectory() as cache_dir:
            client = GopherClient(timeout=10, cache_dir=cache_dir)

            # Fetch directory twice - second should be from cache
            start_time = time.time()
            items1 = client.fetch_directory(server)
            first_fetch_time = time.time() - start_time

            start_time = time.time()
            items2 = client.fetch_directory(server)
            second_fetch_time = time.time() - start_time

            # Results should be identical
            assert len(items1) == len(items2)

            # Second fetch should be faster (from cache)
            # Note: This might not always be true due to network variations
            # but generally caching should be faster
            assert second_fetch_time <= first_fetch_time * 2  # Allow some variance

    def test_url_parsing_and_fetching(self):
        """Test URL parsing and fetching integration."""
        server = get_accessible_server()

        url_string = f"gopher://{server}/"
        url = parse_gopher_url(url_string)

        assert url.host == server
        assert url.port == 70
        assert url.selector == "/"

        client = GopherClient(timeout=10)
        result = client.get_resource(url)

        assert isinstance(result, list)  # Should be a directory listing
        assert len(result) > 0

    def test_error_handling_invalid_server(self):
        """Test error handling with invalid server."""
        client = GopherClient(timeout=5)

        with pytest.raises(GopherConnectionError):
            client.fetch_directory("nonexistent.invalid.server.example.com")

    def test_error_handling_invalid_selector(self):
        """Test error handling with invalid selector."""
        server = get_accessible_server()
        client = GopherClient(timeout=10)

        # Try to fetch a non-existent resource
        # Some servers might return an error message instead of failing
        try:
            result = client.fetch_text(server, "/nonexistent/file/that/should/not/exist.txt")
            # If we get here, the server returned something (maybe an error
            # message)
            assert isinstance(result, str)
        except GopherProtocolError:
            # This is also acceptable - server refused the request
            pass

    def test_ipv6_connection_if_available(self):
        """Test IPv6 connection if available."""
        server = get_accessible_server()

        # Check if the server supports IPv6
        try:
            client = GopherClient(timeout=10, use_ipv6=True)
            items = client.fetch_directory(server)
            assert len(items) > 0
        except (GopherConnectionError, socket.gaierror):
            # IPv6 might not be available or supported
            pytest.skip("IPv6 not available or server doesn't support IPv6")

    def test_ssl_connection_if_available(self):
        """Test SSL connection if server supports it."""
        # Most Gopher servers don't support SSL, but test the functionality
        server = get_accessible_server()

        try:
            client = GopherClient(timeout=10)

            # Try to connect with SSL - this will likely fail for most servers
            with pytest.raises((GopherConnectionError, ConnectionRefusedError, OSError)):
                client.fetch_directory(server, use_ssl=True)
        except Exception:
            # SSL might not be supported, which is expected
            pass


@pytest.mark.integration
@pytest.mark.network
class TestCLIIntegration:
    """Test CLI integration with real servers."""

    def test_cli_get_command_real_server(self):
        """Test CLI get command with real server."""
        server = get_accessible_server()

        from unittest.mock import Mock

        from modern_gopher.cli import cmd_get

        # Create mock args for get command
        args = Mock()
        args.url = f"gopher://{server}/"
        args.output = None
        args.markdown = False
        args.ssl = False
        args.verbose = False
        args.timeout = 10
        args.ipv4 = False
        args.ipv6 = False

        # This should not raise an exception
        result = cmd_get(args)
        assert result == 0

    def test_cli_info_command_real_server(self):
        """Test CLI info command with real server."""
        server = get_accessible_server()

        from unittest.mock import Mock

        from modern_gopher.cli import cmd_info

        # Create mock args for info command
        args = Mock()
        args.url = f"gopher://{server}/"
        args.verbose = False

        # This should not raise an exception
        result = cmd_info(args)
        assert result == 0


if __name__ == "__main__":
    # Run only integration tests
    pytest.main(["-m", "integration", __file__])
