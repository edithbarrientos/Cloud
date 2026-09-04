# -*- coding: utf-8 -*-
"""
Autor: EdithBG <edithbg@corporativo.internal>
Capa de Infraestructura: Generación Dinámica de Planos de Arquitectura (Blueprint-as-Code)
"""

import os

from graphviz import Digraph

from src.domain.qa_contracts import StressJobRequest
from src.domain.qa_observers import QAQualityObserver


class DynamicFlowChartObserver(QAQualityObserver):
    """
    [PATRÓN OBSERVER]: Suscriptor encargado de dibujar de forma 100% interactiva
    el diagrama de flujo de negocio que el motor acaba de validar, aplicando las técnicas avanzadas de Shopify.
    """
    def notificar_evento_final(self, job: StressJobRequest, reporte: dict) -> None:
        print("🎨 [OBSERVER-VISUAL]: Renderizando plano dinámico interactivo por bucles vectoriales (SVG)...")

        # Formato SVG para habilitar Tooltips interactivos flotantes al pasar el puntero en la página web
        dot = Digraph(comment="Dynamic Architecture Blueprint", format="svg")
        dot.attr(rankdir="TB", size="12,12", bgcolor="#FFFFFF")
        dot.attr('node', style='filled,rounded', fontname='Helvetica', penwidth='2')

        # 🪐 MATIZ B Y D: Renderizado condicional de figuras según el tipo de componente y Tooltips dinámicos
        for nodo in job.nodos_arquitectura:
            tipo_label = nodo.label.lower()
            if "database" in tipo_label or "redis" in tipo_label or "lakehouse" in tipo_label:
                figura = "cylinder"
            elif "gate" in tipo_label or "resultado" in tipo_label:
                figura = "ellipse"
            else:
                figura = "rect"  # Caja estándar para microservicios y APIs REST

            dot.node(
                name=nodo.id_nodo,
                label=nodo.label,
                shape=figura,
                fillcolor=nodo.color_hex or "#EDF2F7",
                tooltip=f"Componente: {nodo.label}\nEstatus de la Aduana: Certificado en {job.sprint_activo}"
            )

        # 🪐 MATIZ A (Subgrafos de Alineación): Forzar a que las bases de datos compartan la misma línea horizontal
        nodos_cache = [n.id_nodo for n in job.nodos_arquitectura if "redis" in n.label.lower() or "cache" in n.label.lower()]
        if len(nodos_cache) > 1:
            with dot.subgraph() as subs:
                subs.attr(rank='same')
                for n_id in nodos_cache:
                    subs.node(n_id)

        # Bucle de Relaciones: Conectar los componentes individuales mediante las flechas de transacciones
        for conexion in job.conexiones_arquitectura:
            dot.edge(
                tail_name=conexion.origen,
                head_name=conexion.destino,
                label=f" {conexion.label} ",
                fontname="Helvetica",
                fontsize="10"
            )

        # Estampar el veredicto definitivo del Quality Gate de forma inteligente
        # Cierre del Quality Gate
        status_gate = reporte.get("resultado_auditoria", "FAIL")
        color_final = "#C6F6D5" if status_gate == "PASS" else "#FED7D7"
        texto_final = "🏆 QUALITY GATE: APROBADO" if status_gate == "PASS" else "🚨 QUALITY GATE: RECHAZADO"
        id_cierre = "GATE_RESULT"

        tooltip_final = (
            f"Métricas de Red:\n- Latencia: {reporte['telemetria_red']['latencia_p95_ms']}ms\n"
            f"- Errores: {reporte['telemetria_red']['error_rate_porcentaje']}%"
        )

        # Recortamos los parámetros rompiendo la llamada en múltiples renglones limpios
        dot.node(
            name=id_cierre,
            label=f"{texto_final}\nAudit: {reporte.get('audit_id')}",
            fillcolor=color_final,
            shape='ellipse',
            tooltip=tooltip_final
        )

        if job.nodos_arquitectura:
            ultimo_nodo_id = job.nodos_arquitectura[-1].id_nodo
            dot.edge(ultimo_nodo_id, id_cierre, label=" Veredicto Final")

        os.makedirs("data/diagramas", exist_ok=True)
        ruta_salida = os.path.join("data/diagramas", f"blueprint_{reporte.get('audit_id')}")
        dot.render(ruta_salida, cleanup=True)
        print(f"🏆 [QA-ENGINE-VISUAL]: Plano interactivo SVG exportado con éxito en '{ruta_salida}.gv.svg'.")
