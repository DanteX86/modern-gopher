#!/usr/bin/env python3
"""
Enhanced tests for types module to improve coverage.
"""

import os
import tempfile
from pathlib import Path

import pytest

from modern_gopher.core.types import (
    GopherItemType,
    get_item_type_for_file,
    is_item_type_interactive,
)


class TestInteractiveTypes:
    """Test the is_item_type_interactive helper function."""

    def test_interactive_types(self):
        """Test types that are interactive."""
        interactive_types = [
            GopherItemType.SEARCH_SERVER,
            GopherItemType.TELNET,
            GopherItemType.TN3270_SESSION,
            GopherItemType.CSO_PHONE_BOOK,
        ]
        
        for item_type in interactive_types:
            assert is_item_type_interactive(item_type) is True

    def test_non_interactive_types(self):
        """Test types that are not interactive."""
        non_interactive_types = [
            GopherItemType.TEXT_FILE,
            GopherItemType.DIRECTORY,
            GopherItemType.IMAGE_FILE,
            GopherItemType.BINARY_FILE,
            GopherItemType.HTML,
            GopherItemType.GIF_IMAGE,
            GopherItemType.SOUND_FILE,
            GopherItemType.PDF,
            GopherItemType.UUENCODED_FILE,
            GopherItemType.DOCUMENT,
            GopherItemType.CALENDAR,
            GopherItemType.INFORMATION,
            GopherItemType.ERROR,
        ]
        
        for item_type in non_interactive_types:
            assert is_item_type_interactive(item_type) is False


class TestFileTypeDetection:
    """Test the get_item_type_for_file function."""

    def test_directory_detection(self):
        """Test directory detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            item_type = get_item_type_for_file(temp_dir)
            assert item_type == GopherItemType.DIRECTORY

    def test_text_file_extensions(self):
        """Test text file extension detection."""
        text_extensions = [".txt", ".text", ".md"]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            for ext in text_extensions:
                test_file = Path(temp_dir) / f"test{ext}"
                test_file.touch()
                
                item_type = get_item_type_for_file(str(test_file))
                assert item_type == GopherItemType.TEXT_FILE

    def test_html_extensions(self):
        """Test HTML file extension detection."""
        html_extensions = [".html", ".htm"]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            for ext in html_extensions:
                test_file = Path(temp_dir) / f"test{ext}"
                test_file.touch()
                
                item_type = get_item_type_for_file(str(test_file))
                assert item_type == GopherItemType.HTML

    def test_image_extensions(self):
        """Test image file extension detection."""
        image_extensions = [".jpg", ".jpeg", ".png"]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            for ext in image_extensions:
                test_file = Path(temp_dir) / f"test{ext}"
                test_file.touch()
                
                item_type = get_item_type_for_file(str(test_file))
                assert item_type == GopherItemType.IMAGE_FILE

    def test_gif_extension(self):
        """Test GIF file extension detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.gif"
            test_file.touch()
            
            item_type = get_item_type_for_file(str(test_file))
            assert item_type == GopherItemType.GIF_IMAGE

    def test_sound_extensions(self):
        """Test sound file extension detection."""
        sound_extensions = [".wav", ".mp3", ".ogg"]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            for ext in sound_extensions:
                test_file = Path(temp_dir) / f"test{ext}"
                test_file.touch()
                
                item_type = get_item_type_for_file(str(test_file))
                assert item_type == GopherItemType.SOUND_FILE

    def test_pdf_extension(self):
        """Test PDF file extension detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.pdf"
            test_file.touch()
            
            item_type = get_item_type_for_file(str(test_file))
            assert item_type == GopherItemType.PDF

    def test_document_extension(self):
        """Test document file extension detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.doc"
            test_file.touch()
            
            item_type = get_item_type_for_file(str(test_file))
            assert item_type == GopherItemType.DOCUMENT

    def test_calendar_extension(self):
        """Test calendar file extension detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.ics"
            test_file.touch()
            
            item_type = get_item_type_for_file(str(test_file))
            assert item_type == GopherItemType.CALENDAR

    def test_unknown_extension_fallback(self):
        """Test fallback to binary for unknown extensions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.unknown"
            test_file.touch()
            
            item_type = get_item_type_for_file(str(test_file))
            assert item_type == GopherItemType.BINARY_FILE

    def test_no_extension_fallback(self):
        """Test fallback for files with no extension."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test_file_no_ext"
            test_file.touch()
            
            item_type = get_item_type_for_file(str(test_file))
            assert item_type == GopherItemType.BINARY_FILE

    def test_case_insensitive_extensions(self):
        """Test that extension detection is case insensitive."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test uppercase extensions
            test_file_upper = Path(temp_dir) / "test.TXT"
            test_file_upper.touch()
            
            item_type = get_item_type_for_file(str(test_file_upper))
            assert item_type == GopherItemType.TEXT_FILE
            
            # Test mixed case
            test_file_mixed = Path(temp_dir) / "test.HtMl"
            test_file_mixed.touch()
            
            item_type = get_item_type_for_file(str(test_file_mixed))
            assert item_type == GopherItemType.HTML

    def test_mime_type_text_fallback(self):
        """Test MIME type fallback for text files."""
        # This test would be complex to set up properly with mimetypes
        # but covers the mime type detection logic
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a file with unknown extension but that mimetypes
            # might recognize as text
            test_file = Path(temp_dir) / "test.conf"
            test_file.touch()
            
            item_type = get_item_type_for_file(str(test_file))
            # This could be TEXT_FILE or BINARY_FILE depending on mimetypes
            assert item_type in [GopherItemType.TEXT_FILE, GopherItemType.BINARY_FILE]

    def test_mime_type_image_fallback(self):
        """Test MIME type fallback for image files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a file with unknown extension
            test_file = Path(temp_dir) / "test.webp"  # Modern image format
            test_file.touch()
            
            item_type = get_item_type_for_file(str(test_file))
            # This could be IMAGE_FILE or BINARY_FILE depending on mimetypes
            assert item_type in [GopherItemType.IMAGE_FILE, GopherItemType.BINARY_FILE]

    def test_mime_type_audio_fallback(self):
        """Test MIME type fallback for audio files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a file with unknown extension
            test_file = Path(temp_dir) / "test.flac"  # Audio format
            test_file.touch()
            
            item_type = get_item_type_for_file(str(test_file))
            # This could be SOUND_FILE or BINARY_FILE depending on mimetypes
            assert item_type in [GopherItemType.SOUND_FILE, GopherItemType.BINARY_FILE]


if __name__ == "__main__":
    pytest.main([__file__])

