#!/usr/bin/env python3
"""
Tests for HTML content rendering functionality.

This module tests the Beautiful Soup HTML renderer integration
in the Modern Gopher browser.
"""

import os
import sys
import unittest

from modern_gopher.content.html_renderer import HTMLRenderer
from modern_gopher.content.html_renderer import render_html_to_text

# Add the src directory to the path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestHTMLRenderer(unittest.TestCase):
    """Test cases for the HTMLRenderer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.renderer = HTMLRenderer()

    def test_renderer_initialization(self):
        """Test HTMLRenderer initialization."""
        self.assertIsNotNone(self.renderer.console)
        self.assertEqual(self.renderer.links, [])
        self.assertEqual(self.renderer.images, [])

    def test_simple_html_rendering(self):
        """Test rendering of simple HTML content."""
        html = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Hello World</h1>
                <p>This is a test paragraph.</p>
            </body>
        </html>
        """

        rendered, links = self.renderer.render_html(html)

        # Check that content is rendered
        self.assertIn("📄 Test Page", rendered)
        self.assertIn("🏷️  Hello World", rendered)
        self.assertIn("This is a test paragraph.", rendered)
        self.assertEqual(links, [])

    def test_html_with_links(self):
        """Test HTML rendering with link extraction."""
        html = """
        <html>
            <body>
                <h1>Links Test</h1>
                <p>Visit <a href="gopher://example.com">Example Gopher</a> or
                <a href="https://web.example.com" title="Web Site">Example Web</a>.</p>
            </body>
        </html>
        """

        rendered, links = self.renderer.render_html(html)

        # Check link extraction
        self.assertEqual(len(links), 2)
        self.assertEqual(links[0]['url'], 'gopher://example.com')
        self.assertEqual(links[0]['text'], 'Example Gopher')
        self.assertEqual(links[1]['url'], 'https://web.example.com')
        self.assertEqual(links[1]['text'], 'Example Web')
        self.assertEqual(links[1]['title'], 'Web Site')

        # Check link numbering in rendered text
        self.assertIn("Example Gopher[1]", rendered)
        self.assertIn("Example Web[2]", rendered)
        self.assertIn("🔗 Links:", rendered)
        self.assertIn("[1] Example Gopher", rendered)
        self.assertIn("→ gopher://example.com", rendered)

    def test_html_with_images(self):
        """Test HTML rendering with image placeholders."""
        html = """
        <html>
            <body>
                <h1>Images Test</h1>
                <img src="logo.png" alt="Company Logo" title="Our Logo">
                <img src="photo.jpg" alt="Photo">
            </body>
        </html>
        """

        rendered, links = self.renderer.render_html(html)

        # Check image placeholders
        self.assertIn("[IMG1:Company Logo]", rendered)
        self.assertIn("[IMG2:Photo]", rendered)
        self.assertIn("🖼️  Images:", rendered)
        self.assertIn("[IMG1] Company Logo", rendered)
        self.assertIn("→ logo.png", rendered)

    def test_html_with_lists(self):
        """Test HTML rendering with ordered and unordered lists."""
        html = """
        <html>
            <body>
                <h1>Lists Test</h1>
                <ul>
                    <li>Unordered item 1</li>
                    <li>Unordered item 2</li>
                </ul>
                <ol>
                    <li>Ordered item 1</li>
                    <li>Ordered item 2</li>
                </ol>
            </body>
        </html>
        """

        rendered, links = self.renderer.render_html(html)

        # Check list formatting
        self.assertIn("• Unordered item 1", rendered)
        self.assertIn("• Unordered item 2", rendered)
        self.assertIn("1. Ordered item 1", rendered)
        self.assertIn("2. Ordered item 2", rendered)

    def test_html_with_table(self):
        """Test HTML table rendering."""
        html = """
        <html>
            <body>
                <table>
                    <tr>
                        <th>Name</th>
                        <th>Age</th>
                    </tr>
                    <tr>
                        <td>Alice</td>
                        <td>30</td>
                    </tr>
                    <tr>
                        <td>Bob</td>
                        <td>25</td>
                    </tr>
                </table>
            </body>
        </html>
        """

        rendered, links = self.renderer.render_html(html)

        # Check table structure (basic presence)
        self.assertIn("Name", rendered)
        self.assertIn("Age", rendered)
        self.assertIn("Alice", rendered)
        self.assertIn("Bob", rendered)
        # Check for table borders
        self.assertIn("┌", rendered)
        self.assertIn("│", rendered)
        self.assertIn("└", rendered)

    def test_html_with_formatting(self):
        """Test HTML text formatting (bold, italic, code)."""
        html = """
        <html>
            <body>
                <p>This is <strong>bold</strong> and <em>italic</em> and <code>code</code>.</p>
                <blockquote>
                    <p>This is a quote.</p>
                </blockquote>
                <pre>This is preformatted text</pre>
            </body>
        </html>
        """

        rendered, links = self.renderer.render_html(html)

        # Check formatting
        self.assertIn("**bold**", rendered)
        self.assertIn("*italic*", rendered)
        self.assertIn("`code`", rendered)
        self.assertIn("> This is a quote.", rendered)
        self.assertIn("```", rendered)
        self.assertIn("This is preformatted text", rendered)

    def test_html_with_headers(self):
        """Test HTML header rendering."""
        html = """
        <html>
            <body>
                <h1>Header 1</h1>
                <h2>Header 2</h2>
                <h3>Header 3</h3>
            </body>
        </html>
        """

        rendered, links = self.renderer.render_html(html)

        # Check header formatting
        self.assertIn("🏷️  Header 1", rendered)
        self.assertIn("📌 Header 2", rendered)
        self.assertIn("### Header 3", rendered)
        # Check underlines for headers
        self.assertIn("===", rendered)  # H1 underline
        self.assertIn("---", rendered)  # H2 underline

    def test_html_error_handling(self):
        """Test HTML rendering error handling."""
        # Test with malformed HTML
        malformed_html = "<html><body><p>Unclosed paragraph<body></html>"

        rendered, links = self.renderer.render_html(malformed_html)

        # Should still render something and not crash
        self.assertIsInstance(rendered, str)
        self.assertIsInstance(links, list)

    def test_empty_html(self):
        """Test rendering empty or minimal HTML."""
        empty_html = ""

        rendered, links = self.renderer.render_html(empty_html)

        self.assertIsInstance(rendered, str)
        self.assertEqual(links, [])

    def test_extract_links_only(self):
        """Test link extraction without full rendering."""
        html = """
        <html>
            <body>
                <a href="gopher://test1.com">Link 1</a>
                <a href="gopher://test2.com" title="Test">Link 2</a>
            </body>
        </html>
        """

        links = self.renderer.extract_links_only(html)

        self.assertEqual(len(links), 2)
        self.assertEqual(links[0]['url'], 'gopher://test1.com')
        self.assertEqual(links[0]['text'], 'Link 1')
        self.assertEqual(links[1]['title'], 'Test')

    def test_clean_text(self):
        """Test text cleaning functionality."""
        dirty_text = "  \n\t  Multiple   spaces\n\n\tand    newlines  \n  "
        clean_text = self.renderer._clean_text(dirty_text)

        self.assertEqual(clean_text, "Multiple spaces and newlines")

    def test_skip_script_style_elements(self):
        """Test that script and style elements are skipped."""
        html = """
        <html>
            <head>
                <style>body { color: red; }</style>
                <script>alert('test');</script>
            </head>
            <body>
                <p>Visible content</p>
            </body>
        </html>
        """

        rendered, links = self.renderer.render_html(html)

        # Script and style content should not appear
        self.assertNotIn("color: red", rendered)
        self.assertNotIn("alert", rendered)
        self.assertIn("Visible content", rendered)


