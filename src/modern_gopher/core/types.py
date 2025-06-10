"""
Gopher item types and their handlers.

This module defines the different Gopher item types as specified in RFC 1436
and provides functions for handling each type.
"""

from enum import Enum
from typing import Dict, Optional, List, Tuple, NamedTuple
import mimetypes
import os
import logging

logger = logging.getLogger(__name__)


class GopherItemType(Enum):
    """Enum representing Gopher item types as specified in RFC 1436."""
    
    # Standard Gopher item types
    TEXT_FILE = '0'
    DIRECTORY = '1'
    CSO_PHONE_BOOK = '2'
    ERROR = '3'
    BINHEX_FILE = '4'
    DOS_BINARY = '5'
    UUENCODED_FILE = '6'
    SEARCH_SERVER = '7'
    TELNET = '8'
    BINARY_FILE = '9'
    REDUNDANT_SERVER = '+'
    
    # Gopher+ and commonly used extensions
    TN3270_SESSION = 'T'
    GIF_IMAGE = 'g'
    IMAGE_FILE = 'I'
    SOUND_FILE = 's'
    
    # Additional item types that are common in modern Gopher implementations
    HTML = 'h'
    INFORMATION = 'i'
    DOCUMENT = 'd'
    PDF = 'P'
    CALENDAR = 'c'
    
    @classmethod
    def from_char(cls, char: str) -> Optional['GopherItemType']:
        """
        Get the GopherItemType corresponding to a character identifier.
        
        Args:
            char: The single character identifier
            
        Returns:
            The matching GopherItemType or None if not found
        """
        try:
            return next(item for item in cls if item.value == char)
        except StopIteration:
            return None
    
    @property
    def is_text(self) -> bool:
        """
        Check if this item type represents textual content.
        
        Returns:
            True if the item contains text content, False otherwise
        """
        return self in (self.TEXT_FILE, self.DIRECTORY, 
                       self.ERROR, self.INFORMATION)
    
    @property
    def is_binary(self) -> bool:
        """
        Check if this item type represents binary content.
        
        Returns:
            True if the item contains binary content, False otherwise
        """
        return self in (self.BINHEX_FILE, self.DOS_BINARY, 
                       self.UUENCODED_FILE, self.BINARY_FILE,
                       self.GIF_IMAGE, self.IMAGE_FILE, self.SOUND_FILE,
                       self.PDF)
    
    @property
    def is_interactive(self) -> bool:
        """
        Check if this item type represents an interactive service.
        
        Returns:
            True if the item is interactive, False otherwise
        """
        return self in (self.CSO_PHONE_BOOK, self.SEARCH_SERVER, 
                       self.TELNET, self.TN3270_SESSION)
    
    @property
    def mime_type(self) -> str:
        """
        Get the MIME type for this Gopher item type.
        
        Returns:
            A string containing the MIME type
        """
        mime_map = {
            self.TEXT_FILE: 'text/plain',
            self.DIRECTORY: 'text/plain',
            self.ERROR: 'text/plain',
            self.INFORMATION: 'text/plain',
            self.HTML: 'text/html',
            self.BINHEX_FILE: 'application/mac-binhex40',
            self.DOS_BINARY: 'application/octet-stream',
            self.UUENCODED_FILE: 'text/x-uuencode',
            self.BINARY_FILE: 'application/octet-stream',
            self.GIF_IMAGE: 'image/gif',
            self.IMAGE_FILE: 'image/unknown',
            self.SOUND_FILE: 'audio/unknown',
            self.PDF: 'application/pdf',
            self.DOCUMENT: 'text/plain',
            self.CALENDAR: 'text/calendar',
        }
        return mime_map.get(self, 'application/octet-stream')
    
    @property
    def extension(self) -> str:
        """
        Get a default file extension for this Gopher item type.
        
        Returns:
            A string containing a file extension (with dot)
        """
        ext_map = {
            self.TEXT_FILE: '.txt',
            self.DIRECTORY: '.txt',
            self.ERROR: '.txt',
            self.INFORMATION: '.txt',
            self.HTML: '.html',
            self.BINHEX_FILE: '.hqx',
            self.DOS_BINARY: '.bin',
            self.UUENCODED_FILE: '.uue',
            self.BINARY_FILE: '.bin',
            self.GIF_IMAGE: '.gif',
            self.IMAGE_FILE: '.img',
            self.SOUND_FILE: '.snd',
            self.PDF: '.pdf',
            self.DOCUMENT: '.doc',
            self.CALENDAR: '.ics',
        }
        return ext_map.get(self, '.bin')
    
    @property
    def display_name(self) -> str:
        """
        Get a human-readable display name for this item type.
        
        Returns:
            A string containing the display name
        """
        name_map = {
            self.TEXT_FILE: 'Text File',
            self.DIRECTORY: 'Directory',
            self.CSO_PHONE_BOOK: 'CSO Phone Book',
            self.ERROR: 'Error',
            self.BINHEX_FILE: 'BinHex File',
            self.DOS_BINARY: 'DOS Binary',
            self.UUENCODED_FILE: 'UUEncoded File',
            self.SEARCH_SERVER: 'Search Server',
            self.TELNET: 'Telnet Session',
            self.BINARY_FILE: 'Binary File',
            self.REDUNDANT_SERVER: 'Redundant Server',
            self.TN3270_SESSION: 'TN3270 Session',
            self.GIF_IMAGE: 'GIF Image',
            self.IMAGE_FILE: 'Image File',
            self.SOUND_FILE: 'Sound File',
            self.HTML: 'HTML File',
            self.INFORMATION: 'Information',
            self.DOCUMENT: 'Document',
            self.PDF: 'PDF Document',
            self.CALENDAR: 'Calendar',
        }
        return name_map.get(self, f'Unknown Type ({self.value})')


