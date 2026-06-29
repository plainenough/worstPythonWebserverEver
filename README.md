# worstPythonWebserverEver

A production-capable static HTTP server in Python — still proudly minimal, now with modern protocols.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config.example.yaml config.yaml
python3 -m wpwe -c config.yaml
```

Visit `http://127.0.0.1:8080/` (or your configured port).

## Usage

```bash
python3 -m wpwe -c config.yaml
python3 -m wpwe -c config.yaml -d      # verbose logging
python3 -m wpwe -c config.yaml -dd     # debug logging
pytest
```

## Features (v2.0)

- **HTTP/1.1** with keep-alive, Host validation, streaming, and request limits
- **HTTPS + HTTP/2** when `tls.enabled: true` (ALPN negotiates h2 or http/1.1)
- **Modern static assets** — HTML5, JS modules, CSS, SVG, WebP, WASM, fonts
- **Security headers** — HSTS (HTTPS), CSP (optional), X-Frame-Options, etc.
- **Operational controls** — worker pool, graceful shutdown, health check path, access/error logs

## TLS / HTTP/2

Generate or install certificates, then enable TLS in `config.yaml`:

```yaml
tls:
  enabled: true
  cert_file: /path/to/fullchain.pem
  key_file: /path/to/privkey.pem
  port: 8443
http2:
  enabled: true
```

Test:

```bash
curl -k https://localhost:8443/
curl -k --http2 https://localhost:8443/ -v
```

## Production checklist

1. Terminate TLS with valid certificates (Let's Encrypt, etc.)
2. Run behind a reverse proxy if you need HTTP/3 (QUIC) — use Caddy, nginx, or Cloudflare
3. Set `server_name` to your domain and configure `security_headers`
4. Run as a non-root user (`user` in config) after binding to privileged ports via systemd `AmbientCapabilities` or port forwarding
5. Monitor `access_log_path` and `error_log_path`
6. Use `health_check_path` (`/healthz` by default) for load balancers

## Docker

```bash
docker build -f docker/Dockerfile -t wpwe .
docker run --rm -p 8080:8080 -p 8443:8443 wpwe
```

Mount your own webroot/certs:

```bash
docker run --rm -p 8080:8080 \
  -v "$PWD/example_site:/app/example_site" \
  -v "$PWD/config.yaml:/app/config.yaml" \
  wpwe
```

## Out of scope

- HTTP/3 / QUIC (use a reverse proxy)
- Dynamic apps (WSGI/ASGI/CGI)
- Full POST/PUT/DELETE handlers (returns 501)

## Notes

This is a real static file server now, but it is still not nginx. Use at your own risk — with moderately less bravery than before.
