FROM python:3.12-slim-bookworm AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim-bookworm

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY wpwe/ ./wpwe/
COPY example_site/ ./example_site/
COPY config.example.yaml ./config.yaml

RUN useradd --create-home --shell /usr/sbin/nologin wpwe-data && \
    mkdir -p /var/log/wpwe && \
    chown -R wpwe-data:wpwe-data /app /var/log/wpwe

USER wpwe-data

EXPOSE 8080 8443

CMD ["python3", "-m", "wpwe", "-c", "/app/config.yaml"]

LABEL version="2.0.0"
LABEL description="Production-capable minimal Python static HTTP server"
LABEL maintainer="derrick@tosstalk.com"
