# -*- coding: utf-8 -*-
"""
Autor: EdithBG <edithbg@corporativo.internal>
Capa de Fábrica: Encapsulamiento del Ciclo de Vida de los Eslabones del Testing
"""

from src.domain.qa_chain import CognitiveEvaluationHandler, DataGenerationHandler, ExecutionStressHandler, QAHandler


class QAChainFactory:
    """Implementa el Patrón Abstract Factory para centralizar y aislar la inicialización de las 7 etapas de calidad."""
    @staticmethod
    def construir_pipeline_calidad_total() -> QAHandler:
        """Instancia los componentes individuales y teje la secuencia inmutable de aduanas lógicas."""
        # 1. Aprovisionar los manejadores individuales desacoplados (Responsabilidad Única)
        eslabon_datos = DataGenerationHandler()     # Etapa 1 y 2 (Planificación y Muestreo)
        eslabon_estres = ExecutionStressHandler()   # Etapa 3 y 4 (Inspección y Registro en caliente)
        eslabon_auditoria = CognitiveEvaluationHandler() # Etapa 5 y 6 (Análisis y Acción Correctiva por IA)

        # 2. Configurar el eslabonamiento rígido del flujo de control (Chain of Responsibility)
        eslabon_datos.establecer_siguiente(eslabon_estres).establecer_siguiente(eslabon_auditoria)

        # Retorna el punto de entrada de la cadena listo para recibir requerimientos desde FastAPI
        return eslabon_datos
