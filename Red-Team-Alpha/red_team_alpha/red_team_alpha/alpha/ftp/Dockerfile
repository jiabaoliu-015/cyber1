FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ftp_server.py .
COPY ftp_share/ ./ftp_share/

EXPOSE 2121 30000-30009
CMD ["python", "-u", "ftp_server.py"]
