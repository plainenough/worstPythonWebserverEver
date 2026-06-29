FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY wpwe/ ./wpwe/
COPY example_site/ ./example_site/
COPY config.example.yaml ./config.yaml

RUN mkdir -p /var/log/wpwe

EXPOSE 8080

CMD ["python3", "-m", "wpwe", "-c", "/app/config.yaml"]

LABEL version="1.1.0"
LABEL description="Minimal Python HTTP server"
LABEL maintainer="derrick@tosstalk.com"
