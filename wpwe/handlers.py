#!/usr/bin/env python3

import os
from typing import Optional, Tuple

from wpwe import logutil, method
from wpwe.request import HttpRequest
from wpwe.response import HttpResponse

TEXT_EXTENSIONS = {"html", "htm", "txt", "css", "js", "mjs", "json", "svg", "xml", "map"}
STREAM_THRESHOLD = 65536


def validate_host(config, request: HttpRequest) -> Optional[HttpResponse]:
    expected = config.get("server_name", "").lower()
    if not expected:
        return None

    host_header = request.host_header.lower()
    if not host_header:
        return None

    host_name = request.host_name
    allowed_names = {expected, f"{expected}.local"}
    if expected == "localhost":
        allowed_names.update({"localhost", "127.0.0.1"})

    if host_name in allowed_names or host_header.split(":", 1)[0] in allowed_names:
        return None

    return HttpResponse(
        status_code=421,
        body=b"Misdirected Request",
        headers={"Content-Type": "text/plain; charset=utf-8"},
    )


def safe_join(webroot: str, uri_path: str, allow_symlinks: bool) -> Optional[str]:
    relative = uri_path.lstrip("/")
    if ".." in relative.split("/"):
        return None

    candidate = os.path.normpath(os.path.join(webroot, relative))
    webroot_norm = os.path.normpath(webroot)
    if candidate != webroot_norm and not candidate.startswith(webroot_norm + os.sep):
        return None

    if not allow_symlinks:
        probe = webroot_norm
        for part in relative.split("/"):
            if not part:
                continue
            probe = os.path.join(probe, part)
            if os.path.islink(probe):
                link_target = os.path.realpath(probe)
                if link_target != os.path.normpath(probe) and not link_target.startswith(
                    webroot_norm + os.sep
                ):
                    return None

    return candidate


def resolve_request_path(config, uri_path: str) -> Optional[str]:
    webroot = config["webroot"]
    candidate = safe_join(webroot, uri_path, config.get("allow_symlinks", False))
    if candidate is None:
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


def load_error_page(config, status_code: int) -> bytes:
    error_path = config["error_pages"].get(status_code)
    if not error_path:
        return b"EMPTY ERROR PAGE RESPONSE"

    if not config["custom_error_pages"]:
        error_path = os.path.join(config["server_working_dir"], error_path)

    try:
        with open(error_path, "r", encoding="utf-8") as error_doc:
            return error_doc.read().encode("utf-8")
    except OSError as exc:
        logutil.write_error_log(config, f"Failed to load error page {status_code}: {exc}")
        return b"EMPTY ERROR PAGE RESPONSE"


def read_served_file(request_path: str) -> Tuple[bytes, bool]:
    ext = os.path.splitext(request_path)[1].lstrip(".").lower()
    file_size = os.path.getsize(request_path)
    if file_size >= STREAM_THRESHOLD and ext not in TEXT_EXTENSIONS:
        return b"", True

    if ext in TEXT_EXTENSIONS:
        with open(request_path, "r", encoding="utf-8") as served_file:
            return served_file.read().encode("utf-8"), False

    with open(request_path, "rb") as served_file:
        return served_file.read(), False


def get_file(config, uri_path: str) -> HttpResponse:
    request_path = resolve_request_path(config, uri_path)
    if not request_path:
        return HttpResponse(
            status_code=404,
            body=load_error_page(config, 404),
            headers={"Content-Type": "text/html; charset=utf-8"},
        )

    try:
        body, should_stream = read_served_file(request_path)
        if should_stream:
            return HttpResponse(
                status_code=200,
                file_path=request_path,
                stream_file=True,
                content_length=os.path.getsize(request_path),
            )
        return HttpResponse(
            status_code=200,
            body=body,
            file_path=request_path,
            content_length=len(body),
        )
    except PermissionError:
        return HttpResponse(
            status_code=403,
            body=load_error_page(config, 403),
            headers={"Content-Type": "text/html; charset=utf-8"},
        )
    except FileNotFoundError:
        return HttpResponse(
            status_code=404,
            body=load_error_page(config, 404),
            headers={"Content-Type": "text/html; charset=utf-8"},
        )
    except OSError as exc:
        logutil.write_error_log(config, f"Error reading {request_path}: {exc}")
        return HttpResponse(
            status_code=500,
            body=load_error_page(config, 500),
            headers={"Content-Type": "text/html; charset=utf-8"},
        )


def handle_request(
    config,
    request: HttpRequest,
    client_address,
    tls_enabled: bool = False,
) -> HttpResponse:
    health_path = config.get("health_check_path", "/healthz")
    if request.path == health_path and request.method == "GET":
        return HttpResponse(
            status_code=200,
            body=b"ok",
            headers={"Content-Type": "text/plain; charset=utf-8"},
        )

    host_error = validate_host(config, request)
    if host_error is not None:
        return host_error

    if (
        not tls_enabled
        and config.get("redirect_http_to_https")
        and config["tls"]["enabled"]
    ):
        tls_port = int(config["tls"]["port"])
        host = config["server_name"]
        if tls_port == 443:
            location = f"https://{host}{request.path}"
        else:
            location = f"https://{host}:{tls_port}{request.path}"
        return HttpResponse(
            status_code=301,
            headers={"Location": location, "Content-Type": "text/plain; charset=utf-8"},
            body=b"",
            content_length=0,
        )

    if config["listen_mode"]:
        return HttpResponse(
            status_code=200,
            body=request.raw.encode("utf-8"),
            headers={"Content-Type": "text/plain; charset=utf-8"},
        )

    allowed, status_code, _ = method.validate_method(config, request.method)
    if not allowed:
        return HttpResponse(
            status_code=status_code,
            body=load_error_page(config, status_code),
            headers={"Content-Type": "text/html; charset=utf-8"},
        )

    extra = method.method_extra_headers(config, request.method)
    extra_headers = {}
    for header in extra:
        if ":" in header:
            name, value = header.split(":", 1)
            extra_headers[name.strip()] = value.strip()

    if request.method == "OPTIONS":
        return HttpResponse(status_code=200, headers=extra_headers, content_length=0)

    if method.serves_static_file(request.method):
        response = get_file(config, request.path)
        if request.method == "HEAD":
            if response.status_code == 200 and response.file_path:
                response.content_length = os.path.getsize(response.file_path)
            response.body = b""
            response.stream_file = False
        response.headers.update(extra_headers)
        return response

    if method.is_write_method(request.method):
        return HttpResponse(
            status_code=501,
            body=load_error_page(config, 501),
            headers={"Content-Type": "text/html; charset=utf-8", **extra_headers},
        )

    return HttpResponse(
        status_code=500,
        body=load_error_page(config, 500),
        headers={"Content-Type": "text/html; charset=utf-8"},
    )