class TestRenderHTMLToText(unittest.TestCase):
    """Test cases for the convenience function."""

    def test_render_html_to_text_function(self):
        """Test the convenience function works correctly."""
        html = "<html><body><h1>Test</h1><p>Content</p></body></html>"

        rendered, links = render_html_to_text(html)

        self.assertIsInstance(rendered, str)
        self.assertIsInstance(links, list)
        self.assertIn("Test", rendered)
        self.assertIn("Content", rendered)

    def test_render_html_to_text_with_links_disabled(self):
        """Test rendering with link extraction disabled."""
        html = '<html><body><a href="test.com">Link</a></body></html>'

        rendered, links = render_html_to_text(html, extract_links=False)

        self.assertEqual(links, [])
        self.assertIn("Link", rendered)
        self.assertNotIn("[1]", rendered)  # No link numbering


class TestHTMLDetection(unittest.TestCase):
    """Test HTML detection logic for browser integration."""

    def test_html_detection_by_doctype(self):
        """Test HTML detection by DOCTYPE."""
        html = '<!DOCTYPE html><html><body><p>Test</p></body></html>'

        is_html = ('<!doctype html' in html.lower() or
                   '<html' in html.lower() or
                   '<body' in html.lower())

        self.assertTrue(is_html)

    def test_html_detection_by_tags(self):
        """Test HTML detection by common tags."""
        html_with_body = '<body><p>Test</p></body>'
        html_with_html = '<html><p>Test</p></html>'
        plain_text = 'This is just plain text'

        # Test positive cases
        self.assertTrue('<body' in html_with_body.lower())
        self.assertTrue('<html' in html_with_html.lower())

        # Test negative case
        self.assertFalse('<html' in plain_text.lower())
        self.assertFalse('<body' in plain_text.lower())


if __name__ == '__main__':
    unittest.main()
