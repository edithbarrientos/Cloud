# -*- coding: utf-8 -*-
"""
Ecosistema Conversacional Agéntico TALOS (Total Automated Logistics & Operations System)
Capa de Arquitectura: Capa de Dominio (Reglas de Negocio Puras)
Componente: Contratos Canónicos de Frontera (Validación Estricta de Datos)

Este módulo implementa el escudo de validación de tipos e integridad estructural
para el microservicio 'talos-service-ia-engine' utilizando Pydantic v2. Garantiza
el cumplimiento de la Matriz de Trazabilidad de la Fase 0, obligando la presencia
del Correlation ID para el linaje analítico y OpenTelemetry.

Autor: EdithBG <edithbg@corporativo.internal>
Co-Autores / Revisores: Comité de Gobierno Federado (CDO / CISO)
Fecha de Creación: 2026-07-27
Versión del Contrato: 1.1.0-PROD (Multi-Agent Enriched)
Licencia: Propiedad Intelectual Corporativa Confidencial - Uso Exclusivo TALOS
"""

from typing import List, Optional

from pydantic import BaseModel, Field  # 🚨 Importación mandatoria para validación en la frontera

# ==============================================================================
# 📥 SECCIÓN 1: CONTRATO DE ENTRADA UNIFICADO (Input Contract - AIEngineRequest)
# ==============================================================================

class RAGContext(BaseModel):
    """
    Modelo de Datos para el Contexto de Generation-Augmented Generation (RAG).

    Cerca el comportamiento del LLM inyectando fragmentos verídicos de información
    institucional extraídos previamente de la Malla Vectorial (Azure AI Search),
    mitigando al 100% el riesgo de alucinación semántica.
    """
    origen_documento_id: str = Field(
        ...,
        description="Identificador único (UUID/Hash) del manual, política o PDF corporativo validado en Azure Purview."
    )
    fragmento_legal_veridico: str = Field(
        ...,
        description="Bloque de texto (Chunk) literal y aprobado por el área Legal que contiene la respuesta a la duda del cliente."
    )


class ChatMessage(BaseModel):
    """
    Estructura de Datos Unificada para Mensajes Individuales del Historial.

    Normaliza el formato de intercambio de diálogos del Chatbot de acuerdo con
    los estándares del SDK oficial de OpenAI.
    """
    role: str = Field(
        ...,
        description="Rol emisor del mensaje en el flujo conversacional. Valores válidos: 'user', 'assistant' o 'system'."
    )
    content: str = Field(
        ...,
        description="Contenido textual explícito o cuerpo del mensaje enviado por el emisor."
    )


class ChatContext(BaseModel):
    """
    Modelo del Contexto Conversacional Activo del Cliente.

    Consolida la pregunta actual en lenguaje natural junto con la memoria histórica
    de mensajes vivos recuperados de forma ultrarrápida desde Azure Cache for Redis.
    """
    texto_usuario_libre: str = Field(
        ...,
        description="Consulta o pregunta actual del usuario final o sistema comercial recibida desde el gateway perimetral."
    )
    historial_reciente_cache: List[ChatMessage] = Field(
        default=[],
        description="Colección secuencial de mensajes previos (Memoria de Relación) con un TTL de 24 horas máximo en caché."
    )


class RoutingConfig(BaseModel):
    """
    Matriz de Configuración y Enrutamiento de Hardware e Identidad de Inteligencia Artificial.

    Permite al 'Prompt Router' inyectar variables en caliente para controlar qué modelo
    de lenguaje procesará la solicitud y qué sub-agente dinámico se instanciará desde Redis.
    """
    modelo_asignado: str = Field(
        ...,
        description="Identificador del LLM seleccionado para el cómputo (Ej: 'gpt-4o-mini' para FAQs o 'gpt-4' para contratos complejos)."
    )
    temperatura_computo: float = Field(
        default=0.0,
        description="Grado de aleatoriedad del LLM. El valor 0.0 fuerza al motor a ser determinista, analítico y matemático."
    )
    max_tokens_permitidos: int = Field(
        default=300,
        description="Límite estricto de tokens de salida (generación) asignados para evitar consumos anárquicos o desbordes de presupuesto."
    )
    # 🤖 MULTI-AGENTE: Define la identidad y especialidad del sub-agente inyectado en caliente
    perfil_agente: str = Field(
        ...,
        description="Especialidad del agente: 'logistica', 'finanzas', 'legal', 'general'"
    )


