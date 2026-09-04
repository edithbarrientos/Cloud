import logging
import asyncio
import time
from typing import Dict, Any, List, Optional

from ai_agentic_core.supervisor import QualityDataSupervisor
from ai_agentic_core.ai_engine import StochasticAnomaliesEngine
from ai_agentic_core.privacy_engine import CognitivePrivacyEngine
from ai_agentic_core.lineage_engine import CognitiveLineageEngine
from infrastructure.cloud_cache_provider import CloudCacheProvider
from infrastructure.ledger_dao_factory import LedgerDAOFactory
from infrastructure.cloud_patterns import CloudCircuitBreaker, CloudExponentialRetry, ConnectionRuntimeError

logger = logging.getLogger("ai_agentic_core.structural")

class DamaDimensionFlyweightFactory:
    _shared_flyweights: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def get_dimension_state(dimension_name: str, status: str = "SUCCESS", severity: str = "LOW") -> Dict[str, Any]:
        key = f"{dimension_name}_{status}_{severity}"
        if key not in DamaDimensionFlyweightFactory._shared_flyweights:
            DamaDimensionFlyweightFactory._shared_flyweights[key] = {
                "worker": dimension_name, "status": status, "anomaly_severity": severity, "governance_standard": "DAMA-DMBOK-V2-EXTENDED"
            }
        return DamaDimensionFlyweightFactory._shared_flyweights[key]


class CognitiveCoreFacade:
    def __init__(self) -> None:
        self.supervisor = QualityDataSupervisor()
        self.cache_provider = CloudCacheProvider()
        self.dao_provider = LedgerDAOFactory.get_ledger_dao()
        self.ai_engine = StochasticAnomaliesEngine(threshold=2.5)
        self.privacy_engine = CognitivePrivacyEngine()
        self.lineage_engine = CognitiveLineageEngine()
        
        self.circuit_breaker = CloudCircuitBreaker(failure_threshold=2, recovery_timeout=4.0)
        self.retry_policy = CloudExponentialRetry(max_retries=2, base_delay=0.05)
        
        self._ingestion_queue: asyncio.Queue = asyncio.Queue(maxsize=10000)
        self._worker_task: Optional[asyncio.Task] = None
        self._is_running = False

    async def bootstrap_subsystems(self) -> None:
        await self.cache_provider.connect()
        await self.dao_provider.initialize()
        self._is_running = True
        self._worker_task = asyncio.create_task(self._queue_consumer_worker())
        logger.info("[FACADE] ⚡ Subsistemas de Inferencia, Privacidad y Linaje listos.")

    async def enqueue_payload_speculative(self, raw_data: Dict[str, Any], previous_hash: str, step_sequence: int) -> str:
        trace_id = raw_data.get("trace_id", f"TRC-FAST-{time.time_ns()}")
        task_context = {"trace_id": trace_id, "raw_data": raw_data, "previous_hash": previous_hash, "step_sequence": step_sequence}
        try:
            self._ingestion_queue.put_nowait(task_context)
        except asyncio.QueueFull:
            await self._ingestion_queue.put(task_context)
        return trace_id

    async def query_full_ledger_graph(self, trace_id: str) -> Dict[str, Any]:
        cached_graph = await self.cache_provider.get(f"graph_{trace_id}")
        if cached_graph: return {"source": "CACHE_L1_SPEED", "graph": cached_graph}
        return {"source": "COLD_PERSISTENCE", "graph": {"trace_id": trace_id, "nodes": []}}

    async def _queue_consumer_worker(self):
        while self._is_running:
            try:
                task_ctx = await self._ingestion_queue.get()
                raw_data = task_ctx["raw_data"]
                metric_value = float(raw_data.get("metric_value", 0.90))
                metadata_ctx = raw_data.get("metadata", {})
                framework = str(metadata_ctx.get("regulatory_framework", "internal_governance"))
                
                is_anomaly, z_score, ai_verdict = self.ai_engine.evaluate_metric_drift(metric_value)
                is_pii_exposed, privacy_verdict, security_severity = self.privacy_engine.audit_regulatory_data_leak(raw_data, metadata_ctx)
                
                current_chain_hash, is_lineage_broken = self.lineage_engine.compute_immutable_lineage(
                    raw_data, task_ctx["previous_hash"], task_ctx["step_sequence"], framework
                )
                
                # 🪄 FIX: Argumentos con llaves explícitas mapeados al 100% para evitar fallas en background
                response_graph = await self.supervisor.process_inference_ingestion(
                    raw_data=raw_data, previous_hash=task_ctx["previous_hash"], step_sequence=task_ctx["step_sequence"]
                )
                
                status_dama = "FAILED" if is_anomaly else "SUCCESS"
                severity_dama = "CRITICAL" if is_anomaly else "NOMINAL"
                status_security = "FAILED" if is_pii_exposed else "SUCCESS"
                status_trazabilidad = "FAILED" if is_lineage_broken else "SUCCESS"
                severity_trazabilidad = "CRITICAL" if is_lineage_broken else "NOMINAL"
                
                dimensions_base = ["EXACTITUD", "COMPLETO", "COHERENCIA", "FIABILIDAD", "PERTINENCIA", "OPORTUNIDAD", "UNICIDAD", "VALIDEZ", "INTEGRIDAD"]
                compiled_metrics = [DamaDimensionFlyweightFactory.get_dimension_state(dim, status_dama, severity_dama) for dim in dimensions_base]
                
                compiled_metrics.append(DamaDimensionFlyweightFactory.get_dimension_state("TRAZABILIDAD", status_trazabilidad, severity_trazabilidad))
                compiled_metrics.append(DamaDimensionFlyweightFactory.get_dimension_state("SEGURIDAD", status_security, security_severity))
                
                response_graph["orchestration_details"]["dama_metrics"] = compiled_metrics
                response_graph["security_integrity"]["current_hash"] = current_chain_hash
                
                response_graph["ai_analytics_boundary"] = {
                    "model_verdict": ai_verdict,
                    "calculated_z_score": round(z_score, 4),
                    "privacy_compliance_status": privacy_verdict,
                    "lineage_hash_chain": current_chain_hash,
                    "is_lineage_corrupted": is_lineage_broken
                }
                
                await self.cache_provider.set(f"graph_{task_ctx['trace_id']}", response_graph, ttl=120)
                try:
                    await self.retry_policy.execute(
                        self.dao_provider.save_ledger_node, self.circuit_breaker, response_graph, {"calculated_z_score": z_score}
                    )
                except (Exception, ConnectionRuntimeError): pass
                
                self._ingestion_queue.task_done()
            except asyncio.CancelledError: break
            except Exception as e:
                logger.error(f"[QUEUE_WORKER_CRITICAL] Falla en hilo consumidor: {str(e)}")
                await asyncio.sleep(0.01)

    async def shutdown_subsystems(self) -> None:
        self._is_running = False
        if self._worker_task:
            self._worker_task.cancel()
            try: await self._worker_task
            except asyncio.CancelledError: pass
        await self.cache_provider.disconnect()
        await self.dao_provider.disconnect()
