FROM python:3.11-slim
WORKDIR /app
COPY common/ /app/common/
COPY flag_gate/gate_client.py /app/flag_gate/gate_client.py
COPY sentry_watcher/sentry_watcher.py /app/sentry_watcher/sentry_watcher.py
ENV PYTHONUNBUFFERED=1
CMD ["python", "/app/sentry_watcher/sentry_watcher.py"]
