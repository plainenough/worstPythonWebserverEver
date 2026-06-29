#!/usr/bin/env python3

import os
import socket
from typing import Optional, Tuple

from wpwe import handlers, headers, logutil
from wpwe.headers import STATUS_MESSAGES
from wpwe.request import HttpRequest, parse_http_request
from wpwe.response import HttpResponse


def read_request_bytes(clientsocket: socket.socket, max_bytes: int) -> bytes:
    data = b""
    while b"\r\n\r\n" not in data and len(data) < max_bytes:
        chunk = clientsocket.recv(4096)
        if not chunk:
            break
        data += chunk

    if not data or b"\r\n\r\n" not in data:
        return data

    header_block = data.split(b"\r\n\r\n", 1)[0]
    if any(line.lower().startswith(b"transfer-encoding:") and b"chunked" in line.lower()
           for line in header_block.split(b"\r\n")):
        return data

    content_length = 0
    for line in header_block.split(b"\r\n"):
        if line.lower().startswith(b"content-length:"):
            try:
                content_length = int(line.split(b":", 1)[1].strip())
            except ValueError:
                content_length = 0
            break

    body_start = data.split(b"\r\n\r\n", 1)[1]
    remaining = max(content_length - len(body_start), 0)
    while remaining > 0 and len(data) < max_bytes:
        chunk = clientsocket.recv(min(4096, remaining))
        if not chunk:
            break
        data += chunk
        remaining -= len(chunk)

    return data


def read_request(clientsocket: socket.socket, config) -> Tuple[Optional[HttpRequest], bytes]:
    max_bytes = config["max_request_bytes"]
    raw_data = read_request_bytes(clientsocket, max_bytes)
    if not raw_data:
        return None, b""

    if b"transfer-encoding:" in raw_data.split(b"\r\n\r\n", 1)[0].lower():
        for line in raw_data.split(b"\r\n\r\n", 1)[0].split(b"\r\n"):
            if line.lower().startswith(b"transfer-encoding:") and b"chunked" in line.lower():
                return None, raw_data

    if len(raw_data) > max_bytes:
        return None, raw_data

    return parse_http_request(raw_data), raw_data


def serialize_response(
    config,
    response: HttpResponse,
    request: Optional[HttpRequest],
    tls_enabled: bool,
    keep_alive: bool,
) -> bytes:
    header_map = headers.build_response_headers(
        config,
        response,
        request=request,
        tls_enabled=tls_enabled,
        keep_alive=keep_alive,
    )
    status_code = response.status_code
    if status_code not in STATUS_MESSAGES:
        status_code = 500
    status_line = f"HTTP/1.1 {status_code} {STATUS_MESSAGES[status_code]}"
    header_lines = [status_line]
    for name, value in header_map.items():
        header_lines.append(f"{name}: {value}")
    header_block = "\r\n".join(header_lines).encode("utf-8") + b"\r\n\r\n"
    if response.body and not response.should_stream():
        return header_block + response.body
    return header_block


def send_response(
    clientsocket: socket.socket,
    config,
    response: HttpResponse,
    request: Optional[HttpRequest],
    tls_enabled: bool,
    keep_alive: bool,
) -> None:
    header_bytes = serialize_response(config, response, request, tls_enabled, keep_alive)
    clientsocket.sendall(header_bytes)
    if response.should_stream() and response.file_path:
        with open(response.file_path, "rb") as stream_file:
            while True:
                chunk = stream_file.read(65536)
                if not chunk:
                    break
                clientsocket.sendall(chunk)
    elif response.body and response.should_stream():
        clientsocket.sendall(response.body)


def handle_connection(
    clientsocket: socket.socket,
    config,
    client_address,
    tls_enabled: bool = False,
) -> None:
    keep_alive_enabled = True

    try:
        clientsocket.settimeout(config["request_timeout_seconds"])
        while keep_alive_enabled:
            request_method = "-"
            request_path = "-"
            status_code = 500

            request, _raw = read_request(clientsocket, config)
            if request is None:
                if _raw and b"transfer-encoding:" in _raw.lower():
                    status_code = 400
                    response = HttpResponse(
                        status_code=400,
                        body=b"Chunked transfer encoding is not supported",
                        headers={"Content-Type": "text/plain; charset=utf-8"},
                    )
                    send_response(clientsocket, config, response, None, tls_enabled, False)
                    logutil.write_access_log(
                        config, client_address, "-", "-", status_code
                    )
                break

            request_method = request.method
            request_path = request.path
            response = handlers.handle_request(config, request, client_address, tls_enabled)
            status_code = response.status_code
            keep_alive_enabled = request.wants_keep_alive
            send_response(
                clientsocket,
                config,
                response,
                request,
                tls_enabled,
                keep_alive_enabled,
            )
            logutil.write_access_log(
                config,
                client_address,
                request_method,
                request_path,
                status_code,
            )

            if not keep_alive_enabled:
                break
    except socket.timeout:
        logutil.write_error_log(config, f"Request timeout from {client_address}")
    except OSError as exc:
        logutil.write_error_log(config, f"Socket error from {client_address}: {exc}")
    finally:
        try:
            clientsocket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        clientsocket.close()
