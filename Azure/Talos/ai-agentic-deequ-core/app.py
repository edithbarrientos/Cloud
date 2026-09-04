import os
import sys
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

# 🪄 INYECTOR DE SCOPE PERIMETRAL MULTICAPA PARA PYTHON 3.14
# Obliga al intérprete a reconocer todas las subcarpetas del proyecto al arrancar
base_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(base_dir, "src")
ai_core_dir = os.path.join(src_dir, "ai_agentic_core")
infra_dir = os.path.join(src_dir, "infrastructure")

for folder in [src_dir, ai_core_dir, infra_dir, base_dir]:
    if folder not in sys.path:
        sys.path.insert(0, folder)

# Importaciones directas (Resueltas por el inyector superior en caliente)
from ai_agentic_core.supervisor import QualityDataSupervisor
from infrastructure.cloud_cache_provider import CloudCacheProvider

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ai_agentic_core.api")

supervisor: Optional[QualityDataSupervisor] = None
cache_provider: Optional[CloudCacheProvider] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global supervisor, cache_provider
    logger.info("[AI_LIFESPAN] 🚀 Inicializando Componentes de Inferencia de Nivel Elite...")
    cache_provider = CloudCacheProvider()
    await cache_provider.connect()
    supervisor = QualityDataSupervisor()
    logger.info("[AI_LIFESPAN] ✅ Microservicio Agéntico listo y escuchando en Puerto: 8001.")
    yield
    logger.info("[AI_LIFESPAN] 🛑 Desmantelando recursos de red...")
    if cache_provider:
        await cache_provider.disconnect()

app = FastAPI(
    title="AI-Agentic-Deequ-Core API",
    version="1.0.0",
    description="Gateway de Inferencia de Alto Rendimiento con Aceleración I/O Especulativa.",
    lifespan=lifespan
)

class InferenceRequest(BaseModel):
    trace_id: str = Field(..., example="TRC-987654321")
    step_sequence: int = Field(..., ge=1, example=1)
    previous_hash: str = Field(default="0000000000000000000000000000")
    data: Dict[str, Any] = Field(..., description="Payload de transacciones DAMA")

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "HEALTHY", "cache_layer": "CONNECTED"}

@app.post("/api/v1/inference", status_code=status.HTTP_202_ACCEPTED)
async def ingest_inference_event(request: InferenceRequest, http_request: Request):
    if not supervisor:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Núcleo cognitivo apagado.")
    try:
        response_graph = await supervisor.process_inference_ingestion(
            raw_data=request.data,
            previous_hash=request.previous_hash,
            step_sequence=request.step_sequence
        )
        return response_graph
    except Exception as e:
        logger.error(f"[API_GATEWAY_CRITICAL] Falla en pipeline de inferencia: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
