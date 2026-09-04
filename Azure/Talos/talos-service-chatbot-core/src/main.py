# FILENAME: talos-service-chatbot-core/src/main.py
from fastapi import FastAPI, HTTPException, status, Header, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, AsyncGenerator
import asyncio
import logging
import json
import time
import os
import jwt
import httpx  # 🚀 Driver de red asíncrono de alto rendimiento

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [%(name)s] ──► %(message)s")
logger = logging.getLogger("TalosChatbotCore")

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "orchestra_labs_ultra_secret_key_2026")
ALGORITHM = "HS256"

# 📡 DESTINO DE RED: Redirige de forma atómica a la aduana de Big Data de tu otro proyecto
GATEWAY_API_URL = "http://localhost:8000/api/v1/reason"

app = FastAPI(title="Talos Chatbot Core - Orchestrator V4", version="4.0.0")

class ChatMessagePayload(BaseModel):
    user_prompt: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=3)
    business_domain: str = Field(default="GENERAL")

# 🤖 GENERADOR COGNITIVO REUSABLE CON EMISIÓN WEBHOOK ASÍNCRONA (NIVEL 3)
async def natural_language_stream_generator(prompt: str, session_id: str, domain: str, tenant_id: str, token: str) -> AsyncGenerator[str, None]:
    logger.info(f"🔮 [Nivel 3: Orchestrator] Interpretando prompt semántico para sesión: {session_id}")
    
    # 💼 CONTRATO DE DATOS CONSOLIDADO HOMOLOGADO CON LA ADUANA DE DEEQU CORE
    consolidated_contract = {
        "kpi_target": f"pipeline-deequ-{domain.lower()}",
        "data": {
            "id": f"MSG-{int(time.time() * 1000)}-CHAT",
            "user": "chatbot_agent_cognitive",
            "status": "active",
            "raw_prompt": prompt,
            "session_id": session_id
        },
        "metadata": {
            "schema_mutation": False,
            "execution_mode": "SYNC",
            "timestamp": time.time()
        }
    }

    # ⚡ TAREA EN SEGUNDO PLANO (WEBHOOK ASÍNCRONO NO BLOQUEANTE hacia la Gateway API)
    # Se ejecuta en paralelo para inyectar a Pulsar/Flink sin retrasar los tokens del Chat del cliente
    async def fire_and_forget_webhook():
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Content-Type": "application/json", "X-Tenant-ID": tenant_id, "Authorization": f"Bearer {token}"}
                response = await client.post(GATEWAY_API_URL, json=consolidated_contract, headers=headers, timeout=5.0)
                if response.status_code == 200:
                    logger.info(f"✅ [Nivel 4: Deequ Certified] Contrato analítico inyectado con éxito al Ledger. Status: {response.status_code}")
                else:
                    logger.error(f"⚠️ [Deequ Vetoed] La aduana HTTP 8000 rechazó el contrato: {response.text}")
            except Exception as e:
                logger.error(f"💥 [Webhook Failure] Error al retransmitir el evento analítico al puerto 8000: {str(e)}")

    # Disparamos la retransmisión asíncrona de inmediato en la piscina de hilos de la RAM []
    asyncio.create_task(fire_and_forget_webhook())

    # Generamos la cascada semántica Server-Sent Events (SSE) para el Frontend del chat []
    response_text = f"Hola, soy Talos Core Pro. Procesando de forma totalmente desacoplada tu requerimiento sobre: '{prompt}'."
    for token_text in response_text.split(" "):
        yield f"data: {token_text}\n\n"
        await asyncio.sleep(0.05)
        
    logger.info(f"🏁 [NL Stream Engine] Conversación e inyección completadas con éxito.")

# 📡 ENDPOINT DE ENTRADA CON VALIDACIÓN CRIPTOGRÁFICA
@app.post("/api/v1/chat/stream")
async def stream_natural_language_response(
    payload: ChatMessagePayload,
    authorization: Optional[str] = Header(None),
    x_tenant_id: Optional[str] = Header("tenant-general")
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Falta Token Bearer.")
    try:
        token_pure = authorization.split(" ")[1]
        jwt.decode(token_pure, SECRET_KEY, algorithms=[ALGORITHM], options={"leeway": 60})
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido o caducado en aduana Chatbot.")

    logger.info(f"📥 [Incoming Conversational Request] SessionID: {payload.session_id} -> Retransmitiendo a Deequ...")
    
    return StreamingResponse(
        natural_language_stream_generator(payload.user_prompt, payload.session_id, payload.business_domain, x_tenant_id, token_pure),
        media_type="text/event-stream"
    )
