FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Exponemos AMBOS puertos: 8000 (FastAPI UI) y 50051 (gRPC)
EXPOSE 8000
EXPOSE 50051

CMD ["granian", "main:app", "--interface", "asgi", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
