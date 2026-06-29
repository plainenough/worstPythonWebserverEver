#!/usr/bin/env python3

import socket

import h2.config
import h2.connection
import h2.events

from wpwe import handlers, headers, logutil
from wpwe.request import HttpRequest
from wpwe.response import HttpResponse


def _request_from_headers(stream_headers) -> HttpRequest:
    decoded = {
        name.decode("utf-8").lower(): value.decode("utf-8")
        for name, value in stream_headers
    }
    if ":authority" in decoded and "host" not in decoded:
        decoded["host"] = decoded[":authority"]
    method = decoded.get(":method", "GET").upper()
    path = decoded.get(":path", "/")
    return HttpRequest(
        method=method,
        path=path.split("?", 1)[0],
        uri=path,
        http_version="HTTP/2",
        headers=decoded,
    )


def _send_response(
    conn: h2.connection.H2Connection,
    stream_id: int,
    config,
    response: HttpResponse,
    request: HttpRequest,
) -> None:
    header_map = headers.build_response_headers(
        config,
        response,
        request=request,
        tls_enabled=True,
        keep_alive=True,
    )
    h2_headers = [
        (":status", str(response.status_code)),
    ]
    for name, value in header_map.items():
        h2_headers.append((name.lower(), value))

    conn.send_headers(stream_id, h2_headers, end_stream=not response.should_stream() and not response.body)
    if response.body and not response.should_stream():
        conn.send_data(stream_id, response.body, end_stream=True)
    elif response.should_stream() and response.file_path:
        with open(response.file_path, "rb") as stream_file:
            while True:
                chunk = stream_file.read(65536)
                if not chunk:
                    conn.end_stream(stream_id)
                    break
                conn.send_data(stream_id, chunk, end_stream=False)


def handle_connection(
    clientsocket: socket.socket,
    config,
    client_address,
) -> None:
    request_method = "-"
    request_path = "-"
    status_code = 500

    conn = h2.connection.H2Connection(config=h2.config.H2Configuration(client_side=False))
    conn.initiate_connection()
    clientsocket.sendall(conn.data_to_send())

    try:
        clientsocket.settimeout(config["request_timeout_seconds"])
        while True:
            try:
                data = clientsocket.recv(65536)
            except socket.timeout:
                status_code = 408
                logutil.write_error_log(config, f"HTTP/2 timeout from {client_address}")
                break

            if not data:
                break

            events = conn.receive_data(data)
            for event in events:
                if isinstance(event, h2.events.RequestReceived):
                    request = _request_from_headers(event.headers)
                    request_method = request.method
                    request_path = request.path
                    response = handlers.handle_request(config, request, client_address, True)
                    status_code = response.status_code
                    _send_response(conn, event.stream_id, config, response, request)
                    clientsocket.sendall(conn.data_to_send())
                elif isinstance(event, h2.events.ConnectionTerminated):
                    return

            outbound = conn.data_to_send()
            if outbound:
                clientsocket.sendall(outbound)
    except OSError as exc:
        status_code = 500
        logutil.write_error_log(config, f"HTTP/2 socket error from {client_address}: {exc}")
    finally:
        logutil.write_access_log(
            config,
            client_address,
            request_method,
            request_path,
            status_code,
        )
        try:
            clientsocket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        clientsocket.close()
