#!/usr/bin/env python3
"""
Tests for image handler plugin.
"""

import unittest
from unittest.mock import MagicMock, patch

from modern_gopher.core.types import GopherItem, GopherItemType
from modern_gopher.plugins.builtin.image_handler import ImageHandler


class TestImageHandler(unittest.TestCase):
    """Test ImageHandler plugin."""

    def setUp(self):
        """Set up test fixtures."""
        self.handler = ImageHandler()

    def test_metadata_properties(self):
        """Test metadata properties."""
        metadata = self.handler.metadata
        
        self.assertEqual(metadata.name, "image_handler")
        self.assertEqual(metadata.version, "1.0.0")
        self.assertEqual(metadata.author, "Modern Gopher Team")
        self.assertIn("image", metadata.description)
        self.assertEqual(metadata.supported_item_types, ["g", "I"])

    def test_get_supported_types(self):
        """Test get_supported_types method."""
        supported_types = self.handler.get_supported_types()
        
        self.assertIn(GopherItemType.GIF_IMAGE, supported_types)
        self.assertIn(GopherItemType.IMAGE_FILE, supported_types)
        self.assertEqual(len(supported_types), 2)

    def test_can_handle_supported_item_types(self):
        """Test can_handle with supported item types."""
        content = b"some image data"
        
        self.assertTrue(self.handler.can_handle(GopherItemType.GIF_IMAGE, content))
        self.assertTrue(self.handler.can_handle(GopherItemType.IMAGE_FILE, content))

    def test_can_handle_unsupported_item_types(self):
        """Test can_handle with unsupported item types."""
        content = b"some text data"
        
        self.assertFalse(self.handler.can_handle(GopherItemType.TEXT_FILE, content))
        self.assertFalse(self.handler.can_handle(GopherItemType.DIRECTORY, content))

    def test_can_handle_png_signature(self):
        """Test can_handle with PNG file signature."""
        png_content = b"\x89PNG\r\n\x1a\n" + b"fake png data"
        
        self.assertTrue(self.handler.can_handle(GopherItemType.TEXT_FILE, png_content))

    def test_can_handle_jpeg_signature(self):
        """Test can_handle with JPEG file signature."""
        jpeg_content = b"\xff\xd8\xff" + b"fake jpeg data"
        
        self.assertTrue(self.handler.can_handle(GopherItemType.TEXT_FILE, jpeg_content))

    def test_can_handle_gif87a_signature(self):
        """Test can_handle with GIF87a file signature."""
        gif_content = b"GIF87a" + b"fake gif data"
        
        self.assertTrue(self.handler.can_handle(GopherItemType.TEXT_FILE, gif_content))

    def test_can_handle_gif89a_signature(self):
        """Test can_handle with GIF89a file signature."""
        gif_content = b"GIF89a" + b"fake gif data"
        
        self.assertTrue(self.handler.can_handle(GopherItemType.TEXT_FILE, gif_content))

    def test_can_handle_bmp_signature(self):
        """Test can_handle with BMP file signature."""
        bmp_content = b"BM" + b"fake bmp data"
        
        self.assertTrue(self.handler.can_handle(GopherItemType.TEXT_FILE, bmp_content))

    def test_can_handle_webp_signature(self):
        """Test can_handle with WebP file signature."""
        webp_content = b"RIFF" + b"WEBP" + b"fake webp data"
        
        self.assertTrue(self.handler.can_handle(GopherItemType.TEXT_FILE, webp_content))

    def test_can_handle_short_content(self):
        """Test can_handle with content too short for signature detection."""
        short_content = b"short"
        
        self.assertFalse(self.handler.can_handle(GopherItemType.TEXT_FILE, short_content))

    def test_can_handle_string_content(self):
        """Test can_handle with string content."""
        string_content = "text content"
        
        self.assertFalse(self.handler.can_handle(GopherItemType.TEXT_FILE, string_content))

    def test_can_handle_no_matching_signature(self):
        """Test can_handle with content that doesn't match any signature."""
        unknown_content = b"unknown binary content here"
        
        self.assertFalse(self.handler.can_handle(GopherItemType.TEXT_FILE, unknown_content))

    def test_process_content_string_input(self):
        """Test process_content with string input."""
        content = "image data as string"
        item_type = GopherItemType.IMAGE_FILE
        
        display_text, metadata = self.handler.process_content(item_type, content)
        
        self.assertEqual(metadata["content_type"], "image")
        self.assertEqual(metadata["item_type"], "I")
        self.assertEqual(metadata["size_bytes"], len(content.encode("latin-1")))
        self.assertIn("[IMAGE:", display_text)

    def test_process_content_bytes_input(self):
        """Test process_content with bytes input."""
        content = b"image data as bytes"
        item_type = GopherItemType.GIF_IMAGE
        
        display_text, metadata = self.handler.process_content(item_type, content)
        
        self.assertEqual(metadata["content_type"], "image")
        self.assertEqual(metadata["item_type"], "g")
        self.assertEqual(metadata["size_bytes"], len(content))
        self.assertIn("[IMAGE:", display_text)

    def test_process_content_with_png_format(self):
        """Test process_content with PNG format detection."""
        png_content = b"\x89PNG\r\n\x1a\n" + b"fake png data"
        item_type = GopherItemType.IMAGE_FILE
        
        display_text, metadata = self.handler.process_content(item_type, png_content)
        
        self.assertEqual(metadata["image_format"], "PNG")
        self.assertIn("PNG", display_text)

    def test_process_content_with_jpeg_format(self):
        """Test process_content with JPEG format detection."""
        jpeg_content = b"\xff\xd8\xff" + b"fake jpeg data"
        item_type = GopherItemType.IMAGE_FILE
        
        display_text, metadata = self.handler.process_content(item_type, jpeg_content)
        
        self.assertEqual(metadata["image_format"], "JPEG")
        self.assertIn("JPEG", display_text)

    def test_process_content_with_gif_format(self):
        """Test process_content with GIF format detection."""
        gif_content = b"GIF89a" + b"fake gif data"
        item_type = GopherItemType.GIF_IMAGE
        
        display_text, metadata = self.handler.process_content(item_type, gif_content)
        
        self.assertEqual(metadata["image_format"], "GIF")
        self.assertIn("GIF", display_text)

    def test_process_content_with_bmp_format(self):
        """Test process_content with BMP format detection."""
        bmp_content = b"BM" + b"fake bmp data"
        item_type = GopherItemType.IMAGE_FILE
        
        display_text, metadata = self.handler.process_content(item_type, bmp_content)
        
        self.assertEqual(metadata["image_format"], "BMP")
        self.assertIn("BMP", display_text)

    def test_process_content_with_webp_format(self):
        """Test process_content with WebP format detection."""
        webp_content = b"RIFF" + b"WEBP" + b"fake webp data"
        item_type = GopherItemType.IMAGE_FILE
        
        display_text, metadata = self.handler.process_content(item_type, webp_content)
        
        self.assertEqual(metadata["image_format"], "WebP")
        self.assertIn("WebP", display_text)

    def test_process_content_with_ico_format(self):
        """Test process_content with ICO format detection."""
        ico_content = b"\x00\x00\x01\x00" + b"fake ico data"
        item_type = GopherItemType.IMAGE_FILE
        
        display_text, metadata = self.handler.process_content(item_type, ico_content)
        
        self.assertEqual(metadata["image_format"], "ICO")
        self.assertIn("ICO", display_text)

    def test_process_content_unknown_format(self):
        """Test process_content with unknown format."""
        unknown_content = b"unknown image format"
        item_type = GopherItemType.IMAGE_FILE
        
        display_text, metadata = self.handler.process_content(item_type, unknown_content)
        
        self.assertNotIn("image_format", metadata)
        self.assertIn("Unknown format", display_text)

    def test_process_content_with_png_dimensions(self):
        """Test process_content with PNG dimensions extraction."""
        # Create fake PNG header with dimensions 100x200
        png_header = b"\x89PNG\r\n\x1a\n"
        png_header += b"\x00" * 8  # IHDR chunk length and type
        png_header += b"\x00\x00\x00\x64"  # Width: 100
        png_header += b"\x00\x00\x00\xc8"  # Height: 200
        png_header += b"fake rest of png"
        
        display_text, metadata = self.handler.process_content(GopherItemType.IMAGE_FILE, png_header)
        
        self.assertEqual(metadata["width"], 100)
        self.assertEqual(metadata["height"], 200)
        self.assertEqual(metadata["dimensions"], "100x200")
        self.assertIn("100x200", display_text)

    def test_process_content_with_gif_dimensions(self):
        """Test process_content with GIF dimensions extraction."""
        # Create fake GIF header with dimensions 50x75
        gif_header = b"GIF89a"
        gif_header += b"\x32\x00"  # Width: 50 (little-endian)
        gif_header += b"\x4b\x00"  # Height: 75 (little-endian)
        gif_header += b"fake rest of gif"
        
        display_text, metadata = self.handler.process_content(GopherItemType.GIF_IMAGE, gif_header)
        
        self.assertEqual(metadata["width"], 50)
        self.assertEqual(metadata["height"], 75)
        self.assertEqual(metadata["dimensions"], "50x75")
        self.assertIn("50x75", display_text)

    def test_process_content_with_bmp_dimensions(self):
        """Test process_content with BMP dimensions extraction."""
        # Create fake BMP header with dimensions 150x125
        bmp_header = b"BM"
        bmp_header += b"\x00" * 16  # Skip to width/height offset
        bmp_header += b"\x96\x00\x00\x00"  # Width: 150 (little-endian)
        bmp_header += b"\x7d\x00\x00\x00"  # Height: 125 (little-endian)
        bmp_header += b"fake rest of bmp"
        
        display_text, metadata = self.handler.process_content(GopherItemType.IMAGE_FILE, bmp_header)
        
        self.assertEqual(metadata["width"], 150)
        self.assertEqual(metadata["height"], 125)
        self.assertEqual(metadata["dimensions"], "150x125")
        self.assertIn("150x125", display_text)

    @patch('modern_gopher.plugins.builtin.image_handler.logger')
    def test_process_content_dimension_extraction_error(self, mock_logger):
        """Test process_content when dimension extraction fails."""
        # Create PNG header that's too short for dimension extraction
        short_png = b"\x89PNG\r\n\x1a\n" + b"short"
        
        display_text, metadata = self.handler.process_content(GopherItemType.IMAGE_FILE, short_png)
        
        self.assertEqual(metadata["image_format"], "PNG")
        self.assertNotIn("width", metadata)
        self.assertNotIn("height", metadata)
        self.assertNotIn("dimensions", metadata)
        mock_logger.debug.assert_called()

    def test_process_content_with_gopher_item(self):
        """Test process_content with GopherItem provided."""
        content = b"image data"
        item = GopherItem(
            item_type=GopherItemType.IMAGE_FILE,
            display_string="test.png",
            selector="/images/test.png",
            host="example.com",
            port=70
        )
        
        display_text, metadata = self.handler.process_content(
            GopherItemType.IMAGE_FILE, content, item
        )
        
        self.assertIn("test.png", display_text)
        self.assertIn("example.com:70", display_text)
        self.assertIn("/images/test.png", display_text)

    def test_format_file_size_bytes(self):
        """Test _format_file_size with bytes."""
        result = self.handler._format_file_size(512)
        self.assertEqual(result, "512 B")

    def test_format_file_size_kilobytes(self):
        """Test _format_file_size with kilobytes."""
        result = self.handler._format_file_size(1536)  # 1.5 KB
        self.assertEqual(result, "1.5 KB")

    def test_format_file_size_megabytes(self):
        """Test _format_file_size with megabytes."""
        result = self.handler._format_file_size(2097152)  # 2.0 MB
        self.assertEqual(result, "2.0 MB")

    def test_format_file_size_gigabytes(self):
        """Test _format_file_size with gigabytes."""
        result = self.handler._format_file_size(3221225472)  # 3.0 GB
        self.assertEqual(result, "3.0 GB")

    def test_detect_image_format_png(self):
        """Test _detect_image_format with PNG."""
        png_content = b"\x89PNG\r\n\x1a\n" + b"data"
        result = self.handler._detect_image_format(png_content)
        self.assertEqual(result, "PNG")

    def test_detect_image_format_jpeg(self):
        """Test _detect_image_format with JPEG."""
        jpeg_content = b"\xff\xd8\xff" + b"data"
        result = self.handler._detect_image_format(jpeg_content)
        self.assertEqual(result, "JPEG")

    def test_detect_image_format_gif87a(self):
        """Test _detect_image_format with GIF87a."""
        gif_content = b"GIF87a" + b"data"
        result = self.handler._detect_image_format(gif_content)
        self.assertEqual(result, "GIF")

    def test_detect_image_format_gif89a(self):
        """Test _detect_image_format with GIF89a."""
        gif_content = b"GIF89a" + b"data"
        result = self.handler._detect_image_format(gif_content)
        self.assertEqual(result, "GIF")

    def test_detect_image_format_bmp(self):
        """Test _detect_image_format with BMP."""
        bmp_content = b"BM" + b"data"
        result = self.handler._detect_image_format(bmp_content)
        self.assertEqual(result, "BMP")

    def test_detect_image_format_webp(self):
        """Test _detect_image_format with WebP."""
        webp_content = b"RIFF" + b"WEBP" + b"data"
        result = self.handler._detect_image_format(webp_content)
        self.assertEqual(result, "WebP")

    def test_detect_image_format_ico_type1(self):
        """Test _detect_image_format with ICO type 1."""
        ico_content = b"\x00\x00\x01\x00" + b"data"
        result = self.handler._detect_image_format(ico_content)
        self.assertEqual(result, "ICO")

    def test_detect_image_format_ico_type2(self):
        """Test _detect_image_format with ICO type 2."""
        ico_content = b"\x00\x00\x02\x00" + b"data"
        result = self.handler._detect_image_format(ico_content)
        self.assertEqual(result, "ICO")

    def test_detect_image_format_unknown(self):
        """Test _detect_image_format with unknown format."""
        unknown_content = b"unknown format"
        result = self.handler._detect_image_format(unknown_content)
        self.assertIsNone(result)

    def test_get_image_dimensions_png_success(self):
        """Test _get_image_dimensions with valid PNG."""
        # Create proper PNG header
        png_content = b"\x89PNG\r\n\x1a\n"
        png_content += b"\x00" * 8  # Skip to width/height
        png_content += b"\x00\x00\x01\x00"  # Width: 256
        png_content += b"\x00\x00\x02\x00"  # Height: 512
        
        width, height = self.handler._get_image_dimensions(png_content, "PNG")
        self.assertEqual(width, 256)
        self.assertEqual(height, 512)

    def test_get_image_dimensions_gif_success(self):
        """Test _get_image_dimensions with valid GIF."""
        gif_content = b"GIF89a"
        gif_content += b"\x80\x00"  # Width: 128 (little-endian)
        gif_content += b"\x40\x01"  # Height: 320 (little-endian)
        
        width, height = self.handler._get_image_dimensions(gif_content, "GIF")
        self.assertEqual(width, 128)
        self.assertEqual(height, 320)

    def test_get_image_dimensions_bmp_success(self):
        """Test _get_image_dimensions with valid BMP."""
        bmp_content = b"BM"
        bmp_content += b"\x00" * 16  # Skip to width/height
        bmp_content += b"\x00\x01\x00\x00"  # Width: 256 (little-endian)
        bmp_content += b"\x00\x02\x00\x00"  # Height: 512 (little-endian)
        
        width, height = self.handler._get_image_dimensions(bmp_content, "BMP")
        self.assertEqual(width, 256)
        self.assertEqual(height, 512)

    def test_get_image_dimensions_unsupported_format(self):
        """Test _get_image_dimensions with unsupported format."""
        content = b"some content"
        width, height = self.handler._get_image_dimensions(content, "TIFF")
        self.assertIsNone(width)
        self.assertIsNone(height)

    def test_get_image_dimensions_too_short(self):
        """Test _get_image_dimensions with content too short."""
        short_content = b"short"
        width, height = self.handler._get_image_dimensions(short_content, "PNG")
        self.assertIsNone(width)
        self.assertIsNone(height)

    @patch('modern_gopher.plugins.builtin.image_handler.logger')
    def test_get_image_dimensions_exception_handling(self, mock_logger):
        """Test _get_image_dimensions with exception during parsing."""
        # Create content that will cause an exception
        malformed_content = b"\x89PNG\r\n\x1a\n" + b"x" * 20  # Invalid PNG data
        
        width, height = self.handler._get_image_dimensions(malformed_content, "PNG")
        
        self.assertIsNone(width)
        self.assertIsNone(height)
        mock_logger.debug.assert_called()

    def test_get_priority(self):
        """Test get_priority method."""
        priority = self.handler.get_priority()
        self.assertEqual(priority, 100)


