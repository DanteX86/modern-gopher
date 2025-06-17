# Beautiful Soup Quick Reference

## Setup

```bash
# Activate virtual environment
source venv/bin/activate

# Run your Python scripts
python your_script.py

# Deactivate when done
deactivate
```

## Basic Usage

```python
from bs4 import BeautifulSoup
import requests

# Parse HTML string
html = "<html><body><h1>Title</h1></body></html>"
soup = BeautifulSoup(html, 'html.parser')

# Parse from web request
response = requests.get('https://example.com')
soup = BeautifulSoup(response.content, 'html.parser')

# Parse from file
with open('file.html', 'r') as f:
    soup = BeautifulSoup(f, 'html.parser')
```

## Finding Elements

```python
# Find first element
title = soup.find('title')                    # First <title> tag
first_p = soup.find('p')                      # First <p> tag
by_class = soup.find('div', class_='content') # First div with class="content"
by_id = soup.find('div', id='main')          # Element with id="main"
by_attrs = soup.find('a', {'href': '/about'}) # Link with specific href

# Find all elements
all_links = soup.find_all('a')                # All <a> tags
all_paragraphs = soup.find_all('p')           # All <p> tags
by_class_all = soup.find_all('div', class_='item') # All divs with class="item"

# CSS selectors
first_link = soup.select_one('a')             # First <a> tag
all_links = soup.select('a')                  # All <a> tags
by_class_css = soup.select('.content')        # All elements with class="content"
by_id_css = soup.select('#main')             # Element with id="main"
nested = soup.select('div.content p')        # <p> inside <div class="content">
```

## Extracting Data

```python
# Get text content
title_text = soup.title.text                 # Text content of <title>
clean_text = soup.get_text()                 # All text, cleaned
stripped_text = soup.get_text(strip=True)    # All text, stripped of whitespace

# Get attributes
link_url = soup.find('a')['href']            # href attribute of first link
img_src = soup.find('img').get('src')        # src attribute (safe, returns None if not found)
all_attrs = soup.find('div').attrs           # Dictionary of all attributes

# Get HTML content
inner_html = soup.find('div').decode_contents()  # Inner HTML
outer_html = str(soup.find('div'))               # Outer HTML
```

## Navigation

```python
# Parent/child relationships
parent = soup.find('p').parent               # Parent element
children = list(soup.find('div').children)   # Direct children
descendants = list(soup.find('div').descendants) # All descendants

# Siblings
next_sibling = soup.find('h1').next_sibling
prev_sibling = soup.find('h2').previous_sibling
all_next = soup.find('h1').find_next_siblings()
```

## Common Patterns

```python
# Extract all links with text
links = []
for link in soup.find_all('a', href=True):
    links.append({
        'text': link.get_text(strip=True),
        'url': link['href']
    })

# Extract table data
table_data = []
for row in soup.find('table').find_all('tr')[1:]:  # Skip header
    cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
    table_data.append(cells)

# Extract images
images = []
for img in soup.find_all('img', src=True):
    images.append({
        'src': img['src'],
        'alt': img.get('alt', ''),
        'title': img.get('title', '')
    })

# Clean up text
def clean_text(soup):
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    return '\n'.join(chunk for chunk in chunks if chunk)
```

## Files in this setup:

- `test_beautifulsoup.py` - Test script to verify installation
- `beautifulsoup_template.py` - Starter template for projects
- `beautifulsoup_reference.md` - This reference guide
- `venv/` - Virtual environment with Beautiful Soup installed

## Tips

1. Always use `requests` with proper headers to avoid being blocked
2. Add delays between requests when scraping multiple pages
3. Handle exceptions gracefully
4. Respect robots.txt and terms of service
5. Consider using `html5lib` parser for malformed HTML: `BeautifulSoup(html, 'html5lib')`

