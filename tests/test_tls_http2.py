import ssl
import subprocess
import sys
import time
from pathlib import Path

import pytest

from tests.conftest import _get_free_port, _write_test_config


@pytest.fixture
def tls_certs(tmp_path):
    cert = tmp_path / "cert.pem"
    key = tmp_path / "key.pem"
    subprocess.run(
        [
            "openssl",
            "req",
            "-x509",
            "-newkey",
            "rsa:2048",
            "-nodes",
            "-keyout",
            str(key),
            "-out",
            str(cert),
            "-days",
            "1",
            "-subj",
            "/CN=localhost",
        ],
        check=True,
        capture_output=True,
    )
    return cert, key


def test_https_and_http2(tls_certs, merged_config, tmp_path):
    cert, key = tls_certs
    http_port = _get_free_port()
    tls_port = _get_free_port()
    merged = dict(merged_config)
    merged["tls"] = {
        "enabled": True,
        "cert_file": str(cert),
        "key_file": str(key),
        "min_version": "TLSv1.2",
        "port": tls_port,
    }
    config_path = tmp_path / "tls-config.yaml"
    _write_test_config(config_path, merged, http_port, tls_port=tls_port)

    proc = subprocess.Popen(
        [sys.executable, "-m", "wpwe", "-c", str(config_path)],
        cwd=str(Path(__file__).resolve().parents[1]),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(0.75)
    try:
        assert proc.poll() is None, proc.stderr.read().decode()

        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.set_alpn_protocols(["h2", "http/1.1"])

        import socket

        with socket.create_connection(("127.0.0.1", tls_port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname="localhost") as tls_sock:
                assert tls_sock.selected_alpn_protocol() in {"h2", "http/1.1"}
                if tls_sock.selected_alpn_protocol() == "h2":
                    import h2.connection
                    import h2.config
                    import h2.events

                    conn = h2.connection.H2Connection(
                        config=h2.config.H2Configuration(client_side=True)
                    )
                    conn.initiate_connection()
                    tls_sock.sendall(conn.data_to_send())
                    conn.send_headers(
                        1,
                        [
                            (":method", "GET"),
                            (":path", "/"),
                            (":authority", "localhost"),
                            (":scheme", "https"),
                        ],
                        end_stream=True,
                    )
                    tls_sock.sendall(conn.data_to_send())
                    saw_response = False
                    for _ in range(10):
                        chunk = tls_sock.recv(65536)
                        if not chunk:
                            break
                        events = conn.receive_data(chunk)
                        if any(
                            isinstance(event, (h2.events.ResponseReceived, h2.events.DataReceived))
                            for event in events
                        ):
                            saw_response = True
                            break
                    assert saw_response
                else:
                    tls_sock.sendall(
                        b"GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
                    )
                    response = tls_sock.recv(65536)
                    assert b"HTTP/1.1 200" in response
                    assert b"Strict-Transport-Security" in response
    finally:
        proc.terminate()
        proc.wait(timeout=3)
