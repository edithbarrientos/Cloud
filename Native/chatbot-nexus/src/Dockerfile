FROM python:3.11-alpine

# 1. Instalar cabeceras esenciales de Linux para compilar sockets binarios rápidos
RUN apk add --no-cache gcc musl-dev linux-headers libffi-dev g++ make

WORKDIR /app

# 2. 🚫 PURGA ARQUITECTÓNICA TOTAL: Eliminados uvicorn, gunicorn y fastapi de raíz.
# Solo se instalan las capas de transporte distribuido puro y telemetría.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir grpcio grpcio-tools redis psutil httpx pydantic pydantic-settings

# 3. Copiar tu lógica real de desarrollo
COPY . .

ENV PYTHONPATH="/app:/app/src"

# Abrir exclusivamente la compuerta binaria nativa gRPC sobre HTTP/2
EXPOSE 50051

# Arrancar el bucle de eventos distribuidos puro de tu orquestador central
CMD ["python", "src/main.py"]
