#!/usr/bin/env python3

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class HttpResponse:
    status_code: int
    headers: Dict[str, str] = field(default_factory=dict)
    body: bytes = b""
    file_path: Optional[str] = None
    stream_file: bool = False
    content_length: Optional[int] = None

    def should_stream(self) -> bool:
        return self.stream_file and self.file_path is not None and not self.body