class AIEngineRequest(BaseModel):
    """
    Contrato de Entrada Principal para la Capa de Cómputo Cognitivo.

    Esta clase es la 'Aduana de Software' del microservicio. Valida y tipa todo el
    payload JSON enviado por el Agente Orquestador Central de TypeScript antes de invocar
    las APIs de GenAI externas de forma privada.
    """
    correlation_id: str = Field(
        ...,
        description="Identificador único global (UUID) de la transacción generado en el gateway de ingesta para trazabilidad distribuida (W3C)."
    )
    canal_usuario_id: str = Field(
        ...,
        description="Identificador único físico de la red de contacto (Ej: Número telefónico de WhatsApp o Token de sesión web)."
    )
    configuracion_ruteo: RoutingConfig = Field(
        ...,
        description="Bloque de parámetros de hardware e identidad de IA asignado por el enrutador inteligente."
    )
    contexto_inyectado_rag: Optional[RAGContext] = Field(
        default=None,
        description="Bloque opcional de conocimiento corporativo inyectado si la intención requiere validación de manuales."
    )
    conversacion_actual: ChatContext = Field(
        ...,
        description="Contenido lingüístico e historial histórico unificado que procesará el motor probabilístico."
    )


# ==============================================================================
# 📤 SECCIÓN 2: CONTRATO DE SALIDA UNIFICADO (Output Contract - AIEngineResponse)
# ==============================================================================

class TelemetryConsumption(BaseModel):
    """
    Modelo Analítico de Telemetría e Infraestructura de Consumo de Inteligencia Artificial.

    Soporta el pilar de 'Ingestión Histórica (Triple Beneficio)' enviando métricas crudas
    de costos, latencias y hardware hacia Azure Fabric OneLake para auditorías en tiempo real.
    """
    modelo_utilizado: str = Field(
        ...,
        description="Modelo físico de Azure OpenAI que computó la respuesta (o 'CIRCUIT_BREAKER_LOCAL_FALLBACK' si se activó el Circuit Breaker)."
    )
    tokens_prompt_entrada: int = Field(
        ...,
        description="Cantidad exacta de tokens procesados en el prompt de entrada (Contexto RAG + Identidad de Agente + Historial)."
    )
    tokens_completion_salida: int = Field(
        ...,
        description="Cantidad exacta de tokens generados por el LLM en la respuesta final."
    )
    tokens_totales_facturables: int = Field(
        ...,
        description="Suma total de tokens cobrados en la transacción (Insumo directo para calcular el ROI financiero)."
    )
    latencia_computo_milisegundos: int = Field(
        ...,
        description="Tiempo transcurrido en milisegundos desde que el request tocó FastAPI hasta que se emitió el JSON de salida."
    )


class SecurityAudit(BaseModel):
    """
    Matriz de Control de Riesgo, Seguridad de la Información y Cumplimiento de Guardrails.

    Garantiza al CISO que cada frase generada por la Inteligencia Artificial fue auditada
    y filtrada contra inyecciones de prompts o fuga de datos sensibles operacionales.
    """
    guardrails_entrada_aprobados: bool = Field(
        default=True,
        description="Indica si la pregunta del cliente superó con éxito los filtros de seguridad de entrada (Input Guardrails)."
    )
    guardrails_salida_aprobados: bool = Field(
        default=True,
        description="Indica si el texto generado superó los filtros contra lenguaje inapropiado o fuga de información confidencial."
    )
    score_confianza_rag: float = Field(
        ...,
        description="Métrica matemática de precisión semántica (0.0 a 1.0) que indica la correlación entre la respuesta y el manual de la empresa."
    )


class AIEngineResponse(BaseModel):
    """
    Contrato de Salida Principal Emitido por la Capa de Cómputo Cognitivo.

    Devuelve la respuesta fluida, limpia y gobernada al bus de eventos de salida junto con
    la telemetría distribuida completa. Mantiene el Correlation ID intacto para asegurar
    la trazabilidad tridimensional.
    """
    correlation_id: str = Field(
        ...,
        description="Retorna estrictamente el mismo Correlation ID de entrada para amarrar de forma inmutable el linaje del dato."
    )
    canal_usuario_id: str = Field(
        ...,
        description="Identificador del cliente final que recibirá la respuesta en su pantalla."
    )
    text_respuesta_generada: str = Field(
        ...,
        description="Respuesta final en lenguaje natural estructurada por el motor y acotada rigurosamente por las políticas de la empresa."
    )
    telemetria_consumo: TelemetryConsumption = Field(
        ...,
        description="Bloque de métricas de rendimiento e infraestructura listas para Big Data analítica."
    )
    auditoria_seguridad: SecurityAudit = Field(
        ...,
        description="Bloque de validaciones de ciberseguridad y riesgo corporativo exigidos por el CISO."
    )
