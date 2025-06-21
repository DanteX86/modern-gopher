#!/usr/bin/env python3
"""
Tests for Gopher types and data structures.
"""

import os
import tempfile
from unittest.mock import patch

import pytest

from modern_gopher.core.types import (
    GopherItem,
    GopherItemType,
    get_item_type_for_file,
    is_item_type_binary,
    is_item_type_interactive,
    is_item_type_text,
    parse_gopher_directory,
)


class TestGopherItemType:
    """Test GopherItemType enum functionality."""

    def test_from_char_valid(self):
        """Test creating GopherItemType from valid characters."""
        assert GopherItemType.from_char("0") == GopherItemType.TEXT_FILE
        assert GopherItemType.from_char("1") == GopherItemType.DIRECTORY
        assert GopherItemType.from_char("7") == GopherItemType.SEARCH_SERVER
        assert GopherItemType.from_char("9") == GopherItemType.BINARY_FILE
        assert GopherItemType.from_char("g") == GopherItemType.GIF_IMAGE
        assert GopherItemType.from_char("h") == GopherItemType.HTML
        assert GopherItemType.from_char("i") == GopherItemType.INFORMATION

    def test_from_char_invalid(self):
        """Test creating GopherItemType from invalid characters."""
        assert GopherItemType.from_char("x") is None
        assert GopherItemType.from_char("Z") is None
        assert GopherItemType.from_char("") is None
        assert GopherItemType.from_char("99") is None

    def test_is_text_property(self):
        """Test the is_text property."""
        assert GopherItemType.TEXT_FILE.is_text
        assert GopherItemType.DIRECTORY.is_text
        assert GopherItemType.ERROR.is_text
        assert GopherItemType.INFORMATION.is_text

        assert not GopherItemType.BINARY_FILE.is_text
        assert not GopherItemType.GIF_IMAGE.is_text
        assert not GopherItemType.SOUND_FILE.is_text

    def test_is_binary_property(self):
        """Test the is_binary property."""
        assert GopherItemType.BINARY_FILE.is_binary
        assert GopherItemType.DOS_BINARY.is_binary
        assert GopherItemType.GIF_IMAGE.is_binary
        assert GopherItemType.IMAGE_FILE.is_binary
        assert GopherItemType.SOUND_FILE.is_binary
        assert GopherItemType.PDF.is_binary

        assert not GopherItemType.TEXT_FILE.is_binary
        assert not GopherItemType.DIRECTORY.is_binary
        assert not GopherItemType.HTML.is_binary

    def test_is_interactive_property(self):
        """Test the is_interactive property."""
        assert GopherItemType.CSO_PHONE_BOOK.is_interactive
        assert GopherItemType.SEARCH_SERVER.is_interactive
        assert GopherItemType.TELNET.is_interactive
        assert GopherItemType.TN3270_SESSION.is_interactive

        assert not GopherItemType.TEXT_FILE.is_interactive
        assert not GopherItemType.DIRECTORY.is_interactive
        assert not GopherItemType.BINARY_FILE.is_interactive

    def test_mime_type_property(self):
        """Test the mime_type property."""
        assert GopherItemType.TEXT_FILE.mime_type == "text/plain"
        assert GopherItemType.HTML.mime_type == "text/html"
        assert GopherItemType.GIF_IMAGE.mime_type == "image/gif"
        assert GopherItemType.PDF.mime_type == "application/pdf"
        assert GopherItemType.BINARY_FILE.mime_type == "application/octet-stream"
        assert GopherItemType.SOUND_FILE.mime_type == "audio/unknown"

    def test_extension_property(self):
        """Test the extension property."""
        assert GopherItemType.TEXT_FILE.extension == ".txt"
        assert GopherItemType.HTML.extension == ".html"
        assert GopherItemType.GIF_IMAGE.extension == ".gif"
        assert GopherItemType.PDF.extension == ".pdf"
        assert GopherItemType.BINARY_FILE.extension == ".bin"
        assert GopherItemType.SOUND_FILE.extension == ".snd"

    def test_display_name_property(self):
        """Test the display_name property."""
        assert GopherItemType.TEXT_FILE.display_name == "Text File"
        assert GopherItemType.DIRECTORY.display_name == "Directory"
        assert GopherItemType.SEARCH_SERVER.display_name == "Search Server"
        assert GopherItemType.HTML.display_name == "HTML File"
        assert GopherItemType.BINARY_FILE.display_name == "Binary File"


