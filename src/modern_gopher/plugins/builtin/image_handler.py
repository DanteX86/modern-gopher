"""
Image item type handler plugin.

This plugin handles image files and provides metadata about them.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from modern_gopher.core.types import GopherItem, GopherItemType

from ..base import ItemTypeHandler, PluginMetadata

logger = logging.getLogger(__name__)


class ImageHandler(ItemTypeHandler):
    """Plugin that handles image files."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="image_handler",
            version="1.0.0",
            author="Modern Gopher Team",
            description="Handles image files and provides metadata",
            supported_item_types=["g", "I"],  # GIF and Image types
        )

    def get_supported_types(self) -> List[GopherItemType]:
        """Return supported image types."""
        return [GopherItemType.GIF_IMAGE, GopherItemType.IMAGE_FILE]

    def can_handle(self, item_type: GopherItemType, content: Union[str, bytes]) -> bool:
        """Check if this handler can process the content."""
        if item_type in self.get_supported_types():
            return True

        # Check for binary content that might be an image
        if isinstance(content, bytes) and len(content) > 10:
            # Check common image file signatures
            signatures = {
                b"\x89PNG\r\n\x1a\n": "PNG",
                b"\xff\xd8\xff": "JPEG",
                b"GIF87a": "GIF87a",
                b"GIF89a": "GIF89a",
                b"BM": "BMP",
                b"RIFF": "WebP",  # Actually need to check further for WebP
            }

            for signature in signatures:
                if content.startswith(signature):
                    return True

        return False

    def process_content(
        self,
        item_type: GopherItemType,
        content: Union[str, bytes],
        item: Optional[GopherItem] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """Process image content and return metadata."""
        if isinstance(content, str):
            content = content.encode("latin-1")  # Convert back to bytes

        metadata = {
            "content_type": "image",
            "item_type": item_type.value,
            "size_bytes": len(content),
        }

        # Detect image format
        image_format = self._detect_image_format(content)
        if image_format:
            metadata["image_format"] = image_format

        # Try to get image dimensions if possible
        try:
            width, height = self._get_image_dimensions(content, image_format)
            if width and height:
                metadata["width"] = width
                metadata["height"] = height
                metadata["dimensions"] = f"{width}x{height}"
        except Exception as e:
            # Unable to extract image dimensions, continue without them
            logger.debug(f"Could not extract image dimensions: {e}")

        # Create user-friendly display
        display_text = f"[IMAGE: {image_format or 'Unknown format'}]"
        if "dimensions" in metadata:
            display_text += f" {metadata['dimensions']}"
        display_text += f" ({self._format_file_size(len(content))})"

        if item:
            display_text += f"\n\nImage: {item.display_string}"
            display_text += f"\nLocation: {
                item.host}:{
                item.port}{
                item.selector}"

        display_text += (
            "\n\nThis is a binary image file. "
            "To view it, save it to disk and open with an image viewer."
        )

        return display_text, metadata

    def _detect_image_format(self, content: bytes) -> Optional[str]:
        """Detect image format from content."""
        if content.startswith(b"\x89PNG\r\n\x1a\n"):
            return "PNG"
        elif content.startswith(b"\xff\xd8\xff"):
            return "JPEG"
        elif content.startswith(b"GIF87a") or content.startswith(b"GIF89a"):
            return "GIF"
        elif content.startswith(b"BM"):
            return "BMP"
        elif content.startswith(b"RIFF") and b"WEBP" in content[:12]:
            return "WebP"
        elif content.startswith(b"\x00\x00\x01\x00") or content.startswith(b"\x00\x00\x02\x00"):
            return "ICO"
        return None

    def _get_image_dimensions(
        self, content: bytes, image_format: str
    ) -> Tuple[Optional[int], Optional[int]]:
        """Get image dimensions from content (basic implementation)."""
        try:
            if image_format == "PNG" and len(content) > 24:
                # PNG width and height are at bytes 16-23
                width = int.from_bytes(content[16:20], "big")
                height = int.from_bytes(content[20:24], "big")
                return width, height

            elif image_format == "GIF" and len(content) > 10:
                # GIF width and height are at bytes 6-9 (little-endian)
                width = int.from_bytes(content[6:8], "little")
                height = int.from_bytes(content[8:10], "little")
                return width, height

            elif image_format == "BMP" and len(content) > 26:
                # BMP width and height are at bytes 18-25 (little-endian)
                width = int.from_bytes(content[18:22], "little")
                height = int.from_bytes(content[22:26], "little")
                return width, height

        except Exception as e:
            # Unable to extract dimensions from this format
            logger.debug(f"Could not parse {image_format} dimensions: {e}")

        return None, None

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    def get_priority(self) -> int:
        """High priority for image handling."""
        return 100
