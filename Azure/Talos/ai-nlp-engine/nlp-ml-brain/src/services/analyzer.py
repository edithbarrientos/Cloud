import logging
import time
from spacy.tokens import Doc
from src.services.tenant_router import tenant_router
from src.domain.models import AIAnalyticsResult, ExtractedEntity, InferenceResponse
from src.config.settings import settings

logger = logging.getLogger("AI-Analyzer")

if not Doc.has_extension("intent"):
    Doc.set_extension("intent", default="UNKNOWN_INTENT")
if not Doc.has_extension("sentiment_score"):
    Doc.set_extension("sentiment_score", default=0.0)

class MessageAnalyzer:
    """
    🧪 MOTOR ANALÍTICO ADAPTADO AL CONTRATO EMPRESARIAL DE 12 CAMPOS
    Procesa las intenciones, entidades y el sentimiento continuo del chat.
    """
    def __init__(self):
        logger.info("🧪 [MessageAnalyzer] Inicializando motor de IA corporativo.")

    def process_message(self, tenant_id: str, client_id: str, customer_id: str, session_id: str, 
                        message_id: str, timestamp: str, source: str, message: str, 
                        raw_message: str, issue_category: str, summary: str, attachment: str) -> InferenceResponse:
        """
        Ejecuta la inferencia lingüística sobre el texto limpio del mensaje.
        """
        start_time_ns = time.perf_counter_ns()
        try:
            # 🔀 PATRÓN MODEL ROUTER: Recuperamos el cerebro lingüístico del cliente
            nlp_pipeline = tenant_router.get_pipeline(tenant_id)
            
            # Ejecución de spaCy sobre el campo 'message' limpio
            doc = nlp_pipeline(message)
            
            # Algoritmo 1: NER (Extracción de Tokens de Negocio)
            extracted_entities = [
                ExtractedEntity(entity_type=ent.label_, value=ent.text)
                for ent in doc.ents
            ]

            # Algoritmo 2: Clasificación de Intenciones
            intent_name = "UNKNOWN_INTENT"
            intent_score = 0.0
            if hasattr(doc, "cats") and doc.cats:
                best_intent = max(doc.cats, key=doc.cats.get)
                intent_score = doc.cats[best_intent]
                if intent_score >= settings.INTENT_CONFIDENCE_THRESHOLD:
                    intent_name = best_intent
                    doc._.intent = intent_name

            # Algoritmo 3: Sentimiento Continuo Ponderado
            sentiment_value = 0.0
            neg_tokens = {"error", "mal", "fallo", "problema", "ayuda", "pesimo", "caido", "lento"}
            pos_tokens = {"gracias", "excelente", "bueno", "ok", "perfecto", "api", "exito", "util"}
            matched_pos = sum(1 for token in doc if token.text.lower() in pos_tokens)
            matched_neg = sum(1 for token in doc if token.text.lower() in neg_tokens)
            total_matches = matched_pos + matched_neg
            if total_matches > 0:
                sentiment_value = (matched_pos - matched_neg) / total_matches
                doc._.sentiment_score = round(sentiment_value, 2)

            analytics_payload = AIAnalyticsResult(
                intent=intent_name,
                intent_confidence=round(intent_score, 4),
                sentiment_score=doc._.sentiment_score,
                entities=extracted_entities
            )

            duration_ms = (time.perf_counter_ns() - start_time_ns) / 1_000_000.0
            logger.info(f"📥 [Analyzer] Inferencia Exitosa -> Tenant: [{tenant_id}] | Latencia: [{duration_ms:.2f} ms]")

            return InferenceResponse(
                status="SUCCESS",
                tenant_id=tenant_id,
                client_id=client_id,
                session_id=session_id,
                analytics=analytics_payload
            )

        except Exception as e:
            logger.error(f"💥 [Analyzer-Error] Fallo crítico en el pipeline de IA: {str(e)}", exc_info=True)
            return InferenceResponse(
                status="ERROR",
                tenant_id=tenant_id,
                client_id=client_id,
                session_id=session_id,
                reason=f"Fallo en la inferencia de Machine Learning: {str(e)}"
            )

message_analyzer = MessageAnalyzer()
