#!/usr/bin/env python3

import os
import time
from typing import Dict, Optional

from wpwe.request import HttpRequest
from wpwe.response import HttpResponse

STATUS_MESSAGES = {
    200: "OK",
    301: "Moved Permanently",
    400: "Bad Request",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    408: "Request Timeout",
    421: "Misdirected Request",
    500: "Internal Server Error",
    501: "Not Implemented",
}

CONTENT_TYPES = {
    "html": "text/html; charset=utf-8",
    "htm": "text/html; charset=utf-8",
    "txt": "text/plain; charset=utf-8",
    "css": "text/css; charset=utf-8",
    "js": "application/javascript; charset=utf-8",
    "mjs": "text/javascript; charset=utf-8",
    "json": "application/json; charset=utf-8",
    "svg": "image/svg+xml",
    "xml": "application/xml; charset=utf-8",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "webp": "image/webp",
    "avif": "image/avif",
    "wasm": "application/wasm",
    "ico": "image/x-icon",
    "woff": "font/woff",
    "woff2": "font/woff2",
    "map": "application/json; charset=utf-8",
}


def guess_content_type(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lstrip(".").lower()
    return CONTENT_TYPES.get(ext, "application/octet-stream")


def cache_control_for_path(config, file_path: Optional[str]) -> str:
    cache_rules = config.get("cache_control", {})
    default = cache_rules.get("default", "public, max-age=3600")
    if not file_path:
        return default
    ext = os.path.splitext(file_path)[1].lstrip(".").lower()
    return cache_rules.get(ext, default)


def security_headers(config, tls_enabled: bool) -> Dict[str, str]:
    settings = config.get("security_headers", {})
    if not settings.get("enabled", True):
        return {}

    headers = {}
    if settings.get("x_content_type_options"):
        headers["X-Content-Type-Options"] = settings["x_content_type_options"]
    if settings.get("x_frame_options"):
        headers["X-Frame-Options"] = settings["x_frame_options"]
    if settings.get("referrer_policy"):
        headers["Referrer-Policy"] = settings["referrer_policy"]
    if settings.get("permissions_policy"):
        headers["Permissions-Policy"] = settings["permissions_policy"]
    if settings.get("content_security_policy"):
        headers["Content-Security-Policy"] = settings["content_security_policy"]
    if tls_enabled and settings.get("strict_transport_security"):
        headers["Strict-Transport-Security"] = settings["strict_transport_security"]
    return headers


def build_response_headers(
    config,
    response: HttpResponse,
    request: Optional[HttpRequest] = None,
    tls_enabled: bool = False,
    keep_alive: bool = False,
) -> Dict[str, str]:
    status_code = response.status_code
    if status_code not in STATUS_MESSAGES:
        status_code = 500

    body_len = response.content_length
    if body_len is None:
        body_len = len(response.body)

    headers = {
        "Server": "worstPythonWebserverEver/2.0",
        "Action": "Jackson",
        "Date": time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()),
    }

    if request is not None:
        if request.wants_keep_alive and keep_alive:
            headers["Connection"] = "keep-alive"
        else:
            headers["Connection"] = "close"

    if body_len or status_code in {200, 404, 403, 500, 501}:
        headers["Content-Length"] = str(body_len)

    content_type_source = response.file_path or ""
    if response.body or response.file_path:
        headers["Content-Type"] = guess_content_type(content_type_source)
        if response.file_path:
            headers["Cache-Control"] = cache_control_for_path(config, response.file_path)

    headers.update(security_headers(config, tls_enabled))
    headers.update(response.headers)
    return headers
