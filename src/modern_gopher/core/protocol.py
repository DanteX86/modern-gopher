"""
Basic Gopher protocol implementation with socket handling for both IPv4 and IPv6.

This module provides low-level functions for communicating with Gopher servers
according to RFC 1436.
"""

import logging
import socket
import ssl
from typing import BinaryIO
from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

# Constants
DEFAULT_GOPHER_PORT = 70
DEFAULT_BUFFER_SIZE = 4096
DEFAULT_TIMEOUT = 30

logger = logging.getLogger(__name__)


class GopherProtocolError(Exception):
    """Exception raised for Gopher protocol errors."""
    pass


class GopherConnectionError(GopherProtocolError):
    """Exception raised for Gopher connection errors."""
    pass


class GopherTimeoutError(GopherProtocolError):
    """Exception raised for Gopher timeout errors."""
    pass


def create_socket(host: str, port: int = DEFAULT_GOPHER_PORT,
                  timeout: int = DEFAULT_TIMEOUT, use_ssl: bool = False,
                  use_ipv6: Optional[bool] = None) -> socket.socket:
    """
    Create and connect a socket to the specified Gopher server.

    Args:
        host: The hostname or IP address of the Gopher server
        port: The port to connect to (default: 70, the standard Gopher port)
        timeout: Socket timeout in seconds
        use_ssl: Whether to use SSL/TLS for the connection
        use_ipv6: Force IPv6 usage if True, IPv4 if False, or auto-detect if None

    Returns:
        A connected socket object

    Raises:
        GopherConnectionError: If connection fails
        GopherTimeoutError: If connection times out
    """
    # Determine address family based on IPv6 preference
    if use_ipv6 is None:
        # Auto-detect IP version to use
        try:
            addrinfo = socket.getaddrinfo(host, port,
                                          socket.AF_UNSPEC, socket.SOCK_STREAM)
            if not addrinfo:
                raise GopherConnectionError(f"Could not resolve host: {host}")

            # Use the first available address format
            family, socktype, proto, _, addr = addrinfo[0]
        except socket.gaierror as e:
            raise GopherConnectionError(
                f"Failed to resolve host '{host}': {e}")
    else:
        # Use specified IP version
        family = socket.AF_INET6 if use_ipv6 else socket.AF_INET
        try:
            socktype = socket.SOCK_STREAM
            proto = 0
            addrinfo = socket.getaddrinfo(host, port, family, socktype)
            if not addrinfo:
                raise GopherConnectionError(
                    f"Could not resolve host {host} with {
                        'IPv6' if use_ipv6 else 'IPv4'}")

            _, _, _, _, addr = addrinfo[0]
        except socket.gaierror as e:
            raise GopherConnectionError(
                f"Failed to resolve host '{host}' with {
                    'IPv6' if use_ipv6 else 'IPv4'}: {e}")

    try:
        # Create and connect the socket
        sock = socket.socket(family, socktype, proto)
        sock.settimeout(timeout)

        # Add SSL/TLS wrapper if requested
        if use_ssl:
            context = ssl.create_default_context()
            sock = context.wrap_socket(sock, server_hostname=host)

        sock.connect(addr)
        return sock
    except socket.timeout as e:
        sock.close()
        raise GopherTimeoutError(f"Connection to {host}:{port} timed out: {e}")
    except (ConnectionRefusedError, OSError) as e:
        sock.close()
        raise GopherConnectionError(f"Failed to connect to {host}:{port}: {e}")


def send_request(sock: socket.socket, selector: str = "") -> None:
    """
    Send a request to the Gopher server.

    Args:
        sock: Connected socket to the Gopher server
        selector: The selector string to request (empty for the root menu)

    Raises:
        GopherProtocolError: If the request cannot be sent
    """
    try:
        # Format according to RFC 1436: selector string followed by CRLF
        request = f"{selector}\r\n"
        sock.sendall(request.encode('utf-8'))
    except socket.timeout as e:
        raise GopherTimeoutError(f"Request timed out: {e}")
    except (ConnectionError, OSError) as e:
        raise GopherProtocolError(f"Failed to send request: {e}")


