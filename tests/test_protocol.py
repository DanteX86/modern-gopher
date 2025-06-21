#!/usr/bin/env python3
"""
Tests for Gopher protocol implementation.
"""

import socket
from io import BytesIO
from unittest.mock import Mock, patch

import pytest

from modern_gopher.core.protocol import (
    DEFAULT_GOPHER_PORT,
    GopherConnectionError,
    GopherProtocolError,
    GopherTimeoutError,
    create_socket,
    is_gopher_url,
    receive_response,
    request_gopher_resource,
    save_gopher_resource,
    send_request,
)


class TestSocketCreation:
    """Test socket creation and connection functionality."""

    def test_create_socket_ipv4(self):
        """Test creating an IPv4 socket."""
        with patch("socket.socket") as mock_socket_class:
            with patch("socket.getaddrinfo") as mock_getaddrinfo:
                # Mock getaddrinfo to return IPv4 address
                mock_getaddrinfo.return_value = [
                    (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("127.0.0.1", 70))
                ]

                mock_socket = Mock()
                mock_socket_class.return_value = mock_socket

                # Test IPv4 socket creation
                sock = create_socket("localhost", use_ipv6=False)

                mock_socket_class.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM, 0)
                mock_socket.settimeout.assert_called_once_with(30)
                mock_socket.connect.assert_called_once_with(("127.0.0.1", 70))
                assert sock == mock_socket

    def test_create_socket_ipv6(self):
        """Test creating an IPv6 socket."""
        with patch("socket.socket") as mock_socket_class:
            with patch("socket.getaddrinfo") as mock_getaddrinfo:
                # Mock getaddrinfo to return IPv6 address
                mock_getaddrinfo.return_value = [
                    (socket.AF_INET6, socket.SOCK_STREAM, 0, "", ("::1", 70, 0, 0))
                ]

                mock_socket = Mock()
                mock_socket_class.return_value = mock_socket

                # Test IPv6 socket creation
                sock = create_socket("localhost", use_ipv6=True)

                mock_socket_class.assert_called_once_with(socket.AF_INET6, socket.SOCK_STREAM, 0)
                mock_socket.settimeout.assert_called_once_with(30)
                assert sock == mock_socket

    def test_create_socket_auto_detect(self):
        """Test auto-detecting IP version."""
        with patch("socket.socket") as mock_socket_class:
            with patch("socket.getaddrinfo") as mock_getaddrinfo:
                # Mock getaddrinfo to return IPv4 address
                mock_getaddrinfo.return_value = [
                    (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("127.0.0.1", 70))
                ]

                mock_socket = Mock()
                mock_socket_class.return_value = mock_socket

                # Test auto-detection (use_ipv6=None)
                sock = create_socket("localhost", use_ipv6=None)

                mock_getaddrinfo.assert_called_once_with(
                    "localhost", DEFAULT_GOPHER_PORT, socket.AF_UNSPEC, socket.SOCK_STREAM
                )
                assert sock == mock_socket

    def test_create_socket_with_ssl(self):
        """Test creating an SSL-wrapped socket."""
        with patch("socket.socket") as mock_socket_class:
            with patch("socket.getaddrinfo") as mock_getaddrinfo:
                with patch("ssl.create_default_context") as mock_ssl_context:
                    # Setup mocks
                    mock_getaddrinfo.return_value = [
                        (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("127.0.0.1", 70))
                    ]

                    mock_socket = Mock()
                    mock_socket_class.return_value = mock_socket

                    mock_context = Mock()
                    mock_ssl_context.return_value = mock_context
                    mock_ssl_socket = Mock()
                    mock_context.wrap_socket.return_value = mock_ssl_socket

                    # Test SSL socket creation
                    sock = create_socket("localhost", use_ssl=True)

                    mock_ssl_context.assert_called_once()
                    mock_context.wrap_socket.assert_called_once_with(
                        mock_socket, server_hostname="localhost"
                    )
                    assert sock == mock_ssl_socket

    def test_create_socket_connection_refused(self):
        """Test handling connection refused errors."""
        with patch("socket.socket") as mock_socket_class:
            with patch("socket.getaddrinfo") as mock_getaddrinfo:
                mock_getaddrinfo.return_value = [
                    (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("127.0.0.1", 70))
                ]

                mock_socket = Mock()
                mock_socket_class.return_value = mock_socket
                mock_socket.connect.side_effect = ConnectionRefusedError("Connection refused")

                with pytest.raises(GopherConnectionError, match="Failed to connect"):
                    create_socket("localhost")

                mock_socket.close.assert_called_once()

    def test_create_socket_timeout(self):
        """Test handling connection timeout."""
        with patch("socket.socket") as mock_socket_class:
            with patch("socket.getaddrinfo") as mock_getaddrinfo:
                mock_getaddrinfo.return_value = [
                    (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("127.0.0.1", 70))
                ]

                mock_socket = Mock()
                mock_socket_class.return_value = mock_socket
                mock_socket.connect.side_effect = socket.timeout("Connection timed out")

                with pytest.raises(GopherTimeoutError, match="timed out"):
                    create_socket("localhost")

                mock_socket.close.assert_called_once()

    def test_create_socket_dns_resolution_failure(self):
        """Test handling DNS resolution failures."""
        with patch("socket.getaddrinfo") as mock_getaddrinfo:
            mock_getaddrinfo.side_effect = socket.gaierror("Name resolution failed")

            with pytest.raises(GopherConnectionError, match="Failed to resolve host"):
                create_socket("nonexistent.host")


