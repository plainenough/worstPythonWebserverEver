#!/usr/bin/env python3

import argparse
import copy
import logging
import os

import yaml

DEFAULTS = {
    "server_ipv4": "0.0.0.0",
    "server_port": 8080,
    "access_log_path": "/var/log/wpwe/access.log",
    "error_log_path": "/var/log/wpwe/error.log",
    "methods": ["HEAD", "GET", "OPTIONS"],
    "server_name": "localhost",
    "user": "wpwe-data",
    "webroot": "/var/www/html",
    "custom_error_pages": False,
    "default_indexes": ["index.html", "index.htm", "index.txt"],
    "error_pages": {
        403: "docs/403.html",
        404: "docs/404.html",
        405: "docs/405.html",
        500: "docs/500.html",
        501: "docs/500.html",
    },
    "listen_mode": False,
    "file_ext": [
        "html", "htm", "png", "txt", "jpeg", "jpg", "gif", "css",
        "js", "mjs", "json", "svg", "webp", "avif", "wasm", "ico",
        "woff", "woff2", "map", "xml",
    ],
    "max_request_bytes": 65536,
    "request_timeout_seconds": 30,
    "max_workers": 100,
    "allow_symlinks": False,
    "health_check_path": "/healthz",
    "redirect_http_to_https": False,
    "tls": {
        "enabled": False,
        "cert_file": "",
        "key_file": "",
        "min_version": "TLSv1.2",
        "port": 8443,
    },
    "http2": {
        "enabled": True,
        "max_concurrent_streams": 100,
    },
    "security_headers": {
        "enabled": True,
        "x_content_type_options": "nosniff",
        "x_frame_options": "DENY",
        "referrer_policy": "strict-origin-when-cross-origin",
        "content_security_policy": "",
        "permissions_policy": "geolocation=(), microphone=(), camera=()",
        "strict_transport_security": "max-age=31536000; includeSubDomains",
    },
    "cache_control": {
        "default": "public, max-age=3600",
        "html": "no-cache",
        "htm": "no-cache",
    },
}


def _deep_merge(base, override):
    merged = copy.deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(config_path):
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as rawconfig:
        loaded = yaml.safe_load(rawconfig) or {}

    if not isinstance(loaded, dict):
        raise ValueError("Config file must contain a YAML mapping")

    config = _deep_merge(DEFAULTS, loaded)
    config["server_working_dir"] = os.path.dirname(os.path.realpath(__file__))
    config["methods"] = [method.upper() for method in config["methods"]]
    config["webroot"] = os.path.realpath(config["webroot"])
    config["error_pages"] = {
        int(code): path for code, path in config["error_pages"].items()
    }
    config["max_request_bytes"] = int(config["max_request_bytes"])
    config["request_timeout_seconds"] = float(config["request_timeout_seconds"])
    config["max_workers"] = int(config["max_workers"])
    config["allow_symlinks"] = bool(config["allow_symlinks"])
    config["redirect_http_to_https"] = bool(config["redirect_http_to_https"])
    config["http2"]["max_concurrent_streams"] = int(
        config["http2"]["max_concurrent_streams"]
    )
    return config


def setup_logging(debug_count):
    levels = [logging.INFO, logging.DEBUG]
    level = levels[min(len(levels) - 1, debug_count)]
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def main():
    parser = argparse.ArgumentParser(
        description="worstPythonWebserverEver - production static HTTP server",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="count",
        default=0,
        help="Increase logging verbosity (use twice for DEBUG)",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="./config.yaml",
        help="Path to the YAML config file",
    )
    args = parser.parse_args()
    setup_logging(args.debug)
    config = load_config(args.config)
    return args, config


if __name__ == "__main__":
    print("Run with: python3 -m wpwe -c /path/to/config.yaml")
    raise SystemExit(1)
