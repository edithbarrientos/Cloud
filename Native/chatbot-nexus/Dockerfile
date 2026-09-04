# ==========================================
# ETAPA 1: BUILDER (Compilación y Empaquetamiento de Dependencias)
# ==========================================
FROM docker.io/library/python:3.11-slim AS builder

WORKDIR /build

# Instalar dependencias esenciales del sistema para compilar extensiones de C si es requerido
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos limpio de tu Mac Intel
COPY requirements-backend.txt .

# ⚡ VALIDACIÓN SRE COMPLETA: Instalamos las dependencias base incluyendo el paquete h2 para HTTP/2
RUN pip install --no-cache-dir --prefix=/install -r requirements-backend.txt && \
    pip install --no-cache-dir --prefix=/install h2

# Copiar la subcarpeta de fuentes corporativa hacia el entorno de compilación
COPY src/ ./src/

# Configurar el puente temporal de rutas para que el intérprete del builder localice grpc_tools
ENV PYTHONPATH=/install/lib/python3.11/site-packages

# ⚡ CORRECCIÓN DE DESTINO: Compilamos los Protocol Buffers (.proto) directamente dentro de src/
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. src/chatbot.proto

# ==========================================
# ETAPA 2: RUNNER (Entorno de Producción Ultra-Ligero Seguro)
# ==========================================
FROM docker.io/library/python:3.11-slim AS runner

# Crear un usuario del sistema sin privilegios (Estándar SRE de mínimo privilegio)
RUN useradd -u 10001 -m -s /bin/bash nexususer

WORKDIR /app

# Copiar únicamente las librerías binarias pre-instaladas del builder (Directo a /usr/local)
COPY --from=builder /install /usr/local

# ⚡ SOLUCIÓN QUIRÚRGICA: Copiamos UNICAMENTE la carpeta src (Donde vive tu código limpio y optimizado)
COPY --from=builder /build/src/ ./src/

# Asignar la propiedad absoluta de la aplicación al usuario seguro para bloquear accesos root
RUN chown -R nexususer:nexususer /app

# Configurar variables de entorno optimizadas para la ejecución asíncrona de alta densidad
ENV PYTHONPATH=/app:/app/src \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 📡 DECLARACIÓN DE TODOS LOS PUERTOS CORPORATIVOS
EXPOSE 50051
EXPOSE 8000

# Cambiar al usuario seguro antes del encendido del hilo de Python
USER nexususer

# ⚡ EJECUCIÓN PURIFICADA: Lanzamos directamente el main optimizado de la subcarpeta src/
CMD ["python", "src/main.py"]
