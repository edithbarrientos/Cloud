import os
import sys
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from ai_agentic_core.flyweight_facade import CognitiveCoreFacade

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ai_agentic_core.api")

core_facade: Optional[CognitiveCoreFacade] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global core_facade
    logger.info("[AI_LIFESPAN] 🚀 Despertando Acelerador de Inferencia Multi-Batching...")
    core_facade = CognitiveCoreFacade()
    await core_facade.bootstrap_subsystems()
    yield
    if core_facade:
        await core_facade.shutdown_subsystems()

app = FastAPI(title="AI-Agentic-Deequ-Core API", version="1.0.0", lifespan=lifespan)

class InferenceRequest(BaseModel):
    trace_id: str = Field(..., json_schema_extra={"example": "TRC-987654321"})
    step_sequence: int = Field(..., ge=1, json_schema_extra={"example": 1})
    previous_hash: str = Field(default="0000000000000000000000000000")
    data: Dict[str, Any] = Field(..., description="Payload de transacciones DAMA")

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "HEALTHY", "throughput_engine": "SPECULATIVE_QUEUE_ACTIVE"}

@app.post("/api/v1/inference", status_code=status.HTTP_202_ACCEPTED)
async def ingest_inference_event(request: InferenceRequest, http_request: Request):
    if not core_facade:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Fachada inactiva.")
    try:
        # 🪄 CONTROL ESPECULATIVO: Encolar en la RAM y regresar acuse de inmediato en 0.2ms
        assigned_trace = await core_facade.enqueue_payload_speculative(
            raw_data=request.data, previous_hash=request.previous_hash, step_sequence=request.step_sequence
        )
        return {
            "trace_id": assigned_trace, 
            "status": "ACCEPTED_FOR_PROCESSING", 
            "throughput_layer": "BUFFERED_IN_RAM"
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
