#!/usr/bin/env python3
"""
HTML Rendering Demo for Modern Gopher

This script demonstrates the Beautiful Soup HTML rendering functionality
that's been integrated into the Modern Gopher browser.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from modern_gopher.content.html_renderer import HTMLRenderer, render_html_to_text
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

def demo_html_rendering():
    """Demonstrate HTML rendering with various examples."""
    console = Console()
    
    # Sample HTML documents to test
    html_samples = [
        {
            'name': 'Simple HTML Page',
            'html': '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Welcome to Gopher HTML</title>
            </head>
            <body>
                <h1>Welcome to the Modern Gopher Browser</h1>
                <p>This is a test of HTML rendering capabilities in the terminal.</p>
                
                <h2>Features</h2>
                <ul>
                    <li>Beautiful Soup integration</li>
                    <li>Terminal-friendly formatting</li>
                    <li>Link extraction and enumeration</li>
                    <li>Image placeholder support</li>
                </ul>
                
                <h3>Links</h3>
                <p>Here are some useful links:</p>
                <ul>
                    <li><a href="gopher://gopher.floodgap.com">Floodgap Gopher</a></li>
                    <li><a href="gopher://sdf.org">SDF Gopher</a></li>
                    <li><a href="https://example.com">External Web Link</a></li>
                </ul>
                
                <blockquote>
                    <p>The Gopher protocol is simple and elegant, making it perfect 
                    for browsing in a terminal environment.</p>
                </blockquote>
                
                <p>Visit our <strong>home page</strong> for more information, or 
                read the <em>documentation</em> for technical details.</p>
                
                <pre>
                    # Code example
                    import gopher
                    client = gopher.Client()
                    response = client.get('gopher://example.com')
                </pre>
                
                <hr>
                <p>© 2024 Modern Gopher Browser Project</p>
            </body>
            </html>
            '''
        },
        {
            'name': 'Table Example',
            'html': '''
            <html>
            <body>
                <h1>Gopher Server Directory</h1>
                <table>
                    <tr>
                        <th>Server Name</th>
                        <th>Location</th>
                        <th>Description</th>
                    </tr>
                    <tr>
                        <td>gopher.floodgap.com</td>
                        <td>USA</td>
                        <td>Primary Gopher server</td>
                    </tr>
                    <tr>
                        <td>sdf.org</td>
                        <td>USA</td>
                        <td>SDF Public Access UNIX</td>
                    </tr>
                    <tr>
                        <td>gopher.club</td>
                        <td>Europe</td>
                        <td>Community Gopher server</td>
                    </tr>
                </table>
                
                <p>All servers support both regular and SSL connections.</p>
            </body>
            </html>
            '''
        },
        {
            'name': 'Images and Media',
            'html': '''
            <html>
            <body>
                <h1>Media Content</h1>
                <p>This page demonstrates how images and media are handled:</p>
                
                <img src="logo.png" alt="Modern Gopher Logo" title="Our Logo">
                <img src="screenshot.jpg" alt="Browser Screenshot">
                
                <p>Check out these links:</p>
                <a href="gopher://example.com/0/readme.txt">Read the documentation</a><br>
                <a href="gopher://example.com/9/archive.zip">Download archive</a><br>
                <a href="gopher://example.com/s/music.mp3">Listen to music</a>
            </body>
            </html>
            '''
        }
    ]
    
    console.print(Panel.fit(
        "🌐 Modern Gopher HTML Rendering Demo",
        style="bold blue"
    ))
    console.print()
    
    for i, sample in enumerate(html_samples, 1):
        console.print(f"\n{'='*60}")
        console.print(f"Demo {i}: {sample['name']}")
        console.print(f"{'='*60}")
        
        try:
            # Render the HTML
            rendered_text, links = render_html_to_text(sample['html'])
            
            # Display the rendered result
            console.print(Panel(
                rendered_text,
                title=f"Rendered: {sample['name']}",
                border_style="green"
            ))
            
            # Show extracted links
            if links:
                console.print(f"\n🔗 Extracted {len(links)} links:")
                for j, link in enumerate(links, 1):
                    console.print(f"  [{j}] {link['text']} → {link['url']}")
            
        except Exception as e:
            console.print(f"❌ Error rendering HTML: {e}", style="red")
        
        console.print("\n" + "-"*40)
        input("Press Enter to continue to next demo...")
    
    console.print("\n✨ Demo completed! HTML rendering is working properly.")

def test_renderer_directly():
    """Test the HTML renderer class directly."""
    console = Console()
    
    console.print("\n🧪 Testing HTMLRenderer class directly...")
    
    renderer = HTMLRenderer(console)
    
    simple_html = '''
    <h1>Test Page</h1>
    <p>This is a <strong>test</strong> of the <em>HTML renderer</em>.</p>
    <a href="gopher://test.com">Test Link</a>
    '''
    
    rendered, links = renderer.render_html(simple_html)
    
    console.print(Panel(
        rendered,
        title="Direct Renderer Test",
        border_style="cyan"
    ))
    
    if links:
        console.print(f"\nExtracted links: {links}")
    
    # Test link extraction only
    links_only = renderer.extract_links_only(simple_html)
    console.print(f"\nLinks-only extraction: {links_only}")

if __name__ == "__main__":
    try:
        console = Console()
        
        console.print("Choose demo mode:")
        console.print("1. Full HTML rendering demos")
        console.print("2. Quick renderer test")
        console.print("3. Both")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice in ['1', '3']:
            demo_html_rendering()
        
        if choice in ['2', '3']:
            test_renderer_directly()
            
        if choice not in ['1', '2', '3']:
            console.print("Invalid choice. Running full demo...", style="yellow")
            demo_html_rendering()
            
    except KeyboardInterrupt:
        console.print("\n\nDemo interrupted by user.", style="yellow")
    except Exception as e:
        console = Console()
        console.print(f"\n❌ Error running demo: {e}", style="red")
        sys.exit(1)

