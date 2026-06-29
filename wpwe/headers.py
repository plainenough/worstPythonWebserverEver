#!/usr/bin/env python3

import os
import time

STATUS_MESSAGES = {
    200: "OK",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    500: "Internal Server Error",
    501: "Not Implemented",
}

CONTENT_TYPES = {
    "html": "text/html; charset=utf-8",
    "htm": "text/html; charset=utf-8",
    "txt": "text/plain; charset=utf-8",
    "css": "text/css; charset=utf-8",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
}


def guess_content_type(file_path):
    ext = os.path.splitext(file_path)[1].lstrip(".").lower()
    return CONTENT_TYPES.get(ext, "application/octet-stream")


def build_headers(config, status_code, body, extra_headers=None, file_path=None, content_length=None):
    if status_code not in STATUS_MESSAGES:
        status_code = 500

    if isinstance(body, str):
        body_bytes = body.encode("utf-8")
    else:
        body_bytes = body or b""

    if content_length is None:
        content_length = len(body_bytes)

    headers = [
        f"HTTP/1.1 {status_code} {STATUS_MESSAGES[status_code]}",
        "Server: worstPythonWebserverEver",
        "Action: Jackson",
        f"Date: {time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())}",
    ]

    if content_length or status_code == 200:
        headers.append(f"Content-Length: {content_length}")
    if body_bytes:
        content_type = guess_content_type(file_path or "")
        headers.append(f"Content-Type: {content_type}")
    elif file_path and content_length:
        content_type = guess_content_type(file_path)
        headers.append(f"Content-Type: {content_type}")

    if extra_headers:
        headers.extend(extra_headers)

    return headers
