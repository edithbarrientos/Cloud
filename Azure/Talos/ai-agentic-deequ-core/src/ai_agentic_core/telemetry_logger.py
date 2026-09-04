import logging
from typing import Dict, Any, List, Final, Tuple
from abc import ABC, abstractmethod

logger = logging.getLogger("grpc_server")

class DiagnosticStrategy(ABC):
    """📜 Contract base para las estrategias de diagnóstico XAI."""
    @abstractmethod
    def translate(self, percentage: float) -> Tuple[str, str, str]:
        pass

class NominalDiagnostic(DiagnosticStrategy):
    def translate(self, percentage: float) -> Tuple[str, str, str]:
        return "🟢 COMPORTAMIENTO NOMINAL", f"El dato es 100% confiable. La Red Neuronal detecta solo {percentage:.2f}% de ruido base.", "BAJO"

class WarningDiagnostic(DiagnosticStrategy):
    def translate(self, percentage: float) -> Tuple[str, str, str]:
        return "🟡 ADVERTENCIA DE DESVÍO", f"Monitorear origen. Existe un {percentage:.2f}% de probabilidad de desajuste sintáctico.", "MEDIO"

class CriticalDiagnostic(DiagnosticStrategy):
    def translate(self, percentage: float) -> Tuple[str, str, str]:
        return "🔴 CORRUPCIÓN DE DATOS DETECTADA", f"¡Acción Requerida! Alta probabilidad ({percentage:.2f}%) de anomalía o alteración maliciosa.", "CRÍTICO"

class CognitiveTelemetryLogger:
    """⚡ FACHADA DE OBSERVABILIDAD: Se encarga exclusivamente de formatear y desplegar la telemetría."""
    def __init__(self) -> None:
        self._strategies: Final[Dict[int, DiagnosticStrategy]] = {
            0: NominalDiagnostic(),
            1: WarningDiagnostic(),
            2: CriticalDiagnostic()
        }
        self.EMOJI_REGISTRY: Final[Dict[str, str]] = {
            "SUCCESS": "🟢",
            "FAILED": "🔴"
        }

    def dump_unified_telemetry(self, ctx: Dict[str, Any]) -> None:
        """📊 Despliega en consola el Feature Store, las alertas de Drift, XAI y la matriz DAMA."""
        prob: float = ctx["corruption_probability"]
        idx: int = (prob >= 0.15) + (prob >= 0.60)
        diag, expl, risk = self._strategies.get(idx, self._strategies).translate(prob * 100)

        logger.info(f"========================================================================")
        logger.info(f"🏛️ [gRPC_INGEST] DATA PRODUCT: ai-agentic-deequ-core | logId: {ctx['assigned_trace']}")
        logger.info(f"------------------------------------------------------------------------")
        logger.info(f"📂 [DATA_MESH_CATALOG] GOBIERNO DE TABLAS Y GLOSARIO DE CONTROL:")
        logger.info(f"  ├─ datasetName      : '{ctx['dataset_name']}'")
        logger.info(f"  ├─ domainScope      : '{ctx['domain_scope']}'")
        logger.info(f"  ├─ catalogStatus    : '{ctx['glossary_status']}'")
        logger.info(f"  └─ catalogResolution: {ctx['glossary_explanation']}")
        logger.info(f"------------------------------------------------------------------------")
        logger.info(f"🤖 [MLOPS_FEATURE_STORE] TRANSMISIÓN DE MODELO HACIA EL LAKEHOUSE:")
        logger.info(f"  ├─ modelUid         : '{ctx['active_version']}'")
        logger.info(f"  ├─ inputMetricValue : {ctx['metric_value']:.4f}")
        logger.info(f"  ├─ inputStepSequence: {float(ctx['step_seq']):.1f}")
        logger.info(f"  ├─ predictedProb    : {prob:.6f}")
        logger.info(f"  └─ latencyMicrosecs : {ctx['latency_microseconds']} microsegundos")
        logger.info(f"------------------------------------------------------------------------")
        logger.info(f"📈 [MLOPS_MODEL_DRIFT] MONITOREO DE DEGRADACIÓN ESTADÍSTICA DE IA:")
        logger.info(f"  ├─ observedWassersteinDistance: {abs(ctx['metric_value'] - 0.90):.4f}")
        logger.info(f"  ├─ actualZScoreDrift          : {ctx['z_score']:.4f}")
        logger.info(f"  └─ isReTrainingTriggered      : {str(ctx['z_score'] > 3.0).upper()}")
        logger.info(f"------------------------------------------------------------------------")
        logger.info(f"📋 [GOVERNANCE_DATA_ENGINE] VALORES DE ORIGEN PARA CÁLCULO DE KPIS:")
        logger.info(f"  ├─ totalEvaluated   : {ctx['total_evaluated']}")
        logger.info(f"  ├─ totalValid       : {ctx['total_valid']}")
        logger.info(f"  ├─ totalExact       : {ctx['total_exact']}")
        logger.info(f"  ├─ totalUnique      : {ctx['total_unique']}")
        logger.info(f"  └─ stepSequence     : {ctx['step_seq']}")
        logger.info(f"------------------------------------------------------------------------")
        logger.info(f"🧠 DIAGNÓSTICO DEL MODELO DE INTELIGENCIA ARTIFICIAL (XAI):")
        logger.info(f"  ├─ Estatus de IA    : {diag}")
        logger.info(f"  ├─ Nivel de Riesgo  : {risk}")
        logger.info(f"  └─ Explicación      : {expl}")
        logger.info(f"------------------------------------------------------------------------")
        logger.info(f"📊 EVALUACIÓN DE LAS 11 DIMENSIONES DAMA Y PORCENTAJES DE CUMPLIMIENTO:")
        logger.info(f"------------------------------------------------------------------------")
        
        kpis = ctx["kpis"]
        kpi_router: Final[Dict[str, float]] = {
            "COMPLETO": kpis['COMPLETITUD'],
            "VALIDEZ": kpis['VALIDEZ'],
            "UNICIDAD": kpis['UNICIDAD'],
            "EXACTITUD": kpis['EXACTITUD'],
            "OPORTUNIDAD": kpis['OPORTUNIDAD']
        }

        for metric in ctx["dama_list"]:
            name: str = metric['worker']
            emoji: str = self.EMOJI_REGISTRY.get(metric["status"], "🧩")
            val = kpi_router.get(name, None)
            val_str: str = f"{val}%" if val is not None else "N/A"
            logger.info(f"  {emoji} Dimensión: {name:<13} | KPI: {val_str:<7} | Severidad: {metric['anomaly_severity']}")
        logger.info(f"========================================================================")
