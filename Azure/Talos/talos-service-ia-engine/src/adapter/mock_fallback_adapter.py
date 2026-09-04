# -*- coding: utf-8 -*-
"""
Autor: EdithBG <edithbg@corporativo.internal>
Componente: Adaptador de Contingencia de Costo Cero (MockFallbackAdapter)
"""

import time

from src.domain.contracts import AIEngineRequest, AIEngineResponse, SecurityAudit, TelemetryConsumption
from src.domain.ports.ai_engine_port import AIEnginePort


class MockFallbackAdapter(AIEnginePort):
    """
    Implementa el puerto AIEnginePort para actuar como el sistema de respaldo local.
    Se activa automáticamente mediante el Circuit Breaker ante fallas o timeouts de OpenAI.
    """

    async def procesar_computo_linguistico(self, request: AIEngineRequest) -> AIEngineResponse:
        """
        Retorna de forma asíncrona una respuesta local estandarizada sin latencia.
        Garantiza la continuidad del negocio y desvía la consulta al ERP a costo $0.
        """
        start_time = time.time()

        # Simulación de procesamiento de corrutina (latencia de 2 milisegundos)
        latencia_ms = int((time.time() - start_time) * 1000) or 2

        # Emitir el contrato de salida inmutable amarrando el Correlation ID original
        return AIEngineResponse(
            correlation_id=request.correlation_id,
            canal_usuario_id=request.canal_usuario_id,
            text_respuesta_generada=(
                "Hola. Presentamos una interrupción temporal en el motor de lenguaje. "
                "Para garantizar la precisión de tu trámite en este momento, por favor proporcióname "
                "tu número de folio o pedido para procesarlo de forma directa a través de nuestros "
                "sistemas transaccionales tradicionales."
            ),
            telemetria_consumo=TelemetryConsumption(
                modelo_utilizado="CIRCUIT_BREAKER_LOCAL_FALLBACK",
                tokens_prompt_entrada=0,
                tokens_completion_salida=0,
                tokens_totales_facturables=0,
                latencia_computo_milisegundos=latencia_ms
            ),
            auditoria_seguridad=SecurityAudit(
                guardrails_entrada_aprobados=True,
                guardrails_salida_aprobados=True,
                score_confianza_rag=1.0
            )
        )
