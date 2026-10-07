# Use the Python 3.12 slim image
FROM python:3.12-slim

# Install the necessary packages
RUN apt update && apt install util-linux -y --no-install-recommends
RUN rm -rf /var/lib/apt/lists/*

# Start the web application
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ .
EXPOSE 5005

CMD cd /app && python3 app.py