class TestGopherItem:
    """Test GopherItem functionality."""

    def test_from_menu_line_basic(self):
        """Test parsing basic menu line."""
        line = "0About this server\t/about.txt\texample.com\t70"
        item = GopherItem.from_menu_line(line)

        assert item is not None
        assert item.item_type == GopherItemType.TEXT_FILE
        assert item.display_string == "About this server"
        assert item.selector == "/about.txt"
        assert item.host == "example.com"
        assert item.port == 70

    def test_from_menu_line_directory(self):
        """Test parsing directory menu line."""
        line = "1User Directory\t/users\texample.com\t70"
        item = GopherItem.from_menu_line(line)

        assert item is not None
        assert item.item_type == GopherItemType.DIRECTORY
        assert item.display_string == "User Directory"
        assert item.selector == "/users"
        assert item.host == "example.com"
        assert item.port == 70

    def test_from_menu_line_no_port(self):
        """Test parsing menu line without explicit port."""
        line = "0About this server\t/about.txt\texample.com\t"
        item = GopherItem.from_menu_line(line)

        assert item is not None
        assert item.port == 70  # Default port

    def test_from_menu_line_invalid_port(self):
        """Test parsing menu line with invalid port."""
        line = "0About this server\t/about.txt\texample.com\tinvalid"
        item = GopherItem.from_menu_line(line)

        assert item is not None
        assert item.port == 70  # Default port

    def test_from_menu_line_custom_port(self):
        """Test parsing menu line with custom port."""
        line = "0About this server\t/about.txt\texample.com\t8080"
        item = GopherItem.from_menu_line(line)

        assert item is not None
        assert item.port == 8080

    def test_from_menu_line_unknown_type(self):
        """Test parsing menu line with unknown item type."""
        line = "XUnknown Type\t/unknown\texample.com\t70"
        item = GopherItem.from_menu_line(line)

        assert item is not None
        assert item.item_type == GopherItemType.BINARY_FILE  # Default for unknown
        assert item.display_string == "Unknown Type"

    def test_from_menu_line_information(self):
        """Test parsing information line."""
        line = "iThis is just information\t\terror.host\t1"
        item = GopherItem.from_menu_line(line)

        assert item is not None
        assert item.item_type == GopherItemType.INFORMATION
        assert item.display_string == "This is just information"
        assert item.selector == ""
        assert item.host == "error.host"
        assert item.port == 1

    def test_from_menu_line_insufficient_parts(self):
        """Test parsing menu line with insufficient parts."""
        line = "0About this server\t/about.txt"
        item = GopherItem.from_menu_line(line)

        assert item is None

    def test_from_menu_line_empty(self):
        """Test parsing empty line."""
        assert GopherItem.from_menu_line("") is None
        assert GopherItem.from_menu_line(".") is None

    def test_from_menu_line_no_display_string(self):
        """Test parsing line with no display string."""
        line = "\t/about.txt\texample.com\t70"
        item = GopherItem.from_menu_line(line)

        assert item is None

    def test_to_menu_line(self):
        """Test converting GopherItem back to menu line."""
        item = GopherItem(
            item_type=GopherItemType.TEXT_FILE,
            display_string="About this server",
            selector="/about.txt",
            host="example.com",
            port=70,
        )

        line = item.to_menu_line()
        assert line == "0About this server\t/about.txt\texample.com\t70"


class TestDirectoryParsing:
    """Test Gopher directory parsing functionality."""

    def test_parse_gopher_directory_basic(self):
        """Test parsing basic directory."""
        data = b"""0About this server\t/about.txt\texample.com\t70
1User Directory\t/users\texample.com\t70
iInformation line\t\terror.host\t1
.
"""

        items = parse_gopher_directory(data)

        assert len(items) == 3

        # Check first item
        assert items[0].item_type == GopherItemType.TEXT_FILE
        assert items[0].display_string == "About this server"
        assert items[0].selector == "/about.txt"

        # Check second item
        assert items[1].item_type == GopherItemType.DIRECTORY
        assert items[1].display_string == "User Directory"

        # Check information item
        assert items[2].item_type == GopherItemType.INFORMATION
        assert items[2].display_string == "Information line"

    def test_parse_gopher_directory_utf8(self):
        """Test parsing directory with UTF-8 encoding."""
        data = "0Über uns\t/about.txt\texample.com\t70\n.\n".encode("utf-8")

        items = parse_gopher_directory(data)

        assert len(items) == 1
        assert items[0].display_string == "Über uns"

    def test_parse_gopher_directory_latin1_fallback(self):
        """Test parsing directory with Latin-1 fallback."""
        # Create data that's valid Latin-1 but not UTF-8
        data = b"0Caf\xe9\t/cafe.txt\texample.com\t70\n.\n"

        items = parse_gopher_directory(data)

        assert len(items) == 1
        assert items[0].display_string == "Café"

    def test_parse_gopher_directory_no_terminator(self):
        """Test parsing directory without dot terminator."""
        data = b"""0About this server\t/about.txt\texample.com\t70
1User Directory\t/users\texample.com\t70
"""

        items = parse_gopher_directory(data)

        assert len(items) == 2

    def test_parse_gopher_directory_empty(self):
        """Test parsing empty directory."""
        data = b".\n"

        items = parse_gopher_directory(data)

        assert len(items) == 0

    def test_parse_gopher_directory_invalid_lines(self):
        """Test parsing directory with some invalid lines."""
        data = b"""0Valid line\t/valid.txt\texample.com\t70
invalid line without tabs
1Another valid\t/valid2\texample.com\t70
incomplete\ttabs
.
"""

        items = parse_gopher_directory(data)

        # Should only get the valid lines
        assert len(items) == 2
        assert items[0].display_string == "Valid line"
        assert items[1].display_string == "Another valid"


