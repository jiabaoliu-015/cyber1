FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY webapp ./webapp
COPY entry ./entry
RUN mkdir -p /app/data
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "webapp.app:app", "--host", "0.0.0.0", "--port", "8080"]
