# -*- coding: utf-8 -*-
"""
Autor: EdithBG <edithbg@corporativo.internal>
Organización: Plataforma Tecnológica TALOS - Core QA Team
Capa: Capa de Infraestructura / Analítica Reportes
Componente: Generador Automatizado de Reportes Ejecutivos en PDF (qa_pdf_observer)
"""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer
from src.domain.qa_chart_generator import QaChartGenerator
from src.domain.qa_contracts import StressJobRequest
from src.domain.qa_observers import QAQualityObserver


class LocalReportPdfObserver(QAQualityObserver):
    """
    [PATRÓN OBSERVER]: Suscriptor encargado de consolidar las métricas analíticas,
    las gráficas de Matplotlib y el diagrama de flujo en un PDF dinámico para el Lakehouse.
    """

    def notificar_evento_final(self, job: StressJobRequest, reporte: dict) -> None:
        print("📄 [OBSERVER-PDF]: Generando el Reporte Ejecutivo Certificado en formato PDF...")
        
        # 1. Definición dinámica e inmutable de rutas en la Landing Zone (Capa Bronze)
        sprint_limpio = job.sprint_activo.replace(" ", "_").lower()
        id_caso_uso = job.body_template.get("correlation_id", "UC-GENERIC")
        target_host = job.target_url.split("//")[-1].replace(".", "-").replace(":", "-")
        audit_id = reporte.get("audit_id", "GENERIC-ID")
        
        nombre_pdf = f"certificacion_{sprint_limpio}_{id_caso_uso}_{target_host}_{audit_id}.pdf"
        os.makedirs("data/bronze/reports", exist_ok=True)
        ruta_pdf = os.path.join("data/bronze/reports", nombre_pdf)
        
        # 2. Configuración de lienzo y paleta tipográfica corporativa
        doc = SimpleDocTemplate(ruta_pdf, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        styles = getSampleStyleSheet()
        
        titulo_style = ParagraphStyle(
            'TituloCorp', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#1A365D'), spaceAfter=15
        )
        h2_style = ParagraphStyle(
            'SubtituloCorp', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor('#2B6CB0'), spaceBefore=10, spaceAfter=5
        )
        body_style = ParagraphStyle(
            'CuerpoCorp', parent=styles['BodyText'], fontSize=9, textColor=colors.HexColor('#2D3748'), spaceAfter=5
        )

        # 3. Ensamblaje de la narrativa ejecutiva y el linaje ágil
        story.append(Paragraph("📝 REPORTE EJECUTIVO DE INGENIERÍA DE CALIDAD", titulo_style))
        story.append(Paragraph(f"<b>Identificador Único de Auditoría:</b> {audit_id}", body_style))
        story.append(Paragraph(f"<b>Target Endpoint Evaluado:</b> {reporte.get('target_evaluado')}", body_style))
        story.append(Paragraph(f"<b>Estrategia de Carga Inyectada:</b> {reporte.get('estrategia_aplicada')}", body_style))
        
        status_gate = reporte.get("resultado_auditoria", "FAIL")
        color_status = "GREEN" if status_gate == "PASS" else "RED"
        story.append(Paragraph(f"<b>DICTAMEN FINAL DEL QUALITY GATE:</b> <font color='{color_status}'><b>{status_gate}</b></font>", body_style))
        story.append(Spacer(1, 8))
        
        # Inyección del Resumen Gerencial y Caso de Uso
        story.append(Paragraph("📋 Resumen Ejecutivo y Caso de Uso", h2_style))
        story.append(Paragraph(reporte["📋_resumen_ejecutivo"]["vision_general_gerencial"], body_style))
        story.append(Spacer(1, 8))
        
        # Inyección de Métricas Numéricas de Red
        story.append(Paragraph("📊 Resultados de Infraestructura y SLAs", h2_style))
        metricas = reporte["📊_resultados_y_metricas_clave"]
        story.append(Paragraph(f"• Percentil 95 de Latencia: {metricas['percentil_p95_ms']} ms (SLA Max: {metricas['sla_maximo_tolerado_ms']} ms)", body_style))
        story.append(Paragraph(f"• Total Peticiones en Ráfaga: {metricas['total_peticiones_inyectadas']}", body_style))
        story.append(Paragraph(f"• Tasa de Fallos Registrada: {metricas['tasa_error_porcentaje']}%", body_style))
        story.append(Spacer(1, 8))

        # 📈 INYECCIÓN DE LA GRÁFICA DE MATPLOTLIB: Dibuja las curvas analíticas al vuelo
        story.append(Paragraph("📈 Curva Analítica de Rendimiento e Inyección de Carga", h2_style))
        ruta_grafica_png = QaChartGenerator.generar_grafica_curva_sla(audit_id, job.sla_latencia_p95_ms)
        if os.path.exists(ruta_grafica_png):
            story.append(Image(ruta_grafica_png, width=420, height=210))
            story.append(Spacer(1, 10))

        # 🔄 INYECCIÓN DEL DIAGRAMA DE GRAPHVIZ: Plano visual dinámico multi-proyecto
        ruta_diagrama_png = os.path.join("data/diagramas", f"blueprint_{audit_id}.png")
        if os.path.exists(ruta_diagrama_png):
            story.append(Paragraph("🔄 Plano Visual de Flujo Funcional Validado", h2_style))
            story.append(Image(ruta_diagrama_png, width=420, height=210))
            story.append(Spacer(1, 10))

        # Inyección de Conclusiones y Recomendaciones Predictivas
        story.append(Paragraph("💡 Conclusiones y Ajustes de Infraestructura", h2_style))
        for recom in reporte["💡_conclusiones_y_recomendaciones"]["ajustes_exactos_requeridos"]:
            story.append(Paragraph(f"- {recom}", body_style))

        # 4. Compilar y firmar el binario del PDF de forma inmutable en el Data Lake
        doc.build(story)
        print(f"🏆 [OBSERVER-PDF]: PDF dinámico exportado con éxito en '{ruta_pdf}'. Ready para el Lakehouse.")