#!/usr/bin/env python3

import os
import socket
from urllib.parse import unquote, urlparse

from wpwe import headers, logutil, method


def read_request(clientsocket, initial_data=b"", max_bytes=65536):
    data = initial_data
    while b"\r\n\r\n" not in data and len(data) < max_bytes:
        chunk = clientsocket.recv(4096)
        if not chunk:
            break
        data += chunk

    if not data or b"\r\n\r\n" not in data:
        return data

    header_block = data.split(b"\r\n\r\n", 1)[0]
    content_length = 0
    for line in header_block.split(b"\r\n"):
        if line.lower().startswith(b"content-length:"):
            try:
                content_length = int(line.split(b":", 1)[1].strip())
            except ValueError:
                content_length = 0
            break

    body_start = data.split(b"\r\n\r\n", 1)[1] if b"\r\n\r\n" in data else b""
    remaining = max(content_length - len(body_start), 0)
    while remaining > 0 and len(data) < max_bytes:
        chunk = clientsocket.recv(min(4096, remaining))
        if not chunk:
            break
        data += chunk
        remaining -= len(chunk)

    return data


def parse_request(rawreq):
    try:
        text = rawreq.decode("utf-8", errors="replace")
    except AttributeError:
        text = str(rawreq)

    lines = text.split("\r\n")
    if not lines or not lines[0].strip():
        return None

    parts = lines[0].split()
    if len(parts) < 2:
        return None

    request_method = parts[0].upper()
    uri = parts[1]
    path = urlparse(uri).path or "/"
    path = unquote(path)
    return {
        "method": request_method,
        "uri": uri,
        "path": path,
        "raw": text,
    }


def resolve_request_path(config, uri_path):
    webroot = config["webroot"]
    relative_path = uri_path.lstrip("/")
    candidate = os.path.realpath(os.path.join(webroot, relative_path))
    webroot_real = os.path.realpath(webroot)

    if candidate != webroot_real and not candidate.startswith(webroot_real + os.sep):
        return None

    if os.path.isdir(candidate):
        for index_name in config["default_indexes"]:
            index_path = os.path.join(candidate, index_name)
            if os.path.isfile(index_path):
                return index_path
        return None

    if os.path.isfile(candidate):
        return candidate

    ext = os.path.splitext(candidate)[1].lstrip(".").lower()
    if ext and ext not in config["file_ext"]:
        return None

    return candidate if os.path.isfile(candidate) else None


def load_error_page(config, status_code):
    error_path = config["error_pages"].get(status_code)
    if not error_path:
        return "EMPTY ERROR PAGE RESPONSE"

    if not config["custom_error_pages"]:
        error_path = os.path.join(config["server_working_dir"], error_path)

    try:
        with open(error_path, "r", encoding="utf-8") as error_doc:
            return error_doc.read()
    except OSError as exc:
        logutil.write_error_log(config, f"Failed to load error page {status_code}: {exc}")
        return "EMPTY ERROR PAGE RESPONSE"


TEXT_EXTENSIONS = {"html", "htm", "txt", "css"}


def read_served_file(request_path):
    ext = os.path.splitext(request_path)[1].lstrip(".").lower()
    if ext in TEXT_EXTENSIONS:
        with open(request_path, "r", encoding="utf-8") as served_file:
            return served_file.read()
    with open(request_path, "rb") as served_file:
        return served_file.read()


def get_file(config, uri_path):
    request_path = resolve_request_path(config, uri_path)
    if not request_path:
        return load_error_page(config, 404), 404, None

    try:
        return read_served_file(request_path), 200, request_path
    except PermissionError:
        return load_error_page(config, 403), 403, request_path
    except FileNotFoundError:
        return load_error_page(config, 404), 404, request_path
    except OSError as exc:
        logutil.write_error_log(config, f"Error reading {request_path}: {exc}")
        return load_error_page(config, 500), 500, request_path


def build_response(
    config,
    status_code,
    body="",
    extra_headers=None,
    file_path=None,
    content_length=None,
):
    if isinstance(body, str):
        body_bytes = body.encode("utf-8") if body else b""
    else:
        body_bytes = body or b""

    header_lines = headers.build_headers(
        config,
        status_code,
        body_bytes,
        extra_headers=extra_headers,
        file_path=file_path,
        content_length=content_length,
    )
    if body_bytes:
        return "\r\n".join(header_lines).encode("utf-8") + b"\r\n\r\n" + body_bytes
    return "\r\n".join(header_lines).encode("utf-8") + b"\r\n\r\n"


