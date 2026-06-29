#!/usr/bin/env python3

import logging
import os
import pwd
import signal
import socket
import ssl
import threading
from concurrent.futures import ThreadPoolExecutor

from wpwe import config, http11, http2


class ServerState:
    def __init__(self):
        self.shutdown_event = threading.Event()
        self.executor = None
        self.sockets = []


def drop_privileges(server_config):
    username = server_config.get("user")
    if not username:
        return

    try:
        user_info = pwd.getpwnam(username)
    except KeyError:
        logging.warning("Configured user %r not found; continuing as current user", username)
        return

    if user_info.pw_uid == 0:
        logging.warning("Refusing to drop privileges to root")
        return

    os.setgid(user_info.pw_gid)
    os.setgroups([user_info.pw_gid])
    os.setuid(user_info.pw_uid)
    logging.info("Dropped privileges to user %s", username)


def create_listener(server_config, host, port):
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind((host, port))
    serversocket.listen(128)
    return serversocket


def build_ssl_context(server_config):
    tls_config = server_config["tls"]
    cert_file = tls_config["cert_file"]
    key_file = tls_config["key_file"]
    if not cert_file or not key_file:
        raise ValueError("tls.cert_file and tls.key_file are required when TLS is enabled")

    min_version = tls_config.get("min_version", "TLSv1.2")
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    version_map = {
        "TLSv1.2": ssl.TLSVersion.TLSv1_2,
        "TLSv1.3": ssl.TLSVersion.TLSv1_3,
    }
    context.minimum_version = version_map.get(min_version, ssl.TLSVersion.TLSv1_2)
    context.load_cert_chain(certfile=cert_file, keyfile=key_file)

    alpn = ["http/1.1"]
    if server_config["http2"].get("enabled", True):
        alpn.insert(0, "h2")
    context.set_alpn_protocols(alpn)
    return context


def connection_worker(server_config, clientsocket, client_address, tls_enabled, ssl_context):
    if tls_enabled and ssl_context is not None:
        try:
            clientsocket = ssl_context.wrap_socket(clientsocket, server_side=True)
        except ssl.SSLError as exc:
            logging.debug("TLS handshake failed from %s: %s", client_address, exc)
            clientsocket.close()
            return

        negotiated = clientsocket.selected_alpn_protocol()
        if negotiated == "h2" and server_config["http2"].get("enabled", True):
            http2.handle_connection(clientsocket, server_config, client_address)
            return

    http11.handle_connection(clientsocket, server_config, client_address, tls_enabled)


def accept_loop(server_config, state, serversocket, tls_enabled, ssl_context):
    while not state.shutdown_event.is_set():
        try:
            serversocket.settimeout(1.0)
            clientsocket, client_address = serversocket.accept()
        except socket.timeout:
            continue
        except OSError:
            if state.shutdown_event.is_set():
                break
            raise

        state.executor.submit(
            connection_worker,
            server_config,
            clientsocket,
            client_address,
            tls_enabled,
            ssl_context,
        )


def install_signal_handlers(state):
    def _handle_signal(signum, _frame):
        logging.info("Received signal %s, shutting down", signum)
        state.shutdown_event.set()

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)


def main():
    _args, server_config = config.main()
    state = ServerState()
    state.executor = ThreadPoolExecutor(max_workers=server_config["max_workers"])
    install_signal_handlers(state)

    ssl_context = None
    if server_config["tls"]["enabled"]:
        ssl_context = build_ssl_context(server_config)

    plain_socket = create_listener(
        server_config,
        server_config["server_ipv4"],
        server_config["server_port"],
    )
    state.sockets.append(plain_socket)

    tls_socket = None
    if server_config["tls"]["enabled"]:
        tls_socket = create_listener(
            server_config,
            server_config["server_ipv4"],
            server_config["tls"]["port"],
        )
        state.sockets.append(tls_socket)

    drop_privileges(server_config)

    logging.info(
        "Serving HTTP on http://%s:%s (webroot: %s)",
        server_config["server_ipv4"],
        server_config["server_port"],
        server_config["webroot"],
    )
    if tls_socket is not None:
        logging.info(
            "Serving HTTPS on https://%s:%s (HTTP/2: %s)",
            server_config["server_ipv4"],
            server_config["tls"]["port"],
            server_config["http2"].get("enabled", True),
        )

    threads = [
        threading.Thread(
            target=accept_loop,
            args=(server_config, state, plain_socket, False, None),
            daemon=True,
        )
    ]
    if tls_socket is not None:
        threads.append(
            threading.Thread(
                target=accept_loop,
                args=(server_config, state, tls_socket, True, ssl_context),
                daemon=True,
            )
        )

    for thread in threads:
        thread.start()

    try:
        while not state.shutdown_event.is_set():
            state.shutdown_event.wait(timeout=1.0)
    finally:
        logging.info("Draining worker pool")
        for sock in state.sockets:
            try:
                sock.close()
            except OSError:
                pass
        state.executor.shutdown(wait=True, cancel_futures=False)
        logging.info("Shutdown complete")


if __name__ == "__main__":
    print("Run with: python3 -m wpwe -c /path/to/config.yaml")
    raise SystemExit(1)
