FROM python:3.12-slim

WORKDIR /adc

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN python create_seed_docs.py

EXPOSE 8080

CMD ["python3", "app.py"]