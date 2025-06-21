#!/usr/bin/env python3
"""
Tests for Gopher URL parsing functionality.
"""

import pytest

from modern_gopher.core.protocol import DEFAULT_GOPHER_PORT
from modern_gopher.core.types import GopherItemType
from modern_gopher.core.url import build_gopher_url, is_gopher_url, parse_gopher_url


class TestGopherURLParsing:
    """Test Gopher URL parsing functionality."""

    def test_basic_url_parsing(self):
        """Test parsing of basic Gopher URLs."""
        url = "gopher://gopher.floodgap.com"
        parsed = parse_gopher_url(url)

        assert parsed.host == "gopher.floodgap.com"
        assert parsed.port == DEFAULT_GOPHER_PORT
        assert parsed.selector == ""
        assert parsed.item_type is None
        assert not parsed.use_ssl

    def test_url_with_port(self):
        """Test parsing URLs with custom ports."""
        url = "gopher://example.com:8080"
        parsed = parse_gopher_url(url)

        assert parsed.host == "example.com"
        assert parsed.port == 8080

    def test_url_with_selector(self):
        """Test parsing URLs with selectors."""
        url = "gopher://example.com/1/path/to/directory"
        parsed = parse_gopher_url(url)

        assert parsed.host == "example.com"
        assert parsed.item_type == GopherItemType.DIRECTORY
        assert parsed.selector == "/path/to/directory"

    def test_ssl_url(self):
        """Test parsing secure Gopher URLs."""
        url = "gophers://secure.example.com"
        parsed = parse_gopher_url(url)

        assert parsed.host == "secure.example.com"
        assert parsed.use_ssl

    def test_url_building(self):
        """Test building URLs from components."""
        url = build_gopher_url(
            host="example.com", selector="/test", item_type=GopherItemType.TEXT_FILE
        )

        expected = "gopher://example.com/0/test"
        assert url == expected

    def test_url_validation(self):
        """Test URL validation."""
        assert is_gopher_url("gopher://example.com")
        assert is_gopher_url("gophers://example.com")
        assert not is_gopher_url("http://example.com")
        assert not is_gopher_url("invalid-url")


if __name__ == "__main__":
    pytest.main([__file__])
