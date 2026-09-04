# ==============================================================================
# 🛠️  ETAPA 1: COMPILADOR Y CONSTRUCTOR DE DEPENDENCIAS (Builder Stage)
# ==============================================================================
# Sincronizado a la versión real de tu entorno analítico local (Python 3.12)
FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# ==============================================================================
# 🚀 ETAPA 2: ENTORNO DE INFERENCIA EN PRODUCCIÓN (Runtime Stage)
# ==============================================================================
FROM python:3.12-slim AS runtime

WORKDIR /app

# Importamos los binarios optimizados aislados desde la etapa anterior
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Inyectamos variables de entorno críticas para blindar OpenBLAS en sistemas embebidos de desarrollo
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=development \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1

# Pre-carga del modelo lingüístico base global en español
RUN python -m spacy download es_core_news_sm

# Mapeo de la estructura del monorepo analítico
COPY src/ ./src/
COPY models_store/ ./models_store/

EXPOSE 8000

# 🔌 ARRANQUE SEGURO: Gunicorn levantando con 1 worker elástico no bloqueante.
# Evita la duplicación redundante de tensores en RAM y anula el pánico del Exit Code 137.
CMD ["gunicorn", "src.main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "120"]
