# ==============================================================================
# ARCHIVO:        Dockerfile
# DESCRIPCIÓN:    Empaquetado optimizado multietapa para Azure Container Apps.
# AUTOR:          Edith BG
# FECHA:          2026-07-26
# VERSIÓN:        1.0.0
# ESTADO:         Enterprise Ready / Secure Non-Root Execution / Distroless-like Slim
# ==============================================================================

# ==============================================================================
# ETAPA 1: CONSTRUCTOR (BUILDER)
# ==============================================================================
# Usamos una imagen base oficial de Python optimizada para compilar dependencias
FROM python:3.12-slim AS builder

# Configuración de variables de entorno para una compilación limpia
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# Instalamos herramientas mínimas necesarias para desempaquetar o compilar si hiciera falta
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiamos e instalamos el catálogo depurado de dependencias fijadas en la raíz del usuario
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# ==============================================================================
# ETAPA 2: EJECUCIÓN (RUNNER)
# ==============================================================================
# Volvemos a partir de una imagen ultra-ligera y limpia para mitigar vulnerabilidades CVE
FROM python:3.12-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:${PATH}" \
    PYTHONPATH="/app"

WORKDIR /app

# 1. Práctica de Seguridad Enterprise: Creación de usuario no-raíz (Non-Root User)
# Previene que un atacante tome control total del clúster si el código se ve comprometido.
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -m -s /bin/bash appuser

# 2. Copiamos las librerías precompiladas desde la etapa de construcción
COPY --from=builder /root/.local /home/appuser/.local

# 3. Copiamos el código fuente estructurado del proyecto otorgando los permisos correctos
COPY --chown=appuser:appgroup src/ /app/src/

# Ajustamos la propiedad de las carpetas de ejecución del usuario local
RUN chown -R appuser:appgroup /app /home/appuser

# 4. Cambiamos al contexto del usuario seguro de producción
USER appuser

# Puerto estándar de escucha expuesto para el Ingress de Azure Container Apps
EXPOSE 8080

# 5. Punto de entrada de alta resiliencia usando Uvicorn corriendo el módulo HTTP
CMD ["uvicorn", "src.app.api:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]