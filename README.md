# worstPythonWebserverEver

A deliberately minimal Python HTTP server — rebuilt to actually match its config.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config.example.yaml config.yaml
python3 -m wpwe -c config.yaml
```

Visit `http://127.0.0.1:8080/` (or whatever `server_port` you configured).

## Usage

```bash
python3 -m wpwe -c /path/to/config.yaml
python3 -m wpwe -c config.yaml -d      # verbose logging
python3 -m wpwe -c config.yaml -dd     # debug logging
```

## Config

See `config.example.yaml` and `wpwe/docs/config-template.yaml` for available options.

Supported behavior:

- **GET** — serve files from `webroot` with directory index fallback
- **HEAD** — same as GET without a response body
- **OPTIONS** — returns an `Allow` header listing configured methods
- **POST / PUT / DELETE** — allowed if listed in `methods`, responds with `501 Not Implemented`
- **listen_mode** — echo the raw request back instead of serving files
- **access_log_path** / **error_log_path** — Apache-style access log and error log
- **error_pages** — custom HTML for 403, 404, 405, 500, and 501 responses

Paths are resolved under `webroot` with basic traversal protection.

## Docker

```bash
docker build -f docker/Dockerfile -t wpwe .
docker run --rm -p 8080:8080 wpwe
```

## Notes

This is still not a production web server. It is closer to what the original config promised: logging, method handling, safer config loading, and concurrent request handling via threads.

Use at your own risk — but with slightly less bravery than before.
