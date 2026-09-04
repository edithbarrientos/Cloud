# -*- coding: utf-8 -*-
"""
Autor: EdithBG <edithbg@corporativo.internal>
Organización: Plataforma Tecnológica TALOS - Core QA Team
Contrato Canónico Universal de Entrada para el Quality Gate (Pydantic v2)
"""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class FlowNode(BaseModel):
    """Mapea una entidad física de la arquitectura para el renderizado dinámico."""
    id_nodo: str = Field(..., description="Identificador alfanumérico único del componente (Ej: 'N1')")
    label: str = Field(..., description="Texto descriptivo visible dentro de la caja")
    color_hex: Optional[str] = Field(default="#EBF8FF", description="Código hexadecimal para el fondo visual de la caja")

class FlowEdge(BaseModel):
    """Mapea el flujo funcional y la conexión direccional entre dos componentes."""
    origen: str = Field(..., description="ID del nodo emisor de la transacción")
    destino: str = Field(..., description="ID del nodo receptor de la transacción")
    label: Optional[str] = Field(default="", description="Metadatos o protocolo que viaja en la flecha (Ej: 'HTTPS POST')")

class HumanApprovalSign(BaseModel):
    """Bloque de auditoría inmutable para el mecanismo Human-in-the-Loop."""
    aprobado_por_usuario: Optional[str] = Field(default=None, description="Email institucional del Ingeniero firmante")
    justificacion_comite: Optional[str] = Field(default=None, description="Minuta o justificación del cambio técnico")
    token_autorizacion_rbac: Optional[str] = Field(default=None, description="Firma criptográfica extraída de Microsoft Entra ID")

class StressJobRequest(BaseModel):
    """Esquema universal abstracto que rige las aduanas de inyección del core-qa-engine."""
    target_url: str = Field(..., description="URL base pública o privada del microservicio bajo prueba")
    target_endpoint: str = Field(..., description="Ruta transaccional específica (Ej: '/api/v1/compute/language')")
    perfil_ataque: Literal["stress", "spike", "soak"] = Field(default="stress", description="Estrategia polimórfica de rampa de hilos")
    usuarios_maximos: int = Field(..., description="Límite superior de concurrencia elástica para evaluar escalabilidad")
    duracion_segundos: int = Field(..., description="Tiempo total asignado para la simulación de ráfaga")
    sla_latencia_p95_ms: int = Field(default=2000, description="Umbral máximo tolerado para el percentil 95 de red")
    sla_max_error_rate: float = Field(default=1.0, description="Porcentaje máximo admitido de transacciones HTTP fallidas")
    ai_guidance_prompt: str = Field(..., description="Directrices en lenguaje natural para que el LLM fabrique tráfico sintético")
    body_template: Dict[str, Any] = Field(..., description="Plantilla abstracta en Jinja2 amoldable al contrato del proyecto")
    webhook_notificacion: Optional[str] = Field(default=None, description="URL callback de retorno para el pipeline de CI/CD o Slack")
    sprint_activo: str = Field(..., description="Identificador del ciclo ágil en desarrollo para el Dashboard (Ej: 'Sprint 24')")
    tester_responsable: str = Field(default="Automated AI Engine", description="Entidad o pipeline que gatilla la prueba")
    fase_ciclo_vida: Literal["En revision", "Resuelto", "Necesita volver a probarse"] = Field(default="En revision")
    validacion_humana: Optional[HumanApprovalSign] = Field(default=None, description="Firma de autorización manual post-crisis")
    nodos_arquitectura: List[FlowNode] = Field(default=[], description="Lista de componentes de hardware a dibujar")
    conexiones_arquitectura: List[FlowEdge] = Field(default=[], description="Lista de relaciones lógicas del flujo funcional")
