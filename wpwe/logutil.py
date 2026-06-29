#!/usr/bin/env python3

import logging
import os
from datetime import datetime, timezone


def ensure_log_dir(log_path):
    log_dir = os.path.dirname(log_path)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)


def write_access_log(config, client_address, method, path, status_code):
    log_path = config["access_log_path"]
    ensure_log_dir(log_path)
    client_ip = client_address[0] if client_address else "-"
    timestamp = datetime.now(timezone.utc).strftime("%d/%b/%Y:%H:%M:%S +0000")
    line = f'{client_ip} - - [{timestamp}] "{method} {path} HTTP/1.1" {status_code} -\n'
    with open(log_path, "a", encoding="utf-8") as logfile:
        logfile.write(line)


def write_error_log(config, message):
    log_path = config["error_log_path"]
    ensure_log_dir(log_path)
    timestamp = datetime.now(timezone.utc).isoformat()
    line = f"[{timestamp}] {message}\n"
    with open(log_path, "a", encoding="utf-8") as logfile:
        logfile.write(line)
    logging.error(message)
