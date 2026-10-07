FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY app.py /app/app.py

# Passcode / flag / next-stage creds can be overridden at run time.
ENV PORT=8095 \
    ARIA_PASSCODE="ADRJ-6UDP-BRHD" \
    ARIA_FLAG="CITS3006{LFJkvM1LVy}" \
    ARIA_NEXT_USER="sysmaint" \
    ARIA_NEXT_PASS="ytEfgh2aCLTT" \
    ARIA_SECRET_KEY="change-this-in-prod"

EXPOSE 8095
CMD ["python", "app.py"]