class TestUtilityFunctions:
    """Test utility functions."""

    def test_is_item_type_text(self):
        """Test is_item_type_text function."""
        assert is_item_type_text(GopherItemType.TEXT_FILE)
        assert is_item_type_text(GopherItemType.DIRECTORY)
        assert is_item_type_text(GopherItemType.INFORMATION)

        assert not is_item_type_text(GopherItemType.BINARY_FILE)
        assert not is_item_type_text(GopherItemType.GIF_IMAGE)

    def test_is_item_type_binary(self):
        """Test is_item_type_binary function."""
        assert is_item_type_binary(GopherItemType.BINARY_FILE)
        assert is_item_type_binary(GopherItemType.GIF_IMAGE)
        assert is_item_type_binary(GopherItemType.PDF)

        assert not is_item_type_binary(GopherItemType.TEXT_FILE)
        assert not is_item_type_binary(GopherItemType.DIRECTORY)

    def test_is_item_type_interactive(self):
        """Test is_item_type_interactive function."""
        assert is_item_type_interactive(GopherItemType.SEARCH_SERVER)
        assert is_item_type_interactive(GopherItemType.TELNET)
        assert is_item_type_interactive(GopherItemType.CSO_PHONE_BOOK)

        assert not is_item_type_interactive(GopherItemType.TEXT_FILE)
        assert not is_item_type_interactive(GopherItemType.BINARY_FILE)


class TestFileTypeDetection:
    """Test file type detection functionality."""

    def test_get_item_type_for_directory(self):
        """Test detecting directory type."""
        with tempfile.TemporaryDirectory() as temp_dir:
            item_type = get_item_type_for_file(temp_dir)
            assert item_type == GopherItemType.DIRECTORY

    def test_get_item_type_for_text_files(self):
        """Test detecting text file types."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            temp_file = f.name

        try:
            assert get_item_type_for_file(temp_file) == GopherItemType.TEXT_FILE
        finally:
            os.unlink(temp_file)

        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            temp_file = f.name

        try:
            assert get_item_type_for_file(temp_file) == GopherItemType.TEXT_FILE
        finally:
            os.unlink(temp_file)

    def test_get_item_type_for_html_files(self):
        """Test detecting HTML file types."""
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            temp_file = f.name

        try:
            assert get_item_type_for_file(temp_file) == GopherItemType.HTML
        finally:
            os.unlink(temp_file)

        with tempfile.NamedTemporaryFile(suffix=".htm", delete=False) as f:
            temp_file = f.name

        try:
            assert get_item_type_for_file(temp_file) == GopherItemType.HTML
        finally:
            os.unlink(temp_file)

    def test_get_item_type_for_image_files(self):
        """Test detecting image file types."""
        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as f:
            temp_file = f.name

        try:
            assert get_item_type_for_file(temp_file) == GopherItemType.GIF_IMAGE
        finally:
            os.unlink(temp_file)

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            temp_file = f.name

        try:
            assert get_item_type_for_file(temp_file) == GopherItemType.IMAGE_FILE
        finally:
            os.unlink(temp_file)

    def test_get_item_type_for_pdf_files(self):
        """Test detecting PDF file types."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_file = f.name

        try:
            assert get_item_type_for_file(temp_file) == GopherItemType.PDF
        finally:
            os.unlink(temp_file)

    def test_get_item_type_for_sound_files(self):
        """Test detecting sound file types."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_file = f.name

        try:
            assert get_item_type_for_file(temp_file) == GopherItemType.SOUND_FILE
        finally:
            os.unlink(temp_file)

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            temp_file = f.name

        try:
            assert get_item_type_for_file(temp_file) == GopherItemType.SOUND_FILE
        finally:
            os.unlink(temp_file)

    def test_get_item_type_for_unknown_extension(self):
        """Test detecting type for unknown extension."""
        with tempfile.NamedTemporaryFile(suffix=".unknown", delete=False) as f:
            temp_file = f.name

        try:
            # Should default to binary for unknown types
            assert get_item_type_for_file(temp_file) == GopherItemType.BINARY_FILE
        finally:
            os.unlink(temp_file)

    @patch("mimetypes.guess_type")
    def test_get_item_type_mime_fallback(self, mock_guess_type):
        """Test MIME type fallback for unknown extensions."""
        # Mock MIME type detection
        mock_guess_type.return_value = ("text/plain", None)

        with tempfile.NamedTemporaryFile(suffix=".unknown", delete=False) as f:
            temp_file = f.name

        try:
            assert get_item_type_for_file(temp_file) == GopherItemType.TEXT_FILE
        finally:
            os.unlink(temp_file)


if __name__ == "__main__":
    pytest.main([__file__])