class GopherItem(NamedTuple):
    """
    Represents a single item in a Gopher menu (directory listing).
    
    According to RFC 1436, a Gopher menu item consists of:
    - Item type (single character)
    - Display string (user-visible label)
    - Selector (Gopher path)
    - Host (server hostname)
    - Port (server port)
    """
    item_type: GopherItemType
    display_string: str
    selector: str
    host: str
    port: int
    
    @classmethod
    def from_menu_line(cls, line: str) -> Optional['GopherItem']:
        """
        Parse a line from a Gopher menu into a GopherItem.
        
        Args:
            line: A line from a Gopher menu response
            
        Returns:
            A GopherItem if the line is valid, None otherwise
        """
        # Skip empty lines or lines not starting with a valid item type
        if not line or line == '.':
            return None
        
        parts = line.split('\t')
        if len(parts) < 4:
            return None
        
        # First character of the first part is the item type
        # The rest of the first part is the display string
        if not parts[0]:
            return None
            
        type_char = parts[0][0]
        display_string = parts[0][1:].strip()
        
        # The remaining parts are selector, host, and port
        selector = parts[1]
        host = parts[2]
        
        # Port can be empty, in which case default to 70
        if len(parts) > 3 and parts[3]:
            try:
                port = int(parts[3])
            except ValueError:
                port = 70
        else:
            port = 70
            
        # Get the item type from the character
        item_type = GopherItemType.from_char(type_char)
        if item_type is None:
            # Use binary file as default for unknown types
            item_type = GopherItemType.BINARY_FILE
            
        return cls(
            item_type=item_type,
            display_string=display_string,
            selector=selector,
            host=host,
            port=port
        )
    
    def to_menu_line(self) -> str:
        """
        Convert this GopherItem back to a Gopher menu line.
        
        Returns:
            A formatted line suitable for inclusion in a Gopher menu
        """
        return f"{self.item_type.value}{self.display_string}\t{self.selector}\t{self.host}\t{self.port}"


def parse_gopher_directory(data: bytes) -> List[GopherItem]:
    """
    Parse a Gopher directory (menu) response into a list of GopherItems.
    
    Args:
        data: The raw bytes received from a Gopher server for a directory
        
    Returns:
        A list of GopherItem objects parsed from the data
    """
    items = []
    
    # Split the data into lines and process each line
    try:
        # Try UTF-8 first, as it's most common nowadays
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        # Fall back to Latin-1, which can't fail
        text = data.decode('latin-1')
        
    lines = text.splitlines()
    
    for line in lines:
        # End of menu is marked by a line containing just a dot
        if line == '.':
            break
            
        item = GopherItem.from_menu_line(line)
        if item:
            items.append(item)
            
    return items


def is_item_type_text(item_type: GopherItemType) -> bool:
    """
    Check if a Gopher item type represents text content.
    
    Args:
        item_type: The GopherItemType to check
        
    Returns:
        True if the item type represents text content, False otherwise
    """
    return item_type.is_text


def is_item_type_binary(item_type: GopherItemType) -> bool:
    """
    Check if a Gopher item type represents binary content.
    
    Args:
        item_type: The GopherItemType to check
        
    Returns:
        True if the item type represents binary content, False otherwise
    """
    return item_type.is_binary


def is_item_type_interactive(item_type: GopherItemType) -> bool:
    """
    Check if a Gopher item type represents an interactive service.
    
    Args:
        item_type: The GopherItemType to check
        
    Returns:
        True if the item type represents an interactive service, False otherwise
    """
    return item_type.is_interactive


def get_item_type_for_file(filename: str) -> GopherItemType:
    """
    Determine the appropriate Gopher item type for a local file.
    
    Args:
        filename: Path to the file to check
        
    Returns:
        The most appropriate GopherItemType for the file
    """
    if os.path.isdir(filename):
        return GopherItemType.DIRECTORY
        
    # Check file extension
    _, ext = os.path.splitext(filename.lower())
    
    # Map common extensions to Gopher types
    ext_map = {
        '.txt': GopherItemType.TEXT_FILE,
        '.text': GopherItemType.TEXT_FILE,
        '.md': GopherItemType.TEXT_FILE,
        '.html': GopherItemType.HTML,
        '.htm': GopherItemType.HTML,
        '.gif': GopherItemType.GIF_IMAGE,
        '.jpg': GopherItemType.IMAGE_FILE,
        '.jpeg': GopherItemType.IMAGE_FILE,
        '.png': GopherItemType.IMAGE_FILE,
        '.pdf': GopherItemType.PDF,
        '.wav': GopherItemType.SOUND_FILE,
        '.mp3': GopherItemType.SOUND_FILE,
        '.ogg': GopherItemType.SOUND_FILE,
        '.doc': GopherItemType.DOCUMENT,
        '.ics': GopherItemType.CALENDAR,
    }
    
    if ext in ext_map:
        return ext_map[ext]
    
    # Fall back to MIME type detection
    mime_type, _ = mimetypes.guess_type(filename)
    
    if mime_type:
        if mime_type.startswith('text/'):
            return GopherItemType.TEXT_FILE
        elif mime_type.startswith('image/'):
            return GopherItemType.IMAGE_FILE
        elif mime_type.startswith('audio/'):
            return GopherItemType.SOUND_FILE
        elif mime_type == 'application/pdf':
            return GopherItemType.PDF
    
    # Default to binary for unknown types
    return GopherItemType.BINARY_FILE