class TestImageHandlerIntegration(unittest.TestCase):
    """Integration tests for ImageHandler."""

    def setUp(self):
        """Set up test fixtures."""
        self.handler = ImageHandler()

    def test_full_png_processing_workflow(self):
        """Test complete PNG processing workflow."""
        # Create a minimal valid PNG header
        png_content = b"\x89PNG\r\n\x1a\n"
        png_content += b"\x00\x00\x00\x0D"  # IHDR chunk length
        png_content += b"IHDR"  # IHDR chunk type
        png_content += b"\x00\x00\x01\x90"  # Width: 400
        png_content += b"\x00\x00\x01\x2C"  # Height: 300
        png_content += b"\x08\x02\x00\x00\x00"  # bit depth, color type, etc.
        png_content += b"fake rest of png data"
        
        item = GopherItem(
            item_type=GopherItemType.IMAGE_FILE,
            display_string="test.png",
            selector="/test.png",
            host="example.com",
            port=70
        )
        
        # Test can_handle
        self.assertTrue(self.handler.can_handle(GopherItemType.IMAGE_FILE, png_content))
        
        # Test process_content
        display_text, metadata = self.handler.process_content(
            GopherItemType.IMAGE_FILE, png_content, item
        )
        
        # Verify complete processing
        self.assertEqual(metadata["content_type"], "image")
        self.assertEqual(metadata["image_format"], "PNG")
        self.assertEqual(metadata["width"], 400)
        self.assertEqual(metadata["height"], 300)
        self.assertEqual(metadata["dimensions"], "400x300")
        
        self.assertIn("PNG", display_text)
        self.assertIn("400x300", display_text)
        self.assertIn("test.png", display_text)
        self.assertIn("example.com:70", display_text)

    def test_signature_detection_priority(self):
        """Test that signature detection works even for unsupported item types."""
        jpeg_content = b"\xff\xd8\xff" + b"fake jpeg data"
        
        # Even though it's marked as text, signature detection should identify it as image
        self.assertTrue(self.handler.can_handle(GopherItemType.TEXT_FILE, jpeg_content))
        
        display_text, metadata = self.handler.process_content(
            GopherItemType.TEXT_FILE, jpeg_content
        )
        
        self.assertEqual(metadata["image_format"], "JPEG")
        self.assertIn("JPEG", display_text)


if __name__ == "__main__":
    unittest.main()

