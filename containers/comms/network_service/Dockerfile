FROM python:3.13-slim

WORKDIR /app

# Install minimal dependencies — none required beyond standard library
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Copy Uplink server
COPY auth_server.py /app/auth_server.py

# Entrypoint: serve on port 5432
ENTRYPOINT ["python", "/app/auth_server.py", "--host", "0.0.0.0", "--port", "5432"]