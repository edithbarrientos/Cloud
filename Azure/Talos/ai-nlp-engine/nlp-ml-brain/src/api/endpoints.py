from fastapi import APIRouter, Request, Response, status, Header, BackgroundTasks
from pydantic import BaseModel, Field
import logging
import json
import time
import asyncio
import os
import random
from typing import Dict, Any, List, Tuple, Set
from src.services.tenant_router import tenant_router
from spacy.language import Language
from spacy.tokens import Doc
from spacy.training import Example
import spacy

# ==============================================================================
# MANUAL DE OPERACIONES DE INFRAESTRUCTURA (TELEMETRIA EN VIVO)
# Comando para monitorear este componente: docker compose logs -f nlp-brain-engine
# ==============================================================================

# CONFIGURACION CORE DE ENRUTAMIENTO Y AUDITORIA ANALITICA
router: APIRouter = APIRouter()
logger: logging.Logger = logging.getLogger("AI-Endpoints")


# ==============================================================================
# CONTRATOS DE TRANSFERENCIA DE DATOS (DTOs VIA PYDANTIC)
# ==============================================================================
class ChatMessageDTO(BaseModel):
    """Contrato plano inmutable de 12 campos para ingesta síncrona en tiempo real."""
    tenantId: str
    clientId: str
    customerId: str
    sessionId: str
    messageId: str
    timestamp: str
    source: str
    message: str
    rawMessage: str
    issueCategory: str
    summary: str
    attachment: str

class DataRowDTO(BaseModel):
    """Representa una fila de texto etiquetada para el entrenamiento dinámico."""
    text: str = Field(..., description="Frase o chat muestra en lenguaje natural.")
    categories: Dict[str, float] = Field(..., description="Pesos probabilísticos asignados a cada intención.")

class TrainingPayloadDTO(BaseModel):
    """Payload maestro elástico para gatillar el re-entrenamiento vía JSON."""
    tenantId: str = Field(..., description="ID único del inquilino corporativo a entrenar.")
    epochs: int = Field(15, description="Número máximo de iteraciones sobre el dataset.")
    targetLoss: float = Field(0.0001, description="Umbral de parada temprana (Early Stopping).")
    dataset: List[DataRowDTO] = Field(..., description="Arreglo con el Golden Dataset dinámico.")


# ==============================================================================
# FUNCIONES CORE COMPILADAS EN HILOS DE KERNEL (SUBPROCESOS)
# ==============================================================================
def _execute_inference(nlp: Language, text: str, disabled_components: List[str]) -> Dict[str, float]:
    """Ejecuta de forma aislada la inferencia sobre Cython liberando el GIL."""
    with nlp.select_pipes(disable=disabled_components):
        doc: Doc = nlp(text)
        return doc.cats

def _execute_training(payload: TrainingPayloadDTO, start_time: float) -> None:
    """
    Ejecuta el ciclo estocástico de optimización Adam en un hilo secundario aislado de background.
    Desvía el cálculo pesado de tensores de la CPU fuera del loop web de FastAPI.
    Actualiza el caché in-memory de forma segura al finalizar.
    """
    try:
        logger.info(f"🪐 [Background-Trainer] Inicializando optimización en bloque para: [{payload.tenantId}]")
        
        TRAINING_DATA: List[Tuple[str, Dict[str, Dict[str, float]]]] = [
            (row.text, {"cats": row.categories}) for row in payload.dataset
        ]
        
        # Carga el pipeline base en el hilo aislado
        nlp: Language = spacy.load("es_core_news_sm")
        
        if "textcat" not in nlp.pipe_names:
            textcat = nlp.add_pipe("textcat", last=True)
        else:
            textcat = nlp.get_pipe("textcat") # type: ignore

        all_labels: Set[str] = {label for row in payload.dataset for label in row.categories.keys()}
        for label in all_labels:
            textcat.add_label(label)

        disabled_pipes = [pipe for pipe in nlp.pipe_names if pipe != "textcat"]
        final_loss = 1.0

        with nlp.select_pipes(disable=disabled_pipes):
            optimizer = nlp.initialize()
            logger.info(f"⚙️ [Training-Loop-Start] Optimizador Adam acoplado. Límite máximo: [{payload.epochs}] Épocas.")
            
            for epoch in range(payload.epochs):
                random.shuffle(TRAINING_DATA)
                losses: Dict[str, float] = {}
                batches = spacy.util.minibatch(TRAINING_DATA, size=3)
                
                for batch in batches:
                    examples = [Example.from_dict(nlp.make_doc(text_data), dict_data) for text_data, dict_data in batch]
                    nlp.update(examples, sgd=optimizer, losses=losses)
                
                final_loss = losses.get("textcat", 1.0)
                logger.info(f"[Training-Progress] Época [{epoch + 1}/{payload.epochs}] - Loss actual: [{final_loss:.6f}]")
                if final_loss <= payload.targetLoss:
                    logger.info(f"🎯 [Early-Stopping] Umbral objetivo alcanzado en época {epoch + 1}")
                    break

        # Guardar persistencia del nuevo modelo optimizado en el almacén físico de volúmenes
        output_dir = f"./models_store/{payload.tenantId}"
        os.makedirs(output_dir, exist_ok=True)
        nlp.to_disk(output_dir)
        
        # 🚀 SOLUCIÓN AL WARNING DE PYLANCE:
        # Si tu TenantRouter tiene un diccionario de caché expuesto (como ._pipelines o similar),
        # podemos vaciar la llave para que el próximo mapeo síncrono de Flink lea el nuevo binario del disco.
        if hasattr(tenant_router, "_pipelines") and isinstance(tenant_router._pipelines, dict): # type: ignore
            tenant_router._pipelines.pop(payload.tenantId, None) # type: ignore
        
        # Forzamos una recarga limpia inmediata en RAM para dejar el nuevo grafo tensorial caliente
        tenant_router.get_pipeline(payload.tenantId)
        
        duration_sec = time.perf_counter() - start_time
        logger.info(f"✅ [Background-Trainer-Success] Modelo entrenado y acoplado en RAM. Tiempo total: [{duration_sec:.2f} s] | Pérdida Final: [{final_loss:.6f}]")
        
    except Exception as e:
        logger.error(f"🚨 [Background-Trainer-Failure] Colapso en el hilo de optimización: {str(e)}")


