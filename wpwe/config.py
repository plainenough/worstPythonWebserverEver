#!/usr/bin/env python3

import argparse
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
    "file_ext": ["html", "htm", "png", "txt", "jpeg", "jpg", "gif", "css"],
}


def load_config(config_path):
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as rawconfig:
        loaded = yaml.safe_load(rawconfig) or {}

    if not isinstance(loaded, dict):
        raise ValueError("Config file must contain a YAML mapping")

    config = DEFAULTS.copy()
    config.update(loaded)
    config["server_working_dir"] = os.path.dirname(os.path.realpath(__file__))
    config["methods"] = [method.upper() for method in config["methods"]]
    config["webroot"] = os.path.realpath(config["webroot"])
    config["error_pages"] = {
        int(code): path for code, path in config["error_pages"].items()
    }
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
        description="worstPythonWebserverEver - minimal Python HTTP server",
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