class TestRequestSending:
    """Test request sending functionality."""

    def test_send_request_basic(self):
        """Test sending a basic request."""
        mock_socket = Mock()

        send_request(mock_socket, "/test/selector")

        mock_socket.sendall.assert_called_once_with(b"/test/selector\r\n")

    def test_send_request_empty_selector(self):
        """Test sending request with empty selector."""
        mock_socket = Mock()

        send_request(mock_socket, "")

        mock_socket.sendall.assert_called_once_with(b"\r\n")

    def test_send_request_timeout(self):
        """Test handling request timeout."""
        mock_socket = Mock()
        mock_socket.sendall.side_effect = socket.timeout("Send timed out")

        with pytest.raises(GopherTimeoutError, match="Request timed out"):
            send_request(mock_socket, "/test")

    def test_send_request_connection_error(self):
        """Test handling connection errors during send."""
        mock_socket = Mock()
        mock_socket.sendall.side_effect = ConnectionError("Connection lost")

        with pytest.raises(GopherProtocolError, match="Failed to send request"):
            send_request(mock_socket, "/test")


class TestResponseReceiving:
    """Test response receiving functionality."""

    def test_receive_response_basic(self):
        """Test receiving a basic response."""
        mock_socket = Mock()
        test_data = [b"Hello", b" ", b"World", b""]
        mock_socket.recv.side_effect = test_data

        chunks = list(receive_response(mock_socket))

        assert chunks == [b"Hello", b" ", b"World"]
        mock_socket.close.assert_called_once()

    def test_receive_response_empty(self):
        """Test receiving empty response."""
        mock_socket = Mock()
        mock_socket.recv.return_value = b""

        chunks = list(receive_response(mock_socket))

        assert chunks == []
        mock_socket.close.assert_called_once()

    def test_receive_response_timeout(self):
        """Test handling response timeout."""
        mock_socket = Mock()
        mock_socket.recv.side_effect = socket.timeout("Receive timed out")

        with pytest.raises(GopherTimeoutError, match="Response timed out"):
            list(receive_response(mock_socket))

        mock_socket.close.assert_called_once()

    def test_receive_response_connection_error(self):
        """Test handling connection errors during receive."""
        mock_socket = Mock()
        mock_socket.recv.side_effect = ConnectionError("Connection lost")

        with pytest.raises(GopherProtocolError, match="Error receiving data"):
            list(receive_response(mock_socket))

        mock_socket.close.assert_called_once()


class TestResourceRequests:
    """Test high-level resource request functionality."""

    @patch("modern_gopher.core.protocol.create_socket")
    @patch("modern_gopher.core.protocol.send_request")
    @patch("modern_gopher.core.protocol.receive_response")
    def test_request_gopher_resource_success(self, mock_receive, mock_send, mock_create_socket):
        """Test successful resource request."""
        mock_socket = Mock()
        mock_create_socket.return_value = mock_socket
        mock_receive.return_value = iter([b"test", b"data"])

        chunks = list(request_gopher_resource("localhost", "/test"))

        mock_create_socket.assert_called_once_with("localhost", 70, 30, False, None)
        mock_send.assert_called_once_with(mock_socket, "/test")
        mock_receive.assert_called_once_with(mock_socket, 4096)
        assert chunks == [b"test", b"data"]

    @patch("modern_gopher.core.protocol.create_socket")
    def test_request_gopher_resource_connection_failure(self, mock_create_socket):
        """Test resource request with connection failure."""
        mock_create_socket.side_effect = GopherConnectionError("Connection failed")

        with pytest.raises(GopherConnectionError):
            list(request_gopher_resource("localhost", "/test"))

    @patch("modern_gopher.core.protocol.request_gopher_resource")
    def test_save_gopher_resource(self, mock_request):
        """Test saving resource to file."""
        mock_request.return_value = iter([b"test", b"data"])

        output_file = BytesIO()
        bytes_written = save_gopher_resource("localhost", "/test", output_file)

        assert bytes_written == 8
        assert output_file.getvalue() == b"testdata"
        mock_request.assert_called_once_with("localhost", "/test", 70, False, 30, None, 4096)

    @patch("modern_gopher.core.protocol.request_gopher_resource")
    def test_save_gopher_resource_write_error(self, mock_request):
        """Test handling write errors when saving resource."""
        mock_request.return_value = iter([b"test", b"data"])

        mock_file = Mock()
        mock_file.write.side_effect = IOError("Write failed")

        with pytest.raises(IOError, match="Failed to write to output file"):
            save_gopher_resource("localhost", "/test", mock_file)


class TestUtilityFunctions:
    """Test utility functions."""

    def test_is_gopher_url_valid(self):
        """Test validation of valid Gopher URLs."""
        assert is_gopher_url("gopher://example.com")
        assert is_gopher_url("gophers://secure.example.com")
        assert is_gopher_url("gopher://example.com:8080/1/path")

    def test_is_gopher_url_invalid(self):
        """Test validation of invalid URLs."""
        assert not is_gopher_url("http://example.com")
        assert not is_gopher_url("https://example.com")
        assert not is_gopher_url("ftp://example.com")
        assert not is_gopher_url("not-a-url")
        assert not is_gopher_url("")


if __name__ == "__main__":
    pytest.main([__file__])
