import logging
from fastapi import APIRouter, BackgroundTasks, status, HTTPException
from src.infraestructura.web.whatsappSchema import WhatsAppWebhookSchema
from src.infraestructura.web.webchatSchema import WebchatMessageSchema
from src.domain.chatbotOrchestrator import ChatbotOrchestrator
# 🪄 INYECCIÓN DEL ALGORITMO RATE LIMITER PERIMETRAL
from src.infraestructura.web.rateLimiter import TokenBucketLimiter

router = APIRouter(prefix="/api/v1", tags=["Ingesta Omnicanal Hardened"])
logger = logging.getLogger("talos_chatbot_backend")

orchestrator = ChatbotOrchestrator()
# Instanciar el Token Bucket (Permite maximo 10 llamadas, recupera 2 por segundo)
rate_limiter = TokenBucketLimiter(capacity=10, refill_rate=2.0)

@router.post("/whatsapp/webhook", status_code=status.HTTP_202_ACCEPTED)
async def handle_whatsapp_inbound(payload: WhatsAppWebhookSchema, background_tasks: BackgroundTasks):
    extraction = payload.entry.changes.value.messages
    client_id = extraction.from_field
    
    # 🧮 ALGOGUARD: Evaluacion O(1) del Limitador antes de tocar la memoria RAM
    if not rate_limiter.is_request_allowed(client_id):
        raise HTTPException(status_code=429, detail="Rate Limit Exceeded: Ingestion pipeline flooded")

    background_tasks.add_task(orchestrator.execute_cognitive_pipeline, client_id, extraction.text.body, extraction.timestamp)
    return {"status": "ACCEPTED", "correlationId": f"CORR-{extraction.timestamp}-9843", "canalUsuarioId": client_id}

@router.post("/webchat/message", status_code=status.HTTP_202_ACCEPTED)
async def handle_webchat_inbound(payload: WebchatMessageSchema, background_tasks: BackgroundTasks):
    client_id = payload.clientId
    msg_payload = payload.messagePayload
    
    # 🧮 ALGOGUARD: Evaluacion O(1) del Limitador antes de tocar la memoria RAM
    if not rate_limiter.is_request_allowed(client_id):
        raise HTTPException(status_code=429, detail="Too Many Requests: Token Bucket exhausted")

    logger.info(f"💻 [WEB_INGEST] Request verificado por el Token Bucket Limiter para: {client_id}")
    
    background_tasks.add_task(orchestrator.execute_cognitive_pipeline, client_id, msg_payload.text, msg_payload.timestamp)
    return {"status": "ACCEPTED", "correlationId": f"CORR-{msg_payload.timestamp}-9843", "canalUsuarioId": client_id}
