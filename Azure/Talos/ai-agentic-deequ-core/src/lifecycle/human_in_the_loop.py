# -*- coding: utf-8 -*-
# ======================================================================================================================
# PROJECT: Autonomous Deequ Orchestrator (ADO) - Enterprise Cognitive Engine
# MODULE: Application Lifecycle Management (ALM de IA) - High-Performance Reactive HITL Gatekeeper
# FILE: human_in_the_loop.py
# AUTHOR: Orchestra Labs Enterprise Architecture
# VERSION: 5.0.0
# COMPATIBILITY: Python 3.11+ / asyncio Async Event Loop / Redis Reactive Keyspace
# ======================================================================================================================

import asyncio
import json
import logging
import time
import traceback
from typing import Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field

class HumanReviewTicket(BaseModel):
    """Contrato inmutable fuertemente tipado para el ticket de auditoria humana."""
    ticket_id: str = Field(..., description="Identificador hexadecimal unico del bloqueo transaccional")
    tenant_id: str = Field(..., description="ID del inquilino interceptado")
    kpi_target: str = Field(..., description="Objetivo de negocio bajo revision de mutacion")
    intercept_timestamp: float = Field(default_factory=time.time, description="Sello de tiempo del congelamiento")
    status: str = Field(default="PENDING_REVIEW", description="Estado del ticket: PENDING_REVIEW, APPROVED, REJECTED")

