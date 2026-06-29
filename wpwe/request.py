#!/usr/bin/env python3

from dataclasses import dataclass, field
from typing import Dict, Optional
from urllib.parse import unquote, urlparse


@dataclass
class HttpRequest:
    method: str
    path: str
    uri: str
    http_version: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: bytes = b""
    raw: str = ""

    @property
    def host_header(self) -> str:
        return self.headers.get("host", "")

    @property
    def host_name(self) -> str:
        host = self.host_header
        if not host:
            return ""
        return host.split(":", 1)[0].lower()

    @property
    def wants_keep_alive(self) -> bool:
        connection = self.headers.get("connection", "").lower()
        if self.http_version.upper() == "HTTP/1.0":
            return connection == "keep-alive"
        return connection != "close"


def _parse_header_lines(header_block: str) -> Dict[str, str]:
    headers: Dict[str, str] = {}
    for line in header_block.split("\r\n")[1:]:
        if not line or ":" not in line:
            continue
        name, value = line.split(":", 1)
        headers[name.strip().lower()] = value.strip()
    return headers


def parse_http_request(raw: bytes) -> Optional[HttpRequest]:
    if not raw:
        return None

    try:
        text = raw.decode("utf-8", errors="replace")
    except AttributeError:
        text = str(raw)

    if "\r\n\r\n" not in text:
        return None

    header_block, body_text = text.split("\r\n\r\n", 1)
    lines = header_block.split("\r\n")
    if not lines or not lines[0].strip():
        return None

    parts = lines[0].split()
    if len(parts) < 2:
        return None

    method = parts[0].upper()
    uri = parts[1]
    http_version = parts[2] if len(parts) > 2 else "HTTP/1.1"
    path = urlparse(uri).path or "/"
    path = unquote(path)
    headers = _parse_header_lines(header_block)
    body = body_text.encode("utf-8", errors="replace")

    return HttpRequest(
        method=method,
        path=path,
        uri=uri,
        http_version=http_version,
        headers=headers,
        body=body,
        raw=text,
    )
