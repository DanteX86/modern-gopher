# Modern Gopher

A set of modern tools for interacting with the Gopher protocol (RFC 1436).

## Features

- Pure Python implementation of the Gopher protocol
- Terminal-based browser with modern UI features
- Support for all Gopher item types
- TLS/SSL support for secure Gopher connections
- Local content caching
- Bookmarking system
- History tracking
- Export functionality to modern formats

## Installation

### Requirements

- Python 3.8+
- MacOS (tested on ARM64)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/modern-gopher.git
cd modern-gopher
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install the dependencies:
```bash
pip install -r requirements.txt
```

4. Install the package in development mode:
```bash
pip install -e .
```

## Usage

```bash
# Start the Gopher browser
modern-gopher browse gopher://gopher.floodgap.com

# Fetch a Gopher resource
modern-gopher get gopher://gopher.floodgap.com/0/gopher/proxy.txt
```

## Development

1. Activate the virtual environment:
```bash
source venv/bin/activate
```

2. Run tests:
```bash
pytest
```

## License

MIT