def receive_response(
        sock: socket.socket,
        buffer_size: int = DEFAULT_BUFFER_SIZE) -> Iterator[bytes]:
    """
    Receive response data from the Gopher server.

    Args:
        sock: Connected socket to the Gopher server
        buffer_size: Size of buffer chunks to read

    Yields:
        Chunks of data received from the server

    Raises:
        GopherProtocolError: If data cannot be received
    """
    try:
        while True:
            data = sock.recv(buffer_size)
            if not data:  # End of response
                break
            yield data
    except socket.timeout as e:
        raise GopherTimeoutError(f"Response timed out: {e}")
    except (ConnectionError, OSError) as e:
        raise GopherProtocolError(f"Error receiving data: {e}")
    finally:
        sock.close()


def request_gopher_resource(
        host: str,
        selector: str = "",
        port: int = DEFAULT_GOPHER_PORT,
        use_ssl: bool = False,
        timeout: int = DEFAULT_TIMEOUT,
        use_ipv6: Optional[bool] = None,
        buffer_size: int = DEFAULT_BUFFER_SIZE) -> Iterator[bytes]:
    """
    Request a resource from a Gopher server and return the response.

    This is a high-level function that handles the entire request/response cycle.

    Args:
        host: The hostname or IP address of the Gopher server
        selector: The selector string to request (empty for the root menu)
        port: The port to connect to
        use_ssl: Whether to use SSL/TLS for the connection
        timeout: Socket timeout in seconds
        use_ipv6: Force IPv6 usage if True, IPv4 if False, or auto-detect if None
        buffer_size: Size of buffer chunks to read

    Yields:
        Chunks of data received from the server

    Raises:
        GopherProtocolError: If any part of the request fails
    """
    try:
        logger.debug(f"Connecting to {host}:{port} for selector '{selector}'")
        sock = create_socket(host, port, timeout, use_ssl, use_ipv6)

        logger.debug(f"Sending request for selector '{selector}'")
        send_request(sock, selector)

        logger.debug("Receiving response")
        yield from receive_response(sock, buffer_size)

        logger.debug("Resource retrieval completed")
    except (GopherProtocolError, GopherConnectionError, GopherTimeoutError) as e:
        logger.error(f"Error retrieving resource: {e}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error retrieving resource: {e}")
        raise GopherProtocolError(f"Unexpected error: {e}")


def save_gopher_resource(host: str, selector: str, output_file: BinaryIO,
                         port: int = DEFAULT_GOPHER_PORT,
                         use_ssl: bool = False,
                         timeout: int = DEFAULT_TIMEOUT,
                         use_ipv6: Optional[bool] = None,
                         buffer_size: int = DEFAULT_BUFFER_SIZE) -> int:
    """
    Request a Gopher resource and save it to a file.

    Args:
        host: The hostname or IP address of the Gopher server
        selector: The selector string to request
        output_file: A file-like object open in binary write mode
        port: The port to connect to
        use_ssl: Whether to use SSL/TLS for the connection
        timeout: Socket timeout in seconds
        use_ipv6: Force IPv6 usage if True, IPv4 if False, or auto-detect if None
        buffer_size: Size of buffer chunks to read

    Returns:
        The number of bytes written to the file

    Raises:
        GopherProtocolError: If any part of the request fails
        IOError: If writing to the file fails
    """
    total_bytes = 0
    try:
        for chunk in request_gopher_resource(
            host, selector, port, use_ssl, timeout, use_ipv6, buffer_size
        ):
            output_file.write(chunk)
            total_bytes += len(chunk)

        return total_bytes
    except IOError as e:
        raise IOError(f"Failed to write to output file: {e}")


def is_gopher_url(url: str) -> bool:
    """
    Check if a URL is a valid Gopher URL.

    Args:
        url: The URL to check

    Returns:
        True if the URL is a valid Gopher URL, False otherwise
    """
    return url.startswith(("gopher://", "gophers://"))
