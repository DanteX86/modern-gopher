#!/opt/homebrew/bin/python3
import socket
import json
import argparse
import sys
import time

# Default settings
DEFAULT_MAX_DEPTH = 3
DEFAULT_MAX_ITEMS = 500
DEFAULT_MAX_INDEX_ITEMS = 100  # Limit indexed files for safety
DEFAULT_DELAY = 1.0
DEFAULT_OUTPUT_FILE = "neon_burrow_crawl.json"
DEFAULT_INDEX_FILE = "neon_burrow_index.json"

# Fetch content from a Gopher server
def fetch_gopher_item(host, port, selector, timeout=10, max_bytes=1024*1024):
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            sock.sendall((selector + "\r\n").encode('utf-8'))
            data = bytearray()
            while len(data) < max_bytes:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                data.extend(chunk)
            return bytes(data)
    except socket.timeout:
        print(f"[-] Timeout fetching {host}:{port}{selector}")
    except socket.error as e:
        print(f"[-] Socket error fetching {host}:{port}{selector}: {e}")
    return None

# Decode text content safely
def safe_decode(data):
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        return data.decode('latin-1', errors='replace')

# Parse a Gopher menu
def parse_menu(data):
    lines = data.splitlines()
    entries = []
    for line in lines:
        if line == ".":
            break
        if not line or "\t" not in line:
            continue
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        item_type = parts[0][0]
        display_text = parts[0][1:].strip()
        selector, host, port = parts[1], parts[2], int(parts[3])
        entries.append({
            "item_type": item_type,
            "display_text": display_text,
            "selector": selector,
            "host": host,
            "port": port
        })
    return entries

# Recursive crawl function
def crawl_gopher(host, port, selector, depth, max_depth, max_items, delay, visited, results):
    if len(results) >= max_items or depth > max_depth:
        return

    key = (host, port, selector)
    if key in visited:
        return

    visited.add(key)
    print(f"[+] Crawling: gopher://{host}:{port}{selector} (Depth: {depth})")

    data = fetch_gopher_item(host, port, selector)
    if data is None:
        return

    entries = parse_menu(safe_decode(data))
    for entry in entries:
        entry["parent_selector"] = selector
        results.append(entry)
        if len(results) >= max_items:
            return

    for entry in entries:
        if entry["item_type"] == "1":
            time.sleep(delay)
            crawl_gopher(entry["host"], entry["port"], entry["selector"],
                         depth + 1, max_depth, max_items, delay, visited, results)

# Index text files (item_type '0')
def index_text_files(entries, max_index_items, delay):
    indexed_count = 0
    for entry in entries:
        if indexed_count >= max_index_items:
            print("[!] Maximum indexed file limit reached.")
            break
        if entry["item_type"] == "0":
            print(f"[i] Indexing file: gopher://{entry['host']}:{entry['port']}{entry['selector']}")
            content_bytes = fetch_gopher_item(entry['host'], entry['port'], entry['selector'])
            if content_bytes:
                entry['content'] = safe_decode(content_bytes)
                print(f"[+] Indexed: {entry['display_text']} ({len(entry['content'])} bytes)")
            else:
                entry['content'] = ""
                print(f"[-] Failed to index: {entry['display_text']}")
            indexed_count += 1
            time.sleep(delay)

# Main entry point
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Neon-Burrow Gopher Crawler & Indexer")
    parser.add_argument("--host", default="gopher.floodgap.com", help="Gopher host")
    parser.add_argument("--port", type=int, default=70, help="Gopher port")
    parser.add_argument("--selector", default="/", help="Initial selector path")
    parser.add_argument("--max-depth", type=int, default=DEFAULT_MAX_DEPTH, help="Max crawl depth")
    parser.add_argument("--max-items", type=int, default=DEFAULT_MAX_ITEMS, help="Max items to crawl")
    parser.add_argument("--max-index-items", type=int, default=DEFAULT_MAX_INDEX_ITEMS, help="Max text files to index")
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY, help="Delay between requests (seconds)")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_FILE, help="Crawl output file")
    parser.add_argument("--index-output", default=DEFAULT_INDEX_FILE, help="Index output file")
    args = parser.parse_args()

    visited, results = set(), []

    # Crawling Phase
    print("[*] Starting crawl phase...")
    try:
        crawl_gopher(args.host, args.port, args.selector, 0, args.max_depth,
                     args.max_items, args.delay, visited, results)
    except KeyboardInterrupt:
        print("[!] Crawl interrupted by user.")

    # Save crawl results
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"[✓] Crawl completed: {len(results)} items saved to {args.output}")

    # Indexing Phase
    print("[*] Starting indexing phase (retrieving text files)...")
    try:
        index_text_files(results, args.max_index_items, args.delay)
    except KeyboardInterrupt:
        print("[!] Indexing interrupted by user.")

    # Save indexing results
    with open(args.index_output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"[✓] Indexing completed. Data saved to {args.index_output}")
