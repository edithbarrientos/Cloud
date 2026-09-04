import pytest
import time
from src.services.analyzer import message_analyzer
from src.domain.models import InferenceResponse

def test_spacy_pipeline_performance_latency():
    """⚡ Verifica que el pipeline de inferencia procese el texto en menos de 50 milisegundos."""
    tenant_id = "tenant_generic"
    client_id = "client-test"
    session_id = "sess-test-99"
    sample_text = "Hola, necesito ayuda con un error crítico en mi cuenta de cobro."

    # 🚀 ACCIÓN CORRECTIVA (Warm-up AI Pattern): Forzamos la carga inicial en RAM fuera del cronómetro
    message_analyzer.process_message(
        tenant_id=tenant_id, client_id=client_id, session_id=session_id, text_payload="Warmup"
    )

    # Ahora que el modelo está 100% caliente en la RAM, medimos el rendimiento real en streaming
    start_time = time.perf_counter()
    response: InferenceResponse = message_analyzer.process_message(
        tenant_id=tenant_id,
        client_id=client_id,
        session_id=session_id,
        text_payload=sample_text
    )
    duration_ms = (time.perf_counter() - start_time) * 1000

    assert response.status == "SUCCESS"
    assert duration_ms < 50.0, f"Latencia de IA degradada en caliente: {duration_ms:.2f} ms"

def test_ner_extractor_token_accuracy():
    """🤖 Valida que el algoritmo léxico capture correctamente el sentimiento ponderado."""
    tenant_id = "tenant_generic"
    client_id = "client-test"
    session_id = "sess-test-100"
    negative_text = "Tengo un problema y un error pésimo en el servicio."
    
    response: InferenceResponse = message_analyzer.process_message(
        tenant_id=tenant_id,
        client_id=client_id,
        session_id=session_id,
        text_payload=negative_text
    )
    
    assert response.status == "SUCCESS"
    assert response.analytics is not None
    assert response.analytics.sentiment_score < 0.0
