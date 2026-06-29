#!/usr/bin/env python3


def validate_method(config, method):
    allowed = [entry.upper() for entry in config["methods"]]
    method = method.upper()
    if method not in allowed:
        return False, 405, []
    return True, 200, []


def method_extra_headers(config, method):
    method = method.upper()
    if method == "OPTIONS":
        allowed = " ".join(config["methods"])
        return [f"Allow: {allowed}"]
    return []


def serves_static_file(method):
    return method.upper() in {"GET", "HEAD"}


def is_write_method(method):
    return method.upper() in {"POST", "PUT", "DELETE"}