# ==============================================================================
# COMPUERTA DE RED 1: INFERENCIA DE ALTA VELOCIDAD
# ==============================================================================
@router.post("/v1/analyze", response_model=None, status_code=status.HTTP_200_OK)
async def analyze_stream(
    request: Request, 
    x_tenant_id: str = Header(..., alias="X-Tenant-ID")
):
    """Endpoint productivo no bloqueante para el consumo masivo de Apache Flink."""
    start_time = time.perf_counter()
    try:
        body_bytes = await request.body()
        data_dict = json.loads(body_bytes.decode("utf-8"))
        
        message_text = data_dict.get("message", "")
        session_id = data_dict.get("sessionId", "UNKNOWN_SESSION")
        client_id = data_dict.get("clientId", "UNKNOWN_CLIENT")
        
        nlp = tenant_router.get_pipeline(x_tenant_id)
        disabled_components = [pipe for pipe in nlp.pipe_names if pipe != "textcat"]
        
        intents = await asyncio.to_thread(
            _execute_inference, nlp, message_text, disabled_components
        )

        top_intent = "UNKNOWN_INTENT"
        confidence = 0.0
        if intents:
            top_intent = max(intents, key=intents.get) # type: ignore
            confidence = intents[top_intent]

        sentiment_score = -0.75 if any(w in message_text.lower() for w in ["error", "critico", "pesimo"]) else 0.0
        duration_ms = (time.perf_counter() - start_time) * 1000
        throughput = 1000 / duration_ms if duration_ms > 0 else 0.0

        logger.info(f"[IA-Inference-Success] Procesado exitoso. Latencia: [{duration_ms:.2f} ms] | Intencion: [{top_intent}]")

        return {
            "status": "SUCCESS",
            "tenant_id": x_tenant_id,
            "client_id": client_id,
            "session_id": session_id,
            "analytics": {
                "intent": top_intent,
                "intent_confidence": round(confidence, 4),
                "sentiment_score": sentiment_score,
                "entities": []
            },
            "performance": {
                "inference_latency_ms": round(duration_ms, 2),
                "throughput_capability_msg_sec": round(throughput, 2)
            },
            "reason": None
        }

    except Exception as e:
        logger.error(f"[IA-Error] Falla en pipeline analitico: {str(e)}")
        return Response(
            content=json.dumps({"status": "ERROR", "reason": str(e), "code": 500}),
            media_type="application/json",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==============================================================================
# COMPUERTA DE RED 2: RE-ENTRENAMIENTO DINÁMICO ASÍNCRONO RESILIENTE
# ==============================================================================
@router.post("/v1/train", response_model=None, status_code=status.HTTP_202_ACCEPTED)
async def trigger_dynamic_training(payload: TrainingPayloadDTO, background_tasks: BackgroundTasks):
    """
    🚀 GATILLA LA OPTIMIZACIÓN ESTOCÁSTICA DE PESOS EN BACKGROUND
    Recibe el payload, libera el socket en milisegundos y delega el bucle pesado a la cola de hilos de la CPU.
    """
    start_time = time.perf_counter()
    if not payload.dataset:
        return Response(
            content=json.dumps({"status": "ERROR", "reason": "El dataset provisto no contiene registros muestra."}),
            media_type="application/json",
            status_code=status.HTTP_400_BAD_REQUEST
        )
        
    # 🔥 BLINDAJE ASÍNCRONO PROTEGIDO: Delegamos la ejecución pesada de forma inmediata
    background_tasks.add_task(_execute_training, payload, start_time)
    
    # Retornamos el estatus 202 ACCEPTED en microsegundos rompiendo cualquier riesgo de timeout
    return {
        "status": "ACCEPTED",
        "message": "Capa de optimización estocástica spaCy CNN iniciada en segundo plano de forma segura.",
        "tenantId": payload.tenantId,
        "metrics": {
            "requested_epochs": payload.epochs,
            "target_loss": payload.targetLoss,
            "dataset_size": len(payload.dataset)
        }
    }
