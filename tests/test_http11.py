from tests.conftest import http_request


def test_get_root_over_socket(running_server):
    port, _proc = running_server
    response = http_request(
        port,
        b"GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n",
    )
    assert b"HTTP/1.1 200" in response
    assert b"hello" in response
    assert b"X-Content-Type-Options: nosniff" in response


def test_not_found_over_socket(running_server):
    port, _proc = running_server
    response = http_request(
        port,
        b"GET /missing HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n",
    )
    assert b"HTTP/1.1 404" in response


def test_keep_alive_multiple_requests(running_server):
    port, _proc = running_server
    with __import__("socket").create_connection(("127.0.0.1", port), timeout=5) as sock:
        sock.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\nConnection: keep-alive\r\n\r\n")
        first = sock.recv(65536)
        assert b"HTTP/1.1 200" in first
        sock.sendall(b"GET /assets/app.js HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
        second = sock.recv(65536)
        assert b"HTTP/1.1 200" in second
        assert b"application/javascript" in second.lower() or b"javascript" in second.lower()


def test_bad_host_rejected(running_server):
    port, _proc = running_server
    response = http_request(
        port,
        b"GET / HTTP/1.1\r\nHost: evil.example\r\nConnection: close\r\n\r\n",
    )
    assert b"HTTP/1.1 421" in response
