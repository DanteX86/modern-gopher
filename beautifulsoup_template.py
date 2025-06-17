#!/usr/bin/env python3
"""
Beautiful Soup Starter Template
Use this as a starting point for your web scraping projects
"""

from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
import time

def scrape_webpage(url, headers=None):
    """
    Scrape a webpage and return a BeautifulSoup object
    
    Args:
        url (str): The URL to scrape
        headers (dict): Optional headers for the request
    
    Returns:
        BeautifulSoup: Parsed HTML content
    """
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
        
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_links(soup, base_url=None):
    """
    Extract all links from a BeautifulSoup object
    
    Args:
        soup (BeautifulSoup): Parsed HTML content
        base_url (str): Base URL to resolve relative links
    
    Returns:
        list: List of absolute URLs
    """
    links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if base_url:
            href = urljoin(base_url, href)
        links.append({
            'url': href,
            'text': link.get_text(strip=True),
            'title': link.get('title', '')
        })
    return links

def extract_text_content(soup):
    """
    Extract clean text content from HTML
    
    Args:
        soup (BeautifulSoup): Parsed HTML content
    
    Returns:
        str: Clean text content
    """
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Get text and clean it up
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text

def main():
    """
    Main function - modify this for your specific scraping needs
    """
    # Example usage
    url = "https://example.com"
    
    print(f"Scraping: {url}")
    soup = scrape_webpage(url)
    
    if soup:
        # Extract basic information
        title = soup.title.text if soup.title else "No title"
        print(f"Page Title: {title}")
        
        # Extract links
        links = extract_links(soup, url)
        print(f"\nFound {len(links)} links:")
        for link in links[:5]:  # Show first 5 links
            print(f"  - {link['text'][:50]}... -> {link['url']}")
        
        # Extract specific elements (customize as needed)
        headings = soup.find_all(['h1', 'h2', 'h3'])
        print(f"\nFound {len(headings)} headings:")
        for heading in headings[:3]:  # Show first 3 headings
            print(f"  - {heading.name.upper()}: {heading.get_text(strip=True)}")
        
        # Extract paragraphs
        paragraphs = soup.find_all('p')
        print(f"\nFound {len(paragraphs)} paragraphs")
        if paragraphs:
            print(f"First paragraph: {paragraphs[0].get_text(strip=True)[:100]}...")
    
    else:
        print("Failed to scrape the webpage")

if __name__ == "__main__":
    main()

