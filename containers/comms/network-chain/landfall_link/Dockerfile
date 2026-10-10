FROM python:3.11-slim
WORKDIR /app
COPY common/ /app/common/
COPY flag_gate/gate_client.py /app/flag_gate/gate_client.py
COPY landfall_link/landfall_link.py /app/landfall_link/landfall_link.py
ENV PYTHONUNBUFFERED=1
CMD ["python", "/app/landfall_link/landfall_link.py"]
