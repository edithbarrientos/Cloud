# ==============================================================================
# 🏢 AUTHOR      : EdithBG (ai-agentic-deequ-core Senior Cloud Architect)
# 🛡️ GOVERNANCE  : Multi-Stage Secure & High-Performance O(1) Docker Architecture
# ==============================================================================

# FASE 1: BUILDER (Fase de Compilación Pesada)
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar sockets y C++
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar manifiesto de dependencias e instalar en un directorio aislado
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# FASE 2: RUNTIME (Imagen Final de Producción Pluma y Segura)
FROM python:3.12-slim-bookworm AS runtime

WORKDIR /app

# Copiar las librerías precompiladas desde la fase Builder
COPY --from=builder /root/.local /root/.local
COPY . .

# Configurar variables de entorno estructurales para optimización de Python
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ACTIVE_CLOUD_PROVIDER=azure

# Exponer el puerto binario multiplexado de gRPC
EXPOSE 50051

# 🛡️ HARDENING SEGURIDAD: Crear un usuario no privilegido (Cumplimiento CIS Benchmark)
# Evita que si el contenedor sufre un ataque, puedan escalar privilegios al nodo de AKS
RUN groupadd -g 10001 deequgroup && \
    useradd -u 10001 -g deequgroup -m deequuser && \
    chown -R deequuser:deequgroup /app

USER 10001

# Comando de arranque nativo que gatilla el enjambre multiproceso
CMD ["python", "src/grpc_server.py"]
