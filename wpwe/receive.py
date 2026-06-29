#!/usr/bin/env python3

"""Legacy compatibility layer for request handling."""

from wpwe.handlers import get_file, handle_request, load_error_page, resolve_request_path
from wpwe.http11 import handle_connection, read_request, send_response
from wpwe.request import HttpRequest, parse_http_request
from wpwe.response import HttpResponse


def parse_request(rawreq):
    return parse_http_request(rawreq)


def build_response(config, status_code, body="", extra_headers=None, file_path=None, content_length=None):
    headers = {}
    if extra_headers:
        for header in extra_headers:
            if ":" in header:
                name, value = header.split(":", 1)
                headers[name.strip()] = value.strip()

    if isinstance(body, str):
        body_bytes = body.encode("utf-8") if body else b""
    else:
        body_bytes = body or b""

    return HttpResponse(
        status_code=status_code,
        body=body_bytes,
        headers=headers,
        file_path=file_path,
        content_length=content_length,
    )


def main(args, config, rawreq, client_address=("127.0.0.1", 0)):
    """Backward-compatible entry point used by tests and legacy callers."""
    from wpwe import logutil

    parsed = parse_http_request(rawreq)
    if not parsed:
        response = HttpResponse(
            status_code=400,
            body=b"Bad Request",
            headers={"Content-Type": "text/plain; charset=utf-8"},
        )
        logutil.write_access_log(config, client_address, "-", "-", 400)
        return _response_to_bytes(config, response, parsed)

    response = handle_request(config, parsed, client_address, tls_enabled=False)
    logutil.write_access_log(
        config,
        client_address,
        parsed.method,
        parsed.path,
        response.status_code,
    )
    return _response_to_bytes(config, response, parsed)


def _response_to_bytes(config, response, request):
    from wpwe.http11 import serialize_response

    return serialize_response(config, response, request, tls_enabled=False, keep_alive=False)


def handle_request_legacy(args, config, clientsocket, client_address):
    handle_connection(clientsocket, config, client_address, tls_enabled=False)
