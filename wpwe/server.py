#!/usr/bin/env python3

import logging
import os
import pwd
import socket
import threading

from wpwe import config, receive


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


def create_socket(server_config):
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind((server_config["server_ipv4"], server_config["server_port"]))
    serversocket.listen(128)
    return serversocket


def main():
    args, loaded_config = config.main()
    serversocket = create_socket(loaded_config)
    drop_privileges(loaded_config)
    logging.info(
        "Serving on http://%s:%s (webroot: %s)",
        loaded_config["server_ipv4"],
        loaded_config["server_port"],
        loaded_config["webroot"],
    )

    try:
        while True:
            clientsocket, address = serversocket.accept()
            worker = threading.Thread(
                target=receive.handle_request,
                args=(args, loaded_config, clientsocket, address),
                daemon=True,
            )
            worker.start()
    except KeyboardInterrupt:
        logging.info("Shutting down")
    finally:
        serversocket.close()


if __name__ == "__main__":
    print("Run with: python3 -m wpwe -c /path/to/config.yaml")
    raise SystemExit(1)
