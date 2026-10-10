FROM python:3.11-slim
WORKDIR /app
COPY common/ /app/common/
COPY flag_gate/gate_client.py /app/flag_gate/gate_client.py
COPY beacon_relay/beacon_relay.py /app/beacon_relay/beacon_relay.py
ENV PYTHONUNBUFFERED=1
CMD ["python", "/app/beacon_relay/beacon_relay.py"]
