# ==============================================================================
# Autor: EdithBG <edithbg@corporativo.internal>
# Componente: Contenedor Inmutable Multi-Cloud (core-qa-engine)
# ==============================================================================

FROM python:3.12-slim-bookworm

# 🔌 Instalar Graphviz y dependencias del sistema operativo requeridas para los diagramas vectoriales
RUN apt-get update && apt-get install -y --no-install-recommends \
    graphviz \
    libgraphviz-dev \
    gcc \
    libc-dev \
    && rm -rf /var/lib/apt/lists/*

# Configurar el directorio de trabajo seguro
WORKDIR /app

# Copiar el manifiesto de dependencias e instalar el ecosistema de Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente y los scripts analíticos al contenedor
COPY src/ ./src
COPY scripts/ ./scripts
COPY tests/ ./tests

# Crear los directorios volátiles para la persistencia efímera de reportes y diagramas
RUN mkdir -p data/diagramas data/bronze/reports data/bronze/logs/qa

# Configurar variables de entorno optimizadas para la ejecución en la nube
ENV PYTHONUNBUFFERED=1
ENV PORT=9000

# Exponer el puerto perimetral privado de control de calidad
EXPOSE 9000

# Comando por defecto para arrancar la API Maestra
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "9000"]