# -*- coding: utf-8 -*-
"""
Autor: EdithBG <edithbg@corporativo.internal>
Organización: Plataforma Tecnológica TALOS - Core QA Team
Capa: Capa de Dominio (Reglas de Negocio Puras)
Componente: Observador de Alertas Inmediatas para Canales de Comunicación (qa_slack_observer)
"""

import httpx

from src.domain.qa_contracts import StressJobRequest
from src.domain.qa_observers import QAQualityObserver


class SlackAlertCrisisObserver(QAQualityObserver):
    """
    [PATRÓN OBSERVER]: Suscriptor elástico encargado de disparar notificaciones
    directas e inmediatas a los canales de ingeniería si el Quality Gate dictamina FAIL.
    """

    def notificar_evento_final(self, job: StressJobRequest, reporte: dict) -> None:
        status_gate = reporte.get("resultado_auditoria", "FAIL")

        # Este observador de crisis solo se activa de forma reactiva si el Quality Gate detecta un fallo
        if status_gate == "FAIL" and job.webhook_notificacion:
            print("📡 [OBSERVER-ALERTA]: Violación de SLA detectada. Despachando tarjeta de crisis...")

            # Construcción estructurada del payload con la paleta de colores del CISO
            texto_alerta = f"🚨 [QA-ENGINE VETO]: El {job.sprint_activo} ha sido bloqueado en el Quality Gate."
            diagnostico_ia = reporte["📋_resumen_ejecutivo"]["vision_general_gerencial"]
            target_full = f"{job.target_url}{job.target_endpoint}"
            latencia_str = f"{reporte['telemetria_red']['latencia_p95_ms']} ms"
            sla_str = f"{job.sla_latencia_p95_ms} ms"

            slack_payload = {
                "text": texto_alerta,
                "attachments": [
                    {
                        "color": "#E53E3E",  # Rojo Alerta institucional
                        "title": f"Auditoría Fallida: {reporte.get('audit_id')}",
                        "fields": [
                            {"title": "Caso de Uso", "value": job.sprint_activo, "short": True},
                            {"title": "Target Evaluado", "value": target_full, "short": True},
                            {"title": "Latencia p95 Registrada", "value": latencia_str, "short": True},
                            {"title": "Límite Máximo SLA", "value": sla_str, "short": True},
                            {"title": "Diagnóstico de la IA", "value": diagnostico_ia, "short": False}
                        ]
                    }
                ]
            }

            try:
                # Disparo síncrono con el cliente HTTPX confinado bajo un timeout estricto de 5 segundos
                with httpx.Client(timeout=5.0) as client:
                    client.post(job.webhook_notificacion, json=slack_payload)
                print("🏆 [OBSERVER-ALERTA]: Tarjeta de crisis enviada con éxito al canal de soporte.")
            except Exception as e:
                print(f"🚨 [OBSERVER-ALERTA-ERROR]: No se pudo contactar al canal de comunicación: {str(e)}")
