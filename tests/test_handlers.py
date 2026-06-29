from wpwe.handlers import handle_request, resolve_request_path
from wpwe.request import HttpRequest


def test_health_check(merged_config):
    request = HttpRequest(
        method="GET",
        path="/healthz",
        uri="/healthz",
        http_version="HTTP/1.1",
    )
    response = handle_request(merged_config, request, ("127.0.0.1", 1234))
    assert response.status_code == 200
    assert response.body == b"ok"


def test_get_index(merged_config):
    request = HttpRequest(
        method="GET",
        path="/",
        uri="/",
        http_version="HTTP/1.1",
        headers={"host": "localhost"},
    )
    response = handle_request(merged_config, request, ("127.0.0.1", 1234))
    assert response.status_code == 200
    assert b"hello" in response.body


def test_head_has_no_body(merged_config):
    request = HttpRequest(
        method="HEAD",
        path="/",
        uri="/",
        http_version="HTTP/1.1",
        headers={"host": "localhost"},
    )
    response = handle_request(merged_config, request, ("127.0.0.1", 1234))
    assert response.status_code == 200
    assert response.body == b""
    assert response.content_length is not None


def test_path_traversal_blocked(merged_config):
    assert resolve_request_path(merged_config, "/../secrets") is None


def test_unknown_host_rejected(merged_config):
    request = HttpRequest(
        method="GET",
        path="/",
        uri="/",
        http_version="HTTP/1.1",
        headers={"host": "evil.example"},
    )
    response = handle_request(merged_config, request, ("127.0.0.1", 1234))
    assert response.status_code == 421


def test_options_returns_allow(merged_config):
    request = HttpRequest(
        method="OPTIONS",
        path="/",
        uri="/",
        http_version="HTTP/1.1",
        headers={"host": "localhost"},
    )
    response = handle_request(merged_config, request, ("127.0.0.1", 1234))
    assert response.status_code == 200
    assert "Allow" in response.headers