def handle_request(args, config, clientsocket, client_address):
    request_method = "-"
    request_path = "-"
    status_code = 500

    try:
        clientsocket.settimeout(30.0)
        raw_data = read_request(clientsocket)
        if not raw_data:
            return

        parsed = parse_request(raw_data)
        if not parsed:
            status_code = 400
            response = build_response(config, 400, "Bad Request")
            clientsocket.sendall(response)
            return

        request_method = parsed["method"]
        request_path = parsed["path"]

        if config["listen_mode"]:
            response = build_response(
                config,
                200,
                parsed["raw"],
                extra_headers=["Content-Type: text/plain; charset=utf-8"],
            )
            clientsocket.sendall(response)
            status_code = 200
            return

        allowed, status_code, _ = method.validate_method(config, request_method)
        if not allowed:
            body = load_error_page(config, status_code)
            response = build_response(config, status_code, body)
            clientsocket.sendall(response)
            return

        extra_headers = method.method_extra_headers(config, request_method)

        if request_method == "OPTIONS":
            response = build_response(config, 200, "", extra_headers=extra_headers)
            clientsocket.sendall(response)
            status_code = 200
            return

        if method.serves_static_file(request_method):
            body, status_code, file_path = get_file(config, request_path)
            head_length = None
            if request_method == "HEAD":
                if status_code == 200 and file_path:
                    head_length = os.path.getsize(file_path)
                body = ""
            response = build_response(
                config,
                status_code,
                body,
                extra_headers=extra_headers,
                file_path=file_path,
                content_length=head_length,
            )
            clientsocket.sendall(response)
            return

        if method.is_write_method(request_method):
            status_code = 501
            body = load_error_page(config, status_code)
            response = build_response(config, status_code, body, extra_headers=extra_headers)
            clientsocket.sendall(response)
            return

        status_code = 500
        body = load_error_page(config, status_code)
        response = build_response(config, status_code, body)
        clientsocket.sendall(response)
    except socket.timeout:
        status_code = 408
        logutil.write_error_log(config, f"Request timeout from {client_address}")
    except OSError as exc:
        status_code = 500
        logutil.write_error_log(config, f"Socket error from {client_address}: {exc}")
    finally:
        logutil.write_access_log(
            config,
            client_address,
            request_method,
            request_path,
            status_code,
        )
        try:
            clientsocket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        clientsocket.close()


def main(args, config, rawreq, client_address=("127.0.0.1", 0)):
    """Backward-compatible entry point used by tests and legacy callers."""
    parsed = parse_request(rawreq)
    if not parsed:
        return build_response(config, 400, "Bad Request")

    request_method = parsed["method"]
    request_path = parsed["path"]

    if config["listen_mode"]:
        response = build_response(
            config,
            200,
            parsed["raw"],
            extra_headers=["Content-Type: text/plain; charset=utf-8"],
        )
        logutil.write_access_log(config, client_address, request_method, request_path, 200)
        return response

    allowed, status_code, _ = method.validate_method(config, request_method)
    extra_headers = method.method_extra_headers(config, request_method)
    if not allowed:
        body = load_error_page(config, status_code)
        logutil.write_access_log(
            config, client_address, request_method, request_path, status_code
        )
        return build_response(config, status_code, body)

    if request_method == "OPTIONS":
        logutil.write_access_log(
            config, client_address, request_method, request_path, 200
        )
        return build_response(config, 200, "", extra_headers=extra_headers)

    if method.serves_static_file(request_method):
        body, status_code, file_path = get_file(config, request_path)
        head_length = None
        if request_method == "HEAD":
            if status_code == 200 and file_path:
                head_length = os.path.getsize(file_path)
            body = ""
        logutil.write_access_log(
            config, client_address, request_method, request_path, status_code
        )
        return build_response(
            config,
            status_code,
            body,
            extra_headers=extra_headers,
            file_path=file_path,
            content_length=head_length,
        )

    if method.is_write_method(request_method):
        status_code = 501
        body = load_error_page(config, status_code)
        logutil.write_access_log(
            config, client_address, request_method, request_path, status_code
        )
        return build_response(config, status_code, body, extra_headers=extra_headers)

    logutil.write_access_log(config, client_address, request_method, request_path, 500)
    return build_response(config, 500, load_error_page(config, 500))
