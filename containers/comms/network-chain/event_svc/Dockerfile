FROM python:3.11-slim
WORKDIR /app
COPY common/ /app/common/
COPY event_svc/event_svc.py /app/event_svc/event_svc.py
ENV PYTHONUNBUFFERED=1
CMD ["python", "/app/event_svc/event_svc.py"]
