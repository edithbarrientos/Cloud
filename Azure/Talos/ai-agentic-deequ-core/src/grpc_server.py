import asyncio
import logging
import sys
import os
import time
from typing import Dict, Any, List, Final, Tuple
import multiprocessing

import grpc
import inference_pb2
import inference_pb2_grpc

from ai_agentic_core.flyweight_facade import CognitiveCoreFacade, DamaDimensionFlyweightFactory
from ai_agentic_core.dama_metrics_engine import DamaBusinessMetricsEngine
from ai_agentic_core.telemetry_logger import CognitiveTelemetryLogger

# 🪄 LIGHTWEIGHT_LOGGING: Elevamos el nivel de control a WARNING para silenciar las impresiones I/O pesadas en pantalla
logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(levelname)s] grpc.server: %(message)s")
logger = logging.getLogger("grpc_server")

class InferenceEngineService(inference_pb2_grpc.InferenceEngineServicer):
    def __init__(self) -> None:
        self.core_facade: CognitiveCoreFacade = CognitiveCoreFacade()
        self.metrics_engine: DamaBusinessMetricsEngine = DamaBusinessMetricsEngine()
        self.telemetry_logger: CognitiveTelemetryLogger = CognitiveTelemetryLogger()
        self.DATA_GLOSSARY_CATALOG: Final[Dict[str, Dict[str, Any]]] = {
            "iot_sensor_telemetry": {"domain": "Logistics"},
            "financial_ledger_entries": {"domain": "Finance"}
        }

    async def ProcessInference(self, request: inference_pb2.InferenceRequest, context: grpc.aio.ServicerContext) -> inference_pb2.InferenceResponse:
        start_ticks: float = time.perf_counter_ns()
        metric_value: float = request.telemetry.metric_value
        step_seq: int = request.step_sequence

        dataset_name: str = str(request.metadata.get("datasetName", "unknown_speculative_table")).strip()
        domain_scope: str = str(request.metadata.get("domainScope", "unknown_speculative_domain")).strip()

        glossary_status, glossary_explanation = "CATALOG_CERTIFIED", "La entidad existe formalmente en el Glosario."
        if dataset_name not in self.DATA_GLOSSARY_CATALOG:
            glossary_status, domain_scope = "SPECULATIVE_DISCOVERY_TRIGGERED", "SHADOW_DATA_MESH_DISCOVERY"
            glossary_explanation = f"⚠️ ALERTA: La tabla '{dataset_name}' no existe en el catálogo. Descubrimiento activo."

        assigned_trace: str = await self.core_facade.enqueue_payload_speculative(
            raw_data={"sensor_id": request.telemetry.sensor_id, "metric_value": metric_value, "region": request.telemetry.region, "metadata": request.metadata},
            previous_hash=request.previous_hash, step_sequence=step_seq
        )

        is_anomaly, z_score, ai_verdict = self.core_facade.ai_engine.evaluate_metric_drift(metric_value)
        is_pii_exposed, privacy_verdict, security_severity = self.core_facade.privacy_engine.audit_regulatory_data_leak(request.metadata, request.metadata)
        
        framework: str = str(request.metadata.get("regulatory_framework", "internal_governance"))
        current_hash, is_broken = self.core_facade.lineage_engine.compute_immutable_lineage({"metric_value": metric_value}, request.previous_hash, step_seq, framework)
        corruption_probability: float = self.metrics_engine._execute_onnx_inference(metric_value, float(step_seq))
        
        latency_microseconds: int = int((time.perf_counter_ns() - start_ticks) / 1000)
        kpis: Dict[str, float] = self.metrics_engine.calculate_percentages(step_seq, corruption_probability, is_pii_exposed, is_anomaly)

        status_dama: str = ["SUCCESS", "FAILED"][is_anomaly]
        severity_dama: str = ["NOMINAL", "CRITICAL"][is_anomaly]
        status_security: str = ["SUCCESS", "FAILED"][is_pii_exposed]
        status_trazabilidad: str = ["SUCCESS", "FAILED"][is_broken]
        severity_trazabilidad: str = ["NOMINAL", "HIGH"][glossary_status == "SPECULATIVE_DISCOVERY_TRIGGERED"]

        dimensions = ["EXACTITUD", "COMPLETO", "COHERENCIA", "FIABILIDAD", "PERTINENCIA", "OPORTUNIDAD", "UNICIDAD", "VALIDEZ", "INTEGRIDAD"]
        dama_list = [DamaDimensionFlyweightFactory.get_dimension_state(dim, status_dama, severity_dama) for dim in dimensions]
        dama_list.append(DamaDimensionFlyweightFactory.get_dimension_state("TRAZABILIDAD", status_trazabilidad, severity_trazabilidad))
        dama_list.append(DamaDimensionFlyweightFactory.get_dimension_state("SEGURIDAD", status_security, security_severity))

        # 🪄 EXPERIMENTO CORE: Se ejecuta el calculo de fondo en RAM y la persistencia asincrona,
        # pero silenciamos el dump_unified_telemetry() de consola para romper el bloqueo I/O de red.
        # self.telemetry_logger.dump_unified_telemetry({...})

        return inference_pb2.InferenceResponse(trace_id=assigned_trace, status="SUCCESS", current_hash=current_hash, ledger_id=assigned_trace[:12])

async def serve_single_node() -> None:
    facade_init: CognitiveCoreFacade = CognitiveCoreFacade()
    await facade_init.bootstrap_subsystems()

    server_options = [
        ('grpc.max_receive_message_length', 100 * 1024 * 1024),
        ('grpc.max_send_message_length', 100 * 1024 * 1024),
        ('grpc.so_reuseport', 1) 
    ]

    server = grpc.aio.server(options=server_options)
    inference_pb2_grpc.add_InferenceEngineServicer_to_server(InferenceEngineService(), server)
    
    server.add_insecure_port("[::]:50051")
    await server.start()
    await server.wait_for_termination()

def target_worker_process() -> None:
    asyncio.run(serve_single_node())

def run_multiprocess_cluster():
    cpu_cores = os.cpu_count() or 4
    target_workers = min(4, cpu_cores)
    print(f"🔥 [gRPC_MULTIPROCESS] Clonando {target_workers} procesos independientes libres de I/O Bound en tu Mac.")
    
    processes = []
    for _ in range(target_workers):
        p = multiprocessing.Process(target=target_worker_process)
        p.daemon = True
        p.start()
        processes.append(p)
        
    print(f"🚀 [gRPC_MULTIPROCESS_CLUSTER] Enjambre binario escuchando en paralelo al maximo teorico de hardware.")
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
    multiprocessing.set_start_method('spawn', force=True)
    try:
        run_multiprocess_cluster()
    except KeyboardInterrupt:
        sys.exit(0)