class HumanInTheLoopGatekeeper:
    """
    🔄 ALM DE IA AVANZADO: INTERCEPTOR HUMAN-IN-THE-LOOP RECOLECTOR REACTIVO
    
    Responsabilidad:
        Gobernar mutaciones críticas estructurales utilizando un modelo predictivo de riesgo
        y suspensiones puramente reactivas impulsadas por eventos, eliminando bucles de polling.
    """
    def __init__(self, redis_client: Optional[Any] = None):
        self.logger = logging.getLogger("HumanInTheLoopGatekeeper")
        self.redis = redis_client
        self.hitl_queue_prefix = "ado:core:hitl:tickets"
        self.config_channel_prefix = "ado:core:hitl:signoff"
        self.max_timeout_seconds = 30.0 # Circuit breaker inmutable de tiempo para proteger el cluster

    def _generate_ticket_hash(self, tenant_id: str, kpi_target: str) -> str:
        """Genera un ID unico determinista para el ticket de revision en RAM."""
        return f"tk_hitl_{tenant_id}_{hash(kpi_target) & 0xFFFFFFFF:08X}"

    def _predict_mutation_risk_score(self, json_payload: Dict[str, Any]) -> float:
        """
        🧮 ALGORITMO IA: MUTATION RISK INVARIANCE PREDICTOR
        Infiere estadísticamente el nivel de riesgo del cambio de esquema analizando la cardinalidad.
        Regresa un score entre 0.0 (Inofensivo) y 1.0 (Destructivo).
        """
        try:
            target_data = json_payload.get("data", {})
            metadata = json_payload.get("metadata", {})
            
            # Heurística Bayesiana: Evalúa si es una mutación menor o una alteración masiva de tipos
            fields_count = len(target_data)
            is_sync_mode = metadata.get("execution_mode", "SYNC") == "SYNC"
            
            # Cambios masivos densos en caliente en modo sincrónico elevan exponencialmente el riesgo
            risk = 0.05
            if fields_count > 15: risk += 0.35
            if is_sync_mode: risk += 0.20
            
            return min(0.95, risk)
        except Exception:
            return 0.95 # Ante fallas del predictor, asume el máximo riesgo por aislamiento preventivo

    async def intercept_and_await_approval(self, tenant_id: str, json_payload: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Suspende la ejecución de la transacción de forma puramente reactiva mediante un Future asíncrono.
        Aplica auto-aprobación inteligente si el riesgo predicho se mantiene por debajo de las tolerancias.
        """
        start_time = time.perf_counter()
        kpi_target = json_payload.get("kpi_target", "UNKNOWN_KPI")
        ticket_id = self._generate_ticket_hash(tenant_id, kpi_target)
        
        # 1. EVALUACIÓN DE IA: Inferencia de riesgo en microsegundos sin tocar sockets de red
        predicted_risk = self._predict_mutation_risk_score(json_payload)
        auto_approve_threshold = 0.25 # Tolerancia corporativa para mutaciones inofensivas menores
        
        if predicted_risk < auto_approve_threshold:
            self.logger.info(f"[AI_AUTO_SIGN_OFF] Mutacion menor catalogada como de bajo riesgo ({round(predicted_risk, 2)}). Concediendo pase inmediato en RAM.")
            return True, f"APPROVED_AUTOMATICALLY_BY_AI_RISK_INFERENCE_SCORE_{round(predicted_risk, 2)}"

        self.logger.warning(f"[HITL_REACTIVE_INTERCEPT] Riesgo elevado detectado ({round(predicted_risk, 2)}). Congelando transaccion - Tenant: {tenant_id} | Ticket: {ticket_id}")

        if not self.redis:
            self.logger.critical(f"[HITL_BYPASS_SAFETY] Cliente Redis ausente. Rechazo preventivo perimetral obligado.")
            return False, "VETOED_BY_HITL_INFRASTRUCTURE_DISCONNECT"

        ticket = HumanReviewTicket(ticket_id=ticket_id, tenant_id=tenant_id, kpi_target=kpi_target)
        redis_key = f"{self.hitl_queue_prefix}:{ticket_id}"
        signoff_channel = f"{self.config_channel_prefix}:{ticket_id}"

        # 🚀 REACTIVE FUTURE PATTERN: Contenedor asíncronizado de un solo uso para despertar el kernel
        loop = asyncio.get_running_loop()
        future_signoff = loop.create_future()

        # Listener interno reactivo encargado de procesar la señal remota de Hardware
        async def reactive_redis_listener():
            try:
                pubsub = self.redis.pubsub()
                await pubsub.subscribe(signoff_channel)
                
                # Consumo puramente pasivo (Consumo CPU = Cero absoluto)
                async for message in pubsub.listen():
                    if message and message.get("type") == "message":
                        signal_payload = json.loads(message.get("data", "{}"))
                        verdict_signal = signal_payload.get("verdict", "REJECTED")
                        
                        if not future_signoff.done():
                            future_signoff.set_result(verdict_signal)
                        break
            except Exception as listener_error:
                if not future_signoff.done():
                    future_signoff.set_exception(listener_error)

        # Disparamos la escucha en background conectada de forma elástica al loop
        listener_task = asyncio.create_task(reactive_redis_listener())

        try:
            # Persistimos el ticket en la caché para auditoría del operador manual
            await self.redis.set(redis_key, json.dumps(ticket.model_dump()), ex=600)
            
            # ⏳ SUSPENSIÓN REACTIVA: El event loop congela la corrutina esperando el veredicto o el timeout global
            try:
                verdict_result = await asyncio.wait_for(future_signoff, timeout=self.max_timeout_seconds)
                
                if verdict_result == "APPROVED":
                    self.logger.warning(f"[HITL_REACTIVE_GRANTED] Firma humana aprobada recibida por canal Pub/Sub para {ticket_id}. Reanudando.")
                    return True, "APPROVED_BY_REACTIVE_HUMAN_SIGN_OFF"
                else:
                    self.logger.critical(f"[HITL_REACTIVE_DENIED] Firma humana rechazada recibida para {ticket_id}. Abortando.")
                    return False, "VETOED_BY_REACTIVE_HUMAN_OPERATOR"
                    
            except asyncio.TimeoutError:
                # CIRCUIT BREAKER POR TIEMPO: Contención elástica para evitar leaks de sockets
                self.logger.critical(f"[HITL_REACTIVE_TIMEOUT] Exceso de tiempo en revision reactiva para {ticket_id}. Abortando de forma segura.")
                return False, "VETOED_BY_HITL_REACTIVE_TIMEOUT_FALLBACK"

        except Exception as hitl_crash:
            self.logger.error(f"[HITL_REACTIVE_CRASH] Fallo fatal en el guardián: {str(hitl_crash)} | Trace: {traceback.format_exc().splitlines()[-1]}")
            return False, f"VETOED_BY_HITL_RUNTIME_ERROR: {str(hitl_crash)}"
            
        finally:
            # Región de Limpieza Atómica e Inmaculada: Desmantela hilos y purga registros de la RAM
            listener_task.cancel()
            await self.redis.delete(redis_key)
            elapsed = (time.perf_counter() - start_time) * 1000
            self.logger.info(f"[HITL_METRICS] Operacion de contencion finalizada. Latencia de suspension: {round(elapsed, 2)}ms")
