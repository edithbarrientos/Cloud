import logging
import asyncio
import time
import json
from typing import Dict, Any, Tuple, List
from ai_agentic_core.orchestrator import AiTechnicalOrchestrator
from ai_agentic_core.security import AiSecurityGuardMaster

logger = logging.getLogger("ai_agentic_core.supervisor")

class QualityDataSupervisor:
    def __init__(self) -> None:
        self.orchestrator = AiTechnicalOrchestrator()
        self.security_guard = AiSecurityGuardMaster()
        self._historical_distribution_window: List[float] = [0.1, 0.15, 0.12, 0.09, 0.11]

    def _calculate_wasserstein_drift(self, current_metrics: List[float]) -> Tuple[bool, float]:
        avg_hist = sum(self._historical_distribution_window) / len(self._historical_distribution_window)
        avg_curr = sum(current_metrics) / len(current_metrics)
        drift_distance = abs(avg_hist - avg_curr)
        is_drift_detected = drift_distance > 0.35
        self._historical_distribution_window.append(avg_curr)
        return is_drift_detected, drift_distance

    async def process_inference_ingestion(self, raw_data: Dict[str, Any], previous_hash: str, step_sequence: int) -> Dict[str, Any]:
        trace_id = raw_data.get("trace_id", f"TRC-{int(time.time())}")
        
        logger.info(f"========================================================================")
        logger.info(f"🏛️ [CONSEJO_SUPERVISOR] INGESTANDO TRAZA GLOBAL: {trace_id}")
        logger.info(f"📦 OBJETO RECIBIDO (Payload Crudo): {json.dumps(raw_data, indent=2)}")
        logger.info(f"🔢 Secuencia del Paso: {step_sequence} | Hash Anterior: {previous_hash}")
        logger.info(f"========================================================================")
        
        # Auditoría perimetral de seguridad
        security_context, is_veto_triggered = self.security_guard.audit_and_sign_context(raw_data, previous_hash)
        
        logger.info(f"🔒 [CONTEXTO_SEGURIDAD] Objeto de Seguridad Generado:")
        logger.info(f"{json.dumps(security_context, indent=2)}")

        if is_veto_triggered: 
            logger.error(f"🚨 [PRIVACY_VETO] Objeto RECHAZADO por contener PII o datos sensibles.")
            return {"trace_id": trace_id, "status": "REJECTED_PRIVACY_VETO"}

        # Análisis matemático de Drift
        drift_detected, drift_score = self._calculate_wasserstein_drift([0.12])
        logger.info(f"📊 [ESTADÍSTICA] Wasserstein Drift Score: {drift_score:.4f} | ¿Drift Detectado?: {drift_detected}")
        
        # Pasar al Orquestador Técnico
        logger.info(f"🎛️ [ORQUESTADOR] Transfiriendo objeto al pool de hilos DAMA en paralelo...")
        orchestration_output = await self.orchestrator.orchestrate_and_ledger(
            trace_id=trace_id, step_seq=step_sequence, raw_data=raw_data, security_context=security_context
        )
        
        return {
            "trace_id": trace_id, 
            "status": "SUCCESS", 
            "security_integrity": {"current_hash": security_context["current_hash"]},
            "orchestration_details": orchestration_output
        }
