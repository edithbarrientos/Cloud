# -*- coding: utf-8 -*-
"""
Ecosistema Conversacional Agéntico TALOS (Total Automated Logistics & Operations System)
Capa de Arquitectura: Capa de Dominio / Interfaces de Salida (Output Ports)
Componente: Puerto Abstracto del Motor de Inteligencia Artificial (AIEnginePort)

Aplica el principio de Inversión de Dependencias (SOLID - Dependency Inversion).
Define la abstracción pura del comportamiento que debe cumplir cualquier motor de
procesamiento de lenguaje natural en la plataforma TALOS, aislando el Core de
las librerías físicas o SDKs de proveedores específicos en la nube.

Autor: EdithBG <edithbg@corporativo.internal>
Co-Autores / Revisores: Comité de Gobierno Federado (CISO / CDO)
Fecha de Creación: 2026-07-27
Versión de la Interfaz: 1.0.0-PROD
"""

from abc import ABC, abstractmethod

from src.domain.contracts import AIEngineRequest, AIEngineResponse


class AIEnginePort(ABC):
    """
    Clase Base Abstracta (Interfaz) que actúa como el Puerto del Motor de IA.

    Obliga a que todos los adaptadores tecnológicos de infraestructura (como el
    conector oficial de Azure OpenAI o el sistema de Mock local de contingencia)
    implementen el procesamiento de cómputo lingüístico bajo hilos asíncronos concurrentes.
    """

    @abstractmethod
    async def procesar_computo_linguistico(self, request: AIEngineRequest) -> AIEngineResponse:
        """
        Ejecuta de forma asíncrona la inferencia lingüística y el cercado semántico (RAG).

        Este método representa la aduana de ejecución probabilística del sistema. Recibe
        el payload validado por Pydantic con su Correlation ID integrado, orquesta los
        mensajes y entrega la respuesta final unificada junto con la telemetría de costos.

        Parámetros:
        -----------
        request : AIEngineRequest
            Objeto estructurado del modelo canónico que contiene el contexto RAG,
            el historial de Redis y la pregunta del cliente.

        Retorna:
        --------
        AIEngineResponse
            Objeto estructurado que contiene el texto de salida gobernado, auditoría de
            seguridad del CISO y el desglose financiero de tokens consumidos para OneLake.

        Excepciones:
        ------------
        asyncio.TimeoutError : Cuando el tiempo de respuesta excede el límite del .env
        Exception : Cualquier fallo en los sockets de red de la API externa
        """
        pass
