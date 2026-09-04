# -*- coding: utf-8 -*-
"""
Autor: EdithBG <edithbg@corporativo.internal>
Organización: Plataforma Tecnológica TALOS - Core QA Team
Componente: Servidor API Maestro y Bootstrap del Patrón Observer (main)
"""

import logging
import os

from fastapi import BackgroundTasks, FastAPI, status

from src.domain.qa_contracts import StressJobRequest
from src.domain.qa_log_observer import DataLakeQaLogObserver
from src.domain.qa_observers import HttpPipelineWebhookObserver, LocalReportJsonObserver
from src.domain.qa_pdf_observer import LocalReportPdfObserver
from src.domain.qa_slack_observer import SlackAlertCrisisObserver
from src.domain.qa_visualizer import DynamicFlowChartObserver
from src.factory.chain_factory import QAChainFactory

# ==============================================================================
# 📊 BOOTSTRAP DE LOGS CORPORATIVO DE OBSERVABILIDAD
# ==============================================================================
os.makedirs("data", exist_ok=True)
logging.basicConfig(
    filename="data/app_execution.log",
    level=logging.INFO,
    format="%(message)s"  # Las trazas ya se inyectan como strings JSON estructurados desde la cadena
)

# ==============================================================================
# 📡 INICIALIZACIÓN DEL SERVIDOR API FASTAPI
# ==============================================================================
app = FastAPI(
    title="Core QA Engine API",
    description="Plataforma elástica y agnóstica de Ingeniería de Calidad y Gobernanza Cognitiva en Bucle Cerrado",
    version="6.2.0"
)


class ClosedLoopQualityCoordinator:
    """
    [PATRÓN OBSERVER]: Coordinador central que implementa la orquestación
    de las 6 salidas analíticas simultáneas al cerrarse el ciclo de calidad.
    """
    _observers = [
        LocalReportJsonObserver(),      # 1. Persiste el JSON para el Dashboard Web de Sprints
        HttpPipelineWebhookObserver(),  # 2. Responde el veredicto PASS/FAIL al Webhook de CI/CD
        DynamicFlowChartObserver(),     # 3. Dibuja de forma dinámica el diagrama de flujo SVG interactivo
        LocalReportPdfObserver(),       # 4. Compila el reporte PDF gerencial con gráficas de Matplotlib
        SlackAlertCrisisObserver(),     # 5. Dispara tarjetas de crisis de red inmediatas a los ingenieros
        DataLakeQaLogObserver()         # 6. Vuelca de forma inmutable el linaje de logs al Data Lakehouse
    ]

    @classmethod
    def despachar_notificaciones_finales(cls, job: StressJobRequest, reporte: dict) -> None:
        """Gatilla de forma iterativa y polimórfica a todos los suscriptores registrados."""
        for observer in cls._observers:
            try:
                observer.notificar_evento_final(job, reporte)
            except Exception as obs_error:
                # Recorte de cadena larga para cumplir con el margen de 150 caracteres de Ruff
                print(
                    f"🚨 [OBSERVER-ERROR]: Falla en suscriptor analítico "
                    f"{observer.__class__.__name__}: {str(obs_error)}"
                )


# ==============================================================================
# ⚙️ TRABAJADOR DE FONDO ASÍNCRONO (Nativo de Python)
# ==============================================================================
def pipeline_ingenieria_calidad_worker(job: StressJobRequest):
    """
    [TAREA EN SEGUNDO PLANO]: Esta función procesa de forma aislada las ráfagas pesadas de Locust,
    las 7 etapas de calidad y la evaluación del LLM sin congelar el hilo de FastAPI.
    """
    # 🏭 ABSTRACT FACTORY: El worker no sabe cómo se arma la cadena, solo invoca la cabeza del pipeline
    pipeline_calidad = QAChainFactory.construir_pipeline_calidad_total()

    # Inyectar el ID de auditoría efímero para este Sprint y Caso de Uso
    audit_id = f"AUDIT-GATE-PERFECTION-{os.getpid()}"
    contexto_compartido = {"audit_id": audit_id}

    # 🔀 DISPARAR LA CADENA DE RESPONSABILIDAD (Las 7 etapas industriales automatizadas)
    exito_cadena = pipeline_calidad.procesar_aduana_qa(job, contexto_compartido)

    if exito_cadena and "reporte_ejecutivo" in contexto_compartido:
        print("🏆 [COORDINADOR]: Cadena de calidad completada con éxito. Gatillando matriz de observadores...")
        ClosedLoopQualityCoordinator.despachar_notificaciones_finales(
            job, contexto_compartido["reporte_ejecutivo"]
        )
    else:
        # Recorte estético de string para el linter
        print(
            "🚨 [COORDINADOR-ABORTADO]: El flujo de control se interrumpió "
            "por violación de SLA o falla crítica."
        )


# ==============================================================================
# 📡 ENDPOINTS DE CONTROL PERIMETRAL
# ==============================================================================
@app.post(
    "/api/v1/stress/launch",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Quality Gate Central: Detona una prueba automatizada en bucle cerrado guiada por GenAI"
)
async def launch_stress_test(request: StressJobRequest, background_tasks: BackgroundTasks):
    """
    Aduana de entrada de la API. Valida el contrato universal Pydantic en 2 milisegundos,
    responde de inmediato con estatus 202 (Accepted) y encola la ráfaga de forma asíncrona.
    """
    # Delegar la tarea pesada al pool de corrutinas de fondo nativas de FastAPI
    background_tasks.add_task(pipeline_ingenieria_calidad_worker, request)

    return {
        "status": "QUEUED_ARCHITECTURAL_PERFECTION",
        "message": "Evaluando el Caso de Uso en bucle cerrado de forma asíncrona. El pipeline de CI/CD ha sido liberado.",
        "perfil_ataque_activo": request.perfil_ataque.upper(),
        "sprint_asociado": request.sprint_activo
    }
