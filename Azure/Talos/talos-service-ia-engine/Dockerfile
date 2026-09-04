# ==============================================================================
# Dockerfile de Producción - Plataforma Agéntica TALOS
# Componente: talos-service-ia-engine
# ==============================================================================

# Usar una imagen oficial de Python ligera basada en Debian Slim
FROM python:3.12-slim

# Establecer variables de entorno optimizadas para contenedores en la nube
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Definir el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias del sistema mínimas necesarias para compilaciones de red
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar las librerías bloqueadas de producción
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente de la aplicación excluyendo lo marcado en .gitignore
COPY src/ ./src/

# Exponer el puerto interno privado de la subred
EXPOSE 8000

# Declarar al usuario no-root por seguridad del CISO (Evita ejecución como administrador)
USER replica

# Comando maestro para levantar el servidor asíncrono con Uvicorn en producción
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]