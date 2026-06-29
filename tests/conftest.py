#!/usr/bin/env python3

import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

import pytest


@pytest.fixture
def temp_site(tmp_path):
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text("<html><body>hello</body></html>", encoding="utf-8")
    (site / "assets").mkdir()
    (site / "assets" / "app.js").write_text("console.log('ok');", encoding="utf-8")
    return site


@pytest.fixture
def base_config(temp_site, tmp_path):
    logs = tmp_path / "logs"
    logs.mkdir()
    return {
        "server_ipv4": "127.0.0.1",
        "server_port": 0,
        "access_log_path": str(logs / "access.log"),
        "error_log_path": str(logs / "error.log"),
        "methods": ["HEAD", "GET", "OPTIONS", "POST"],
        "server_name": "localhost",
        "webroot": str(temp_site),
        "custom_error_pages": False,
        "default_indexes": ["index.html"],
        "error_pages": {
            403: "docs/403.html",
            404: "docs/404.html",
            405: "docs/405.html",
            500: "docs/500.html",
            501: "docs/500.html",
        },
        "listen_mode": False,
        "file_ext": ["html", "js", "css", "txt"],
        "max_request_bytes": 65536,
        "request_timeout_seconds": 5,
        "max_workers": 20,
        "allow_symlinks": False,
        "health_check_path": "/healthz",
        "redirect_http_to_https": False,
        "tls": {
            "enabled": False,
            "cert_file": "",
            "key_file": "",
            "min_version": "TLSv1.2",
            "port": 0,
        },
        "http2": {"enabled": True, "max_concurrent_streams": 100},
        "security_headers": {
            "enabled": True,
            "x_content_type_options": "nosniff",
            "x_frame_options": "DENY",
            "referrer_policy": "strict-origin-when-cross-origin",
            "content_security_policy": "",
            "permissions_policy": "geolocation=()",
            "strict_transport_security": "max-age=31536000",
        },
        "cache_control": {"default": "public, max-age=3600", "html": "no-cache"},
    }


@pytest.fixture
def merged_config(base_config):
    from wpwe.config import DEFAULTS, _deep_merge

    config = _deep_merge(DEFAULTS, base_config)
    config["server_working_dir"] = str(Path(__file__).resolve().parents[1] / "wpwe")
    config["methods"] = [method.upper() for method in config["methods"]]
    config["webroot"] = os.path.realpath(config["webroot"])
    config["error_pages"] = {int(code): path for code, path in config["error_pages"].items()}
    return config


def _get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _write_test_config(config_path, merged_config, port, tls_port=None):
    import yaml

    payload = dict(merged_config)
    payload["server_port"] = port
    if tls_port is not None:
        payload["tls"] = dict(payload["tls"])
        payload["tls"]["port"] = tls_port
    config_path.write_text(yaml.safe_dump(payload), encoding="utf-8")


@pytest.fixture
def running_server(merged_config, tmp_path):
    port = _get_free_port()
    config_path = tmp_path / "config.yaml"
    _write_test_config(config_path, merged_config, port)

    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "wpwe",
            "-c",
            str(config_path),
        ],
        cwd=str(Path(__file__).resolve().parents[1]),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(0.5)
    if proc.poll() is not None:
        stderr = proc.stderr.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Server failed to start: {stderr}")
    yield port, proc
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()


def http_request(port, request_bytes):
    with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
        sock.sendall(request_bytes)
        chunks = []
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                break
            chunks.append(chunk)
            if b"\r\n\r\n" in b"".join(chunks):
                break
        return b"".join(chunks)
