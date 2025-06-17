#!/usr/bin/env python3
"""
Beautiful Soup Test Script
This script demonstrates basic Beautiful Soup functionality
"""

from bs4 import BeautifulSoup
import requests

def test_basic_parsing():
    """Test basic HTML parsing with Beautiful Soup"""
    html_content = """
    <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <h1>Welcome to Beautiful Soup!</h1>
            <p class="intro">This is a test paragraph.</p>
            <div id="content">
                <p>Another paragraph with <a href="https://example.com">a link</a>.</p>
                <ul>
                    <li>Item 1</li>
                    <li>Item 2</li>
                    <li>Item 3</li>
                </ul>
            </div>
        </body>
    </html>
    """
    
    # Create Beautiful Soup object
    soup = BeautifulSoup(html_content, 'html.parser')
    
    print("=== Beautiful Soup Test Results ===")
    print(f"Title: {soup.title.text}")
    print(f"H1 text: {soup.h1.text}")
    print(f"Intro paragraph: {soup.find('p', class_='intro').text}")
    
    # Find all list items
    items = soup.find_all('li')
    print("\nList items:")
    for i, item in enumerate(items, 1):
        print(f"  {i}. {item.text}")
    
    # Find link
    link = soup.find('a')
    print(f"\nLink text: {link.text}")
    print(f"Link URL: {link['href']}")
    
    print("\n✅ Beautiful Soup is working correctly!")

def test_web_scraping():
    """Test web scraping with requests and Beautiful Soup"""
    try:
        print("\n=== Web Scraping Test ===")
        print("Fetching example.com...")
        
        response = requests.get('https://example.com', timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        title = soup.title.text if soup.title else "No title found"
        print(f"Page title: {title}")
        
        # Find the main content
        main_content = soup.find('body')
        if main_content:
            # Get first paragraph
            first_p = main_content.find('p')
            if first_p:
                print(f"First paragraph: {first_p.text[:100]}...")
        
        print("✅ Web scraping test successful!")
        
    except requests.RequestException as e:
        print(f"❌ Web scraping test failed: {e}")
        print("This might be due to network connectivity issues.")

if __name__ == "__main__":
    test_basic_parsing()
    test_web_scraping()

