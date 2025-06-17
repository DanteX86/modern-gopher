"""
HTML Content Renderer using Beautiful Soup

This module provides functionality to render HTML content in a terminal-friendly format
using Beautiful Soup for parsing and the Rich library for terminal formatting.
"""

from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup, Tag, NavigableString
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.rule import Rule
import re
import logging

logger = logging.getLogger(__name__)


class HTMLRenderer:
    """
    Renders HTML content for terminal display using Beautiful Soup and Rich.
    """
    
    def __init__(self, console: Optional[Console] = None):
        """
        Initialize the HTML renderer.
        
        Args:
            console: Optional Rich console instance. If None, creates a new one.
        """
        self.console = console or Console()
        self.links: List[Dict[str, str]] = []
        self.images: List[Dict[str, str]] = []
        
    def render_html(self, html_content: str, extract_links: bool = True) -> Tuple[str, List[Dict[str, str]]]:
        """
        Render HTML content to terminal-friendly text.
        
        Args:
            html_content: Raw HTML content string
            extract_links: Whether to extract and enumerate links
            
        Returns:
            Tuple of (rendered_text, links_list)
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Reset link and image counters
            self.links = []
            self.images = []
            
            # Extract and process different HTML elements
            rendered_parts = []
            
            # Handle title
            title = soup.find('title')
            if title:
                title_text = self._clean_text(title.get_text())
                rendered_parts.append(f"📄 {title_text}")
                rendered_parts.append("=" * len(f"📄 {title_text}"))
                rendered_parts.append("")
            
            # Process body content
            body = soup.find('body') or soup
            rendered_content = self._render_element(body, extract_links)
            rendered_parts.append(rendered_content)
            
            # Add links section if any links were found
            if extract_links and self.links:
                rendered_parts.append("")
                rendered_parts.append("🔗 Links:")
                rendered_parts.append("-" * 10)
                for i, link in enumerate(self.links, 1):
                    text = link['text'] or link['url']
                    rendered_parts.append(f"[{i}] {text}")
                    rendered_parts.append(f"    → {link['url']}")
                    
            # Add images section if any images were found
            if self.images:
                rendered_parts.append("")
                rendered_parts.append("🖼️  Images:")
                rendered_parts.append("-" * 11)
                for i, img in enumerate(self.images, 1):
                    alt_text = img.get('alt', 'Image')
                    rendered_parts.append(f"[IMG{i}] {alt_text}")
                    rendered_parts.append(f"        → {img['src']}")
            
            return "\n".join(rendered_parts), self.links
            
        except Exception as e:
            logger.error(f"Error rendering HTML: {e}")
            return f"Error rendering HTML content: {e}", []
    
    def _render_element(self, element, extract_links: bool = True) -> str:
        """
        Recursively render an HTML element and its children.
        
        Args:
            element: BeautifulSoup element to render
            extract_links: Whether to extract and enumerate links
            
        Returns:
            Rendered text string
        """
        if isinstance(element, NavigableString):
            return self._clean_text(str(element))
        
        if not isinstance(element, Tag):
            return ""
        
        tag_name = element.name.lower()
        text_parts = []
        
        # Handle specific HTML tags
        if tag_name in ['script', 'style', 'meta', 'link', 'head']:
            # Skip these elements entirely
            return ""
        
        elif tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(tag_name[1])
            text = self._get_element_text(element, extract_links)
            if text.strip():
                if level == 1:
                    text_parts.append(f"\n{'=' * len(text)}")
                    text_parts.append(f"🏷️  {text}")
                    text_parts.append(f"{'=' * len(text)}\n")
                elif level == 2:
                    text_parts.append(f"\n📌 {text}")
                    text_parts.append(f"{'-' * len(text)}\n")
                else:
                    text_parts.append(f"\n{'#' * level} {text}\n")
        
        elif tag_name == 'p':
            text = self._get_element_text(element, extract_links)
            if text.strip():
                text_parts.append(f"\n{text}\n")
        
        elif tag_name == 'a':
            href = element.get('href', '')
            text = self._get_element_text(element, False)  # Don't extract nested links
            if extract_links and href:
                self.links.append({
                    'url': href,
                    'text': text,
                    'title': element.get('title', '')
                })
                link_num = len(self.links)
                text_parts.append(f"{text}[{link_num}]")
            else:
                text_parts.append(text)
        
        elif tag_name == 'img':
            src = element.get('src', '')
            alt = element.get('alt', 'Image')
            if src:
                self.images.append({
                    'src': src,
                    'alt': alt,
                    'title': element.get('title', '')
                })
                img_num = len(self.images)
                text_parts.append(f"[IMG{img_num}:{alt}]")
            else:
                text_parts.append(f"[{alt}]")
        
        elif tag_name in ['ul', 'ol']:
            text_parts.append("\n")
            for i, li in enumerate(element.find_all('li', recursive=False), 1):
                li_text = self._get_element_text(li, extract_links)
                if li_text.strip():
                    if tag_name == 'ol':
                        text_parts.append(f"  {i}. {li_text}")
                    else:
                        text_parts.append(f"  • {li_text}")
            text_parts.append("\n")
        
        elif tag_name == 'li':
            # Handle individual list items (when not in ul/ol context)
            text = self._get_element_text(element, extract_links)
            if text.strip():
                text_parts.append(f"• {text}")
        
        elif tag_name in ['table']:
            text_parts.append(self._render_table(element, extract_links))
        
        elif tag_name in ['blockquote']:
            text = self._get_element_text(element, extract_links)
            if text.strip():
                quoted_lines = [f"  > {line}" for line in text.strip().split('\n')]
                text_parts.append("\n" + "\n".join(quoted_lines) + "\n")
        
        elif tag_name in ['br']:
            text_parts.append("\n")
        
        elif tag_name in ['hr']:
            text_parts.append("\n" + "-" * 50 + "\n")
        
        elif tag_name in ['strong', 'b']:
            text = self._get_element_text(element, extract_links)
            text_parts.append(f"**{text}**")
        
        elif tag_name in ['em', 'i']:
            text = self._get_element_text(element, extract_links)
            text_parts.append(f"*{text}*")
        
        elif tag_name in ['code']:
            text = self._get_element_text(element, extract_links)
            text_parts.append(f"`{text}`")
        
        elif tag_name in ['pre']:
            text = self._get_element_text(element, extract_links, preserve_whitespace=True)
            text_parts.append(f"\n```\n{text}\n```\n")
        
        else:
            # Default: just render children
            for child in element.children:
                child_text = self._render_element(child, extract_links)
                if child_text:
                    text_parts.append(child_text)
        
        return "".join(text_parts)
    
    def _get_element_text(self, element, extract_links: bool = True, preserve_whitespace: bool = False) -> str:
        """
        Get text content from an element, processing children appropriately.
        
        Args:
            element: BeautifulSoup element
            extract_links: Whether to extract and enumerate links
            preserve_whitespace: Whether to preserve whitespace formatting
            
        Returns:
            Text content string
        """
        text_parts = []
        for child in element.children:
            child_text = self._render_element(child, extract_links)
            if child_text:
                text_parts.append(child_text)
        
        text = "".join(text_parts)
        if not preserve_whitespace:
            text = self._clean_text(text)
        return text
    
    def _render_table(self, table_element, extract_links: bool = True) -> str:
        """
        Render an HTML table in a terminal-friendly format.
        
        Args:
            table_element: BeautifulSoup table element
            extract_links: Whether to extract and enumerate links
            
        Returns:
            Formatted table string
        """
        rows = []
        
        # Process table rows
        for tr in table_element.find_all('tr'):
            cells = []
            for cell in tr.find_all(['td', 'th']):
                cell_text = self._get_element_text(cell, extract_links)
                cells.append(cell_text.strip() or " ")
            if cells:
                rows.append(cells)
        
        if not rows:
            return ""
        
        # Calculate column widths
        max_cols = max(len(row) for row in rows) if rows else 0
        col_widths = [0] * max_cols
        
        for row in rows:
            for i, cell in enumerate(row):
                if i < max_cols:
                    col_widths[i] = max(col_widths[i], len(cell))
        
        # Render table
        table_lines = []
        table_lines.append("\n┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐")
        
        for i, row in enumerate(rows):
            # Pad row to max columns
            padded_row = row + [""] * (max_cols - len(row))
            
            line = "│"
            for j, (cell, width) in enumerate(zip(padded_row, col_widths)):
                line += f" {cell.ljust(width)} │"
            table_lines.append(line)
            
            # Add separator after header row
            if i == 0 and len(rows) > 1:
                table_lines.append("├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤")
        
        table_lines.append("└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘\n")
        
        return "\n".join(table_lines)
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text content.
        
        Args:
            text: Raw text string
            
        Returns:
            Cleaned text string
        """
        if not text:
            return ""
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def extract_links_only(self, html_content: str) -> List[Dict[str, str]]:
        """
        Extract only links from HTML content without rendering.
        
        Args:
            html_content: Raw HTML content string
            
        Returns:
            List of link dictionaries
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            links = []
            
            for link in soup.find_all('a', href=True):
                links.append({
                    'url': link['href'],
                    'text': self._clean_text(link.get_text()),
                    'title': link.get('title', '')
                })
            
            return links
            
        except Exception as e:
            logger.error(f"Error extracting links from HTML: {e}")
            return []


def render_html_to_text(html_content: str, extract_links: bool = True) -> Tuple[str, List[Dict[str, str]]]:
    """
    Convenience function to render HTML content to text.
    
    Args:
        html_content: Raw HTML content string
        extract_links: Whether to extract and enumerate links
        
    Returns:
        Tuple of (rendered_text, links_list)
    """
    renderer = HTMLRenderer()
    return renderer.render_html(html_content, extract_links)

