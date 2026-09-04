# -*- coding: utf-8 -*-
"""
Ecosistema Conversacional Agéntico TALOS (Total Automated Logistics & Operations System)
Capa de Arquitectura: Capa de Dominio (Reglas de Negocio Puras)
Componente: Catálogo Centralizado de Identidades y Fallback de Agentes (agents_registry)

Gobernado por la matriz de la Fase 0, este componente actúa como el registro oficial
de sub-agentes autorizados para operar en la plataforma. Provee las directrices base
e identidades del sistema (System Prompts) en caso de que ocurra una degradación del
servicio o desconexión con el clúster central de Azure Cache for Redis.

Autor: EdithBG <edithbg@corporativo.internal>
Co-Autores / Revisores: Comité de Gobierno Federado (CISO / CDO)
Fecha de Creación: 2026-07-27
Versión del Registro: 1.1.0-PROD
"""

from typing import Dict, Set

# ==============================================================================
# 🤖 SECCIÓN 1: VALIDACIÓN DE IDENTIDADES AUTORIZADAS (White List)
# ==============================================================================

# Conjunto inmutable de sub-agentes autorizados para operar en el bus interno.
# Si un payload de entrada solicita un perfil fuera de esta lista, el sistema lo rechaza.
AGENTES_AUTORIZADOS: Set[str] = {
    "logistica",
    "finanzas",
    "legal",
    "retencion",
    "general"
}


# ==============================================================================
# 🛡️ SECCIÓN 2: MATRIZ DE RESPALDO DE SYSTEM PROMPTS (Local Fallback Registry)
# ==============================================================================

# Diccionario tipado con las instrucciones de comportamiento base por especialidad.
# Garantiza que el microservicio de IA conserve su personalidad corporativa a costo $0.
AGENT_PROMPTS_FALLBACK: Dict[str, str] = {
    "logistica": (
        "Eres el Agente Especialista en Logística de TALOS. Tu única función es gestionar folios "
        "de envío, rastreo de camiones en ruta, validación de inventarios y estatus del almacén central. "
        "No estás autorizado para resolver dudas financieras o de facturación."
    ),
    "finanzas": (
        "Eres el Agente Especialista en Finanzas y Facturación de TALOS. Tu trabajo es interpretar "
        "estados de cuenta, recibos de pago, saldos pendientes y conciliaciones de facturas fiscales. "
        "Está estrictamente prohibido emitir datos de rutas de entrega o logística."
    ),
    "legal": (
        "Eres el Agente Consultor Legal and de Cumplimiento de TALOS. Tu objetivo es analizar "
        "cláusulas de contratos, términos de servicio institucionales y políticas de devoluciones. "
        "Debes responder con un lenguaje estrictamente formal, preciso y de alta cortesía corporativa."
    ),
    "retencion": (
        "Eres el Agente de Retención y Mitigación de Pérdida de Clientes (Churn) de TALOS. Tu única "
        "prioridad es calmar al usuario inconforme, entender la causa raíz de su frustración y "
        "ofrecer de forma autónoma las opciones de compensación preaprobadas por el área comercial."
    ),
    "general": (
        "Eres TALOS Core, el asistente central e inteligente de la empresa. Tu función es dar la "
        "bienvenida a los usuarios, resolver dudas informativas generales de la compañía, guiar al "
        "cliente a través del chat y canalizar la interacción con el sub-agente especialista adecuado."
    )
}


# ==============================================================================
# 🎛️ SECCIÓN 3: LOGICA DE NEGOCIO DEL REGISTRO (Helper Functions)
# ==============================================================================

def validar_y_obtener_prompt_local(perfil: str) -> str:
    """
    Función de control del dominio que valida el formato y extrae el prompt de respaldo.

    Parámetros:
    -----------
    perfil : str
        Nombre del sub-agente solicitado en el payload JSON.

    Retorna:
    --------
    str
        System Prompt inmutable de respaldo asignado al agente.
    """
    perfil_normalizado = perfil.strip().lower()

    # Validar contra la lista blanca para blindar las fronteras de la IA
    if perfil_normalizado not in AGENTES_AUTORIZADOS:
        return AGENT_PROMPTS_FALLBACK["general"]

    return AGENT_PROMPTS_FALLBACK.get(perfil_normalizado, AGENT_PROMPTS_FALLBACK["general"])
